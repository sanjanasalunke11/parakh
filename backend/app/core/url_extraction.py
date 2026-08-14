from urllib.parse import urlparse

import httpx
import trafilatura

MAX_CHARS = 6000


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Please provide a valid http(s) URL.")
    return url


def extract_article_text(url: str) -> str:
    url = _validate_url(url)

    downloaded = None
    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception:
        downloaded = None

    if not downloaded:
        try:
            response = httpx.get(
                url,
                timeout=12,
                follow_redirects=True,
                headers={"User-Agent": "Parakh/1.0 (+truth-verification-bot)"},
            )
            response.raise_for_status()
            downloaded = response.text
        except Exception as exc:
            raise ValueError(f"Could not fetch this URL: {exc}") from exc

    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)

    if not text:
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(downloaded, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
        except Exception:
            text = ""

    return (text or "").strip()[:MAX_CHARS]
