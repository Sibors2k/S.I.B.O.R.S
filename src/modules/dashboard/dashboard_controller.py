# src/modules/dashboard/dashboard_controller.py

from typing import Dict, List
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.ventas.ventas_controller import VentasController
# --- INICIO DE LA CORRECCIÓN ---
from modules.productos.producto_controller import ProductoController
# --- FIN DE LA CORRECCIÓN ---

class DashboardController:
    # --- INICIO DE LA CORRECCIÓN ---
    def __init__(self, contabilidad_ctrl: ContabilidadController, ventas_ctrl: VentasController, producto_ctrl: ProductoController):
        self.contabilidad_ctrl = contabilidad_ctrl
        self.ventas_ctrl = ventas_ctrl
        self.producto_ctrl = producto_ctrl
    # --- FIN DE LA CORRECCIÓN ---

    def obtener_kpis_principales(self) -> Dict:
        try:
            resumen_contable = self.contabilidad_ctrl.obtener_resumen()
            ventas_totales = len(self.ventas_ctrl.listar_ventas())
            # --- INICIO DE LA CORRECCIÓN ---
            productos = self.producto_ctrl.listar_productos()
            # --- FIN DE LA CORRECCIÓN ---
            stock_total = sum(p.stock for p in productos)

            return {
                "ingresos_totales": resumen_contable.get("total_ingresos", 0.0),
                "ventas_totales": ventas_totales,
                "productos_en_stock": stock_total,
            }
        except Exception as e:
            print(f"Error al obtener KPIs para el Dashboard: {e}")
            return {"ingresos_totales": 0.0, "ventas_totales": 0, "productos_en_stock": 0}

    def obtener_datos_grafico_financiero(self, dias: int = 15) -> List[Dict]:
        try:
            return self.contabilidad_ctrl.obtener_resumen_diario(dias)
        except Exception as e:
            print(f"Error al obtener datos del gráfico financiero: {e}")
            return []