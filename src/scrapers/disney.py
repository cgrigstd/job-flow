import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_BASE_URL = "https://www.disneycareers.com/en/search-jobs"
_CATEGORIES = [
    "Animation and Visual Effects",
    "Creative",
    "Graphic Design",
    "Production",
]
_MAX_PAGES = 10
_MAX_JOBS = 100


def _parse_disney_date(date_text: str) -> str:
    if not date_text:
        return ""
    text = date_text.lower().strip()
    now = datetime.now()

    m = re.search(r"(\d+)\s+day", text)
    if m:
        days = int(m.group(1))
        return (now - timedelta(days=days)).strftime("%Y-%m-%d")

    m = re.search(r"(\d+)\s+week", text)
    if m:
        weeks = int(m.group(1))
        return (now - timedelta(weeks=weeks)).strftime("%Y-%m-%d")

    m = re.search(r"(\d+)\s+month", text)
    if m:
        months = int(m.group(1))
        return (now - timedelta(days=months * 30)).strftime("%Y-%m-%d")

    if "today" in text:
        return now.strftime("%Y-%m-%d")

    if "yesterday" in text:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")

    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_text.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return ""


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for li in soup.select("ul#search-results-jobs li"):
        link = li.find("a")
        if not link:
            continue

        href = link.get("href", "")
        if not href or "/job/" not in href:
            continue

        url = f"https://www.disneycareers.com{href}" if href.startswith("/") else href

        h2 = link.find("h2")
        title = h2.get_text(strip=True) if h2 else ""
        if not title:
            continue

        brand_el = link.select_one("span.job-brand")
        brand = brand_el.get_text(strip=True) if brand_el else ""

        location_el = link.select_one("span.job-location")
        location = location_el.get_text(strip=True) if location_el else ""

        date_el = link.select_one("span.job-date-posted")
        date_posted = date_el.get_text(strip=True) if date_el else ""
        posted_at = _parse_disney_date(date_posted)

        jobs.append({
            "url": url,
            "title": title,
            "brand": brand,
            "location": location,
            "posted_at": posted_at,
        })

    return jobs


def _get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    pagination = soup.select_one("input.pagination-current")
    if pagination:
        max_page = pagination.get("max", "1")
        try:
            return min(int(max_page), _MAX_PAGES)
        except ValueError:
            pass
    return 1


def scrape_disney(seen_urls: set[str], cutoff: datetime | None = None) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for category in _CATEGORIES:
        if len(jobs) >= _MAX_JOBS:
            break

        import json
        import urllib.parse
        facet = json.dumps([{"key": "category", "value": category}])
        url = f"{_BASE_URL}?acm=ALL&alrpm=ALL&ascf={urllib.parse.quote(facet)}"

        html = fetch_page(url)
        if not html:
            continue

        total_pages = _get_total_pages(html)

        for page in range(1, total_pages + 1):
            if len(jobs) >= _MAX_JOBS:
                break

            page_url = f"{url}&p={page}" if page > 1 else url
            page_html = fetch_page(page_url) if page > 1 else html
            if not page_html:
                break

            results = _extract_jobs(page_html)
            if not results:
                break

            for r in results:
                if r["url"] in seen_urls or r["url"] in collected_urls:
                    continue

                if cutoff and r["posted_at"]:
                    try:
                        job_date = datetime.strptime(r["posted_at"], "%Y-%m-%d")
                        if job_date < cutoff:
                            continue
                    except ValueError:
                        pass

                collected_urls.add(r["url"])

                description = f"{r['brand']} | {r['location']}"
                if r["posted_at"]:
                    description += f" | Posted: {r['posted_at']}"

                jobs.append(Job(
                    title=r["title"],
                    url=r["url"],
                    source="Disney",
                    country=r["location"],
                    workplace="On-site",
                    description=description,
                    posted_at=r["posted_at"],
                ))

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
