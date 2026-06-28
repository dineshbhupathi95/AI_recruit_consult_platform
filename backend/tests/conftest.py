"""Pytest configuration and fixtures."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-for-pytest-min-32-chars")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-pytest-min-32")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("AI_PROVIDER", "mock")

from app.core.database import Base, get_db_session
from app.core.dependencies import get_storage_service
from app.main import app
from app.services.storage_service import StorageService


class _FakeStorageService(StorageService):
    """In-memory storage stub for tests — avoids MinIO."""

    def __init__(self) -> None:
        self._objects: dict[str, tuple[bytes, str | None]] = {}

    def upload_candidate_resume(
        self,
        tenant_id,
        application_id,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        key = f"tenants/{tenant_id}/applications/{application_id}/resumes/{safe_name}"
        return key, len(content)

    def upload_job_attachment(
        self,
        tenant_id,
        job_id,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        key = f"tenants/{tenant_id}/jobs/{job_id}/attachments/{safe_name}"
        return key, len(content)

    def upload_resume_template(
        self,
        tenant_id,
        template_id,
        file_name: str,
        content: bytes,
        content_type: str | None,
    ) -> tuple[str, int]:
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        key = f"tenants/{tenant_id}/resume-templates/{template_id}/{safe_name}"
        self._objects[key] = (content, content_type)
        return key, len(content)

    def get_object_bytes(self, object_key: str) -> tuple[bytes, str | None]:
        if object_key not in self._objects:
            from app.core.exceptions import ValidationError
            raise ValidationError("File not found")
        data, content_type = self._objects[object_key]
        return data, content_type

    def delete_object(self, object_key: str) -> None:
        self._objects.pop(object_key, None)


_fake_storage = _FakeStorageService()


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
        await db_session.commit()

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_storage_service] = lambda: _fake_storage

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
