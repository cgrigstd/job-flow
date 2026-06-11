from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_BASE_URL = "https://mx.ingamejob.com"
_MAX_PAGES = 15
_MAX_JOBS = 120


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for card in soup.find_all("div", class_="listing-job-info"):
        title_el = card.find("h5").find("a") if card.find("h5") else None
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if not title or not href:
            continue

        company_el = card.select_one("p:has(i.la-building-o) strong")
        company = company_el.get_text(strip=True) if company_el else ""

        location_el = card.select_one("p:has(i.la-map-marker)")
        location = location_el.get_text(strip=True) if location_el else ""
        if location:
            location = location.replace("\n", " ").strip()

        seniority_el = card.select_one("p:has(i.la-area-chart)")
        seniority = seniority_el.get_text(strip=True) if seniority_el else ""
        if seniority:
            seniority = seniority.replace("\n", " ").strip()

        emp_type_el = card.select_one("p:has(i.la-briefcase) span")
        emp_type = emp_type_el.get_text(strip=True) if emp_type_el else ""

        description_parts = [company] if company else []
        if location:
            description_parts.append(location)
        if seniority:
            description_parts.append(seniority)
        if emp_type:
            description_parts.append(emp_type)

        country = "Mexico"
        workplace = ""
        if location and "remote" in location.lower():
            workplace = "remote"

        jobs.append({
            "url": href,
            "title": title,
            "company": company,
            "location": location,
            "description": " - ".join(description_parts),
            "country": country,
            "workplace": workplace,
        })

    return jobs


def scrape_ingamejob(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for page in range(1, _MAX_PAGES + 1):
        if len(collected_urls) >= _MAX_JOBS:
            break

        url = f"{_BASE_URL}/en/jobs"
        if page > 1:
            url += f"?page={page}"

        html = fetch_page(url)
        if not html:
            break

        results = _extract_jobs(html)
        if not results:
            break

        for r in results:
            if r["url"] in seen_urls or r["url"] in collected_urls:
                continue
            collected_urls.add(r["url"])

            job = Job(
                title=r["title"],
                url=r["url"],
                source="InGameJob",
                country=r["country"],
                workplace=r["workplace"],
                description=r["description"],
            )
            jobs.append(job)

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
