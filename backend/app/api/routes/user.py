from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.models.user import User as UserModel
from app.schemas.user import UserRead, UserUpdate, UserCreate

from app.services.user import UserService
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

# Endpoint de creación de usuario
@router.post("/", response_model=UserRead, status_code=http_status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.create_user(user_data=user_data, current_user=current_user)



@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.list_users(skip=skip, limit=limit, current_user=current_user)


@router.get("/test-permissions", response_model=dict, include_in_schema=False)
async def test_permissions(
    current_user: UserModel = Depends(get_current_user),
):
    return {
        "message": "¡Tienes permiso para ver usuarios!",
        "user": current_user.email,
        "role": current_user.role,
    }


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.get_user(user_id=user_id, current_user=current_user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.update_user(
        user_id=user_id,
        user_data=user_data,
        current_user=current_user,
    )


@router.delete("/{user_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: UserModel = Depends(get_current_user),
):
    await service.delete_user(user_id=user_id, current_user=current_user)
    return None