"""Convert uploaded resume files into Jinja2 HTML templates."""

from io import BytesIO
from typing import Any


def docx_to_html(content: bytes) -> str:
    try:
        import mammoth
    except ImportError as exc:
        raise RuntimeError("mammoth is required for DOCX template upload") from exc

    result = mammoth.convert_to_html(BytesIO(content))
    return result.value


def fallback_jinja_from_parsed(parsed: dict[str, Any]) -> tuple[str, str]:
    from app.data.resume_templates import CLASSIC_BODY, CLASSIC_CSS

    return CLASSIC_BODY.strip(), CLASSIC_CSS.strip()
