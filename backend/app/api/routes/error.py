from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.error import ErrorDetail, ErrorSummary, ErrorStamping
from app.services.error import ErrorService
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/errors", tags=["Errors"])


def get_error_service(db: AsyncSession = Depends(get_db)) -> ErrorService:
    return ErrorService(db)


@router.get("/", response_model=list[ErrorStamping])
async def list_errors(
    business_id: int | None = Query(default=None),
    buffer_id: int | None = Query(default=None),
    invoice_uuid: str | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserModel = Depends(get_current_user),
    service: ErrorService = Depends(get_error_service),
):
    return await service.list_errors(
        business_id=business_id,
        buffer_id=buffer_id,
        invoice_uuid=invoice_uuid,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )




@router.get("/{error_id}", response_model=ErrorDetail)
async def get_error(
    error_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: ErrorService = Depends(get_error_service),
):
    return await service.get_error(
        error_id=error_id,
        current_user=current_user,
    )