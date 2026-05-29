import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning


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


def detect_country(content: str) -> str:
    content_lower = content.lower()

    if "argentina" in content_lower:
        return "Argentina"

    if "remote" in content_lower:
        return "Remote"

    return ""
