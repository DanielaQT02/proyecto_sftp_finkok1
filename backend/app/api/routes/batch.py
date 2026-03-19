from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.batch import BatchCreate, BatchUpdate, BatchRead
from app.services.batch import StampingBatchService
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/batches", tags=["Batches"])


def get_batch_service(db: AsyncSession = Depends(get_db)) -> StampingBatchService:
    return StampingBatchService(db)


@router.post("/", response_model=BatchRead, status_code=http_status.HTTP_201_CREATED)
async def create_batch(
    batch_data: BatchCreate,
    current_user: UserModel = Depends(get_current_user),
    service: StampingBatchService = Depends(get_batch_service),
):
    return await service.create_batch(batch_data=batch_data, current_user=current_user)


@router.get("/", response_model=list[BatchRead])
async def list_batches(
    business_id: int | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=1000),
    current_user: UserModel = Depends(get_current_user),
    service: StampingBatchService = Depends(get_batch_service),
):
    return await service.list_batches(
        business_id=business_id,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/{batch_id}", response_model=BatchRead)
async def get_batch(
    batch_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: StampingBatchService = Depends(get_batch_service),
):
    return await service.get_batch(batch_id=batch_id, current_user=current_user)


@router.put("/{batch_id}", response_model=BatchRead)
async def update_batch(
    batch_id: int,
    batch_data: BatchUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: StampingBatchService = Depends(get_batch_service),
):
    return await service.update_batch(
        batch_id=batch_id,
        batch_data=batch_data,
        current_user=current_user,
    )


@router.delete("/{batch_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_batch(
    batch_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: StampingBatchService = Depends(get_batch_service),
):
    await service.delete_batch(batch_id=batch_id, current_user=current_user)
    return None