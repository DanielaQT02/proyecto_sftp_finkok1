from typing import List, Optional

from app.models.batch import StampingBatch
from app.models.user import User as UserModel
from app.repositories.business import BusinessRepository
from app.repositories.batch import StampingBatchRepository
from app.schemas.batch import BatchCreate, BatchUpdate
from app.services.base import BaseService


class StampingBatchService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.batch_repo = StampingBatchRepository(db)
        self.business_repo = BusinessRepository(db)

    async def create_batch(self, batch_data: BatchCreate, current_user: UserModel) -> StampingBatch:
        business = await self._get_or_404(self.business_repo.get, batch_data.business_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para crear lotes en esta empresa"
            )
        else:
            self._forbidden("No tienes permiso para crear lotes")

        return await self.batch_repo.create(batch_data.model_dump())

    async def list_batches(
        self,
        current_user: UserModel,
        business_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[StampingBatch]:
        if business_id:
            business = await self._get_or_404(self.business_repo.get, business_id)

            if current_user.role in ["superuser", "admin", "soporte"]:
                return await self.batch_repo.list_by_business(business_id, limit=limit, offset=skip)

            if current_user.role == "cliente":
                self._allow_superuser_admin_or_owner(
                    current_user,
                    business.account.user_id,
                    "No autorizado"
                )
                return await self.batch_repo.list_by_business(business_id, limit=limit, offset=skip)

            return []

        if current_user.role in ["superuser", "admin", "soporte"]:
            return await self.batch_repo.list(limit=limit, offset=skip)

        if current_user.role == "cliente":
            business_ids = [
                business.id
                for account in current_user.accounts
                for business in account.businesses
            ]
            if not business_ids:
                return []
            all_batches = []
            for bid in business_ids:
                batches = await self.batch_repo.list_by_business(bid, limit=1000, offset=0)
                all_batches.extend(batches)
            return self._manual_paginate(all_batches, skip, limit)

        return []

    async def get_batch(self, batch_id: int, current_user: UserModel) -> StampingBatch:
        batch = await self._get_or_404(self.batch_repo.get, batch_id)
        await self._check_batch_access(batch, current_user)
        return batch

    async def get_batch_with_buffers(self, batch_id: int, current_user: UserModel) -> StampingBatch:
        batch = await self._get_or_404(self.batch_repo.get_with_buffers, batch_id)
        await self._check_batch_access(batch, current_user)
        return batch

    async def update_batch(self, batch_id: int, batch_data: BatchUpdate, current_user: UserModel) -> StampingBatch:
        await self._get_or_404(self.batch_repo.get, batch_id)

        self._require_roles(
            current_user,
            ["superuser", "admin"],
            "No tienes permiso para actualizar lotes"
        )

        return await self.batch_repo.update(batch_id, batch_data.dict(exclude_unset=True))

    async def _check_batch_access(self, batch: StampingBatch, current_user: UserModel) -> None:
        if current_user.role in ["superuser", "admin", "soporte"]:
            return

        if current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                batch.business.account.user_id,
                "No autorizado para ver este lote"
            )
            return

        self._forbidden("No tienes permiso para ver lotes")