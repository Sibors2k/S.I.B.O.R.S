# tests/test_producto_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.productos.producto_controller import ProductoController
from modules.productos.plantilla_controller import PlantillaController
from modules.productos.models import TipoAjusteStock
from modules.usuarios.usuarios_model import Usuario

# Asumimos que conftest.py provee las fixtures 'db_session' y 'test_usuario'

@pytest.fixture
def producto_de_prueba(db_session: Session, test_usuario: Usuario) -> int:
    """Fixture para crear un producto simple y devolver el ID de su variante."""
    plantilla_ctrl = PlantillaController(db_session)
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes(
        {"nombre": "Producto para Ajuste"},
        [{"sku": "ADJ-01", "precio": 50, "stock": 100}],
        test_usuario.id
    )
    return plantilla.variantes[0]

def test_ajustar_stock_aumento(db_session: Session, test_usuario: Usuario, producto_de_prueba):
    """
    Verifica que un ajuste positivo de stock funcione y cree un movimiento.
    """
    # Arrange
    producto_ctrl = ProductoController(db_session)
    producto_id = producto_de_prueba.id
    stock_inicial = producto_de_prueba.stock
    
    # Act
    movimiento = producto_ctrl.ajustar_stock(
        producto_id=producto_id,
        cantidad_ajuste=25,
        tipo_ajuste=TipoAjusteStock.AJUSTE_CONTEO_POSITIVO,
        motivo="Conteo de inventario",
        usuario_id=test_usuario.id
    )
    
    # Assert
    producto_actualizado = db_session.get(type(producto_de_prueba), producto_id)
    assert producto_actualizado.stock == stock_inicial + 25
    assert movimiento is not None
    assert movimiento.cantidad == 25
    assert movimiento.stock_anterior == stock_inicial
    assert movimiento.stock_nuevo == stock_inicial + 25

def test_ajustar_stock_reduccion(db_session: Session, test_usuario: Usuario, producto_de_prueba):
    """
    Verifica que un ajuste negativo de stock funcione.
    """
    # Arrange
    producto_ctrl = ProductoController(db_session)
    producto_id = producto_de_prueba.id
    stock_inicial = producto_de_prueba.stock

    # Act
    producto_ctrl.ajustar_stock(
        producto_id=producto_id,
        cantidad_ajuste=-10,
        tipo_ajuste=TipoAjusteStock.SALIDA_MERMA,
        motivo="Producto dañado",
        usuario_id=test_usuario.id
    )
    
    # Assert
    producto_actualizado = db_session.get(type(producto_de_prueba), producto_id)
    assert producto_actualizado.stock == stock_inicial - 10

def test_ajustar_stock_a_negativo_falla(db_session: Session, test_usuario: Usuario, producto_de_prueba):
    """
    Verifica que el sistema impida que un ajuste de stock resulte en un valor negativo.
    """
    # Arrange
    producto_ctrl = ProductoController(db_session)
    producto_id = producto_de_prueba.id
    stock_inicial = producto_de_prueba.stock
    
    # Act & Assert
    with pytest.raises(ValueError, match="El ajuste resultaría en stock negativo"):
        producto_ctrl.ajustar_stock(
            producto_id=producto_id,
            cantidad_ajuste=-(stock_inicial + 1), # Intentamos quitar más de lo que hay
            tipo_ajuste=TipoAjusteStock.SALIDA_ROTURA,
            motivo="Error de prueba",
            usuario_id=test_usuario.id
        )