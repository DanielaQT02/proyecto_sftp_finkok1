from datetime import datetime

from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.invoice import InvoiceRead, InvoiceCreate, InvoiceUpdate, InvoiceSummary
from app.services.invoice import InvoiceService

router = APIRouter(prefix="/invoices", tags=["Invoices"])


def get_invoice_service(db: AsyncSession = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


@router.post("/", response_model=InvoiceRead, status_code=http_status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.create_invoice(
        invoice_data=invoice_data,
        current_user=current_user,
    )


@router.get("/", response_model=list[InvoiceRead])
async def list_invoices(
    business_id: int | None = Query(default=None),
    taxpayer_id: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
    stamping_status: str | None = Query(
        default=None,
        pattern="^(success|error|pending)$",
        alias="status",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.list_invoices(
        business_id=business_id,
        taxpayer_id=taxpayer_id,
        from_date=from_date,
        to_date=to_date,
        stamping_status=stamping_status,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )


@router.get("/summary", response_model=InvoiceSummary, include_in_schema=False)
async def get_invoice_summary(
    business_id: int | None = Query(default=None),
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.get_invoice_summary(
        business_id=business_id,
        current_user=current_user,
    )


@router.get("/{uuid}", response_model=InvoiceRead)
async def get_invoice(
    uuid: str,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.get_invoice(
        uuid=uuid,
        current_user=current_user,
    )


@router.put("/{uuid}", response_model=InvoiceRead)
async def update_invoice(
    uuid: str,
    invoice_data: InvoiceUpdate,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    return await service.update_invoice(
        uuid=uuid,
        invoice_data=invoice_data,
        current_user=current_user,
    )


@router.delete("/{uuid}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    uuid: str,
    service: InvoiceService = Depends(get_invoice_service),
    current_user: UserModel = Depends(get_current_user),
):
    await service.delete_invoice(
        uuid=uuid,
        current_user=current_user,
    )
    return None