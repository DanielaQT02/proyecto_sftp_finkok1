from enum import Enum

class Permiso(str, Enum):
    # Usuarios
    VER_USUARIO = "ver:usuario"
    CREAR_USUARIO = "crear:usuario"
    EDITAR_USUARIO = "editar:usuario"
    ELIMINAR_USUARIO = "eliminar:usuario"

    # Cuentas
    VER_CUENTA = "ver:cuenta"
    CREAR_CUENTA = "crear:cuenta"
    EDITAR_CUENTA = "editar:cuenta"
    ELIMINAR_CUENTA = "eliminar:cuenta"

    # Empresas
    VER_EMPRESA = "ver:empresa"
    CREAR_EMPRESA = "crear:empresa"
    EDITAR_EMPRESA = "editar:empresa"
    ELIMINAR_EMPRESA = "eliminar:empresa"

    # Facturas
    VER_FACTURA = "ver:factura"
    CREAR_FACTURA = "crear:factura"
    EDITAR_FACTURA = "editar:factura"
    ELIMINAR_FACTURA = "eliminar:factura"

    # Lotes
    VER_LOTE = "ver:lote"
    CREAR_LOTE = "crear:lote"
    EDITAR_LOTE = "editar:lote"
    ELIMINAR_LOTE = "eliminar:lote"

    # Buffer
    VER_BUFFER = "ver:buffer"
    CREAR_BUFFER = "crear:buffer"
    EDITAR_BUFFER = "editar:buffer"
    ELIMINAR_BUFFER = "eliminar:buffer"

    # Estadísticas
    VER_ESTADISTICAS = "ver:estadisticas"
    VER_ESTADISTICAS_FINANCIERAS = "ver:estadisticas_financieras"

    # Errores
    VER_ERROR = "ver:error"

    # Roles y permisos
    VER_ROL = "ver:rol"
    CREAR_ROL = "crear:rol"
    EDITAR_ROL = "editar:rol"
    ELIMINAR_ROL = "eliminar:rol"
    ASIGNAR_PERMISO = "asignar:permiso"