# tests/test_dashboard_controller.py

import pytest
from unittest.mock import Mock
from modules.dashboard.dashboard_controller import DashboardController

def test_obtener_kpis_principales_con_mocks():
    mock_contabilidad = Mock()
    mock_ventas = Mock()
    # --- INICIO DE LA CORRECCIÓN ---
    # Cambiamos el nombre del mock para que coincida con el nuevo controlador
    mock_producto = Mock()

    mock_contabilidad.obtener_resumen.return_value = {"total_ingresos": 5000.0}
    mock_ventas.listar_ventas.return_value = [Mock(), Mock(), Mock()]

    producto_mock_1 = Mock()
    producto_mock_1.stock = 10
    producto_mock_2 = Mock()
    producto_mock_2.stock = 25
    mock_producto.listar_productos.return_value = [producto_mock_1, producto_mock_2]

    # Creamos el controlador usando el nombre de argumento correcto: 'producto_ctrl'
    dashboard_ctrl = DashboardController(
        contabilidad_ctrl=mock_contabilidad,
        ventas_ctrl=mock_ventas,
        producto_ctrl=mock_producto
    )
    # --- FIN DE LA CORRECCIÓN ---
    
    kpis = dashboard_ctrl.obtener_kpis_principales()

    assert kpis["ingresos_totales"] == 5000.0
    assert kpis["ventas_totales"] == 3
    assert kpis["productos_en_stock"] == 35