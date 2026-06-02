from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import (
    clean_imagecampus_description,
    fetch_page,
    is_job_covered,
    truncate_description,
)


LISTING_URL = "https://www.imagecampus.edu.ar/busquedas"
_PAGE_CACHE: dict[str, str] = {}


def _cached_fetch(url: str) -> str | None:
    if url in _PAGE_CACHE:
        return _PAGE_CACHE[url]
    html = fetch_page(url)
    if html is not None:
        _PAGE_CACHE[url] = html
    return html


def _collect_listing_urls() -> list[str]:
    html = _cached_fetch(LISTING_URL)
    if not html:
        return []
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


def scrape_imagecampus(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    listing_urls = _collect_listing_urls()

    for href in listing_urls:
        if href in seen_urls:
            continue
        seen_urls.add(href)

        slug = href.split("/")[-1]
        title = slug.replace("-", " ").title()
        description = ""

        job_html = _cached_fetch(href)
        if job_html:
            if is_job_covered(job_html):
                continue
            soup_job = BeautifulSoup(job_html, "html.parser")
            raw_text = soup_job.get_text(" ", strip=True)
            description = clean_imagecampus_description(raw_text)
            description = truncate_description(description)

        job = Job(
            title=title,
            url=href,
            source="ImageCampus",
            country="Argentina",
            description=description,
        )
        jobs.append(job)

    return jobs
