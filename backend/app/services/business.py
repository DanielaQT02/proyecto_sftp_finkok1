from typing import List, Optional

from app.models.business import Business as BusinessModel
from app.models.user import User as UserModel
from app.repositories.account import AccountRepository
from app.repositories.business import BusinessRepository
from app.repositories.invoice import InvoiceRepository
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessStatistics
from app.services.base import BaseService


class BusinessService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.account_repo = AccountRepository(db)
        self.business_repo = BusinessRepository(db)
        self.invoice_repo = InvoiceRepository(db)

    async def create_business(self, business_data: BusinessCreate, current_user: UserModel):
        account = await self._get_or_404(self.account_repo.get, business_data.account_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para crear empresas en esta cuenta"
            )
        else:
            self._forbidden("No tienes permiso para crear empresas")

        await self._ensure_unique(
            self.business_repo.get_by_taxpayer_id,
            business_data.taxpayer_id,
            error_msg="RFC ya registrado"
        )

        return await self.business_repo.create(business_data.dict())

    async def list_businesses(
        self,
        current_user: UserModel,
        skip: int = 0,
        limit: int = 100,
        account_id: Optional[int] = None,
    ) -> List[BusinessModel]:
        if current_user.role in ["superuser", "admin", "soporte"]:
            return await self.business_repo.list(limit=limit, offset=skip)

        if current_user.role == "cliente":
            if account_id:
                account = await self._get_or_404(self.account_repo.get, account_id)
                self._allow_superuser_admin_or_owner(
                    current_user,
                    account.user_id,
                    "No autorizado para ver esta cuenta"
                )
                return await self.business_repo.list_by_account(account_id, limit=limit, offset=skip)

            account_ids = [acc.id for acc in current_user.accounts]
            if not account_ids:
                return []
            all_businesses = []
            for acc_id in account_ids:
                businesses = await self.business_repo.list_by_account(acc_id, limit=1000, offset=0)
                all_businesses.extend(businesses)
            return self._manual_paginate(all_businesses, skip, limit)

        self._forbidden("No tienes permiso para ver empresas")

    async def get_business(self, business_id: int, current_user: UserModel):
        business = await self._get_or_404(self.business_repo.get, business_id)

        if current_user.role in ["superuser", "admin", "soporte"]:
            return business

        if current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para ver esta empresa"
            )
            return business

        self._forbidden("No tienes permiso para ver empresas")

    async def update_business(self, business_id: int, business_data: BusinessUpdate, current_user: UserModel):
        business = await self._get_or_404(self.business_repo.get, business_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para actualizar esta empresa"
            )
        else:
            self._forbidden("No tienes permiso para actualizar empresas")

        if business_data.taxpayer_id and business_data.taxpayer_id != business.taxpayer_id:
            existing = await self.business_repo.get_by_taxpayer_id(business_data.taxpayer_id)
            if existing:
                self._bad_request("RFC ya registrado por otra empresa")

        return await self.business_repo.update(business_id, business_data.dict(exclude_unset=True))

    async def delete_business(self, business_id: int, current_user: UserModel) -> None:
        business = await self._get_or_404(self.business_repo.get, business_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para eliminar esta empresa"
            )
        else:
            self._forbidden("No tienes permiso para eliminar empresas")

        deleted = await self.business_repo.delete(business_id)
        if not deleted:
            self._not_found("Empresa no encontrada")

    async def get_business_statistics(
        self,
        business_id: int,
        current_user: UserModel,
    ) -> BusinessStatistics:
        business = await self._get_or_404(self.business_repo.get, business_id)

        if current_user.role in ["superuser", "admin", "soporte", "cobranza"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para ver estadísticas de esta empresa"
            )
        else:
            self._forbidden("No tienes permiso para ver estadísticas")

        stats = await self.invoice_repo.get_statistics(business_id=business_id)
        return BusinessStatistics(
            business_id=business_id,
            business_name=business.business_name,
            taxpayer_id=business.taxpayer_id,
            total_invoices=stats["total_invoices"],
            stamped_success=stats["success_count"],
            stamped_error=stats["error_count"],
            success_rate=stats["success_rate"]
        )