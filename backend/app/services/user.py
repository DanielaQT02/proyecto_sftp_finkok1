from typing import List

from app.models.user import User as UserModel
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def list_users(self, current_user: UserModel, skip: int = 0, limit: int = 100) -> List[UserModel]:
        if current_user.role in ["superuser", "admin"]:
            return await self.user_repo.list(limit=limit, offset=skip)
        return [current_user]

    async def get_user(self, user_id: int, current_user: UserModel) -> UserModel:
        user = await self._get_or_404(self.user_repo.get, user_id)

        if current_user.role in ["superuser", "admin"]:
            return user

        if current_user.id != user_id:
            self._forbidden("No autorizado para ver este usuario")

        return user

    async def update_user(self, user_id: int, user_data: UserUpdate, current_user: UserModel) -> UserModel:
        if current_user.role not in ["superuser", "admin"] and current_user.id != user_id:
            self._forbidden("No autorizado para actualizar este usuario")

        await self._get_or_404(self.user_repo.get, user_id)
        return await self.user_repo.update(user_id, user_data.dict(exclude_unset=True))

    async def delete_user(self, user_id: int, current_user: UserModel) -> None:
        if current_user.role not in ["superuser", "admin"] and current_user.id != user_id:
            self._forbidden("No autorizado para eliminar este usuario")

        await self._get_or_404(self.user_repo.get, user_id)

        if current_user.id == user_id and current_user.role == "admin":
            self._bad_request("Los administradores no pueden eliminarse a sí mismos")

        deleted = await self.user_repo.delete(user_id)
        if not deleted:
            self._not_found("Usuario no encontrado")

    async def test_permissions(self, current_user: UserModel) -> dict:
        return {
            "message": "¡Tienes permiso para ver usuarios!",
            "user": current_user.email,
            "roles": [role.name for role in current_user.roles],
            "permissions": current_user.permissions,
        }