# tests/test_cliente_controller.py
import pytest
from modules.clientes.cliente_controller import ClienteController
from modules.clientes.cliente_model import Cliente, EstadoCliente
from modules.ventas.ventas_model import Venta
from typing import Dict

@pytest.fixture
def cliente_valido_data() -> Dict:
    return {
        "nombre_completo": "Ana Sofía López", "razon_social": "Servicios Creativos ASL",
        "rfc": "LOLA900101ABC", "email": "ana.lopez@email.com",
        "telefono": "3312345678", "direccion": "Av. Creatividad 456, GDL",
        "estado": EstadoCliente.ACTIVO, "limite_credito": 10000.0
    }

def test_crear_cliente_exitoso(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    cliente = controller.agregar_cliente(cliente_valido_data)
    assert cliente.id is not None
    assert cliente.estado == EstadoCliente.ACTIVO
    assert cliente.limite_credito == 10000.0

def test_actualizar_cliente(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    cliente = controller.agregar_cliente(cliente_valido_data)
    nuevos_datos = {"telefono": "5599887766", "estado": EstadoCliente.INACTIVO, "limite_credito": 15000}
    cliente_actualizado = controller.actualizar_cliente(cliente.id, nuevos_datos)
    assert cliente_actualizado.telefono == "5599887766"
    assert cliente_actualizado.estado == EstadoCliente.INACTIVO
    assert cliente_actualizado.limite_credito == 15000.0

def test_crear_cliente_rfc_duplicado_falla(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    controller.agregar_cliente(cliente_valido_data)
    cliente_valido_data["email"] = "otro@email.com"
    with pytest.raises(ValueError, match="El RFC 'LOLA900101ABC' ya está registrado."):
        controller.agregar_cliente(cliente_valido_data)

# El resto de las pruebas no necesitan cambios, las incluyo por completitud.
def test_listar_clientes(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    assert len(controller.listar_clientes()) == 0
    controller.agregar_cliente(cliente_valido_data)
    assert len(controller.listar_clientes()) == 1

def test_eliminar_cliente_vacio_exitoso(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    cliente = controller.agregar_cliente(cliente_valido_data)
    resultado = controller.eliminar_cliente(cliente.id)
    assert resultado is True
    assert len(controller.listar_clientes()) == 0

def test_eliminar_cliente_con_ventas_asociadas_falla(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    cliente = controller.agregar_cliente(cliente_valido_data)
    venta_asociada = Venta(producto_id=1, cliente_id=cliente.id, cantidad=1, precio_unitario_venta=100.0, total_venta=100.0)
    db_session.add(venta_asociada)
    db_session.commit()
    with pytest.raises(ValueError, match="No se puede eliminar el cliente porque tiene ventas asociadas."):
        controller.eliminar_cliente(cliente.id)

def test_crear_cliente_email_invalido_falla(db_session, cliente_valido_data):
    controller = ClienteController(db_session)
    cliente_valido_data["email"] = "email-invalido"
    with pytest.raises(ValueError, match="El formato del correo electrónico no es válido."):
        controller.agregar_cliente(cliente_valido_data)