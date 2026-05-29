import json
from src.pipeline import search_jobs

if __name__ == "__main__":
    result = search_jobs()

    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"JSON generado: jobs.json ({result['total_jobs']} jobs)")
