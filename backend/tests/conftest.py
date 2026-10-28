from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.dependencies import (
    get_db,
    get_prisma_client,
    get_timbre_client,
)
from app.integrations.gnani_prisma import TranscriptionResult
from app.main import create_app
from app.models.activity import Activity
from app.models.base import Base
from app.seed.activities import SEED_ACTIVITIES

# Use SQLite in-memory with aiosqlite and StaticPool for automated test suite isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


class FakePrismaClient:
    def __init__(self, transcript: str = "12", request_id: str = "test-req-123"):
        self.transcript = transcript
        self.request_id = request_id
        self.call_count = 0

    async def transcribe(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        language_code: str = "kn-IN",
    ) -> TranscriptionResult:
        self.call_count += 1
        return TranscriptionResult(
            transcript=self.transcript,
            request_id=self.request_id,
            model="gnani-prisma-v2.5",
            language_code=language_code,
        )


class FakeTimbreClient:
    def __init__(self):
        self.call_count = 0

    async def synthesize(
        self,
        text: str,
        language_code: str = "kn-IN",
    ) -> bytes:
        self.call_count += 1
        # Return a minimal 44-byte dummy WAV header
        return b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed activities
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        for act in SEED_ACTIVITIES:
            session.add(Activity(**act))
        await session.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def fake_prisma() -> FakePrismaClient:
    return FakePrismaClient(transcript="12")


@pytest.fixture
def fake_timbre() -> FakeTimbreClient:
    return FakeTimbreClient()


@pytest_asyncio.fixture
async def client(test_engine, fake_prisma, fake_timbre) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_prisma_client] = lambda: fake_prisma
    app.dependency_overrides[get_timbre_client] = lambda: fake_timbre

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
