# tests/test_plantilla_controller.py

import pytest
from sqlalchemy.orm import Session
from modules.productos.plantilla_controller import PlantillaController
from modules.productos.producto_controller import ProductoController
from modules.usuarios.usuarios_model import Usuario

# Asumimos que conftest.py provee las fixtures 'db_session' y 'test_usuario'

def test_crear_producto_simple(db_session: Session, test_usuario: Usuario):
    """
    Verifica que se pueda crear un producto simple (una plantilla con una sola variante sin atributos).
    """
    # Arrange
    plantilla_ctrl = PlantillaController(db_session)
    datos_plantilla = {"nombre": "Monitor 24 pulgadas", "categoria_id": None, "proveedor_id": None}
    datos_variante = [{"sku": "MON-24", "precio_venta": 250.0, "stock": 10, "costo_compra": 180.0}]
    
    # Act
    nueva_plantilla = plantilla_ctrl.crear_plantilla_con_variantes(
        datos_plantilla, datos_variante, test_usuario.id
    )
    
    # Assert
    assert nueva_plantilla is not None
    assert nueva_plantilla.nombre == "Monitor 24 pulgadas"
    assert len(nueva_plantilla.variantes) == 1
    assert nueva_plantilla.variantes[0].sku == "MON-24"
    assert nueva_plantilla.variantes[0].stock == 10
    assert len(nueva_plantilla.variantes[0].historial_stock) == 1
    assert nueva_plantilla.variantes[0].historial_stock[0].cantidad == 10

def test_crear_producto_con_variantes(db_session: Session, test_usuario: Usuario, setup_atributos):
    """
    Verifica la creación de un producto con múltiples variantes.
    """
    # Arrange
    plantilla_ctrl = PlantillaController(db_session)
    talla_s_id, talla_m_id, color_rojo_id, color_azul_id = setup_atributos
    
    datos_plantilla = {"nombre": "Camiseta Basica"}
    datos_variantes = [
        {"sku": "CAM-S-RO", "precio_venta": 15.0, "stock": 20, "ids_valores": [talla_s_id, color_rojo_id]},
        {"sku": "CAM-M-AZ", "precio_venta": 15.0, "stock": 15, "ids_valores": [talla_m_id, color_azul_id]},
    ]
    
    # Act
    nueva_plantilla = plantilla_ctrl.crear_plantilla_con_variantes(
        datos_plantilla, datos_variantes, test_usuario.id
    )
    
    # Assert
    assert nueva_plantilla is not None
    assert len(nueva_plantilla.variantes) == 2
    
    variante_roja = next(v for v in nueva_plantilla.variantes if v.sku == "CAM-S-RO")
    assert variante_roja is not None
    assert variante_roja.stock == 20
    assert len(variante_roja.valores) == 2


def test_calcular_stock_kit(db_session: Session, test_usuario: Usuario):
    """
    Prueba clave: Verifica que el cálculo de stock para un kit sea correcto.
    """
    # Arrange: Crear los componentes y el kit
    plantilla_ctrl = PlantillaController(db_session)
    
    plantilla_vino = plantilla_ctrl.crear_plantilla_con_variantes(
        {"nombre": "Botella de Vino"}, [{"sku": "VINO-750", "precio_venta": 10.0, "stock": 10}], test_usuario.id
    )
    vino_id = plantilla_vino.variantes[0].id
    
    plantilla_queso = plantilla_ctrl.crear_plantilla_con_variantes(
        {"nombre": "Queso Gouda"}, [{"sku": "QUESO-G", "precio_venta": 5.0, "stock": 20}], test_usuario.id
    )
    queso_id = plantilla_queso.variantes[0].id
    
    componentes_kit = [
        {"componente_id": vino_id, "cantidad": 2},
        {"componente_id": queso_id, "cantidad": 1}
    ]
    plantilla_kit = plantilla_ctrl.crear_plantilla_con_variantes(
        {"nombre": "Canasta Gourmet"},
        [{"sku": "KIT-GOURMET", "precio_venta": 30.0, "stock": 0}],
        test_usuario.id,
        componentes=componentes_kit
    )
    
    # Act: Calcular el stock del kit
    stock_calculado = plantilla_ctrl.calcular_stock_disponible_kit(plantilla_kit.id)
    
    # Assert
    assert stock_calculado == 5

def test_eliminar_plantilla_con_stock_falla(db_session: Session, test_usuario: Usuario):
    """
    Verifica que no se pueda eliminar un producto si alguna de sus variantes tiene stock.
    """
    # Arrange
    plantilla_ctrl = PlantillaController(db_session)
    plantilla = plantilla_ctrl.crear_plantilla_con_variantes(
        {"nombre": "Producto Con Stock"}, [{"sku": "PCS-01", "precio_venta": 10, "stock": 1}], test_usuario.id
    )

    # Act & Assert
    # --- INICIO DE LA MODIFICACIÓN ---
    # Actualizamos el texto del 'match' para que coincida con el nuevo y mejorado mensaje de error.
    with pytest.raises(ValueError, match="No se puede eliminar el producto porque una o más de sus variantes \(o componentes de kit\) tienen existencias en el inventario."):
        plantilla_ctrl.eliminar_plantilla(plantilla.id)
    # --- FIN DE LA MODIFICACIÓN ---