"""Object storage: MinIO when available, local `files/` directory as fallback."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)

_META_SUFFIX = ".meta.json"


def _safe_file_name(file_name: str) -> str:
    return file_name.replace("/", "_").replace("\\", "_")


class _StorageBackend(ABC):
    @abstractmethod
    def verify_connection(self) -> None:
        """Raise if the backend is not reachable."""

    @abstractmethod
    def put(self, object_key: str, content: bytes, content_type: str | None) -> None:
        pass

    @abstractmethod
    def get(self, object_key: str) -> tuple[bytes, str | None]:
        pass

    @abstractmethod
    def delete(self, object_key: str) -> None:
        pass


class _MinioBackend(_StorageBackend):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str, secure: bool) -> None:
        self._bucket = bucket
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def verify_connection(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def put(self, object_key: str, content: bytes, content_type: str | None) -> None:
        self._ensure_bucket()
        self._client.put_object(
            self._bucket,
            object_key,
            BytesIO(content),
            length=len(content),
            content_type=content_type or "application/octet-stream",
        )

    def get(self, object_key: str) -> tuple[bytes, str | None]:
        self._ensure_bucket()
        response = self._client.get_object(self._bucket, object_key)
        data = response.read()
        content_type = response.headers.get("Content-Type")
        response.close()
        response.release_conn()
        return data, content_type

    def delete(self, object_key: str) -> None:
        self._client.remove_object(self._bucket, object_key)


class _LocalFileBackend(_StorageBackend):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def verify_connection(self) -> None:
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, object_key: str) -> Path:
        return self._base_dir / object_key

    def _meta_path(self, object_key: str) -> Path:
        return self._base_dir / f"{object_key}{_META_SUFFIX}"

    def put(self, object_key: str, content: bytes, content_type: str | None) -> None:
        path = self._file_path(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self._meta_path(object_key).write_text(
            json.dumps({"content_type": content_type or "application/octet-stream"}),
            encoding="utf-8",
        )

    def get(self, object_key: str) -> tuple[bytes, str | None]:
        path = self._file_path(object_key)
        if not path.is_file():
            raise ValidationError("Failed to read file from storage")
        content_type: str | None = None
        meta_path = self._meta_path(object_key)
        if meta_path.is_file():
            content_type = json.loads(meta_path.read_text(encoding="utf-8")).get("content_type")
        return path.read_bytes(), content_type

    def delete(self, object_key: str) -> None:
        path = self._file_path(object_key)
        if path.is_file():
            path.unlink()
        meta_path = self._meta_path(object_key)
        if meta_path.is_file():
            meta_path.unlink()


def _create_backend() -> _StorageBackend:
    settings = get_settings()
    local_path = settings.local_files_path

    if settings.storage_backend == "local":
        logger.info("storage_backend_local", path=str(local_path))
        return _LocalFileBackend(local_path)

    minio_backend = _MinioBackend(
        settings.minio_endpoint,
        settings.minio_access_key,
        settings.minio_secret_key,
        settings.minio_bucket,
        settings.minio_secure,
    )

    if settings.storage_backend == "minio":
        minio_backend.verify_connection()
        logger.info("storage_backend_minio", endpoint=settings.minio_endpoint)
        return minio_backend

    try:
        minio_backend.verify_connection()
        logger.info("storage_backend_minio", endpoint=settings.minio_endpoint)
        return minio_backend
    except Exception as exc:
        logger.warning(
            "minio_unavailable_using_local_files",
            error=str(exc),
            path=str(local_path),
        )
        local_backend = _LocalFileBackend(local_path)
        local_backend.verify_connection()
        return local_backend


class StorageService:
    """Upload and retrieve files via MinIO or local filesystem fallback."""

    def __init__(self) -> None:
        self._backend = _create_backend()

    def upload_job_attachment(
        self,
        tenant_id: UUID,
        job_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = _safe_file_name(file_name)
        object_key = f"tenants/{tenant_id}/jobs/{job_id}/{safe_name}"
        try:
            self._backend.put(object_key, content, content_type)
        except S3Error as exc:
            logger.error("storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload file to storage") from exc
        except OSError as exc:
            logger.error("local_storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload file to storage") from exc
        return object_key, len(content)

    def upload_candidate_resume(
        self,
        tenant_id: UUID,
        application_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = _safe_file_name(file_name)
        object_key = f"tenants/{tenant_id}/applications/{application_id}/resumes/{safe_name}"
        try:
            self._backend.put(object_key, content, content_type)
        except S3Error as exc:
            logger.error("storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload resume to storage") from exc
        except OSError as exc:
            logger.error("local_storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload resume to storage") from exc
        return object_key, len(content)

    def upload_resume_template(
        self,
        tenant_id: UUID,
        template_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = _safe_file_name(file_name)
        object_key = f"tenants/{tenant_id}/resume-templates/{template_id}/{safe_name}"
        try:
            self._backend.put(object_key, content, content_type)
        except S3Error as exc:
            logger.error("storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload template file to storage") from exc
        except OSError as exc:
            logger.error("local_storage_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload template file to storage") from exc
        return object_key, len(content)

    def get_object_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        try:
            return self._backend.get(object_key)
        except S3Error as exc:
            logger.error("storage_get_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to read file from storage") from exc
        except ValidationError:
            raise
        except OSError as exc:
            logger.error("local_storage_get_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to read file from storage") from exc

    def delete_object(self, object_key: str) -> None:
        try:
            self._backend.delete(object_key)
        except S3Error as exc:
            logger.warning("storage_delete_failed", error=str(exc), object_key=object_key)
        except OSError as exc:
            logger.warning("local_storage_delete_failed", error=str(exc), object_key=object_key)
