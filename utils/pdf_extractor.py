import io
from pypdf import PdfReader

MAX_CHARS = 4000


def extract_pdf(file_bytes: bytes) -> tuple[str, str]:
    """
    Returns (title, text) from PDF bytes.
    Title is the PDF metadata title or empty string.
    Text is truncated to MAX_CHARS.
    """
    reader = PdfReader(io.BytesIO(file_bytes))

    title = ""
    if reader.metadata and reader.metadata.title:
        title = reader.metadata.title.strip()

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text.strip())

    full_text = "\n\n".join(pages_text)

    if len(full_text) > MAX_CHARS:
        full_text = full_text[:MAX_CHARS] + "..."

    return title, full_text
