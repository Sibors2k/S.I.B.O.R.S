# src/modules/variantes/variantes_model.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.db import Base

class Atributo(Base):
    """
    Define un tipo de variación para un producto. 
    Ejemplos: "Color", "Talla", "Material", "Capacidad".
    """
    __tablename__ = "atributos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)

    valores = relationship("AtributoValor", back_populates="atributo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Atributo(id={self.id}, nombre='{self.nombre}')>"

class AtributoValor(Base):
    """
    Define un valor específico para un Atributo.
    Ejemplos: "Rojo" (para Color), "XL" (para Talla), "256GB" (para Capacidad).
    """
    __tablename__ = "atributo_valores"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(String(100), nullable=False)
    
    # --- INICIO DE LA MODIFICACIÓN ---
    # Nueva columna para almacenar el código de color hexadecimal (ej. #FF0000).
    # Es opcional, ya que solo se usará para el atributo "Color".
    codigo_color = Column(String(7), nullable=True)
    # --- FIN DE LA MODIFICACIÓN ---

    atributo_id = Column(Integer, ForeignKey("atributos.id"), nullable=False)
    atributo = relationship("Atributo", back_populates="valores")

    def __repr__(self):
        return f"<AtributoValor(id={self.id}, valor='{self.valor}')>"