"""MinIO object storage client."""

from io import BytesIO
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """S3-compatible file storage using MinIO."""

    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.minio_bucket
        self._client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def _ensure_bucket(self) -> None:
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def upload_job_attachment(
        self,
        tenant_id: UUID,
        job_id: UUID,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        """Upload a job attachment and return object key and size."""
        self._ensure_bucket()
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        object_key = f"tenants/{tenant_id}/jobs/{job_id}/{safe_name}"

        try:
            self._client.put_object(
                self._bucket,
                object_key,
                BytesIO(content),
                length=len(content),
                content_type=content_type or "application/octet-stream",
            )
        except S3Error as exc:
            logger.error("minio_upload_failed", error=str(exc), object_key=object_key)
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
        """Upload original candidate resume."""
        self._ensure_bucket()
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        object_key = f"tenants/{tenant_id}/applications/{application_id}/resumes/{safe_name}"
        try:
            self._client.put_object(
                self._bucket, object_key, BytesIO(content),
                length=len(content), content_type=content_type or "application/octet-stream",
            )
        except S3Error as exc:
            logger.error("minio_upload_failed", error=str(exc), object_key=object_key)
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
        self._ensure_bucket()
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        object_key = f"tenants/{tenant_id}/resume-templates/{template_id}/{safe_name}"
        try:
            self._client.put_object(
                self._bucket,
                object_key,
                BytesIO(content),
                length=len(content),
                content_type=content_type or "application/octet-stream",
            )
        except S3Error as exc:
            logger.error("minio_upload_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to upload template file to storage") from exc
        return object_key, len(content)

    def get_object_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        self._ensure_bucket()
        try:
            response = self._client.get_object(self._bucket, object_key)
            data = response.read()
            content_type = response.headers.get("Content-Type")
            response.close()
            response.release_conn()
            return data, content_type
        except S3Error as exc:
            logger.error("minio_get_failed", error=str(exc), object_key=object_key)
            raise ValidationError("Failed to read file from storage") from exc

    def delete_object(self, object_key: str) -> None:
        """Remove an object from storage."""
        try:
            self._client.remove_object(self._bucket, object_key)
        except S3Error as exc:
            logger.warning("minio_delete_failed", error=str(exc), object_key=object_key)
