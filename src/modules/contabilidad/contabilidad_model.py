# src/modules/contabilidad/contabilidad_model.py

import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, func, case
from typing import List, Optional, Dict, Any
from core.db import Base
# --- INICIO DE LA CORRECCIÓN ---
from datetime import datetime, timedelta, timezone
# --- FIN DE LA CORRECCIÓN ---

class TipoMovimiento(enum.Enum):
    INGRESO = "ingreso"
    EGRESO = "egreso"

class MovimientoContable(Base):
    __tablename__ = "movimientos_contables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    concepto = Column(String, nullable=False)
    descripcion = Column(String)
    monto = Column(Float, nullable=False)
    # --- INICIO DE LA CORRECCIÓN ---
    # Usamos la función moderna, envuelta en una lambda para que se ejecute en cada inserción.
    fecha = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # --- FIN DE LA CORRECCIÓN ---
    categoria = Column(String)

# El resto del archivo (clase ContabilidadRepository) no necesita cambios.
# ...