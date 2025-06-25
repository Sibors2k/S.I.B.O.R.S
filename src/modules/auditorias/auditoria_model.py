# src/modules/auditorias/auditoria_model.py

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class EstadoAuditoria(str, enum.Enum):
    """Define los estados posibles de una auditoría de inventario."""
    EN_PROGRESO = "En Progreso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"

class Auditoria(Base):
    """
    Modelo ORM para la tabla 'auditorias'.
    Representa un evento de conteo de inventario (un expediente de auditoría).
    """
    __tablename__ = "auditorias"

    id = Column(Integer, primary_key=True, index=True)
    fecha_inicio = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    fecha_fin = Column(DateTime(timezone=True), nullable=True)
    estado = Column(SQLAlchemyEnum(EstadoAuditoria), nullable=False, default=EstadoAuditoria.EN_PROGRESO)
    notas = Column(Text, nullable=True)

    # Relación con el usuario que realiza la auditoría
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    usuario = relationship("Usuario")

    # Relación uno-a-muchos: Una auditoría tiene muchos detalles (un producto contado por línea)
    detalles = relationship("AuditoriaDetalle", back_populates="auditoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Auditoria(id={self.id}, estado='{self.estado.value}')>"

class AuditoriaDetalle(Base):
    """
    Modelo ORM para la tabla 'auditoria_detalles'.
    Almacena el conteo de un producto específico dentro de una auditoría.
    """
    __tablename__ = "auditoria_detalles"
    
    id = Column(Integer, primary_key=True)
    
    # Relación con la auditoría principal a la que pertenece este detalle
    auditoria_id = Column(Integer, ForeignKey("auditorias.id"), nullable=False)
    auditoria = relationship("Auditoria", back_populates="detalles")

    # Relación con el producto que se contó
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto = relationship("Producto")

    stock_sistema = Column(Integer, nullable=False)  # El stock que el sistema decía que había
    stock_fisico = Column(Integer, nullable=False)   # El stock que se contó realmente
    diferencia = Column(Integer, nullable=False)     # stock_fisico - stock_sistema

    def __repr__(self):
        return f"<AuditoriaDetalle(id={self.id}, producto_id={self.producto_id}, diferencia={self.diferencia})>"