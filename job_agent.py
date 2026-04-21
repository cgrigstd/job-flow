import feedparser
from datetime import datetime, timedelta
import urllib.request
import requests
from bs4 import BeautifulSoup
import json

feeds = {
    "ArcDev":
"https://arc.dev/en-ar/remote-jobs",
    "Entertainment Careers": "https://www.entertainmentcareers.net/ecnjcat173",
    "WorkWithIndies": "https://www.workwithindies.com/careers/rss.xml",
    "Remotive Game Dev": "https://remotive.io/remote-jobs.rss",
    "Remote OK Dev": "https://remoteok.com/remote-dev-jobs.rss",
    "GameDev.net Jobs": "https://gamedev.net/jobs/rss",
    "Remote Game Jobs": "https://remotegamejobs.com/feed.rss",
    "Polycount Freelance": "https://polycount.com/categories/freelance-job-postings/feed.rss",
    "BlenderArtists Paid Jobs": "https://blenderartists.org/c/jobs/paid-work/53.rss"
}

KEYWORDS = [
    "vfx", "3d", "blender", "maya", "nuke",
    "houdini", "3dsmax", "2d", "visual effects",
    "rigger", "rigging",
    "3d modeler", "modeling", "fusion 360", "solidworks",
    "generalist", "generalista",
    "technical artist", "game", "animation",
    "vr", "ar", "dev", "project manager", "IT",
    "Senior"
]

location = "argentina"
limit_days = 7


def parse_feed(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=10) as response:
        data = response.read()

    return feedparser.parse(data)


def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()


def clean_imagecampus_description(text):
    if not text:
        return ""

    marker = "Descripción del empleo:"

    if marker in text:
        return text.split(marker, 1)[1].strip()

    return text.strip()


def is_job_covered(html):
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.select_one(".sectores-cubierto"))


def score_job(content):
    score = 0

    for k in KEYWORDS:
        if k in content:
            score += 2

    if "remote" in content:
        score += 1

    if "senior" in content or "mid" in content:
        score += 1

    return score


def get_imagecampus_jobs(keywords, seen_urls):
    jobs = []
    seen_local = set()

    for keyword in keywords:
        url = f"https://www.imagecampus.edu.ar/?s={keyword}&post_type%5B%5D=empleos"

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
        except:
            continue

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

            covered = False
            description = ""

            try:
                job_page = requests.get(href, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

                covered = is_job_covered(job_page.text)

                # 🚫 saltar jobs cubiertos
                if covered:
                    continue
                
                soup_job = BeautifulSoup(job_page.text, "html.parser")
                raw_text = soup_job.get_text(" ", strip=True)
                
                description = clean_imagecampus_description(raw_text)
                description = description[:300].rsplit(" ", 1)[0]

            except:
                pass

            job = {
                "title": title,
                "url": href,
                "country": "Argentina",
                "description": description,
                "score": score_job((title + " " + description).lower())
            }

            jobs.append(job)

    return jobs


def search_jobs():
    now = datetime.now()
    cutoff = now - timedelta(days=limit_days)

    sites = []
    total_jobs = 0
    seen_urls = set()

    for site, url in feeds.items():

        try:
            data = parse_feed(url)
        except:
            continue

        site_jobs = []

        for entry in data.entries:

            if site != "Entertainment Careers":
                if hasattr(entry, "published_parsed"):
                    job_date = datetime(*entry.published_parsed[:6])
                    if job_date < cutoff:
                        continue

            if entry.link in seen_urls:
                continue
            seen_urls.add(entry.link)

            title = entry.title
            content = title.lower()

            for field in ["summary", "description"]:
                if hasattr(entry, field):
                    content += " " + getattr(entry, field).lower()

            if site != "Entertainment Careers":
                if not any(k in content for k in KEYWORDS):
                    continue

            if "unpaid" in content or "volunteer" in content:
                continue

            country = "Argentina" if location in content else ""

            description = ""
            if hasattr(entry, "description"):
                description = clean_html(entry.description)
            elif hasattr(entry, "summary"):
                description = clean_html(entry.summary)

            description = description[:300].rsplit(" ", 1)[0]

            job = {
                "title": title,
                "url": entry.link,
                "country": country,
                "description": description,
                "score": score_job(content)
            }

            site_jobs.append(job)

        # fallback scraping
        if site == "Entertainment Careers" and len(site_jobs) < 5:
            try:
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                soup = BeautifulSoup(html, "html.parser")

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

                    site_jobs.append({
                        "title": title,
                        "url": href,
                        "country": "",
                        "description": "",
                        "score": 1
                    })

            except:
                pass

        site_jobs = sorted(site_jobs, key=lambda x: x["score"], reverse=True)
        site_jobs = site_jobs[:50]

        if site_jobs:
            sites.append({
                "name": site,
                "job_count": len(site_jobs),
                "jobs": site_jobs
            })
            total_jobs += len(site_jobs)

    # ✅ ImageCampus restored
    imagecampus_jobs = get_imagecampus_jobs(KEYWORDS, seen_urls)

    if imagecampus_jobs:
        imagecampus_jobs = sorted(imagecampus_jobs, key=lambda x: x["score"], reverse=True)
        imagecampus_jobs = imagecampus_jobs[:50]

        sites.append({
            "name": "ImageCampus",
            "job_count": len(imagecampus_jobs),
            "jobs": imagecampus_jobs
        })
        total_jobs += len(imagecampus_jobs)

    return {
        "title": "JobFlow",
        "updated": now.strftime("%Y-%m-%d %H:%M"),
        "total_jobs": total_jobs,
        "sites": sites
    }


if __name__ == "__main__":
    result = search_jobs()

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ JSON generado: jobs.json")
