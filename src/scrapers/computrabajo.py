import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.classifiers.specialties import SPECIALTIES
from src.utils.html_utils import fetch_page, truncate_description


_COUNTRY_DOMAINS = [
    ("Mexico", "www.computrabajo.com.mx"),
    ("Argentina", "www.computrabajo.com.ar"),
    ("Colombia", "www.computrabajo.com.co"),
]

_SEARCH_TERMS = [
    "animacion 3d", "modelado 3d", "diseñador 3d",
    "game developer", "rigging", "unity", "unreal",
    "diseño grafico", "multimedia", "vfx",
]

_MAX_SEARCH_TERMS = 4
_MAX_JOBS_PER_DOMAIN = 80


def _extract_search_results(html: str, domain: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for article in soup.find_all("article", class_="box_offer"):
        link = article.find("a", href=re.compile(r"/ofertas-de-trabajo/oferta-de-trabajo-de-"))
        if not link:
            continue

        href = link.get("href", "")
        if not href.startswith("http"):
            href = f"https://{domain}{href}"

        title = link.get_text(strip=True)
        if not title:
            continue

        text = article.get_text(" ", strip=True)

        company = ""
        company_link = article.find("a", href=re.compile(r"/empresas/"))
        if company_link:
            company = company_link.get_text(strip=True)

        location = ""
        location_match = re.search(r"(?:^|\s)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:,\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)(?:\s|$)", text)
        if location_match:
            location = location_match.group(1)

        jobs.append({
            "url": href,
            "title": title,
            "company": company,
            "location": location,
        })

    return jobs


def _scrape_domain(domain: str, country: str, seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for term in _SEARCH_TERMS[:_MAX_SEARCH_TERMS]:
        if len(collected_urls) >= _MAX_JOBS_PER_DOMAIN:
            break

        search_url = f"https://{domain}/ofertas-de-trabajo/?q={quote(term)}"
        html = fetch_page(search_url)
        if not html:
            continue

        results = _extract_search_results(html, domain)
        for r in results:
            if r["url"] in seen_urls or r["url"] in collected_urls:
                continue
            collected_urls.add(r["url"])

            description = r["company"]
            if r["location"]:
                description += f" - {r['location']}"

            job = Job(
                title=r["title"],
                url=r["url"],
                source="Computrabajo",
                country=country,
                description=description,
            )
            jobs.append(job)

    return jobs


def scrape_computrabajo(seen_urls: set[str]) -> list[Job]:
    all_jobs: list[Job] = []

    for country, domain in _COUNTRY_DOMAINS:
        jobs = _scrape_domain(domain, country, seen_urls)
        for job in jobs:
            seen_urls.add(job.url)
        all_jobs.extend(jobs)

    return all_jobs
