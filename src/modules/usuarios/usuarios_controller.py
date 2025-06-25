# src/modules/usuarios/usuarios_controller.py

from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import joinedload, Session
from .usuarios_model import Usuario

PERIODO_DE_GRACIA = timedelta(days=30)

class UsuariosController:
    def __init__(self, db_session: Session):
        self.db = db_session

    # ... (métodos login, listar_usuarios, crear_usuario, editar_usuario no cambian desde la última versión) ...
    def login(self, usuario: str, contrasena: str) -> Optional[Usuario]:
        user = self.db.query(Usuario).options(
            joinedload(Usuario.rol_asignado)
        ).filter(Usuario.usuario == usuario).first()
        
        if user and user.activo and user.verificar_contrasena(contrasena):
            return user
        return None

    def listar_usuarios(self) -> List[Usuario]:
        return self.db.query(Usuario).options(
            joinedload(Usuario.rol_asignado)
        ).order_by(Usuario.id).all()

    def crear_usuario(self, datos: Dict):
        if not all(k in datos for k in ["nombre", "usuario", "contrasena", "rol_id"]):
            raise ValueError("El nombre, usuario, contraseña y rol son obligatorios.")

        usuario_existente = self.db.query(Usuario).filter_by(usuario=datos["usuario"]).first()
        if usuario_existente:
            raise ValueError(f"El nombre de usuario '{datos['usuario']}' ya existe.")

        datos["contrasena"] = Usuario.hash_contrasena(datos["contrasena"])
        nuevo_usuario = Usuario(**datos)
        self.db.add(nuevo_usuario)
        self.db.commit()

    def editar_usuario(self, user_id: int, datos: Dict):
        user = self.db.get(Usuario, user_id)
        if not user: return

        if 'nueva_contrasena' in datos and datos['nueva_contrasena']:
            user.contrasena = Usuario.hash_contrasena(datos['nueva_contrasena'])
        
        if 'activo' in datos and user.activo != datos['activo']:
            user.activo = datos['activo']
            user.fecha_desactivacion = datetime.now(timezone.utc) if not datos['activo'] else None
        
        user.nombre = datos.get('nombre', user.nombre)
        user.usuario = datos.get('usuario', user.usuario)
        user.rol_id = datos.get('rol_id', user.rol_id)
        
        self.db.commit()

    def eliminar_permanentemente(self, user_id: int):
        user = self.db.get(Usuario, user_id)
        if not user: return
        if user.activo: raise ValueError("No se puede eliminar a un usuario que está activo.")
        if user.rol_asignado and user.rol_asignado.nombre.lower() == 'admin': raise ValueError("La cuenta de 'Admin' no puede ser eliminada.")
        if not user.fecha_desactivacion: raise ValueError("El usuario no tiene fecha de desactivación.")

        # --- INICIO DE LA CORRECCIÓN ---
        # Hacemos la fecha de la DB consciente de su zona horaria (UTC)
        fecha_desactivacion_aware = user.fecha_desactivacion.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) - fecha_desactivacion_aware < PERIODO_DE_GRACIA:
            dias_restantes = (PERIODO_DE_GRACIA - (datetime.now(timezone.utc) - fecha_desactivacion_aware)).days
            raise ValueError(f"Aún no se puede eliminar. Faltan {dias_restantes + 1} día(s).")
        # --- FIN DE LA CORRECCIÓN ---
        
        self.db.delete(user)
        self.db.commit()