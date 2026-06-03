import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_ELEMPLEO_DOMAIN = "www.elempleo.com"
_ELEMPLEO_COUNTRY = "co"

_SEARCH_TERMS = [
    "animacion 3d", "modelado 3d", "game developer",
    "vfx", "rigging", "blender", "unreal", "unity",
    "animador", "videojuegos",
]

_MAX_SEARCH_TERMS = 5
_MAX_JOBS = 80


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for item in soup.find_all("div", class_=re.compile(r"result-item")):
        title_el = item.find("a", class_=re.compile(r"js-offer-title"))
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        if not title:
            continue

        href = title_el.get("href", "")
        if not href.startswith("http"):
            if href.startswith("/"):
                href = f"https://{_ELEMPLEO_DOMAIN}{href}"
            else:
                href = f"https://{_ELEMPLEO_DOMAIN}/{_ELEMPLEO_COUNTRY}/{href}"

        company_el = item.find(class_=re.compile(r"info-company-name"))
        company = company_el.get_text(strip=True) if company_el else ""

        city_el = item.find(class_=re.compile(r"info-city"))
        city = city_el.get_text(strip=True) if city_el else ""

        jobs.append({
            "url": href,
            "title": title,
            "company": company,
            "location": city,
        })

    return jobs


def scrape_elempleo(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for term in _SEARCH_TERMS[:_MAX_SEARCH_TERMS]:
        if len(collected_urls) >= _MAX_JOBS:
            break

        search_url = f"https://{_ELEMPLEO_DOMAIN}/{_ELEMPLEO_COUNTRY}/ofertas-empleo/?q={quote(term)}"
        html = fetch_page(search_url)
        if not html:
            continue

        results = _extract_jobs(html)
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
                source="Elempleo",
                country="Colombia",
                description=description,
            )
            jobs.append(job)

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
