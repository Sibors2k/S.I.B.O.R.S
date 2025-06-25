# src/modules/compras/compra_model.py
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from core.db import Base

class EstadoOrdenCompra(str, enum.Enum):
    PENDIENTE = "Pendiente"
    RECIBIDA = "Recibida"
    CANCELADA = "Cancelada"

class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"
    id = Column(Integer, primary_key=True, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    fecha_emision = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    fecha_recepcion = Column(DateTime(timezone=True), nullable=True)
    estado = Column(SQLAlchemyEnum(EstadoOrdenCompra), nullable=False, default=EstadoOrdenCompra.PENDIENTE)
    total = Column(Float, nullable=False, default=0.0)
    
    proveedor = relationship("Proveedor")
    detalles = relationship("DetalleCompra", back_populates="orden", cascade="all, delete-orphan")

class DetalleCompra(Base):
    __tablename__ = "detalles_compra"
    id = Column(Integer, primary_key=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=False)
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Apuntamos a la tabla correcta: 'productos.id'
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    # --- FIN DE LA CORRECCIÓN ---
    
    cantidad = Column(Integer, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    
    orden = relationship("OrdenCompra", back_populates="detalles")
    # Esta relación ahora podrá encontrar la tabla 'productos' correctamente.
    producto = relationship("Producto")