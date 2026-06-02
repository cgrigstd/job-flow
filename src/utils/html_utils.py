import warnings

import requests
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

from src.config import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT


def fetch_page(url: str) -> str | None:
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.text
    except Exception:
        return None


warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def clean_html(text: str) -> str:
    parser = BeautifulSoup(text, "html.parser")
    return parser.get_text()


def clean_imagecampus_description(text: str) -> str:
    if not text:
        return ""

    marker = "Descripción del empleo:"

    if marker in text:
        return text.split(marker, 1)[1].strip()

    return text.strip()


def is_job_covered(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    return bool(soup.select_one(".sectores-cubierto"))


def truncate_description(text: str, max_chars: int = 300) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0]


LATAM_COUNTRIES = {
    "argentina": "Argentina",
    "bolivia": "Bolivia",
    "brazil": "Brazil",
    "brasil": "Brazil",
    "chile": "Chile",
    "colombia": "Colombia",
    "costa rica": "Costa Rica",
    "cuba": "Cuba",
    "republica dominicana": "Dominican Republic",
    "dominican republic": "Dominican Republic",
    "ecuador": "Ecuador",
    "el salvador": "El Salvador",
    "guatemala": "Guatemala",
    "honduras": "Honduras",
    "mexico": "Mexico",
    "méxico": "Mexico",
    "nicaragua": "Nicaragua",
    "panama": "Panama",
    "panamá": "Panama",
    "paraguay": "Paraguay",
    "peru": "Peru",
    "perú": "Peru",
    "puerto rico": "Puerto Rico",
    "uruguay": "Uruguay",
    "venezuela": "Venezuela",
}

REMOTE_KEYWORDS = {"remote", "anywhere", "worldwide", "100% remoto", "trabajo remoto"}

LATAM_REGION = "latin_america"
REMOTE_REGION = "remote"
US_EU_REGION = "us_canada_europe"
OTHER_REGION = "other"

US_EU_COUNTRIES = {
    "usa", "united states", "united states of america", "eeuu", "estados unidos",
    "canada", "canadá",
    "uk", "united kingdom", "england", "scotland", "wales", "northern ireland",
    "spain", "españa", "germany", "alemania", "france", "francia",
    "italy", "italia", "netherlands", "holanda", "belgium", "belgica",
    "switzerland", "suiza", "sweden", "suecia", "norway", "noruega",
    "denmark", "dinamarca", "finland", "finlandia", "portugal",
    "ireland", "irlanda", "austria", "poland", "polonia",
    "czech republic", "hungary", "hungria", "romania", "rumania",
    "greece", "grecia", "japan", "japon", "australia", "new zealand",
}


def detect_country(content: str) -> str:
    content_lower = content.lower()

    for keyword, country in LATAM_COUNTRIES.items():
        if keyword in content_lower:
            return country

    for token in REMOTE_KEYWORDS:
        if token in content_lower:
            return "Remote"

    for keyword in US_EU_COUNTRIES:
        if keyword in content_lower:
            return keyword.title()

    return ""


def detect_region(country: str) -> str:
    if not country or country == "Remote":
        return REMOTE_REGION

    for keyword in LATAM_COUNTRIES:
        if keyword in country.lower():
            return LATAM_REGION

    for keyword in US_EU_COUNTRIES:
        if keyword in country.lower():
            return US_EU_REGION

    return OTHER_REGION
