from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_BASE_URL = "https://www.workwithindies.com/categories"
_CATEGORIES = [
    "art-animation",
    "audio",
    "business",
    "design",
    "marketing",
    "production",
    "programming",
    "qa-cs",
    "writing",
]
_MAX_JOBS = 100


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for link in soup.select("a.job-card"):
        href = link.get("href", "")
        if not href or "/careers/" not in href:
            continue

        url = f"https://www.workwithindies.com{href}" if href.startswith("/") else href

        title_el = link.select_one("div.job-card-title")
        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue

        company_el = link.select_one("div.job-card-text.bold")
        company = company_el.get_text(strip=True) if company_el else ""

        location_els = link.select("div.job-card-text.bold")
        location = location_els[-1].get_text(strip=True) if len(location_els) > 1 else ""

        jobs.append({
            "url": url,
            "title": title,
            "company": company,
            "location": location,
        })

    return jobs


def scrape_workwithindies(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for category in _CATEGORIES:
        if len(jobs) >= _MAX_JOBS:
            break

        url = f"{_BASE_URL}/{category}"
        html = fetch_page(url)
        if not html:
            continue

        results = _extract_jobs(html)
        for r in results:
            if r["url"] in seen_urls or r["url"] in collected_urls:
                continue
            collected_urls.add(r["url"])

            description = f"{r['company']} | {r['location']}" if r["company"] else r["location"]

            jobs.append(Job(
                title=r["title"],
                url=r["url"],
                source="Work With Indies",
                country=r["location"],
                workplace="Remote" if "anywhere" in r["location"].lower() else "On-site",
                description=description,
            ))

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
