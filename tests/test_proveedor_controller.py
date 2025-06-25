# tests/test_proveedor_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.proveedores.proveedor_controller import ProveedorController
from modules.proveedores.proveedor_model import Proveedor
from modules.productos.plantilla_controller import PlantillaController
from modules.usuarios.usuarios_model import Usuario

@pytest.fixture
def proveedor_valido_data():
    return {"nombre_empresa": "Tech Solutions", "email": "contacto@tech.com"}

def test_crear_proveedor_exitoso(db_session: Session, proveedor_valido_data):
    controller = ProveedorController(db_session)
    proveedor = controller.agregar_proveedor(proveedor_valido_data)
    assert proveedor.id is not None

def test_eliminar_proveedor_con_productos_asociados_falla(db_session: Session, proveedor_valido_data, test_usuario: Usuario):
    """
    Prueba que no se puede eliminar un proveedor si tiene plantillas de producto asociadas.
    """
    # Arrange
    proveedor_ctrl = ProveedorController(db_session)
    plantilla_ctrl = PlantillaController(db_session)
    
    proveedor = proveedor_ctrl.agregar_proveedor(proveedor_valido_data)
    
    # Creamos una plantilla y la asociamos con el proveedor
    datos_plantilla = {"nombre": "Laptop Pro", "proveedor_id": proveedor.id}
    datos_variante = [{"sku": "LP-01", "precio": 25000.0}]
    plantilla_ctrl.crear_plantilla_con_variantes(datos_plantilla, datos_variante, test_usuario.id)
    
    # Act & Assert
    with pytest.raises(ValueError, match="No se puede eliminar el proveedor porque tiene productos asociados."):
        proveedor_ctrl.eliminar_proveedor(proveedor.id)

def test_crear_proveedor_email_duplicado_falla(db_session: Session, proveedor_valido_data):
    controller = ProveedorController(db_session)
    controller.agregar_proveedor(proveedor_valido_data)
    with pytest.raises(ValueError):
        controller.agregar_proveedor(proveedor_valido_data)
        
def test_listar_proveedores(db_session: Session, proveedor_valido_data):
    controller = ProveedorController(db_session)
    assert len(controller.listar_proveedores()) == 0
    controller.agregar_proveedor(proveedor_valido_data)
    assert len(controller.listar_proveedores()) == 1

def test_actualizar_proveedor(db_session: Session, proveedor_valido_data):
    controller = ProveedorController(db_session)
    proveedor = controller.agregar_proveedor(proveedor_valido_data)
    controller.actualizar_proveedor(proveedor.id, {"telefono": "8187654321"})
    proveedor_actualizado = db_session.get(Proveedor, proveedor.id)
    assert proveedor_actualizado.telefono == "8187654321"

def test_eliminar_proveedor_vacio_exitoso(db_session: Session, proveedor_valido_data):
    controller = ProveedorController(db_session)
    proveedor = controller.agregar_proveedor(proveedor_valido_data)
    assert controller.eliminar_proveedor(proveedor.id) is True