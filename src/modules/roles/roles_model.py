# src/modules/roles/roles_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.db import Base
import json

class Rol(Base):
    """
    Modelo para la tabla 'roles'. Define los roles predeterminados del sistema
    y los permisos asociados a cada uno.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False, index=True)
    
    # Guardaremos los permisos como un string en formato JSON.
    # Ej: '["ventas", "inventario", "perfil"]'
    permisos = Column(String, nullable=False)

    # La relación inversa: Un rol puede estar asignado a muchos usuarios.
    # Esto nos permitirá en el futuro preguntar: "¿Qué usuarios son Vendedores?"
    usuarios = relationship("Usuario", back_populates="rol_asignado")

    def obtener_permisos_como_lista(self) -> list:
        """Devuelve los permisos del string JSON como una lista de Python."""
        try:
            return json.loads(self.permisos)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}')>"