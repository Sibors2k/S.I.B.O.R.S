# src/modules/auditorias/auditoria_controller.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from .auditoria_model import Auditoria, AuditoriaDetalle, EstadoAuditoria
from modules.productos.producto_controller import ProductoController

# --- INICIO DE LA MODIFICACIÓN ---
# Apuntamos al nuevo 'models.py' unificado para obtener las definiciones.
from modules.productos.models import TipoAjusteStock, Producto
# --- FIN DE LA MODIFICACIÓN ---

class AuditoriaController:
    """
    Controlador para la lógica de negocio de las auditorías de inventario.
    """
    def __init__(self, db_session: Session, producto_ctrl: ProductoController):
        """
        Inicializa el controlador con una sesión de base de datos y el controlador de productos.
        """
        self.db = db_session
        self.producto_ctrl = producto_ctrl

    def iniciar_nueva_auditoria(self, usuario_id: int, notas: Optional[str] = None) -> Auditoria:
        """
        Crea un nuevo registro de auditoría en estado 'En Progreso'.
        """
        auditoria_activa = self.db.query(Auditoria).filter_by(estado=EstadoAuditoria.EN_PROGRESO).first()
        if auditoria_activa:
            raise ValueError(f"Ya existe una auditoría en progreso (ID: {auditoria_activa.id}). Complétala o cancélala antes de iniciar una nueva.")

        nueva_auditoria = Auditoria(
            usuario_id=usuario_id,
            notas=notas
        )
        self.db.add(nueva_auditoria)
        self.db.commit()
        self.db.refresh(nueva_auditoria)
        print(f"Auditoría #{nueva_auditoria.id} iniciada por el usuario #{usuario_id}.")
        return nueva_auditoria

    def registrar_conteo_producto(self, auditoria_id: int, producto_id: int, conteo_fisico: int) -> AuditoriaDetalle:
        """
        Registra el conteo físico de un producto para una auditoría específica.
        """
        auditoria = self.db.get(Auditoria, auditoria_id)
        if not auditoria or auditoria.estado != EstadoAuditoria.EN_PROGRESO:
            raise ValueError("La auditoría no existe o no está en progreso.")

        # Ahora 'Producto' está definido gracias a la importación corregida.
        producto = self.db.get(Producto, producto_id)
        if not producto:
            raise ValueError("El producto especificado no existe.")

        stock_sistema = producto.stock
        diferencia = conteo_fisico - stock_sistema
        
        detalle_existente = self.db.query(AuditoriaDetalle).filter_by(auditoria_id=auditoria_id, producto_id=producto_id).first()
        
        if detalle_existente:
            detalle_existente.stock_fisico = conteo_fisico
            detalle_existente.diferencia = diferencia
            detalle = detalle_existente
        else:
            detalle = AuditoriaDetalle(
                auditoria_id=auditoria_id,
                producto_id=producto_id,
                stock_sistema=stock_sistema,
                stock_fisico=conteo_fisico,
                diferencia=diferencia
            )
            self.db.add(detalle)
        
        self.db.commit()
        self.db.refresh(detalle)
        return detalle

    def finalizar_auditoria(self, auditoria_id: int, usuario_id: int) -> Auditoria:
        """
        Finaliza una auditoría. Recorre todos los detalles y aplica los ajustes de stock necesarios.
        """
        auditoria = self.db.get(Auditoria, auditoria_id)
        if not auditoria or auditoria.estado != EstadoAuditoria.EN_PROGRESO:
            raise ValueError("La auditoría no existe o no está en progreso.")

        if not auditoria.detalles:
            raise ValueError("No se puede finalizar una auditoría sin haber contado al menos un producto.")

        for detalle in auditoria.detalles:
            if detalle.diferencia != 0:
                tipo_ajuste = TipoAjusteStock.AJUSTE_CONTEO_POSITIVO if detalle.diferencia > 0 else TipoAjusteStock.AJUSTE_CONTEO_NEGATIVO
                self.producto_ctrl.ajustar_stock(
                    producto_id=detalle.producto_id,
                    cantidad_ajuste=detalle.diferencia,
                    tipo_ajuste=tipo_ajuste,
                    motivo=f"Ajuste por Auditoría #{auditoria.id}",
                    usuario_id=usuario_id
                )

        auditoria.estado = EstadoAuditoria.COMPLETADA
        auditoria.fecha_fin = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(auditoria)
        print(f"Auditoría #{auditoria.id} finalizada y ajustes aplicados.")
        return auditoria

    def obtener_auditoria_en_progreso(self) -> Optional[Auditoria]:
        """Busca y devuelve la auditoría que esté actualmente activa."""
        return self.db.query(Auditoria).options(joinedload(Auditoria.detalles).joinedload(AuditoriaDetalle.producto)).filter_by(estado=EstadoAuditoria.EN_PROGRESO).first()
        
    def listar_auditorias(self) -> List[Auditoria]:
        """Devuelve un historial de todas las auditorías, ordenadas por fecha."""
        return self.db.query(Auditoria).options(joinedload(Auditoria.usuario)).order_by(Auditoria.fecha_inicio.desc()).all()