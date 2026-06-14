from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from src.models import Job
from src.classifiers.specialties import SPECIALTIES
from src.utils.html_utils import (
    clean_imagecampus_description,
    fetch_page,
    is_job_covered,
    truncate_description,
)
from src.config import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT


_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
})


LISTING_URL = "https://www.imagecampus.edu.ar/busquedas"
_PAGE_CACHE: dict[str, str] = {}
_MAX_SEARCH_TERMS = 15


def _session_fetch(url: str) -> str | None:
    try:
        resp = _SESSION.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def _cached_fetch(url: str) -> str | None:
    if url in _PAGE_CACHE:
        return _PAGE_CACHE[url]
    html = _session_fetch(url)
    if html is not None:
        _PAGE_CACHE[url] = html
    return html


def _extract_job_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    urls: list[str] = []
    for link in soup.select("a"):
        href = link.get("href")
        if not href or "/busqueda/" not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        if not href.startswith("http"):
            href = "https://www.imagecampus.edu.ar" + href
        urls.append(href)
    return urls


def _build_search_terms() -> list[str]:
    used = set()
    terms: list[str] = []
    for spec in SPECIALTIES:
        if not spec.keywords:
            continue
        term = spec.keywords[0]
        if term in used:
            continue
        used.add(term)
        terms.append(term)
    return terms[:_MAX_SEARCH_TERMS]


def _parse_job_detail(href: str) -> tuple[str, str, str]:
    slug = href.split("/")[-1]
    title = slug.replace("-", " ").title()
    description = ""
    workplace = ""

    job_html = _cached_fetch(href)
    if not job_html:
        return title, description, workplace

    if is_job_covered(job_html):
        return "", "", ""

    soup_job = BeautifulSoup(job_html, "html.parser")
    raw_text = soup_job.get_text(" ", strip=True)

    workplace = _extract_workplace(raw_text)
    description = clean_imagecampus_description(raw_text)
    description = truncate_description(description)
    return title, description, workplace


def _extract_workplace(text: str) -> str:
    import re
    m = re.search(
        r'Lugar\s+de\s+trabajo\s*:\s*(remoto|presencial|híbrido|hibrido)',
        text,
        re.IGNORECASE,
    )
    if m:
        val = m.group(1).lower()
        return {"remoto": "remote", "presencial": "onsite", "híbrido": "hybrid", "hibrido": "hybrid"}.get(val, val)
    return ""


def _collect_all_urls() -> list[str]:
    all_urls: list[str] = []
    seen_urls: set[str] = set()

    html = _cached_fetch(LISTING_URL)
    if html:
        all_urls.extend(_extract_job_links(html))
        seen_urls.update(all_urls)

    for term in _build_search_terms():
        search_url = f"https://www.imagecampus.edu.ar/?s={quote(term)}&post_type%5B%5D=empleos"
        html = _cached_fetch(search_url)
        if not html:
            continue
        for url in _extract_job_links(html):
            if url not in seen_urls:
                seen_urls.add(url)
                all_urls.append(url)

    return all_urls


def _check_site_access() -> bool:
    html = _session_fetch(LISTING_URL)
    if not html:
        print(f"[ImageCampus] No se pudo acceder a {LISTING_URL}")
        return False
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "sin title"
    busqueda_links = [a.get("href") for a in soup.select("a") if a.get("href") and "/busqueda/" in a.get("href")]
    all_links = [a.get("href") for a in soup.select("a[href]") if a.get("href")]
    print(f"[ImageCampus] Listing: {len(html)}b | title={title[:60]} | enlaces totales={len(all_links)} | /busqueda/={len(busqueda_links)}")
    if len(html) < 1000:
        print(f"[ImageCampus] HTML completo ({len(html)}b): {html[:200]}")
    if not busqueda_links and all_links:
        print(f"[ImageCampus]   Muestra de enlaces: {all_links[:5]}")
    return len(busqueda_links) > 0


def scrape_imagecampus(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []

    if not _check_site_access():
        return jobs

    all_urls = _collect_all_urls()
    if not all_urls:
        print("[ImageCampus] No se encontraron URLs tras recorrer listing + búsquedas")
        return jobs

    for href in all_urls:
        if href in seen_urls:
            continue
        seen_urls.add(href)

        title, description, workplace = _parse_job_detail(href)
        if not title:
            continue

        job = Job(
            title=title,
            url=href,
            source="ImageCampus",
            country="Argentina",
            description=description,
            workplace=workplace,
        )
        jobs.append(job)

    return jobs
