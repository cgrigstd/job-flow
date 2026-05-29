from datetime import datetime, timedelta
from collections import defaultdict

from src.config import (
    FEEDS,
    LIMIT_DAYS,
    MAX_JOBS_PER_SPECIALTY,
    BYPASS_SOURCES,
)
from src.models import Job
from src.classifiers.specialties import SPECIALTIES, classify_job
from src.classifiers.scorer import score_job
from src.scrapers.rss_feed import (
    scrape_rss_feed,
    scrape_entertainment_careers_fallback,
)
from src.scrapers.arcdev import scrape_arcdev
from src.scrapers.imagecampus import scrape_imagecampus


EXCLUDED_TERMS = {"unpaid", "volunteer"}

FLAT_KEYWORDS = {kw for spec in SPECIALTIES for kw in spec.keywords}


def _is_excluded(content: str) -> bool:
    return any(term in content for term in EXCLUDED_TERMS)


def _is_relevant(title: str, description: str) -> bool:
    content = (title + " " + description).lower()
    return any(kw in content for kw in FLAT_KEYWORDS)


def _build_output_specialties(specialty_map: dict[str, list[Job]]) -> list[dict]:
    output = []

    for spec in SPECIALTIES:
        jobs = specialty_map.get(spec.slug, [])
        jobs.sort(key=lambda j: j.score, reverse=True)
        jobs = jobs[:MAX_JOBS_PER_SPECIALTY]
        output.append({
            "slug": spec.slug,
            "label": spec.label,
            "job_count": len(jobs),
            "jobs": [j.to_dict() for j in jobs],
        })

    other_jobs = specialty_map.get("other", [])
    if other_jobs:
        other_jobs.sort(key=lambda j: j.score, reverse=True)
        other_jobs = other_jobs[:MAX_JOBS_PER_SPECIALTY]
        output.append({
            "slug": "other",
            "label": "Other",
            "job_count": len(other_jobs),
            "jobs": [j.to_dict() for j in other_jobs],
        })

    main = [s for s in output if s["slug"] != "other"]
    main.sort(key=lambda s: s["job_count"], reverse=True)
    other = [s for s in output if s["slug"] == "other"]

    return main + other


def search_jobs():
    now = datetime.now()
    cutoff = now - timedelta(days=LIMIT_DAYS)
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for name, url in FEEDS:
        jobs = scrape_rss_feed(name, url, seen_urls, cutoff)
        all_jobs.extend(jobs)

        if name == "Entertainment Careers" and len(jobs) < 5:
            fallback = scrape_entertainment_careers_fallback(url, seen_urls)
            all_jobs.extend(fallback)

    all_jobs.extend(scrape_arcdev(seen_urls))
    all_jobs.extend(scrape_imagecampus(seen_urls))

    valid_jobs: list[Job] = []

    for job in all_jobs:
        content = (job.title + " " + job.description).lower()

        if _is_excluded(content):
            continue

        if job.source not in BYPASS_SOURCES and not _is_relevant(job.title, job.description):
            continue

        job.specialties = classify_job(job.title, job.description)
        job.score = score_job(job.title, job.description)
        valid_jobs.append(job)

    specialty_map: dict[str, list[Job]] = defaultdict(list)

    for job in valid_jobs:
        if job.specialties:
            for slug in job.specialties:
                specialty_map[slug].append(job)
        else:
            specialty_map["other"].append(job)

    specialties_output = _build_output_specialties(specialty_map)
    total_unique = len({j.url for j in valid_jobs})

    return {
        "title": "JobFlow",
        "updated": now.strftime("%Y-%m-%d %H:%M"),
        "total_jobs": total_unique,
        "specialties": specialties_output,
    }
