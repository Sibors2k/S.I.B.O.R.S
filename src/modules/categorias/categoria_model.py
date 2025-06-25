# src/modules/categorias/categoria_model.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    
    categoria_padre_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    padre = relationship("Categoria", remote_side=[id], back_populates="subcategorias")
    subcategorias = relationship("Categoria", back_populates="padre", cascade="all, delete-orphan")
    
    # --- INICIO DE LA CORRECCIÓN ---
    # La relación ya no es con 'Producto', sino con 'ProductoPlantilla'.
    # Cambiamos el nombre de la relación de 'productos' a 'plantillas' para ser consistentes.
    plantillas = relationship("ProductoPlantilla", back_populates="categoria")
    # --- FIN DE LA CORRECCIÓN ---

    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre='{self.nombre}')>"