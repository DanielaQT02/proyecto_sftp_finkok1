from typing import List, Optional

from app.models.error import ErrorStamping
from app.models.user import User as UserModel
from app.repositories.error import ErrorStampingRepository
from app.repositories.buffer import BufferRepository
from app.repositories.business import BusinessRepository
from app.services.base import BaseService


class ErrorService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.repo = ErrorStampingRepository(db)
        self.buffer_repo = BufferRepository(db)
        self.business_repo = BusinessRepository(db)

    async def list_errors(
        self,
        current_user: UserModel,
        business_id: Optional[int] = None,
        buffer_id: Optional[int] = None,
        invoice_uuid: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ErrorStamping]:
        # Check permissions
        if current_user.role in ["superuser", "admin", "soporte"]:
            return await self.repo.list(limit=limit, offset=skip)

        if current_user.role == "cliente":
            # For cliente, filter by their resources
            user_business_ids = [
                business.id
                for account in current_user.accounts
                for business in account.businesses
            ]
            if business_id and business_id not in user_business_ids:
                self._forbidden("No autorizado para ver errores de esta empresa")
            return await self.repo.list(limit=limit, offset=skip)

        self._forbidden("No tienes permiso para ver errores")

    async def get_error(self, error_id: int, current_user: UserModel) -> ErrorStamping:
        error = await self._get_or_404(self.repo.get, error_id)

        if current_user.role in ["superuser", "admin", "soporte"]:
            return error

        if current_user.role == "cliente":
            # Check if the error belongs to the user's business
            if error.buffer and error.buffer.batch:
                self._allow_superuser_admin_or_owner(
                    current_user,
                    error.buffer.batch.business.account.user_id,
                    "No autorizado para ver este error"
                )
            return error

        self._forbidden("No tienes permiso para ver errores")
