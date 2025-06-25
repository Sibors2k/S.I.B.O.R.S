# src/modules/empresa/empresa_model.py

from sqlalchemy import Column, Integer, String
from typing import Optional
from dataclasses import dataclass
from core.db import Base

@dataclass
class EmpresaData:
    """DTO para mover los datos de la empresa."""
    id: Optional[int] = None
    nombre: Optional[str] = None
    rfc: Optional[str] = None
    correo_principal: Optional[str] = None
    telefono_principal: Optional[str] = None
    calle_fiscal: Optional[str] = None
    numero_fiscal: Optional[str] = None
    colonia_fiscal: Optional[str] = None
    cp_fiscal: Optional[str] = None
    ciudad_fiscal: Optional[str] = None
    estado_fiscal: Optional[str] = None
    nombre_representante: Optional[str] = None
    curp_representante: Optional[str] = None
    ruta_logo: Optional[str] = None

class Empresa(Base):
    """Modelo ORM para la tabla 'empresa'."""
    __tablename__ = 'empresa'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200))
    rfc = Column(String(13), unique=True)
    correo_principal = Column(String(100))
    telefono_principal = Column(String(20))
    calle_fiscal = Column(String(200))
    numero_fiscal = Column(String(50))
    colonia_fiscal = Column(String(100))
    cp_fiscal = Column(String(10))
    ciudad_fiscal = Column(String(100))
    estado_fiscal = Column(String(100))
    nombre_representante = Column(String(200))
    curp_representante = Column(String(18))
    ruta_logo = Column(String(255))