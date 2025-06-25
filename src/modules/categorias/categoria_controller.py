# src/modules/categorias/categoria_controller.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc, distinct
from typing import List, Optional

from .categoria_model import Categoria
# --- INICIO DE LA MODIFICACIÓN ---
# Esta es la importación absoluta correcta desde el módulo de productos
from modules.productos.models import ProductoPlantilla
# --- FIN DE LA MODIFICACIÓN ---

class CategoriaController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def crear_categoria(self, nombre: str, padre_id: Optional[int] = None) -> Categoria:
        nombre_existente = self.db.query(Categoria).filter(Categoria.nombre.ilike(nombre)).first()
        if nombre_existente:
            raise ValueError(f"La categoría '{nombre}' ya existe.")
        
        if padre_id:
            padre = self.db.get(Categoria, padre_id)
            if not padre:
                raise ValueError(f"La categoría padre con ID {padre_id} no existe.")

        nueva_categoria = Categoria(nombre=nombre.strip(), categoria_padre_id=padre_id)
        self.db.add(nueva_categoria)
        self.db.commit()
        self.db.refresh(nueva_categoria)
        return nueva_categoria

    def actualizar_categoria(self, categoria_id: int, nombre: Optional[str] = None, padre_id: Optional[int] = None) -> Categoria:
        categoria = self.db.get(Categoria, categoria_id)
        if not categoria:
            raise ValueError(f"La categoría con ID {categoria_id} no existe.")

        if padre_id is not None:
            if categoria_id == padre_id:
                raise ValueError("Una categoría no puede ser su propio padre.")
            
            descendiente = self.db.get(Categoria, padre_id)
            while descendiente:
                if descendiente.categoria_padre_id == categoria_id:
                    raise ValueError("No se puede mover una categoría a una de sus propias subcategorías.")
                descendiente = descendiente.padre

        if nombre:
            nombre_existente = self.db.query(Categoria).filter(Categoria.nombre.ilike(nombre), Categoria.id != categoria_id).first()
            if nombre_existente:
                raise ValueError(f"La categoría '{nombre}' ya existe.")
            categoria.nombre = nombre.strip()

        categoria.categoria_padre_id = padre_id
        
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def eliminar_categoria(self, categoria_id: int) -> bool:
        categoria = self.db.get(Categoria, categoria_id)
        if not categoria:
            return True 

        if self.db.query(Categoria).filter(Categoria.categoria_padre_id == categoria_id).first():
            raise ValueError("No se puede eliminar la categoría porque tiene subcategorías.")

        if self.db.query(ProductoPlantilla).filter(ProductoPlantilla.categoria_id == categoria_id).first():
            raise ValueError("No se puede eliminar la categoría porque tiene productos asociados.")

        self.db.delete(categoria)
        self.db.commit()
        return True

    def listar_categorias_jerarquicamente(self) -> List[Categoria]:
        return self.db.query(Categoria).filter(Categoria.categoria_padre_id.is_(None)).order_by(Categoria.nombre).all()

    def obtener_todas_las_categorias(self) -> List[Categoria]:
        return self.db.query(Categoria).order_by(Categoria.nombre).all()
        
    def listar_categorias_con_productos(self) -> List[Categoria]:
        return self.db.query(Categoria).join(ProductoPlantilla).distinct().order_by(Categoria.nombre).all()

    def obtener_categoria_por_id(self, categoria_id: int) -> Optional[Categoria]:
        return self.db.query(Categoria).options(joinedload(Categoria.plantillas)).filter(Categoria.id == categoria_id).first()