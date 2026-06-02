import re

from src.classifiers.specialties import SPECIALTIES


def score_job(title: str, description: str) -> int:
    content = (title + " " + description).lower()
    score = 0

    for spec in SPECIALTIES:
        for keyword in spec.keywords:
            if re.search(rf'\b{re.escape(keyword)}\b', content):
                score += 2

    if re.search(r'\bremote\b', content):
        score += 1

    if re.search(r'\bsenior\b', content) or re.search(r'\bmid\b', content):
        score += 1

    title_lower = title.lower()
    for spec in SPECIALTIES:
        if re.search(rf'\b{re.escape(spec.label.lower())}\b', title_lower):
            score += 3
            break

    return score
