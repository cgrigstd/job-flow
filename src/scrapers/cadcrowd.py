from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_BASE_URL = "https://www.cadcrowd.com/jobs/search"

_MAX_PAGES = 15
_MAX_JOBS = 150



def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for card in soup.select("div.job-search-job-item"):
        url = card.get("data-url", "")
        if not url:
            link = card.select_one("h4 a")
            url = link.get("href", "") if link else ""
        if not url or "/job/" not in url:
            continue

        title = card.get("data-title", "")
        if not title:
            title_el = card.select_one("h4 a")
            title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue

        info_items = card.select("div.job-search-job-info ul li")
        job_type = ""
        workplace = ""
        for li in info_items:
            text = li.get_text(strip=True)
            strong = li.find("strong")
            if strong:
                job_type = strong.get_text(strip=True)
            if text in ("Remote", "Hybrid", "On-site"):
                workplace = text

        description_el = card.select_one("div.jobs-description")
        description = description_el.get_text(" ", strip=True) if description_el else ""
        if len(description) > 300:
            description = description[:300] + "..."

        tags = [
            a.get_text(strip=True)
            for a in card.select("div.job-search-job-Category.labels a.badge")
        ]
        if tags:
            description += " | Skills: " + ", ".join(tags)

        country = ""
        for li in card.select("div.jobs-info-client-info ul li"):
            text = li.get_text(strip=True)
            if li.find("i", class_="fa-location-dot"):
                country = text
                break

        time_el = card.select_one("time.timeago")
        datetime_str = time_el.get("datetime", "") if time_el else ""

        jobs.append({
            "url": url,
            "title": title,
            "job_type": job_type,
            "workplace": workplace,
            "description": description,
            "country": country,
            "datetime": datetime_str,
        })

    return jobs


def scrape_cadcrowd(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for page in range(1, _MAX_PAGES + 1):
        if len(jobs) >= _MAX_JOBS:
            break

        url = f"{_BASE_URL}?page={page}"
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

            jobs.append(Job(
                title=r["title"],
                url=r["url"],
                source="CadCrowd",
                country=r["country"],
                workplace=r["workplace"],
                description=r["description"],
            ))

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
