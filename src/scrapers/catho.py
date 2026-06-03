import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page, truncate_description


_CATHO_DOMAIN = "www.catho.com.br"

_SEARCH_TERMS = [
    "animacao 3d", "modelagem 3d", "animador 3d",
    "game", "unreal", "unity", "vfx",
    "ilustrador", "designer grafico", "video edicao",
]

_MAX_SEARCH_TERMS = 5
_MAX_JOBS = 100


def _extract_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[dict] = []

    for article in soup.find_all("article", class_="offer"):
        h2 = article.find("h2", class_="title_offer")
        if not h2:
            continue

        title = h2.get_text(strip=True)
        if not title:
            continue

        link = h2.find("a") or article.find("a", href=re.compile(r"/vagas/"))
        if not link:
            continue

        href = link.get("href", "")
        if not href.startswith("http"):
            href = f"https://{_CATHO_DOMAIN}{href}"

        company_el = article.find("span", class_="text-12")
        company = company_el.get_text(strip=True) if company_el else ""

        location = ""
        location_icon = article.find("span", class_="i_job_location")
        if location_icon:
            loc_p = location_icon.find_parent("p")
            if loc_p:
                loc_text = loc_p.get_text(" ", strip=True)
                loc_match = re.search(r"-\s*(.+?)$", loc_text)
                if loc_match:
                    location = loc_match.group(1).strip()

        jobs.append({
            "url": href,
            "title": title,
            "company": company,
            "location": location,
        })

    return jobs


def scrape_catho(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for term in _SEARCH_TERMS[:_MAX_SEARCH_TERMS]:
        if len(collected_urls) >= _MAX_JOBS:
            break

        search_url = f"https://{_CATHO_DOMAIN}/vagas/?q={quote(term)}"
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
                source="Catho",
                country="Brazil",
                description=description,
            )
            jobs.append(job)

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
