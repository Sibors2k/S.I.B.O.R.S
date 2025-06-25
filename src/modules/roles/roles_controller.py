# src/modules/roles/roles_controller.py

from typing import List
import json
from sqlalchemy.orm import joinedload, Session
from .roles_model import Rol
from modules.usuarios.usuarios_model import Usuario

class RolesController:
    # --- INICIO DE LA REFACTORIZACIÓN ---
    def __init__(self, db_session: Session):
        """
        Inicializa el controlador con una sesión de base de datos activa.
        """
        self.db = db_session

    def crear_rol(self, nombre: str, permisos: List[str]) -> Rol:
        """Crea un nuevo rol en la base de datos."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del rol no puede estar vacío.")
        nombre_limpio = nombre.strip()
        
        if self.db.query(Rol).filter_by(nombre=nombre_limpio).first():
            raise ValueError(f"El rol '{nombre_limpio}' ya existe.")
        
        permisos_json = json.dumps(permisos)
        nuevo_rol = Rol(nombre=nombre_limpio, permisos=permisos_json)
        self.db.add(nuevo_rol)
        self.db.commit()
        self.db.refresh(nuevo_rol)
        return nuevo_rol

    def listar_roles(self) -> List[Rol]:
        """Lista todos los roles, cargando la información de los usuarios asociados."""
        return self.db.query(Rol).options(joinedload(Rol.usuarios)).order_by(Rol.nombre).all()
    # --- FIN DE LA REFACTORIZACIÓN --- (El resto de métodos seguirían este patrón)

    # Nota: Los métodos para editar, eliminar y reasignar también deberían ser refactorizados
    # a métodos de instancia, pero por ahora nos centramos en hacer pasar las pruebas actuales.