"""Extract plain text from resume documents."""

from io import BytesIO

from app.core.exceptions import ValidationError


def extract_text_from_document(content: bytes, content_type: str | None, file_name: str) -> str:
    """Extract readable text from PDF or DOCX resume files."""
    lower_name = file_name.lower()
    is_pdf = content_type == "application/pdf" or lower_name.endswith(".pdf")
    is_docx = (
        content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        or lower_name.endswith(".docx")
    )

    if is_pdf:
        return _extract_pdf_text(content)
    if is_docx:
        return _extract_docx_text(content)

    raise ValidationError("Unsupported file type. Upload PDF or DOCX only.")


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValidationError("PDF extraction dependency not installed") from exc

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise ValidationError("Could not extract text from PDF. The file may be scanned or empty.")
    return text


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise ValidationError("DOCX extraction dependency not installed") from exc

    document = Document(BytesIO(content))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    text = "\n".join(paragraphs).strip()
    if not text:
        raise ValidationError("Could not extract text from DOCX.")
    return text
