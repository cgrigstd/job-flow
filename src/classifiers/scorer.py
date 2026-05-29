from src.classifiers.specialties import SPECIALTIES


def score_job(title: str, description: str) -> int:
    content = (title + " " + description).lower()
    score = 0

    for spec in SPECIALTIES:
        for keyword in spec.keywords:
            if keyword in content:
                score += 2

    if "remote" in content:
        score += 1

    if "senior" in content or "mid" in content:
        score += 1

    title_lower = title.lower()
    for spec in SPECIALTIES:
        if spec.label.lower() in title_lower:
            score += 3
            break

    return score
