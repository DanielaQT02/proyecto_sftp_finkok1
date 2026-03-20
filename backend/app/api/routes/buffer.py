from fastapi import APIRouter, Depends, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.buffer import BufferCreate, BufferRead
from app.services.buffer import BufferService

router = APIRouter(prefix="/buffers", tags=["Buffers"])


def get_buffer_service(db: AsyncSession = Depends(get_db)) -> BufferService:
    return BufferService(db)


@router.post("/", response_model=BufferRead, status_code=http_status.HTTP_201_CREATED)
async def create_buffer(
    buffer_data: BufferCreate,
    current_user: UserModel = Depends(get_current_user),
    service: BufferService = Depends(get_buffer_service),
):
    return await service.create_buffer(
        buffer_data=buffer_data,
        current_user=current_user,
    )


@router.get("/{buffer_id}", response_model=BufferRead)
async def get_buffer(
    buffer_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: BufferService = Depends(get_buffer_service),
):
    return await service.get_buffer(
        buffer_id=buffer_id,
        current_user=current_user,
    )


@router.get("/{buffer_id}/details", response_model=BufferRead)
async def get_buffer_details(
    buffer_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: BufferService = Depends(get_buffer_service),
):
    return await service.get_buffer_details(
        buffer_id=buffer_id,
        current_user=current_user,
    )