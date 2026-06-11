from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_BASE_URL = "https://www.occ.com.mx"
_SEARCH_TERMS = [
    "animacion 3d", "modelado 3d", "diseñador 3d",
    "game developer", "rigging", "unity", "unreal",
    "diseño grafico", "multimedia", "vfx",
    "ilustrador", "animador", "videojuegos",
]
_MAX_SEARCH_TERMS = 5
_MAX_JOBS = 80


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for card in soup.find_all("div", class_="card-job-offer"):
        data_id = card.get("data-id", "")
        if not data_id:
            continue

        title_el = card.select_one("h2.ellipsis")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        if not title:
            continue

        company_el = card.select_one('a[href*="bolsa-de-trabajo"]')
        company = company_el.get_text(strip=True) if company_el else ""

        location_el = card.select_one("p.text-grey-900.m-0.text-sm.font-light")
        location = location_el.get_text(strip=True) if location_el else ""

        salary_el = card.find("span", class_=lambda c: c is not None and "text-grey-900" in c and "font-base" in c)
        salary = salary_el.get_text(strip=True) if salary_el else ""

        description = company
        if location:
            description += f" - {location}"
        if salary:
            description += f" | {salary}"

        jobs.append({
            "url": f"{_BASE_URL}/empleos/?job_id={data_id}",
            "title": title,
            "company": company,
            "location": location,
            "salary": salary,
            "description": description,
        })

    return jobs


def scrape_occ_mundial(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for term in _SEARCH_TERMS[:_MAX_SEARCH_TERMS]:
        if len(collected_urls) >= _MAX_JOBS:
            break

        search_url = f"{_BASE_URL}/empleos/?q={quote(term)}"
        html = fetch_page(search_url)
        if not html:
            continue

        results = _extract_jobs(html)
        for r in results:
            if r["url"] in seen_urls or r["url"] in collected_urls:
                continue
            collected_urls.add(r["url"])

            job = Job(
                title=r["title"],
                url=r["url"],
                source="OCC Mundial",
                country="Mexico",
                description=r["description"],
            )
            jobs.append(job)

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
