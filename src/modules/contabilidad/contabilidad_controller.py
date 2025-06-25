# src/modules/contabilidad/contabilidad_controller.py

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, case

from .contabilidad_model import TipoMovimiento, MovimientoContable
from utils.validators import validar_longitud

class ContabilidadController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def agregar_movimiento(self, tipo: TipoMovimiento, concepto: str, monto: float, descripcion: str = "", categoria: str = None):
        if not validar_longitud(concepto, 3):
            raise ValueError("El concepto debe tener al menos 3 caracteres.")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0.")
        
        nuevo_movimiento = MovimientoContable(
            tipo=tipo, 
            concepto=concepto.strip(), 
            monto=monto,
            descripcion=descripcion.strip(),
            categoria=categoria.strip() if categoria else None
        )
        self.db.add(nuevo_movimiento)
        self.db.commit()
        return nuevo_movimiento

    def obtener_todos_movimientos(self) -> List[MovimientoContable]:
        return self.db.query(MovimientoContable).order_by(MovimientoContable.fecha.desc()).all()

    def obtener_resumen(self) -> Dict[str, float]:
        total_ingresos = self.db.query(func.sum(MovimientoContable.monto)).filter(MovimientoContable.tipo == TipoMovimiento.INGRESO).scalar() or 0.0
        total_egresos = self.db.query(func.sum(MovimientoContable.monto)).filter(MovimientoContable.tipo == TipoMovimiento.EGRESO).scalar() or 0.0
        balance = total_ingresos - total_egresos
        return {"total_ingresos": total_ingresos, "total_egresos": total_egresos, "balance": balance}