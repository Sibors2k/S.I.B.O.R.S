# src/modules/ventas/ventas_model.py (v2.0 - Reescritura completa)

import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from core.db import Base
from modules.usuarios.usuarios_model import Usuario
from modules.clientes.cliente_model import Cliente
from modules.productos.models import Producto

class EstadoVenta(str, enum.Enum):
    """Define los estados de una transacción de venta."""
    EN_PROGRESO = "En Progreso"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    EN_ESPERA = "En Espera" # Para la futura funcionalidad de "pausar" ventas

class MetodoPago(str, enum.Enum):
    """Define los métodos de pago aceptados."""
    EFECTIVO = "Efectivo"
    TARJETA_CREDITO = "Tarjeta de Crédito"
    TARJETA_DEBITO = "Tarjeta de Débito"
    TRANSFERENCIA = "Transferencia"
    CREDITO_TIENDA = "Crédito de la Tienda"
    OTRO = "Otro"

class Venta(Base):
    """
    Representa una transacción de venta completa (un ticket o factura).
    Contiene la información general de la venta.
    """
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    estado = Column(Enum(EstadoVenta), nullable=False, default=EstadoVenta.EN_PROGRESO)
    
    subtotal = Column(Float, nullable=False, default=0.0)
    descuento_total = Column(Float, nullable=False, default=0.0)
    impuestos = Column(Float, nullable=False, default=0.0)
    total = Column(Float, nullable=False, default=0.0)

    # Relaciones
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    cliente = relationship("Cliente", back_populates="ventas")
    usuario = relationship("Usuario")
    
    detalles = relationship("VentaDetalle", back_populates="venta", cascade="all, delete-orphan")
    pagos = relationship("VentaPago", back_populates="venta", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venta(id={self.id}, total={self.total}, estado='{self.estado.value}')>"

class VentaDetalle(Base):
    """
    Representa una línea de producto dentro de una Venta.
    Ej: 2 x Camiseta Roja Talla M a $19.99 c/u.
    """
    __tablename__ = "venta_detalles"
    
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    descuento_linea = Column(Float, nullable=False, default=0.0)
    subtotal_linea = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")

class VentaPago(Base):
    """
    Registra los pagos aplicados a una Venta.
    """
    __tablename__ = "venta_pagos"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    metodo_pago = Column(Enum(MetodoPago), nullable=False)
    monto = Column(Float, nullable=False)
    
    venta = relationship("Venta", back_populates="pagos")