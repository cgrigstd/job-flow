import requests
from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import detect_country
from src.config import ARC_DEV_URL


def scrape_arcdev(seen_urls: set[str]) -> list[Job]:
    try:
        response = requests.get(
            ARC_DEV_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception:
        return []

    jobs: list[Job] = []

    for link in soup.select("a"):
        href = link.get("href")

        if not href or "/remote-jobs/" not in href:
            continue

        if "/remote-jobs/details/" not in href and "/remote-jobs/j/" not in href:
            continue

        if not href.startswith("http"):
            href = "https://arc.dev" + href

        if href in seen_urls:
            continue
        seen_urls.add(href)

        title = link.get_text(strip=True)

        if not title or len(title) < 5:
            continue

        content = title.lower()
        country = detect_country(content)

        job = Job(
            title=title,
            url=href,
            source="ArcDev",
            country=country,
        )
        jobs.append(job)

    return jobs
