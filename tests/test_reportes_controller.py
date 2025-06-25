# tests/test_reportes_controller.py

import pytest
from unittest.mock import Mock
from modules.reportes.reportes_controller import ReportesController

def test_preparar_reporte_ventas():
    # Esta prueba no tiene cambios y se omite por brevedad, pero debe permanecer
    mock_ventas_ctrl = Mock()
    mock_producto_ctrl = Mock()
    mock_empresa_ctrl = Mock()
    venta_mock_1 = Mock()
    venta_mock_1.id = 1; venta_mock_1.fecha_venta.strftime.return_value = "2025-06-20 10:00"; venta_mock_1.cliente.nombre_completo = "Cliente de Prueba"; venta_mock_1.producto.nombre = "Producto A"; venta_mock_1.cantidad = 2; venta_mock_1.total_venta = 200.0
    mock_ventas_ctrl.listar_ventas.return_value = [venta_mock_1]
    reportes_ctrl = ReportesController(mock_ventas_ctrl, mock_producto_ctrl, mock_empresa_ctrl)
    reporte = reportes_ctrl.obtener_datos_para_reporte("ventas", {})
    assert reporte["titulo"] == "Reporte de Ventas"
    assert len(reporte["data"]) == 1

def test_preparar_reporte_productos(): # Cambiado el nombre de la prueba para reflejar la realidad
    """
    Prueba que el reporte de productos se formatee correctamente.
    """
    mock_ventas_ctrl = Mock()
    mock_producto_ctrl = Mock()
    mock_empresa_ctrl = Mock()

    producto_mock_1 = Mock()
    producto_mock_1.id = 101; producto_mock_1.nombre = "Producto B"; producto_mock_1.descripcion = "Descripción B"; producto_mock_1.stock = 50; producto_mock_1.precio_venta = 25.50; producto_mock_1.proveedor.nombre_empresa = "Proveedor Z"
    
    mock_producto_ctrl.listar_productos.return_value = [producto_mock_1]

    reportes_ctrl = ReportesController(mock_ventas_ctrl, mock_producto_ctrl, mock_empresa_ctrl)
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Pedimos el reporte 'productos' en lugar de 'inventario'
    reporte = reportes_ctrl.obtener_datos_para_reporte("productos", {})
    # --- FIN DE LA CORRECCIÓN ---

    assert reporte["titulo"] == "Reporte de Productos"
    assert len(reporte["data"]) == 1
    assert reporte["data"][0][1] == "Producto B"