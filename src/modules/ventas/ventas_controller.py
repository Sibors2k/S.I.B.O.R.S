# src/modules/ventas/ventas_controller.py (v2.2 - Sincronización Forzada)

from typing import List, Dict, Optional
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from .ventas_model import Venta, VentaDetalle, VentaPago, EstadoVenta, MetodoPago
from modules.productos.producto_controller import ProductoController
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.clientes.cliente_controller import ClienteController
from modules.contabilidad.contabilidad_model import TipoMovimiento
from modules.productos.models import Producto, TipoAjusteStock

class VentasController:
    def __init__(self, db_session: Session, producto_ctrl: ProductoController, contabilidad_ctrl: ContabilidadController, cliente_ctrl: ClienteController):
        self.db = db_session
        self.producto_ctrl = producto_ctrl
        self.contabilidad_ctrl = contabilidad_ctrl
        self.cliente_ctrl = cliente_ctrl

    def crear_nueva_venta(self, usuario_id: int, cliente_id: Optional[int] = None) -> Venta:
        venta_existente = self.obtener_venta_activa(usuario_id)
        if venta_existente:
            self.cancelar_venta(venta_existente)
        
        nueva_venta = Venta(usuario_id=usuario_id, cliente_id=cliente_id)
        self.db.add(nueva_venta)
        self.db.commit()
        self.db.refresh(nueva_venta)
        return nueva_venta

    def obtener_venta_activa(self, usuario_id: int) -> Optional[Venta]:
        return self.db.query(Venta).options(
            joinedload(Venta.detalles).joinedload(VentaDetalle.producto).joinedload(Producto.plantilla)
        ).filter_by(usuario_id=usuario_id, estado=EstadoVenta.EN_PROGRESO).first()

    def agregar_item(self, venta: Venta, producto_id: int, cantidad: int) -> Venta:
        producto = self.db.get(Producto, producto_id)
        if not producto: raise ValueError("Producto no encontrado.")
        if cantidad <= 0: raise ValueError("La cantidad debe ser positiva.")
        if producto.stock < cantidad: raise ValueError(f"Stock insuficiente para {producto.sku}. Disponible: {producto.stock}")

        detalle_existente = next((d for d in venta.detalles if d.producto_id == producto_id), None)

        if detalle_existente:
            detalle_existente.cantidad += cantidad
        else:
            detalle_nuevo = VentaDetalle(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta
            )
            venta.detalles.append(detalle_nuevo)
        
        self._recalcular_y_guardar_totales(venta)
        self.db.refresh(venta)
        return venta

    def quitar_item(self, venta: Venta, detalle_id: int) -> Optional[Venta]:
        detalle = self.db.get(VentaDetalle, detalle_id)
        if not detalle or detalle.venta_id != venta.id:
            raise ValueError("El item no pertenece a esta venta.")
        
        venta.detalles.remove(detalle)
        self.db.delete(detalle)
        
        if not venta.detalles:
            self.cancelar_venta(venta)
            return None
        
        self._recalcular_y_guardar_totales(venta)
        self.db.refresh(venta)
        return venta

    def _recalcular_y_guardar_totales(self, venta: Venta):
        subtotal = sum(d.precio_unitario * d.cantidad for d in venta.detalles)
        venta.subtotal = subtotal
        venta.total = subtotal
        self.db.commit()

    def finalizar_venta(self, venta: Venta, pagos: List[Dict]):
        if not venta.detalles: raise ValueError("No se puede finalizar una venta vacía.")
        total_pagado = sum(p['monto'] for p in pagos)
        if total_pagado < venta.total: raise ValueError("El monto pagado es insuficiente.")
        for detalle in venta.detalles:
            self.producto_ctrl.ajustar_stock(
                producto_id=detalle.producto_id,
                cantidad_ajuste=-detalle.cantidad,
                tipo_ajuste=TipoAjusteStock.SALIDA_VENTA,
                motivo=f"Venta #{venta.id}",
                usuario_id=venta.usuario_id
            )
        for pago_data in pagos:
            pago = VentaPago(venta_id=venta.id, metodo_pago=MetodoPago(pago_data['metodo']), monto=pago_data['monto'])
            self.db.add(pago)
        if venta.total > 0:
            self.contabilidad_ctrl.agregar_movimiento(tipo=TipoMovimiento.INGRESO, concepto=f"Ingreso por Venta #{venta.id}", monto=venta.total)
        venta.estado = EstadoVenta.COMPLETADA
        venta.fecha = datetime.now(timezone.utc)
        self.db.commit()

    def cancelar_venta(self, venta: Venta):
        venta.estado = EstadoVenta.CANCELADA
        self.db.commit()