import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from src.models import Job
from src.utils.html_utils import clean_html, truncate_description, detect_country
from src.config import DEFAULT_USER_AGENT, DEFAULT_TIMEOUT


def _parse_rss(url: str):
    resp = requests.get(
        url,
        headers={"User-Agent": DEFAULT_USER_AGENT},
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    return feedparser.parse(resp.content)


def scrape_rss_feed(
    name: str,
    url: str,
    seen_urls: set[str],
    cutoff: datetime,
) -> list[Job]:
    try:
        feed = _parse_rss(url)
    except Exception:
        return []

    jobs: list[Job] = []

    for entry in feed.entries:
        published = getattr(entry, "published_parsed", None)
        posted_at = ""

        if published:
            job_date = datetime(*published[:6])

            if job_date < cutoff:
                continue

            posted_at = job_date.strftime("%Y-%m-%d")

        if entry.link in seen_urls:
            continue
        seen_urls.add(entry.link)

        title = entry.title
        description = ""

        if hasattr(entry, "description"):
            description = clean_html(entry.description)
        elif hasattr(entry, "summary"):
            description = clean_html(entry.summary)

        country = detect_country(title + " " + description)
        description = truncate_description(description)

        job = Job(
            title=title,
            url=entry.link,
            source=name,
            country=country,
            description=description,
            posted_at=posted_at,
        )
        jobs.append(job)

    return jobs


def scrape_entertainment_careers_fallback(
    url: str,
    seen_urls: set[str],
) -> list[Job]:
    try:
        html = requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        ).text
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return []

    jobs: list[Job] = []

    for link in soup.select("a"):
        href = link.get("href")

        if not href or "/job/" not in href:
            continue

        if not href.startswith("http"):
            href = "https://www.entertainmentcareers.net" + href

        if href in seen_urls:
            continue
        seen_urls.add(href)

        title = link.get_text(strip=True)

        job = Job(
            title=title,
            url=href,
            source="Entertainment Careers",
        )
        jobs.append(job)

    return jobs
