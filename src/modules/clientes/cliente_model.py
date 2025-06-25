# src/modules/clientes/cliente_model.py

from sqlalchemy import Column, Integer, String, Float, Enum
from sqlalchemy.orm import relationship
from core.db import Base
import enum

class EstadoCliente(str, enum.Enum):
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    MOROSO = "Moroso"

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(150), nullable=False)
    razon_social = Column(String(200))
    rfc = Column(String(13), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    telefono = Column(String(20))
    direccion = Column(String(255))
    
    estado = Column(Enum(EstadoCliente), nullable=False, default=EstadoCliente.ACTIVO)
    limite_credito = Column(Float, nullable=False, default=0.0)

    ventas = relationship("Venta", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente(id={self.id}, nombre='{self.nombre_completo}')>"