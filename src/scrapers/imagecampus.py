from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.classifiers.specialties import SPECIALTIES
from src.utils.html_utils import (
    clean_imagecampus_description,
    fetch_page,
    is_job_covered,
    truncate_description,
)


LISTING_URL = "https://www.imagecampus.edu.ar/busquedas"
_PAGE_CACHE: dict[str, str] = {}
_MAX_SEARCH_TERMS = 15


def _cached_fetch(url: str) -> str | None:
    if url in _PAGE_CACHE:
        return _PAGE_CACHE[url]
    html = fetch_page(url)
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


def _parse_job_detail(href: str) -> tuple[str, str]:
    slug = href.split("/")[-1]
    title = slug.replace("-", " ").title()
    description = ""

    job_html = _cached_fetch(href)
    if not job_html:
        return title, description

    if is_job_covered(job_html):
        return "", ""

    soup_job = BeautifulSoup(job_html, "html.parser")
    raw_text = soup_job.get_text(" ", strip=True)
    description = clean_imagecampus_description(raw_text)
    description = truncate_description(description)
    return title, description


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


def scrape_imagecampus(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    all_urls = _collect_all_urls()

    for href in all_urls:
        if href in seen_urls:
            continue
        seen_urls.add(href)

        title, description = _parse_job_detail(href)
        if not title:
            continue

        job = Job(
            title=title,
            url=href,
            source="ImageCampus",
            country="Argentina",
            description=description,
        )
        jobs.append(job)

    return jobs
