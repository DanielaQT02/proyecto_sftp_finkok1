from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException

from app.models.invoice import Invoice
from app.models.user import User as UserModel
from app.repositories.account import AccountRepository
from app.repositories.business import BusinessRepository
from app.repositories.invoice import InvoiceRepository
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceSummary
from app.services.base import BaseService


class InvoiceService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.invoice_repo = InvoiceRepository(db)
        self.business_repo = BusinessRepository(db)
        self.account_repo = AccountRepository(db)

    async def create_invoice(self, invoice_data: InvoiceCreate, current_user: UserModel) -> Invoice:
        business = await self._get_or_404(self.business_repo.get, invoice_data.business_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            account = await self._get_or_404(self.account_repo.get, business.account_id)
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para crear facturas en esta empresa"
            )
        else:
            self._forbidden("No tienes permiso para crear facturas")

        try:
            return await self.invoice_repo.create(invoice_data.model_dump())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def list_invoices(
        self,
        current_user: UserModel,
        business_id: Optional[int] = None,
        taxpayer_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        invoice_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Invoice]:
        if current_user.role in ["superuser", "admin", "soporte", "cobranza"]:
            return await self.invoice_repo.get_all_filtered(
                business_id=business_id,
                taxpayer_id=taxpayer_id,
                from_date=from_date,
                to_date=to_date,
                status=invoice_status,
                skip=skip,
                limit=limit
            )

        if current_user.role == "cliente":
            user_accounts = await self.account_repo.get_by_user_id(current_user.id)
            if not user_accounts:
                return []
            
            # Obtener IDs de negocios de las cuentas
            user_business_ids = []
            for account in user_accounts:
                businesses = await self.business_repo.list_by_account(account.id, limit=1000, offset=0)
                user_business_ids.extend([b.id for b in businesses])
            
            if not user_business_ids:
                return []

            if business_id and business_id not in user_business_ids:
                self._forbidden("No autorizado para ver facturas de esta empresa")

            all_invoices = []
            target_ids = [business_id] if business_id else user_business_ids
            for target_id in target_ids:
                invoices = await self.invoice_repo.get_all_filtered(
                    business_id=target_id,
                    taxpayer_id=taxpayer_id,
                    from_date=from_date,
                    to_date=to_date,
                    status=invoice_status,
                    skip=0,
                    limit=1000
                )
                all_invoices.extend(invoices)
            return self._manual_paginate(all_invoices, skip, limit)

        self._forbidden("No tienes permiso para ver facturas")

    async def get_invoice(self, uuid: str, current_user: UserModel) -> Invoice:
        invoice = await self._get_or_404(self.invoice_repo.get_by_uuid, uuid)

        if current_user.role in ["superuser", "admin", "soporte", "cobranza"]:
            return invoice

        if current_user.role == "cliente":
            # Obtener business y account sin lazy loading
            business = await self._get_or_404(self.business_repo.get, invoice.business_id)
            account = await self._get_or_404(self.account_repo.get, business.account_id)
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para ver esta factura"
            )
            return invoice

        self._forbidden("No tienes permiso para ver facturas")

    async def update_invoice(self, uuid: str, invoice_data: InvoiceUpdate, current_user: UserModel) -> Invoice:
        await self._get_or_404(self.invoice_repo.get_by_uuid, uuid)

        self._require_roles(
            current_user,
            ["superuser", "admin"],
            "No tienes permiso para actualizar facturas"
        )

        return await self.invoice_repo.update(uuid, invoice_data.model_dump(exclude_unset=True))

    async def delete_invoice(self, uuid: str, current_user: UserModel) -> None:
        await self._get_or_404(self.invoice_repo.get_by_uuid, uuid)

        self._require_roles(
            current_user,
            ["superuser", "admin"],
            "No tienes permiso para eliminar facturas"
        )

        deleted = await self.invoice_repo.delete(uuid)
        if not deleted:
            self._not_found("Factura no encontrada")

    async def get_invoice_summary(
        self,
        current_user: UserModel,
        business_id: Optional[int] = None
    ) -> InvoiceSummary:
        if business_id:
            business = await self._get_or_404(self.business_repo.get, business_id)

            if current_user.role == "cliente":
                self._allow_superuser_admin_or_owner(
                    current_user,
                    business.account.user_id,
                    "No autorizado para ver resumen de esta empresa"
                )

        stats = await self.invoice_repo.get_statistics(business_id=business_id)
        return InvoiceSummary(**stats)