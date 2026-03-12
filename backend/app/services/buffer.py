from app.models.buffer import Buffer
from app.models.user import User as UserModel
from app.repositories.buffer import BufferRepository
from app.repositories.batch import StampingBatchRepository
from app.schemas.buffer import BufferCreate
from app.services.base import BaseService


class BufferService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.repo = BufferRepository(db)
        self.batch_repo = StampingBatchRepository(db)

    async def create_buffer(self, data: BufferCreate, current_user: UserModel) -> Buffer:
        if data.batch_id:
            batch = await self._get_or_404(self.batch_repo.get, data.batch_id)

            if current_user.role == "cliente":
                self._allow_superuser_admin_or_owner(
                    current_user,
                    batch.business.account.user_id,
                    detail="No autorizado para crear buffers en este lote"
                )
            elif current_user.role not in ["superuser", "admin"]:
                self._forbidden("No tienes permiso para crear buffers")

        return await self.repo.create(data.dict())

    async def get_buffer(self, buffer_id: int, current_user: UserModel) -> Buffer:
        buffer = await self._get_or_404(self.repo.get, buffer_id)
        await self._check_buffer_access(buffer, current_user)
        return buffer

    async def get_buffer_details(self, buffer_id: int, current_user: UserModel) -> Buffer:
        buffer = await self._get_or_404(self.repo.get_with_details, buffer_id)
        await self._check_buffer_access(buffer, current_user)
        return buffer

    async def _check_buffer_access(self, buffer: Buffer, current_user: UserModel) -> None:
        if current_user.role in ["superuser", "admin", "soporte"]:
            return

        if current_user.role == "cliente":
            if buffer.batch:
                self._allow_superuser_admin_or_owner(
                    current_user,
                    buffer.batch.business.account.user_id,
                    detail="No autorizado para ver este buffer"
                )
            return

        self._forbidden("No tienes permiso para ver buffers")