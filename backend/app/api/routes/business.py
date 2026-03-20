from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessRead, BusinessStatistics
from app.services.business import BusinessService
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/businesses", tags=["Businesses"])


def get_business_service(db: AsyncSession = Depends(get_db)) -> BusinessService:
    return BusinessService(db)


@router.post("/", response_model=BusinessRead, status_code=http_status.HTTP_201_CREATED)
async def create_business(
    business_data: BusinessCreate,
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    return await service.create_business(
        business_data=business_data,
        current_user=current_user,
    )


@router.get("/", response_model=list[BusinessRead])
async def list_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: int | None = Query(default=None),
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    return await service.list_businesses(
        skip=skip,
        limit=limit,
        account_id=account_id,
        current_user=current_user,
    )


@router.get("/{business_id}", response_model=BusinessRead)
async def get_business(
    business_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    return await service.get_business(
        business_id=business_id,
        current_user=current_user,
    )


@router.put("/{business_id}", response_model=BusinessRead)
async def update_business(
    business_id: int,
    business_data: BusinessUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    return await service.update_business(
        business_id=business_id,
        business_data=business_data,
        current_user=current_user,
    )


@router.delete("/{business_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    await service.delete_business(
        business_id=business_id,
        current_user=current_user,
    )
    return None


@router.get("/{business_id}/statistics", response_model=BusinessStatistics, include_in_schema=False)
async def get_business_statistics(
    business_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: BusinessService = Depends(get_business_service),
):
    return await service.get_business_statistics(
        business_id=business_id,
        current_user=current_user,
    )