import asyncio
import os
from pathlib import Path
import sys

# Añadir el directorio raíz al path para poder importar los módulos de la app
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.permissions import Permiso
from app.models.user import Role, Permission, RolePermission, User, UserRole
from app.core.database import DATABASE_URL

load_dotenv()

async def seed_roles_and_permissions():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            print("roles y permisos...")

            # ============================================
            # 1. Crear permisos
            # ============================================
            print("   Creando permisos...")
            permisos_creados = {}

            for perm in Permiso:
                partes = perm.value.split(':', 1)
                resource = partes[0]
                action = partes[1] if len(partes) > 1 else "unknown"

                stmt = text("SELECT id FROM permissions WHERE name = :name")
                result = await db.execute(stmt, {"name": perm.value})
                existing = result.scalar_one_or_none()

                if existing:
                    permisos_creados[perm.value] = existing
                    print(f"     ⏩ {perm.value} ya existe")
                    continue

                stmt = text("""
                    INSERT INTO permissions (name, resource, action, description)
                    VALUES (:name, :resource, :action, :description)
                    RETURNING id
                """)
                result = await db.execute(stmt, {
                    "name": perm.value,
                    "resource": resource,
                    "action": action,
                    "description": f"Permiso para {action} {resource}"
                })
                perm_id = result.scalar_one()
                permisos_creados[perm.value] = perm_id
                print(f"     ✅ {perm.value}")

            await db.commit()
            print(f"   ✅ {len(permisos_creados)} permisos creados/verificados")

            # ============================================
            # 2. Crear roles
            # ============================================
            print("\n   Creando roles...")

            admin_permissions = [
                perm for perm in Permiso
                if perm not in {
                    Permiso.VER_ROL,
                    Permiso.CREAR_ROL,
                    Permiso.EDITAR_ROL,
                    Permiso.ELIMINAR_ROL,
                    Permiso.ASIGNAR_PERMISO,
                }
            ]

            roles_data = [
                {
                    "name": "superuser",
                    "description": "Superusuario con acceso total al sistema",
                    "permissions": list(Permiso)
                },
                {
                    "name": "admin",
                    "description": "Administrador operativo del sistema",
                    "permissions": admin_permissions
                },
                {
                    "name": "soporte",
                    "description": "Personal de soporte técnico",
                    "permissions": [
                        Permiso.VER_USUARIO,
                        Permiso.VER_CUENTA,
                        Permiso.VER_EMPRESA,
                        Permiso.VER_FACTURA,
                        Permiso.VER_LOTE,
                        Permiso.VER_BUFFER,
                        Permiso.VER_ESTADISTICAS,
                        Permiso.VER_ERROR
                    ]
                },
                {
                    "name": "cobranza",
                    "description": "Departamento de cobranza",
                    "permissions": [
                        Permiso.VER_FACTURA,
                        Permiso.VER_ESTADISTICAS_FINANCIERAS
                    ]
                },
                {
                    "name": "cliente",
                    "description": "Cliente final (socio de negocio)",
                    "permissions": [
                        Permiso.VER_FACTURA,
                        Permiso.VER_ESTADISTICAS,
                        Permiso.VER_EMPRESA,
                        Permiso.VER_CUENTA,
                        Permiso.VER_LOTE,
                        Permiso.VER_BUFFER,
                        Permiso.VER_ERROR,
                        Permiso.CREAR_FACTURA,
                        Permiso.CREAR_EMPRESA,
                        Permiso.CREAR_CUENTA,
                        Permiso.CREAR_LOTE,
                        Permiso.CREAR_BUFFER,
                        Permiso.EDITAR_EMPRESA,
                        Permiso.EDITAR_CUENTA,
                        Permiso.ELIMINAR_EMPRESA,
                        Permiso.ELIMINAR_CUENTA
                    ]
                }
            ]

            roles_creados = {}
            for role_data in roles_data:
                stmt = text("SELECT id FROM roles WHERE name = :name")
                result = await db.execute(stmt, {"name": role_data["name"]})
                existing = result.scalar_one_or_none()

                if existing:
                    roles_creados[role_data["name"]] = existing
                    print(f"     ⏩ {role_data['name']} ya existe")
                    continue

                stmt = text("""
                    INSERT INTO roles (name, description)
                    VALUES (:name, :description)
                    RETURNING id
                """)
                result = await db.execute(stmt, {
                    "name": role_data["name"],
                    "description": role_data["description"]
                })
                role_id = result.scalar_one()
                roles_creados[role_data["name"]] = role_id
                print(f"     ✅ {role_data['name']}")

            await db.commit()
            print(f"   ✅ {len(roles_creados)} roles creados/verificados")

            # ============================================
            # 3. Asignar permisos a roles
            # ============================================
            print("\n   Asignando permisos a roles...")

            asignaciones = 0
            revocaciones = 0

            for role_data in roles_data:
                role_name = role_data["name"]
                role_id = roles_creados.get(role_name)
                if not role_id:
                    continue

                # Obtener IDs de permisos deseados
                desired_perm_ids = set()
                for perm in role_data["permissions"]:
                    perm_id = permisos_creados.get(perm.value)
                    if perm_id:
                        desired_perm_ids.add(perm_id)

                # Obtener permisos actuales
                stmt = text("SELECT permission_id FROM role_permissions WHERE role_id = :role_id")
                result = await db.execute(stmt, {"role_id": role_id})
                current_perm_ids = {row[0] for row in result.fetchall()}

                missing = desired_perm_ids - current_perm_ids
                extra = current_perm_ids - desired_perm_ids

                # Insertar permisos faltantes
                for perm_id in missing:
                    stmt = text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)")
                    await db.execute(stmt, {"role_id": role_id, "perm_id": perm_id})
                    asignaciones += 1

                # Eliminar permisos extra
                for perm_id in extra:
                    stmt = text("DELETE FROM role_permissions WHERE role_id = :role_id AND permission_id = :perm_id")
                    await db.execute(stmt, {"role_id": role_id, "perm_id": perm_id})
                    revocaciones += 1

            await db.commit()
            print(f"   ✅ {asignaciones} nuevas asignaciones de permisos")
            print(f"   ✅ {revocaciones} permisos revocados")

            # ============================================
            # 4. Asignar roles a usuarios existentes
            # ============================================
            print("\n   Asignando roles a usuarios existentes...")

            stmt = text("SELECT id, email, role FROM users")
            result = await db.execute(stmt)
            usuarios = result.fetchall()
            print(f"   Usuarios encontrados: {len(usuarios)}")

            asignaciones_user = 0

            role_mapping = {
                "superuser": "superuser",
                "admin": "admin",
                "soporte": "soporte",
                "cobranza": "cobranza",
                "user": "cliente",
                "cliente": "cliente"
            }

            for user_id, email, old_role in usuarios:
                print(f"   Procesando usuario: {email} (role: {old_role})")

                # Verificar si ya tiene roles
                stmt = text("SELECT role_id FROM user_roles WHERE user_id = :user_id")
                res = await db.execute(stmt, {"user_id": user_id})
                if res.first():
                    print(f"     ⏩ Usuario {email} ya tiene roles")
                    continue

                role_name = role_mapping.get(old_role, "cliente")
                role_id = roles_creados.get(role_name)

                if role_id:
                    stmt = text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)")
                    await db.execute(stmt, {"user_id": user_id, "role_id": role_id})
                    asignaciones_user += 1
                    print(f"     ✅ Usuario {email} -> {role_name}")
                else:
                    print(f"     ❌ No se encontró rol para: {role_name}")

            await db.commit()
            print(f"   ✅ {asignaciones_user} usuarios actualizados con roles")

            print("\n" + "="*50)
            print("✅ SEED COMPLETADO EXITOSAMENTE")
            print("="*50)
            print(f"   Permisos: {len(permisos_creados)}")
            print(f"   Roles: {len(roles_creados)}")
            print(f"   Asignaciones de permisos: {asignaciones}")
            print(f"   Usuarios con roles: {asignaciones_user}")
            print("="*50)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            await db.rollback()
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_roles_and_permissions())