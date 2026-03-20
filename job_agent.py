import feedparser
from datetime import datetime, timedelta
import urllib.request
import requests
from bs4 import BeautifulSoup
import json

feeds = {
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
    "3d modeler", "modeling",
    "generalist", "generalista",
    "technical artist", "game", "animation"
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

            # 🔥 skip date filter ONLY for Entertainment Careers
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

            # 🔥 relaxed filtering for Entertainment Careers
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

        # 🔥 fallback scraping if too few results
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

        # 🔥 sort by score
        site_jobs = sorted(site_jobs, key=lambda x: x["score"], reverse=True)

        site_jobs = site_jobs[:50]

        if site_jobs:
            sites.append({
                "name": site,
                "job_count": len(site_jobs),
                "jobs": site_jobs
            })
            total_jobs += len(site_jobs)

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
