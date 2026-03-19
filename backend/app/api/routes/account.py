from fastapi import APIRouter, Depends, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.account import AccountCreate, AccountUpdate, AccountRead
from app.schemas.business import BusinessRead
from app.services.account import AccountService
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)


@router.post("/", response_model=AccountRead, status_code=http_status.HTTP_201_CREATED, include_in_schema=False)
async def create_account(
    account_data: AccountCreate,
    current_user: UserModel = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.create_account(account_data, current_user)


@router.get("/", response_model=list[AccountRead])
async def list_accounts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=1000),
    current_user: UserModel = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.list_accounts(
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(
    account_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.get_account(account_id, current_user)


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    return await service.update_account(account_id, account_data, current_user)


@router.delete("/{account_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    current_user: UserModel = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
):
    await service.delete_account(account_id, current_user)
    return None

