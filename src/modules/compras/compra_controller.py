# src/modules/compras/compra_controller.py

from typing import List, Dict, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload

from .compra_model import OrdenCompra, DetalleCompra, EstadoOrdenCompra
from modules.productos.producto_controller import ProductoController
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.contabilidad.contabilidad_model import TipoMovimiento

# --- INICIO DE LA MODIFICACIÓN ---
from modules.productos.models import Producto, TipoAjusteStock
# --- FIN DE LA MODIFICACIÓN ---

class CompraController:
    def __init__(self, db_session: Session, producto_ctrl: ProductoController, contabilidad_ctrl: ContabilidadController):
        self.db = db_session
        self.producto_ctrl = producto_ctrl
        self.contabilidad_ctrl = contabilidad_ctrl

    def crear_orden_compra(self, proveedor_id: int, detalles_data: List[Dict]) -> OrdenCompra:
        if not proveedor_id: raise ValueError("Se debe seleccionar un proveedor.")
        if not detalles_data: raise ValueError("La orden de compra debe contener al menos un producto.")
        
        total_orden = sum(item['cantidad'] * item['costo_unitario'] for item in detalles_data)
        
        nueva_orden = OrdenCompra(proveedor_id=proveedor_id, total=total_orden)
        self.db.add(nueva_orden)
        self.db.flush() 

        for item_data in detalles_data:
            detalle = DetalleCompra(orden_id=nueva_orden.id, **item_data)
            self.db.add(detalle)
            
        self.db.commit()
        self.db.refresh(nueva_orden)
        return nueva_orden

    def marcar_orden_como_recibida(self, orden_id: int, usuario_id: int) -> OrdenCompra:
        orden = self.db.query(OrdenCompra).options(joinedload(OrdenCompra.detalles), joinedload(OrdenCompra.proveedor)).filter(OrdenCompra.id == orden_id).first()

        if not orden: raise ValueError("La orden de compra no existe.")
        if orden.estado != EstadoOrdenCompra.PENDIENTE: raise ValueError(f"La orden ya está en estado '{orden.estado.value}'.")

        for detalle in orden.detalles:
            self.producto_ctrl.ajustar_stock(
                producto_id=detalle.producto_id,
                cantidad_ajuste=detalle.cantidad,
                tipo_ajuste=TipoAjusteStock.ENTRADA_COMPRA,
                motivo=f"Recepción de Orden de Compra #{orden.id}",
                usuario_id=usuario_id
            )
        
        concepto = f"Compra a proveedor: {orden.proveedor.nombre_empresa} (Orden #{orden.id})"
        self.contabilidad_ctrl.agregar_movimiento(
            tipo=TipoMovimiento.EGRESO, concepto=concepto, monto=orden.total, categoria="Compras"
        )

        orden.estado = EstadoOrdenCompra.RECIBIDA
        orden.fecha_recepcion = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(orden)
        return orden

    def listar_ordenes_compra(self) -> List[OrdenCompra]:
        return self.db.query(OrdenCompra).options(joinedload(OrdenCompra.proveedor)).order_by(OrdenCompra.fecha_emision.desc()).all()