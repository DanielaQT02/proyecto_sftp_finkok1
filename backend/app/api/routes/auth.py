from fastapi import APIRouter, Depends, status as http_status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserRead, UserCreate
from app.services.auth_user import AuthService
from app.models.user import User as UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserModel:
    user = await service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


@router.post("/register", response_model=UserRead, status_code=http_status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register_user(user_data=user_data)


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(
        username=form_data.username,
        password=form_data.password,
    )