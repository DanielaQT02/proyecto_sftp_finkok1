from fastapi import Depends, HTTPException, status
from typing import List, Union
from .permissions import Permiso
from .security import get_current_user
from app.models.user import User


class PermissionChecker:
    """
    Dependencia que verifica si el usuario autenticado tiene los permisos requeridos.
    require_all=True -> se requieren todos los permisos listados.
    require_all=False -> se requiere al menos uno de los permisos listados.
    """
    def __init__(
        self,
        required_permissions: List[Union[Permiso, str]],
        require_all: bool = True,
    ):
        self.required_permissions = [
            p.value if isinstance(p, Permiso) else str(p)
            for p in required_permissions
        ]
        self.require_all = require_all

    async def __call__(self, current_user: User = Depends(get_current_user)):
        user_permissions = set(current_user.permissions)

        if self.require_all:
            missing = [p for p in self.required_permissions if p not in user_permissions]
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permisos requeridos: {missing}"
                )
        else:
            has_any = any(p in user_permissions for p in self.required_permissions)
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Se requiere alguno de estos permisos: {self.required_permissions}"
                )
        return current_user


def require_permission(required_permission: Union[Permiso, str]):
    """Helper para requerir un solo permiso."""
    return PermissionChecker([required_permission])


def require_any_permission(required_permissions: List[Union[Permiso, str]]):
    """Helper para requerir al menos uno de los permisos listados."""
    return PermissionChecker(required_permissions, require_all=False)