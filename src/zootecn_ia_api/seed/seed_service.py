from pathlib import Path
import json
from typing import Any, Callable
from sqlalchemy.orm import Session
from zootecn_ia_api.models.userModel import Role, RoleEnum, User

# Definición de rutas
ROLES_FILE = Path(__file__).with_name("data") / "roles.json"
USER_FILE = Path(__file__).with_name("data") / "users.json"

def _load_data_files(list_of_files: list[Path]) -> dict[str, list[dict[str, Any]]]:
    data = {}
    for file_path in list_of_files:
        with file_path.open(encoding="utf-8") as file:
            data[file_path.name] = json.load(file)
    return data


# --- 1. FUNCIÓN ESPECÍFICA PARA ROLES ---
def seed_roles(db: Session, records: list[dict[str, Any]]) -> dict[str, int]:
    """Inserta o actualiza roles desde los datos del JSON."""
    created = 0
    updated = 0

    for role_data in records:
        role_id = role_data.get("id")
        role_name = RoleEnum(role_data["name"]) # Asegúrate de tener importado RoleEnum y Role
        
        # Buscar por ID o por Nombre como tenías originalmente
        role = None
        if role_id:
            role = db.query(Role).filter(Role.id == role_id).first()
        
        if role is None:
            role = db.query(Role).filter(Role.name == role_name).first()

        if role is None:
            db.add(
                Role(
                    id=role_id,
                    name=role_name,
                    description=role_data.get("description"),
                )
            )
            created += 1
        else:
            role.name = role_name
            role.description = role_data.get("description")
            updated += 1

    return {"created": created, "updated": updated, "total": len(records)}


# --- 2. FUNCIÓN ESPECÍFICA PARA USUARIOS (Ejemplo de nueva tabla) ---
def seed_users(db: Session, records: list[dict[str, Any]]) -> dict[str, int]:
    """Inserta o actualiza usuarios desde los datos del JSON."""
    created = 0
    updated = 0

    for user_data in records:
        email = user_data["email"]
        user = db.query(User).filter(User.email == email).first() # Asumiendo modelo User

        if user is None:
            # Lógica para crear usuario (ej. hashear password, etc.)
            db.add(User(**user_data))
            created += 1
        else:
            # Lógica para actualizar campos si ya existe
            for key, value in user_data.items():
                setattr(user, key, value)
            updated += 1

    return {"created": created, "updated": updated, "total": len(records)}


# --- MAPA DE SEEDS (Aquí vinculas archivo -> función) ---
# Usamos el nombre del archivo exacto como clave
SEED_REGISTRY: dict[str, Callable[[Session, list[dict[str, Any]]], dict[str, int]]] = {
    "roles.json": seed_roles,
    "users.json": seed_users,
}


# --- 3. FUNCIÓN PRINCIPAL UNIFICADA ---
def load_seeds(db: Session) -> dict[str, Any]:
    """Carga todas las seeds iterando sobre el registro de archivos."""
    # Mapeamos los archivos que queremos procesar
    files_to_load = [
        ROLES_FILE
        # USER_FILE
    ]
    data = _load_data_files(list_of_files=files_to_load)

    total_created = 0
    total_updated = 0
    total_records = 0
    summary = {}

    try:
        for file_path in files_to_load:
            file_name = file_path.name
            records = data.get(file_name, [])

            # Buscamos si existe una función registrada para este archivo
            if file_name in SEED_REGISTRY:
                print(f"Procesando seeds de: {file_name}...")
                result = SEED_REGISTRY[file_name](db, records)
                
                # Acumulamos estadísticas generales
                total_created += result["created"]
                total_updated += result["updated"]
                total_records += result["total"]
                summary[file_name] = result
            else:
                print(f"Advertencia: No hay función de seed registrada para {file_name}")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error cargando seeds: {e}")
        raise

    return {
        "created": total_created,
        "updated": total_updated,
        "total": total_records,
        "details": summary # Opcional: te muestra el desglose por archivo
    }