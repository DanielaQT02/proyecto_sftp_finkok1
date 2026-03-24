from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from app.core.database import Base, engine

# Cargar variables de entorno desde .env
load_dotenv()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Configurar limitador de velocidad
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# Agregar rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Demasiadas solicitudes. Por favor espera antes de intentar de nuevo."}
))

# Importar routers
from app.api.routes import (
    account_router,
    auth_router,
    batch_router,
    buffer_router,
    business_router,
    error_router,
    invoice_router,
    statistics_router,
    user_router,
)

# Incluir routers
app.include_router(account_router)
app.include_router(auth_router)
app.include_router(batch_router)
app.include_router(buffer_router)
app.include_router(business_router)
app.include_router(error_router)
app.include_router(invoice_router)
app.include_router(statistics_router)
app.include_router(user_router)