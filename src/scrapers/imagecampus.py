from bs4 import BeautifulSoup

from src.models import Job
from src.config import IMAGE_CAMPUS_SEARCH_TERMS
from src.utils.html_utils import (
    clean_imagecampus_description,
    fetch_page,
    is_job_covered,
    truncate_description,
)


def scrape_imagecampus(seen_urls: set[str]) -> list[Job]:
    jobs: list[Job] = []
    seen_local: set[str] = set()

    for keyword in IMAGE_CAMPUS_SEARCH_TERMS:
        url = f"https://www.imagecampus.edu.ar/?s={keyword}&post_type%5B%5D=empleos"
        html = fetch_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("a"):
            href = link.get("href")

            if not href or "/busqueda/" not in href:
                continue

            if href in seen_local or href in seen_urls:
                continue

            seen_local.add(href)
            seen_urls.add(href)

            if not href.startswith("http"):
                href = "https://www.imagecampus.edu.ar" + href

            slug = href.split("/")[-1]
            title = slug.replace("-", " ").title()
            description = ""

            job_html = fetch_page(href)
            if job_html:
                if is_job_covered(job_html):
                    continue
                soup_job = BeautifulSoup(job_html, "html.parser")
                raw_text = soup_job.get_text(" ", strip=True)
                description = clean_imagecampus_description(raw_text)
                description = truncate_description(description)

            job = Job(
                title=title,
                url=href,
                source="ImageCampus",
                country="Argentina",
                description=description,
            )
            jobs.append(job)

    return jobs
