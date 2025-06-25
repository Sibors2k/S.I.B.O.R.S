# tests/test_compra_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.productos.producto_controller import ProductoController
from modules.productos.plantilla_controller import PlantillaController
from modules.compras.compra_controller import CompraController
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.proveedores.proveedor_controller import ProveedorController
from modules.compras.compra_model import EstadoOrdenCompra
from modules.contabilidad.contabilidad_model import MovimientoContable, TipoMovimiento
from modules.productos.models import Producto, TipoAjusteStock
from modules.usuarios.usuarios_model import Usuario

@pytest.fixture
def setup_controllers(db_session: Session):
    producto_ctrl = ProductoController(db_session)
    plantilla_ctrl = PlantillaController(db_session)
    contabilidad_ctrl = ContabilidadController(db_session)
    proveedor_ctrl = ProveedorController(db_session)
    compra_ctrl = CompraController(db_session, producto_ctrl, contabilidad_ctrl)
    return compra_ctrl, producto_ctrl, plantilla_ctrl, contabilidad_ctrl, proveedor_ctrl

def test_crear_orden_compra(setup_controllers, test_usuario: Usuario):
    compra_ctrl, _, plantilla_ctrl, _, proveedor_ctrl = setup_controllers
    proveedor = proveedor_ctrl.agregar_proveedor({"nombre_empresa": "ProveeTech", "email": "contact@proveetech.com"})
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "Cable USB-C"}, [{"sku":"CABLE-C", "precio_venta": 150.0}], test_usuario.id)
    producto1_id = plantilla.variantes[0].id

    detalles = [{"producto_id": producto1_id, "cantidad": 10, "costo_unitario": 80.0}]
    orden = compra_ctrl.crear_orden_compra(proveedor_id=proveedor.id, detalles_data=detalles)
    
    assert orden.id is not None
    assert orden.total == 800.0

def test_marcar_orden_como_recibida(setup_controllers, test_usuario: Usuario):
    compra_ctrl, producto_ctrl, plantilla_ctrl, contabilidad_ctrl, proveedor_ctrl = setup_controllers
    proveedor = proveedor_ctrl.agregar_proveedor({"nombre_empresa": "ProveeTech", "email": "contact@proveetech.com"})
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "SSD 1TB"}, [{"sku":"SSD-1T", "precio_venta": 2500.0, "costo_compra": 1800.0, "stock": 0}], test_usuario.id)
    producto1 = plantilla.variantes[0]
    
    detalles = [{"producto_id": producto1.id, "cantidad": 5, "costo_unitario": 1800.0}]
    orden = compra_ctrl.crear_orden_compra(proveedor_id=proveedor.id, detalles_data=detalles)
    
    compra_ctrl.marcar_orden_como_recibida(orden.id, test_usuario.id)
    
    db_session = producto_ctrl.db
    producto_actualizado = db_session.get(Producto, producto1.id)
    assert producto_actualizado.stock == 5
    
    # --- INICIO DE LA MODIFICACIÓN ---
    # La aserción correcta es 1, porque el producto se creó con stock 0, por lo que no
    # hubo movimiento inicial. El único movimiento es el de la compra.
    assert len(producto_actualizado.historial_stock) == 1
    # --- FIN DE LA MODIFICACIÓN ---
    
    mov_contable = db_session.query(MovimientoContable).one()
    assert mov_contable.tipo == TipoMovimiento.EGRESO
    assert mov_contable.monto == 9000.0

def test_marcar_orden_ya_recibida_falla(setup_controllers, test_usuario: Usuario):
    compra_ctrl, _, plantilla_ctrl, _, proveedor_ctrl = setup_controllers
    proveedor = proveedor_ctrl.agregar_proveedor({"nombre_empresa": "ProveeTech", "email": "contact@proveetech.com"})
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "RAM 16GB"}, [{"sku":"RAM-16", "precio_venta": 900.0}], test_usuario.id)
    producto1_id = plantilla.variantes[0].id

    detalles = [{"producto_id": producto1_id, "cantidad": 2, "costo_unitario": 600.0}]
    orden = compra_ctrl.crear_orden_compra(proveedor_id=proveedor.id, detalles_data=detalles)
    
    compra_ctrl.marcar_orden_como_recibida(orden.id, test_usuario.id)
    with pytest.raises(ValueError):
        compra_ctrl.marcar_orden_como_recibida(orden.id, test_usuario.id)

def test_listar_ordenes_compra(setup_controllers, test_usuario: Usuario):
    compra_ctrl, _, plantilla_ctrl, _, proveedor_ctrl = setup_controllers
    assert len(compra_ctrl.listar_ordenes_compra()) == 0
    proveedor = proveedor_ctrl.agregar_proveedor({"nombre_empresa": "ProveeTech", "email": "contact@proveetech.com"})
    
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes({"nombre": "Mousepad XL"}, [{"sku":"MOUSE-XL", "precio_venta": 250.0}], test_usuario.id)
    producto1_id = plantilla.variantes[0].id

    detalles = [{"producto_id": producto1_id, "cantidad": 1, "costo_unitario": 200.0}]
    compra_ctrl.crear_orden_compra(proveedor_id=proveedor.id, detalles_data=detalles)
    assert len(compra_ctrl.listar_ordenes_compra()) == 1