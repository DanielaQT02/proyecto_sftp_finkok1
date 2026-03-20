from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.pool import NullPool

from app.core.database import Base, engine
from app.models import *


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"BIENVENIDO"}