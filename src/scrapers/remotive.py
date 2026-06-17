import requests

from src.config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from src.models import Job
from src.utils.html_utils import detect_country

_REMOTIVE_API = "https://remotive.com/api/remote-jobs?limit=100"

_RELEVANT_CATEGORIES = {
    "Software Development",
    "Artificial Intelligence",
    "Product Management",
    "Data and Analytics",
}


def scrape_remotive(seen_urls: set[str]) -> list[Job]:
    try:
        resp = requests.get(
            _REMOTIVE_API,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return []

    jobs: list[Job] = []
    raw = data.get("jobs") or []

    for item in raw:
        url = item.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = (item.get("title") or "").strip()
        if not title or len(title) < 5:
            continue

        category = item.get("category") or ""
        if category not in _RELEVANT_CATEGORIES:
            continue

        company = (item.get("company_name") or "").strip()
        location = (item.get("candidate_required_location") or "").strip()
        job_type = (item.get("job_type") or "").strip()

        description = company
        if location:
            description += f" - {location}"
        if job_type:
            description += f" ({job_type})"

        country = detect_country(location + " " + description)
        if not country:
            country = "Remote"

        job = Job(
            title=title,
            url=url,
            source="Remotive",
            country=country,
            description=description[:300],
        )
        jobs.append(job)

    return jobs
