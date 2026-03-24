from typing import List

from app.models.user import User as UserModel
from app.repositories.user import UserRepository
from app.schemas.user import UserUpdate, UserCreate
from app.core import security
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def create_user(self, user_data: UserCreate, current_user: UserModel) -> UserModel:
        if current_user.role not in ["superuser", "admin"]:
            self._forbidden("No tienes permiso para crear usuarios")

        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            self._bad_request("El email ya está registrado")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = security.hash_password(user_dict.pop("password"))

        return await self.user_repo.create(user_dict)

    async def list_users(self, current_user: UserModel, skip: int = 0, limit: int = 100) -> List[UserModel]:
        if current_user.role in ["superuser", "admin"]:
            return await self.user_repo.list(limit=limit, offset=skip)
        return [current_user] if current_user.active else []

    async def get_user(self, user_id: int, current_user: UserModel) -> UserModel:
        user = await self._get_or_404(self.user_repo.get, user_id)

        if not user.active:
            self._not_found("Usuario no encontrado")

        if current_user.role in ["superuser", "admin"]:
            return user

        if current_user.id != user_id:
            self._forbidden("No autorizado para ver este usuario")

        return user

    async def update_user(self, user_id: int, user_data: UserUpdate, current_user: UserModel) -> UserModel:
        if current_user.role not in ["superuser", "admin"] and current_user.id != user_id:
            self._forbidden("No autorizado para actualizar este usuario")

        await self._get_or_404(self.user_repo.get, user_id)
        return await self.user_repo.update(user_id, user_data.model_dump(exclude_unset=True))

    async def delete_user(self, user_id: int, current_user: UserModel) -> None:
        if current_user.role not in ["superuser", "admin"] and current_user.id != user_id:
            self._forbidden("No autorizado para suspender este usuario")

        user = await self._get_or_404(self.user_repo.get, user_id)

        if current_user.id == user_id and current_user.role == "admin":
            self._bad_request("Los administradores no pueden suspender sus propias cuentas")

        await self.user_repo.update(user_id, {"active": False})

    async def test_permissions(self, current_user: UserModel) -> dict:
        return {
            "message": "¡Tienes permiso para ver usuarios!",
            "user": current_user.email,
            "roles": [role.name for role in current_user.roles],
            "permissions": current_user.permissions,
        }