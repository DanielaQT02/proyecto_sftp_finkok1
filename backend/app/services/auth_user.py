from fastapi import HTTPException, status

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
import hashlib
import base64
from datetime import datetime, timedelta
from app.services.base import BaseService


class AuthService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: UserCreate):
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            self._bad_request("El email ya está registrado")
        return await self.user_repo.create(user_data.dict())

    async def login(self, username: str, password: str):
        user = await self.user_repo.get_by_email(username)
        def simple_verify_password(plain, hashed):
            return hashed == base64.b64encode(hashlib.sha256(plain.encode()).digest()).decode()
        if not user or not simple_verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.active:
            self._bad_request("Usuario inactivo")
        token_data = {
            "sub": user.email,
            "user_id": user.id,
            "roles": [user.role],
            "exp": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }
        access_token = base64.b64encode(str(token_data).encode()).decode()
        return {"access_token": access_token, "token_type": "bearer"}