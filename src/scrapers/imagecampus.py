import feedparser
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


_IMAGE_FEED_URL = "https://www.imagecampus.edu.ar/?feed=rss2&post_type=empleos"
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
})


_PAGE_CACHE: dict[str, str] = {}
_SITE_BLOCKED = False

MAX_SEARCH_TERMS = 15


def _session_fetch(url: str) -> str | None:
    try:
        resp = _SESSION.get(url, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


def _cached_fetch(url: str) -> str | None:
    global _SITE_BLOCKED
    if _SITE_BLOCKED:
        return None
    if url in _PAGE_CACHE:
        return _PAGE_CACHE[url]
    html = _session_fetch(url)
    if html is not None and len(html) >= 500:
        _PAGE_CACHE[url] = html
    else:
        _SITE_BLOCKED = True
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
    return terms[:MAX_SEARCH_TERMS]


def _parse_job_detail(href: str) -> tuple[str, str, str, str]:
    slug = href.split("/")[-1]
    title = slug.replace("-", " ").title()
    description = ""
    workplace = ""
    posted_at = ""

    job_html = _cached_fetch(href)
    if not job_html:
        return title, description, workplace, posted_at

    if is_job_covered(job_html):
        return "", "", "", ""

    soup_job = BeautifulSoup(job_html, "html.parser")
    raw_text = soup_job.get_text(" ", strip=True)

    workplace = _extract_workplace(raw_text)
    description = clean_imagecampus_description(raw_text)
    description = truncate_description(description)
    return title, description, workplace, posted_at


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


def _collect_urls_via_search() -> list[str]:
    all_urls: list[str] = []
    seen: set[str] = set()

    for term in _build_search_terms():
        search_url = (
            "https://www.imagecampus.edu.ar/"
            f"?s={quote(term)}&post_type%5B%5D=empleos"
        )
        html = _cached_fetch(search_url)
        if not html:
            continue
        for url in _extract_job_links(html):
            if url not in seen:
                seen.add(url)
                all_urls.append(url)

    return all_urls


def _collect_urls_via_rss() -> list[str]:
    resp = _session_fetch(_IMAGE_FEED_URL)
    if not resp or len(resp) < 500:
        return []

    feed = feedparser.parse(resp)
    if not feed.entries:
        return []

    return [e.link for e in feed.entries if e.link]


def scrape_imagecampus(seen_urls: set[str]) -> list[Job]:
    global _SITE_BLOCKED
    all_urls = _collect_urls_via_search()

    if not all_urls:
        _SITE_BLOCKED = False
        all_urls = _collect_urls_via_rss()
        if not all_urls:
            print("[ImageCampus] No se pudo acceder (búsquedas ni RSS)")
            return []
        print(f"[ImageCampus] Usando RSS ({len(all_urls)} URLs)")

    jobs: list[Job] = []
    for href in all_urls:
        if href in seen_urls:
            continue
        seen_urls.add(href)

        title, description, workplace, posted_at = _parse_job_detail(href)
        if not title:
            continue

        job = Job(
            title=title,
            url=href,
            source="ImageCampus",
            country="Argentina",
            description=description,
            workplace=workplace,
            posted_at=posted_at,
        )
        jobs.append(job)

    return jobs
