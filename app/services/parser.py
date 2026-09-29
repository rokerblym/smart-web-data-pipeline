from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from app.core.hashing import normalize_text

@dataclass
class ParsedPage:
    title: str | None
    description: str | None
    canonical_url: str | None
    text: str
    word_count: int

def parse_html(html: str, base_url: str) -> ParsedPage:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "template"]):
        tag.decompose()

    title = normalize_text(soup.title.get_text(" ", strip=True)) if soup.title else None

    description_tag = soup.find("meta", attrs={"name": "description"})
    description = (
        normalize_text(description_tag.get("content", ""))
        if description_tag and description_tag.get("content")
        else None
    )

    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical_url = (
        urljoin(base_url, canonical["href"])
        if canonical and canonical.get("href")
        else None
    )

    root = soup.find("article") or soup.find("main") or soup.body or soup
    text = normalize_text(root.get_text(" ", strip=True))
    word_count = len(text.split()) if text else 0

    return ParsedPage(
        title=title,
        description=description,
        canonical_url=canonical_url,
        text=text,
        word_count=word_count,
    )
