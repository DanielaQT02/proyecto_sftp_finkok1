from fastapi import HTTPException, status
from typing import Callable, List, Optional, TypeVar, Awaitable, Any

T = TypeVar('T')

class BaseService:
    def __init__(self, db=None):
        self.db = db

    def _forbidden(self, detail: str = "No autorizado") -> None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    def _not_found(self, detail: str = "Recurso no encontrado") -> None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    def _bad_request(self, detail: str = "Solicitud incorrecta") -> None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    def _require_roles(self, current_user, allowed_roles: List[str], detail: str = "No tienes permiso") -> None:
        if current_user.role not in allowed_roles:
            self._forbidden(detail)

    def _require_owner_or_roles(self, current_user, owner_user_id: int,
                                 allowed_roles: Optional[List[str]] = None,
                                 detail: str = "No autorizado para este recurso") -> None:
        if allowed_roles is None:
            allowed_roles = ["superuser", "admin"]
        if current_user.role in allowed_roles:
            return
        if current_user.id == owner_user_id:
            return
        self._forbidden(detail)

    def _check_ownership(self, current_user, owner_user_id: int,
                         detail: str = "No eres el dueño de este recurso") -> None:
        if current_user.id != owner_user_id:
            self._forbidden(detail)

    def _allow_superuser_admin_or_owner(self, current_user, owner_user_id: int,
                                        detail: str = "No autorizado para este recurso") -> None:
        if current_user.role in ["superuser", "admin"]:
            return
        if current_user.id == owner_user_id:
            return
        self._forbidden(detail)

    def _client_owns_resource(self, current_user, owner_user_id: int,
                              detail: str = "No autorizado para este recurso") -> None:
        if current_user.role != "cliente":
            self._forbidden(detail)
        self._check_ownership(current_user, owner_user_id, detail)

    async def _get_or_404(self, repo_method: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        result = await repo_method(*args, **kwargs)
        if result is None:
            self._not_found()
        return result

    async def _exists(self, repo_method: Callable[..., Awaitable[Any]], *args, **kwargs) -> bool:
        result = await repo_method(*args, **kwargs)
        return result is not None

    async def _ensure_unique(self, repo_method: Callable[..., Awaitable[Any]], *args,
                             error_msg: str = "Ya existe un recurso con esos datos",
                             **kwargs) -> None:
        if await self._exists(repo_method, *args, **kwargs):
            self._bad_request(error_msg)

    def _manual_paginate(self, items: List[T], skip: int, limit: int) -> List[T]:
        return items[skip:skip + limit]