# tests/test_contabilidad_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.contabilidad.contabilidad_model import TipoMovimiento, MovimientoContable

def test_agregar_movimiento_ingreso_exitoso(db_session: Session):
    """
    Prueba que se puede agregar un movimiento de ingreso con datos válidos.
    """
    # Arrange
    controller = ContabilidadController(db_session)
    
    # Act
    movimiento = controller.agregar_movimiento(
        tipo=TipoMovimiento.INGRESO,
        concepto="Venta de prueba",
        monto=150.75,
        categoria="Ventas Online"
    )
    
    # Assert
    assert movimiento.id is not None
    assert movimiento.monto == 150.75
    assert movimiento.tipo == TipoMovimiento.INGRESO
    
    movimiento_en_db = db_session.query(MovimientoContable).one()
    assert movimiento_en_db.concepto == "Venta de prueba"

def test_agregar_movimiento_egreso_exitoso(db_session: Session):
    """
    Prueba que se puede agregar un movimiento de egreso.
    """
    # Arrange
    controller = ContabilidadController(db_session)
    
    # Act
    controller.agregar_movimiento(
        tipo=TipoMovimiento.EGRESO,
        concepto="Pago de luz",
        monto=99.99
    )
    
    # Assert
    assert db_session.query(MovimientoContable).count() == 1

def test_agregar_movimiento_monto_cero_falla(db_session: Session):
    """
    Verifica que la validación de monto <= 0 funcione correctamente.
    """
    # Arrange
    controller = ContabilidadController(db_session)
    
    # Act & Assert
    with pytest.raises(ValueError, match="El monto debe ser mayor a 0."):
        controller.agregar_movimiento(
            tipo=TipoMovimiento.INGRESO,
            concepto="Ingreso fallido",
            monto=0
        )

def test_obtener_resumen_contable(db_session: Session):
    """
    Prueba que el cálculo del resumen (ingresos, egresos, balance) es correcto.
    """
    # Arrange
    controller = ContabilidadController(db_session)
    controller.agregar_movimiento(TipoMovimiento.INGRESO, "Venta 1", 1000)
    controller.agregar_movimiento(TipoMovimiento.INGRESO, "Venta 2", 500)
    controller.agregar_movimiento(TipoMovimiento.EGRESO, "Compra material", 300)
    
    # Act
    resumen = controller.obtener_resumen()
    
    # Assert
    assert resumen["total_ingresos"] == 1500.0
    assert resumen["total_egresos"] == 300.0
    assert resumen["balance"] == 1200.0