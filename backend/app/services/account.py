from typing import List

from app.models.account import Account as AccountModel
from app.models.user import User as UserModel
from app.repositories.account import AccountRepository
from app.repositories.user import UserRepository
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.base import BaseService


class AccountService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.account_repo = AccountRepository(db)
        self.user_repo = UserRepository(db)

    async def create_account(self, account_data: AccountCreate, current_user: UserModel):
        target_user_id = None
        if current_user.role in ["superuser", "admin"]:
            target_user_id = account_data.user_id
        elif current_user.role == "cliente":
            if account_data.user_id != current_user.id:
                self._forbidden("Solo puedes crear cuentas para ti mismo")
            target_user_id = current_user.id
        else:
            self._forbidden("No tienes permiso para crear cuentas")

        target_user = await self.user_repo.get(target_user_id)
        if not target_user:
            self._not_found("Usuario no encontrado")

        return await self.account_repo.create(
            {"user_id": target_user_id, "account_name": account_data.account_name}
        )

    async def list_accounts(self, current_user: UserModel) -> List[AccountModel]:
        if current_user.role in ["superuser", "admin", "soporte"]:
            return await self.account_repo.list(limit=1000)
        if current_user.role == "cliente":
            return await self.account_repo.get_by_user_id(current_user.id)
        self._forbidden("No tienes permiso para ver cuentas")

    async def get_account(self, account_id: int, current_user: UserModel):
        account = await self._get_or_404(self.account_repo.get, account_id)
        if current_user.role in ["superuser", "admin", "soporte"]:
            return account
        if current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para ver esta cuenta"
            )
            return account
        self._forbidden("No tienes permiso para ver cuentas")

    async def update_account(self, account_id: int, account_data: AccountUpdate, current_user: UserModel):
        account = await self._get_or_404(self.account_repo.get, account_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para actualizar esta cuenta"
            )
        else:
            self._forbidden("No tienes permiso para actualizar cuentas")

        return await self.account_repo.update(account_id, account_data.dict(exclude_unset=True))

    async def delete_account(self, account_id: int, current_user: UserModel) -> None:
        account = await self._get_or_404(self.account_repo.get, account_id)

        if current_user.role in ["superuser", "admin"]:
            pass
        elif current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para eliminar esta cuenta"
            )
        else:
            self._forbidden("No tienes permiso para eliminar cuentas")

        deleted = await self.account_repo.delete(account_id)
        if not deleted:
            self._not_found("Cuenta no encontrada")

    async def get_account_businesses(self, account_id: int, current_user: UserModel):
        account = await self.account_repo.get_with_businesses(account_id)
        if not account:
            self._not_found("Cuenta no encontrada")
        if current_user.role in ["superuser", "admin", "soporte"]:
            return account.businesses
        if current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                account.user_id,
                "No autorizado para ver empresas de esta cuenta"
            )
            return account.businesses
        self._forbidden("No tienes permiso para ver empresas")