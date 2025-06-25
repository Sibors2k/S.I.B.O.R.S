# src/modules/productos/models.py

import enum
from datetime import datetime, timezone

from sqlalchemy import (Column, Integer, String, Text, Boolean, Float,
                        ForeignKey, DateTime, Enum, Table)
from sqlalchemy.orm import relationship

from core.db import Base
from modules.categorias.categoria_model import Categoria
from modules.proveedores.proveedor_model import Proveedor
from modules.variantes.variantes_model import AtributoValor

# --- CORRECCIÓN REALIZADA ---
# La ruta correcta es 'usuarios_model.py' (plural).
from modules.usuarios.usuarios_model import Usuario
# --- FIN DE LA CORRECCIÓN ---


# --- Tabla de Asociación ---
# Define la relación muchos a muchos entre una variante (Producto) y sus valores de atributo
variante_valor_association = Table('variante_valor_association', Base.metadata,
    Column('producto_id', ForeignKey('productos.id'), primary_key=True),
    Column('atributo_valor_id', ForeignKey('atributo_valores.id'), primary_key=True)
)

# --- Modelos Principales ---

class ProductoPlantilla(Base):
    """
    Representa el producto 'padre' o 'molde'. No tiene stock ni precio propio,
    sino que agrupa a las diferentes variantes. Ej: 'Camiseta Modelo X'.
    """
    __tablename__ = "producto_plantillas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, nullable=False)
    activo = Column(Boolean, default=True)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)

    # Relaciones
    categoria = relationship("Categoria", back_populates="plantillas")
    proveedor = relationship("Proveedor", back_populates="plantillas")
    variantes = relationship("Producto", back_populates="plantilla", cascade="all, delete-orphan")
    imagenes = relationship("ProductoImagen", back_populates="plantilla", cascade="all, delete-orphan")
    
    # Relación para cuando la plantilla es un Kit
    componentes = relationship("KitComponente", foreign_keys='KitComponente.kit_plantilla_id', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ProductoPlantilla(id={self.id}, nombre='{self.nombre}')>"

class Producto(Base):
    """
    Representa la variante final y vendible de un producto. Esta es la entidad
    que tiene SKU, precio y stock. Ej: 'Camiseta Modelo X, Talla M, Color Rojo'.
    Para productos simples, habrá una sola variante sin valores de atributo.
    """
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    plantilla_id = Column(Integer, ForeignKey("producto_plantillas.id"), nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    codigo_barras_upc = Column(String(12), unique=True, nullable=True)
    codigo_barras_ean = Column(String(13), unique=True, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    precio_venta = Column(Float, nullable=False)
    costo_compra = Column(Float, nullable=True)
    
    # Relaciones
    plantilla = relationship("ProductoPlantilla", back_populates="variantes")
    valores = relationship("AtributoValor", secondary=variante_valor_association)
    historial_stock = relationship("MovimientoStock", back_populates="producto", cascade="all, delete-orphan")

# --- Modelos de Soporte ---

class ProductoImagen(Base):
    """ Almacena la ruta de las imágenes asociadas a una ProductoPlantilla. """
    __tablename__ = "producto_imagenes"
    id = Column(Integer, primary_key=True)
    plantilla_id = Column(Integer, ForeignKey("producto_plantillas.id"), nullable=False)
    ruta_imagen = Column(String(255), nullable=False)
    orden = Column(Integer, default=0)
    
    plantilla = relationship("ProductoPlantilla", back_populates="imagenes")

class KitComponente(Base):
    """

    Define la relación entre un Kit (ProductoPlantilla) y los
    productos (Variantes) que lo componen.
    """
    __tablename__ = "kit_componentes"

    id = Column(Integer, primary_key=True)
    kit_plantilla_id = Column(Integer, ForeignKey("producto_plantillas.id"), nullable=False)
    componente_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False, default=1)

    # Relación para acceder fácilmente al producto componente
    componente = relationship("Producto")

# --- Modelos para Historial y Control ---

class TipoAjusteStock(str, enum.Enum):
    """ Define los tipos de movimientos de stock permitidos en el sistema. """
    ENTRADA_COMPRA = "Entrada por Compra"
    ENTRADA_MANUAL = "Entrada Manual"
    ENTRADA_DEVOLUCION = "Entrada por Devolución"
    AJUSTE_CONTEO_POSITIVO = "Ajuste por Conteo (Sobrante)"
    AJUSTE_CONTEO_NEGATIVO = "Ajuste por Conteo (Faltante)"
    SALIDA_VENTA = "Salida por Venta"
    SALIDA_ROTURA = "Salida por Rotura o Daño"
    SALIDA_MERMA = "Salida por Merma"
    SALIDA_DEVOLUCION_PROV = "Salida a Proveedor"

class MovimientoStock(Base):
    """ Registra cada cambio en el stock de una variante de producto. """
    __tablename__ = "movimientos_stock"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) # Quién hizo el ajuste
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tipo_ajuste = Column(Enum(TipoAjusteStock), nullable=False)
    cantidad = Column(Integer, nullable=False) # Positivo para entradas, negativo para salidas
    motivo = Column(Text, nullable=True)
    stock_anterior = Column(Integer, nullable=False)
    stock_nuevo = Column(Integer, nullable=False)
    
    # Relaciones
    producto = relationship("Producto", back_populates="historial_stock")
    usuario = relationship("Usuario")