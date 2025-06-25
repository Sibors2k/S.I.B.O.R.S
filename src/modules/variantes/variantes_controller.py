# src/modules/variantes/variantes_controller.py

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .variantes_model import Atributo, AtributoValor
from modules.productos.models import variante_valor_association

class VariantesController:
    def __init__(self, db_session: Session):
        self.db = db_session

    # --- Métodos para Atributos --- (Sin cambios)
    def crear_atributo(self, nombre: str) -> Atributo:
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre del atributo no puede estar vacío.")
        if self.db.query(Atributo).filter(Atributo.nombre.ilike(nombre)).first():
            raise ValueError(f"El atributo '{nombre}' ya existe.")
        
        nuevo_atributo = Atributo(nombre=nombre)
        self.db.add(nuevo_atributo)
        self.db.commit()
        self.db.refresh(nuevo_atributo)
        return nuevo_atributo

    def listar_atributos(self) -> List[Atributo]:
        return self.db.query(Atributo).options(joinedload(Atributo.valores)).order_by(Atributo.nombre).all()

    def actualizar_atributo(self, atributo_id: int, nuevo_nombre: str) -> Atributo:
        atributo = self.db.get(Atributo, atributo_id)
        if not atributo:
            raise ValueError("El atributo no existe.")
        
        nuevo_nombre = nuevo_nombre.strip()
        if not nuevo_nombre:
            raise ValueError("El nombre del atributo no puede estar vacío.")
        
        nombre_existente = self.db.query(Atributo).filter(Atributo.nombre.ilike(nuevo_nombre), Atributo.id != atributo_id).first()
        if nombre_existente:
            raise ValueError(f"El atributo '{nuevo_nombre}' ya existe.")
            
        atributo.nombre = nuevo_nombre
        self.db.commit()
        self.db.refresh(atributo)
        return atributo

    def eliminar_atributo(self, atributo_id: int) -> bool:
        atributo = self.db.get(Atributo, atributo_id)
        if not atributo:
            return True
        
        ids_valores = [valor.id for valor in atributo.valores]
        if ids_valores:
            en_uso = self.db.query(variante_valor_association).filter(
                variante_valor_association.c.atributo_valor_id.in_(ids_valores)
            ).first()
            if en_uso:
                raise ValueError("No se puede eliminar el atributo porque uno de sus valores está en uso por un producto.")

        self.db.delete(atributo)
        self.db.commit()
        return True

    # --- Métodos para AtributoValores ---
    
    # --- INICIO DE LA MODIFICACIÓN ---
    def agregar_valor_a_atributo(self, atributo_id: int, valor: str, codigo_color: Optional[str] = None) -> AtributoValor:
    # --- FIN DE LA MODIFICACIÓN ---
        valor = valor.strip()
        if not valor:
            raise ValueError("El valor no puede estar vacío.")

        atributo = self.db.get(Atributo, atributo_id)
        if not atributo:
            raise ValueError("El atributo especificado no existe.")

        valor_existente = self.db.query(AtributoValor).filter_by(atributo_id=atributo_id, valor=valor).first()
        if valor_existente:
            raise ValueError(f"El valor '{valor}' ya existe para el atributo '{atributo.nombre}'.")
            
        # --- INICIO DE LA MODIFICACIÓN ---
        nuevo_valor = AtributoValor(valor=valor, atributo_id=atributo_id, codigo_color=codigo_color)
        # --- FIN DE LA MODIFICACIÓN ---
        self.db.add(nuevo_valor)
        self.db.commit()
        self.db.refresh(nuevo_valor)
        return nuevo_valor

    # --- INICIO DE LA MODIFICACIÓN ---
    def actualizar_valor(self, valor_id: int, nuevo_valor_str: str, nuevo_codigo_color: Optional[str] = None) -> AtributoValor:
    # --- FIN DE LA MODIFICACIÓN ---
        valor_obj = self.db.get(AtributoValor, valor_id)
        if not valor_obj:
            raise ValueError("El valor no existe.")
        
        nuevo_valor_str = nuevo_valor_str.strip()
        if not nuevo_valor_str:
            raise ValueError("El valor no puede estar vacío.")
            
        valor_existente = self.db.query(AtributoValor).filter(
            AtributoValor.atributo_id == valor_obj.atributo_id,
            AtributoValor.valor.ilike(nuevo_valor_str),
            AtributoValor.id != valor_id
        ).first()
        if valor_existente:
            raise ValueError(f"El valor '{nuevo_valor_str}' ya existe para este atributo.")
        
        # --- INICIO DE LA MODIFICACIÓN ---
        valor_obj.valor = nuevo_valor_str
        valor_obj.codigo_color = nuevo_codigo_color
        # --- FIN DE LA MODIFICACIÓN ---
        self.db.commit()
        self.db.refresh(valor_obj)
        return valor_obj

    def eliminar_valor(self, valor_id: int) -> bool:
        valor = self.db.get(AtributoValor, valor_id)
        if not valor:
            return True

        en_uso = self.db.query(variante_valor_association).filter_by(atributo_valor_id=valor_id).first()
        if en_uso:
            raise ValueError("No se puede eliminar el valor porque está en uso por un producto.")
        
        self.db.delete(valor)
        self.db.commit()
        return True