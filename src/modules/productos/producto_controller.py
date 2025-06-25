# src/modules/productos/producto_controller.py

import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

# --- ESTA ES LA LÍNEA CORRECTA ---
from .models import Producto, MovimientoStock, TipoAjusteStock, ProductoPlantilla
# --- FIN DE LA LÍNEA CORRECTA ---

from modules.variantes.variantes_model import AtributoValor
from utils import validators

class ProductoController:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.imagenes_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "assets", "product_images"
        ))
        os.makedirs(self.imagenes_dir, exist_ok=True)
        
    def ajustar_stock(self, producto_id: int, cantidad_ajuste: int, tipo_ajuste: TipoAjusteStock, motivo: str, usuario_id: Optional[int]) -> MovimientoStock:
        """
        Ajusta el stock de una VARIANTE de producto específica.
        """
        producto = self.db.get(Producto, producto_id)
        if not producto: raise ValueError(f"La variante de producto con ID {producto_id} no existe.")
        
        stock_anterior = producto.stock
        stock_nuevo = stock_anterior + cantidad_ajuste
        if stock_nuevo < 0: raise ValueError("El ajuste resultaría en stock negativo.")
        
        producto.stock = stock_nuevo
        
        movimiento = MovimientoStock(
            producto_id=producto_id, 
            usuario_id=usuario_id, 
            tipo_ajuste=tipo_ajuste, 
            cantidad=cantidad_ajuste, 
            motivo=motivo.strip(), 
            stock_anterior=stock_anterior, 
            stock_nuevo=stock_nuevo
        )
        self.db.add(movimiento)
        self.db.commit()
        self.db.refresh(producto)
        self.db.refresh(movimiento)
        return movimiento

    def obtener_variante_por_id(self, producto_id: int) -> Optional[Producto]:
        """Obtiene una variante específica por su ID, con sus relaciones."""
        return self.db.query(Producto).options(
            joinedload(Producto.plantilla).joinedload(ProductoPlantilla.proveedor),
            joinedload(Producto.plantilla).joinedload(ProductoPlantilla.categoria),
            joinedload(Producto.valores).joinedload(AtributoValor.atributo)
        ).filter(Producto.id == producto_id).first()

    def listar_todas_las_variantes(self, filtro: Optional[str] = None) -> List[Producto]:
        """Devuelve una lista plana de todas las variantes/productos vendibles."""
        query = self.db.query(Producto).options(joinedload(Producto.plantilla))
        if filtro:
            termino_busqueda = f"%{filtro.lower()}%"
            query = query.join(Producto.plantilla).filter(
                or_(
                    Producto.sku.ilike(termino_busqueda),
                    ProductoPlantilla.nombre.ilike(termino_busqueda)
                )
            )
        return query.order_by(Producto.sku).all()