from urllib.parse import quote

from bs4 import BeautifulSoup

from src.models import Job
from src.utils.html_utils import fetch_page


_SEARCH_TERMS = [
    "animacion 3d", "modelado 3d", "game developer",
    "diseño grafico", "multimedia", "vfx", "unity",
    "ilustrador", "animador", "videojuegos",
]
_MAX_SEARCH_TERMS = 3
_MAX_JOBS = 60


def scrape_bumeran(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    collected_urls: set[str] = set()

    for term in _SEARCH_TERMS[:_MAX_SEARCH_TERMS]:
        if len(collected_urls) >= _MAX_JOBS:
            break

        search_url = f"https://www.bumeran.com.mx/empleos/busqueda/{quote(term)}"
        html = fetch_page(search_url)
        if not html:
            continue

        if "enable JavaScript" in html or "Enable JavaScript" in html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_=lambda c: c and "card" in " ".join(c).lower()):
            title_el = item.find("h2") or item.find("h3")
            if not title_el:
                continue
            link = title_el.find("a") or item.find("a", href=True)
            if not link:
                continue

            href = link.get("href", "")
            if href and not href.startswith("http"):
                if href.startswith("/"):
                    href = f"https://www.bumeran.com.mx{href}"
                else:
                    href = f"https://www.bumeran.com.mx/{href}"

            title = title_el.get_text(strip=True)
            if not title:
                continue

            company_el = item.find(class_=lambda c: c and "company" in " ".join(c).lower())
            company = company_el.get_text(strip=True) if company_el else ""
            location_el = item.find(class_=lambda c: c and "location" in " ".join(c).lower())
            location = location_el.get_text(strip=True) if location_el else ""

            description = company
            if location:
                description += f" - {location}"

            if href in seen_urls or href in collected_urls:
                continue
            collected_urls.add(href)

            job = Job(
                title=title,
                url=href,
                source="Bumeran",
                country="Mexico",
                description=description,
            )
            jobs.append(job)

    for job in jobs:
        seen_urls.add(job.url)

    return jobs
