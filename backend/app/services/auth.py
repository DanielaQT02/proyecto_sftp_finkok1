from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import security
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.base import BaseService
from app.models.user import Role, UserRole


class AuthService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: UserCreate):
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            self._bad_request("El email ya está registrado")
        
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = security.hash_password(user_dict.pop("password"))
        new_user = await self.user_repo.create(user_dict)
        
        # Asignar rol "cliente" por defecto
        stmt = select(Role).where(Role.name == "cliente")
        role = (await self.db.execute(stmt)).scalar_one_or_none()
        if role:
            user_role = UserRole(user_id=new_user.id, role_id=role.id)
            self.db.add(user_role)
            await self.db.commit()
        
        return new_user

    async def login(self, username: str, password: str):
        user = await self.user_repo.get_by_email(username)
        if not user or not security.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.active:
            self._bad_request("Usuario inactivo")
        
        # Obtener roles y permisos
        roles = [role.name for role in user.roles]
        permissions = user.permissions
        
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "roles": roles,
            "permissions": permissions,
        }
        token = security.create_access_token(token_data)
        return {"access_token": token, "token_type": "bearer"}