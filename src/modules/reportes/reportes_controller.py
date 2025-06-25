# src/modules/reportes/reportes_controller.py
from datetime import datetime
from typing import Dict, List, Any

from modules.ventas.ventas_controller import VentasController
# --- INICIO DE LA CORRECCIÓN ---
from modules.productos.producto_controller import ProductoController
# --- FIN DE LA CORRECCIÓN ---
from modules.empresa.empresa_controller import EmpresaController

class ReportesController:
    # --- INICIO DE LA CORRECCIÓN ---
    def __init__(self, ventas_ctrl: VentasController, producto_ctrl: ProductoController, empresa_ctrl: EmpresaController):
        self.ventas_ctrl = ventas_ctrl
        self.producto_ctrl = producto_ctrl
        self.empresa_ctrl = empresa_ctrl
    # --- FIN DE LA CORRECCIÓN ---

    def obtener_datos_para_reporte(self, tipo_reporte: str, filtros: Dict) -> Dict[str, Any]:
        print(f"Obteniendo datos para reporte tipo '{tipo_reporte}'...")
        if tipo_reporte == "ventas":
            return self._preparar_reporte_ventas(filtros)
        # --- INICIO DE LA CORRECCIÓN ---
        elif tipo_reporte == "productos":
        # --- FIN DE LA CORRECCIÓN ---
            return self._preparar_reporte_productos(filtros)
        else:
            raise ValueError(f"El tipo de reporte '{tipo_reporte}' no es reconocido.")

    def _preparar_reporte_ventas(self, filtros: Dict) -> Dict[str, Any]:
        ventas = self.ventas_ctrl.listar_ventas()
        if not ventas: raise ValueError("No hay ventas para generar el reporte.")
        titulo = "Reporte de Ventas"
        headers = ["ID Venta", "Fecha", "Cliente", "Producto", "Cantidad", "Total"]
        data_rows = []
        for venta in ventas:
            cliente_nombre = venta.cliente.nombre_completo if venta.cliente else "Público General"
            producto_nombre = venta.producto.nombre if venta.producto else "N/A"
            data_rows.append([
                venta.id, venta.fecha_venta.strftime('%Y-%m-%d %H:%M'),
                cliente_nombre, producto_nombre, venta.cantidad, f"${venta.total_venta:,.2f}"
            ])
        return {"titulo": titulo, "headers": headers, "data": data_rows}

    def _preparar_reporte_productos(self, filtros: Dict) -> Dict[str, Any]:
        # --- INICIO DE LA CORRECCIÓN ---
        productos = self.producto_ctrl.listar_productos()
        # --- FIN DE LA CORRECCIÓN ---
        if not productos: raise ValueError("No hay productos para generar el reporte.")
        titulo = "Reporte de Productos"
        headers = ["ID", "Nombre", "Descripción", "Stock", "Precio Venta", "Proveedor"]
        data_rows = []
        for producto in productos:
            proveedor_nombre = producto.proveedor.nombre_empresa if producto.proveedor else "N/A"
            data_rows.append([
                producto.id, producto.nombre, producto.descripcion or "",
                producto.stock, f"${producto.precio_venta:,.2f}", proveedor_nombre
            ])
        return {"titulo": titulo, "headers": headers, "data": data_rows}