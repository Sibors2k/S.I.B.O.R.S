# tests/test_ventas_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.ventas.ventas_controller import VentasController
from modules.productos.producto_controller import ProductoController
from modules.productos.plantilla_controller import PlantillaController
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.clientes.cliente_controller import ClienteController
from modules.contabilidad.contabilidad_model import MovimientoContable
from modules.productos.models import Producto
from modules.usuarios.usuarios_model import Usuario

@pytest.fixture
def setup_controllers(db_session: Session):
    producto_ctrl = ProductoController(db_session)
    plantilla_ctrl = PlantillaController(db_session)
    contabilidad_ctrl = ContabilidadController(db_session)
    cliente_ctrl = ClienteController(db_session)
    ventas_ctrl = VentasController(db_session, producto_ctrl, contabilidad_ctrl, cliente_ctrl)
    return ventas_ctrl, producto_ctrl, plantilla_ctrl, contabilidad_ctrl, cliente_ctrl

def test_registrar_venta_exitosa(setup_controllers, test_usuario: Usuario):
    ventas_ctrl, producto_ctrl, plantilla_ctrl, contabilidad_ctrl, _ = setup_controllers
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "Teclado"}, [{"sku":"KEY-01", "precio_venta": 1500.0, "stock": 10}], test_usuario.id)
    producto = plantilla.variantes[0]
    
    venta = ventas_ctrl.registrar_venta(producto_id=producto.id, cantidad=3)
    
    db_session = producto_ctrl.db
    producto_actualizado = db_session.get(Producto, producto.id)
    assert producto_actualizado.stock == 7
    movimientos = contabilidad_ctrl.obtener_todos_movimientos()
    assert len(movimientos) == 1
    assert movimientos[0].monto == 4500.0

def test_registrar_venta_sin_stock_suficiente_falla(setup_controllers, test_usuario: Usuario):
    ventas_ctrl, _, plantilla_ctrl, _, _ = setup_controllers
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "Mouse"}, [{"sku":"MSE-01", "precio_venta": 800.0, "stock": 5}], test_usuario.id)
    producto = plantilla.variantes[0]
    
    with pytest.raises(ValueError):
        ventas_ctrl.registrar_venta(producto_id=producto.id, cantidad=6)

def test_registrar_venta_producto_inexistente_falla(setup_controllers):
    ventas_ctrl, _, _, _, _ = setup_controllers
    with pytest.raises(ValueError):
        ventas_ctrl.registrar_venta(producto_id=999, cantidad=1)

def test_listar_ventas(setup_controllers, test_usuario: Usuario):
    ventas_ctrl, _, plantilla_ctrl, _, _ = setup_controllers
    assert len(ventas_ctrl.listar_ventas()) == 0
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "Monitor"}, [{"sku":"MON-27", "precio_venta": 4000.0, "stock": 100}], test_usuario.id)
    producto = plantilla.variantes[0]

    ventas_ctrl.registrar_venta(producto_id=producto.id, cantidad=1)
    assert len(ventas_ctrl.listar_ventas()) == 1