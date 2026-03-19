from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.statistics import StampingStatisticsCreate, StampingStatisticsRead
from app.services.statistics import StampingStatisticsService
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/statistics", tags=["Statistics"])


def get_statistics_service(db: AsyncSession = Depends(get_db)) -> StampingStatisticsService:
    return StampingStatisticsService(db)


@router.get("/", response_model=list[StampingStatisticsRead])
async def list_statistics(
    business_id: int = Query(..., description="ID de la empresa"),
    limit: int = Query(50, ge=1, le=1000),
    current_user: UserModel = Depends(get_current_user),
    service: StampingStatisticsService = Depends(get_statistics_service),
):
    return await service.get_statistics(
        business_id=business_id,
        limit=limit,
        current_user=current_user,
    )
