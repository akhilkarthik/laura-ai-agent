import trafilatura

MAX_CHARS = 4000


def fetch_article(url: str) -> tuple:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise ValueError("Could not fetch the URL. Check if it's accessible.")

    text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
    if not text:
        raise ValueError("Could not extract readable content from this page.")

    metadata = trafilatura.extract_metadata(downloaded)
    title = metadata.title if metadata and metadata.title else ""

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "..."

    return title, text
