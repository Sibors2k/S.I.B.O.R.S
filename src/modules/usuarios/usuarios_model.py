# src/modules/usuarios/usuarios_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base
import bcrypt
from datetime import datetime
from modules.roles.roles_model import Rol

class Usuario(Base):
    """
    Modelo de la tabla 'usuarios'. Ahora incluye una fecha de desactivación.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    usuario = Column(String(50), unique=True, nullable=False, index=True)
    contrasena = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    creado = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- INICIO DEL CAMBIO ---
    # Nuevo campo para registrar cuándo se desactiva un usuario.
    # Puede ser nulo, porque solo tendrá valor si el usuario está inactivo.
    fecha_desactivacion = Column(DateTime(timezone=True), nullable=True)
    # --- FIN DEL CAMBIO ---

    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    rol_asignado = relationship("Rol", back_populates="usuarios")
    
    # El campo 'modulos' se deja por si se quiere re-implementar una lógica
    # de permisos extra además del rol, pero ya no lo usamos activamente.
    modulos = Column(String, nullable=True)

    perfil = relationship(
        "Perfil",
        back_populates="usuario",
        cascade="all, delete-orphan",
        uselist=False
    )
    
    def verificar_contrasena(self, contrasena_plana: str) -> bool:
        return bcrypt.checkpw(contrasena_plana.encode(), self.contrasena.encode())

    @staticmethod
    def hash_contrasena(contrasena_plana: str) -> str:
        hashed_bytes = bcrypt.hashpw(contrasena_plana.encode(), bcrypt.gensalt())
        return hashed_bytes.decode()