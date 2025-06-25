# src/modules/proveedores/proveedor_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.db import Base

class Proveedor(Base):
    """
    Modelo ORM para la tabla 'proveedores'.
    Almacena la información de las empresas o personas que suministran productos.
    """
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String(150), nullable=False, unique=True)
    persona_contacto = Column(String(150))
    email = Column(String(100), unique=True, index=True)
    telefono = Column(String(20))
    direccion = Column(String(255))
    sitio_web = Column(String(100))

    # --- INICIO DE LA CORRECCIÓN ---
    # La relación ya no es con 'Producto', sino con 'ProductoPlantilla'.
    # Un proveedor ahora suministra plantillas de producto.
    plantillas = relationship("ProductoPlantilla", back_populates="proveedor")
    # --- FIN DE LA CORRECCIÓN ---


    def __repr__(self):
        return f"<Proveedor(id={self.id}, nombre='{self.nombre_empresa}')>"