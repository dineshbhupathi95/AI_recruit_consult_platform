"""Unit tests for local file storage backend."""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.exceptions import ValidationError
from app.services.storage_service import _LocalFileBackend, _safe_file_name


def test_safe_file_name_replaces_path_separators() -> None:
    assert _safe_file_name("foo/bar\\resume.pdf") == "foo_bar_resume.pdf"


def test_local_file_backend_put_get_delete(tmp_path: Path) -> None:
    backend = _LocalFileBackend(tmp_path)
    object_key = f"tenants/{uuid4()}/jobs/{uuid4()}/spec.pdf"
    content = b"%PDF-1.4 test"
    backend.put(object_key, content, "application/pdf")

    file_path = tmp_path / object_key
    meta_path = tmp_path / f"{object_key}.meta.json"
    assert file_path.is_file()
    assert meta_path.is_file()
    assert json.loads(meta_path.read_text())["content_type"] == "application/pdf"

    data, content_type = backend.get(object_key)
    assert data == content
    assert content_type == "application/pdf"

    backend.delete(object_key)
    assert not file_path.is_file()
    assert not meta_path.is_file()


def test_local_file_backend_get_missing_raises(tmp_path: Path) -> None:
    backend = _LocalFileBackend(tmp_path)
    with pytest.raises(ValidationError, match="Failed to read file from storage"):
        backend.get("tenants/missing/file.pdf")
