import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal, engine, Base


@pytest_asyncio.fixture
async def client():
    """Cliente HTTP para pruebas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    """Sesión de BD para pruebas."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def setup_db():
    """Crea todas las tablas antes de pruebas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Limpiar después
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
