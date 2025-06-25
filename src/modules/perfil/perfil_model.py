# src/modules/perfil/perfil_model.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.db import Base

class Perfil(Base):
    """
    Modelo de la tabla 'perfiles'. Almacena la información personal y
    extendida de un usuario. Está vinculada en una relación uno-a-uno
    con la tabla 'usuarios'.
    """
    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- La Llave Foránea: La conexión con la tabla de usuarios ---
    # Cada perfil DEBE pertenecer a un único usuario y no puede ser nulo.
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)

    # --- Campos de Información del Perfil ---
    nombre = Column(String(100), nullable=True)
    apellidos = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True, index=True)
    telefono = Column(String(20), nullable=True)
    cargo = Column(String(100), nullable=True)
    biografia = Column(Text, nullable=True)
    avatar_path = Column(String(255), nullable=True) # Ruta a la imagen del avatar

    # --- Campos de Fecha para Auditoría ---
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # --- La Relación Inversa ---
    # Este es el otro extremo del "hilo" que conecta con la relación 'perfil'
    # definida en el modelo Usuario.
    usuario = relationship("Usuario", back_populates="perfil")

    def __repr__(self):
        return f"<Perfil(id={self.id}, usuario_id={self.usuario_id}, nombre='{self.nombre}')>"