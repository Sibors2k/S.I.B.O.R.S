# src/modules/proveedores/proveedor_controller.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .proveedor_model import Proveedor
from utils import validators

# NOTA: Este controlador en realidad no necesitaba ninguna importación del modelo de producto.
# La lógica de negocio se basa en las relaciones de SQLAlchemy.
# Sin embargo, he corregido la lógica para usar 'proveedor.plantillas' en lugar de 'proveedor.productos'.

class ProveedorController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def agregar_proveedor(self, datos: Dict) -> Proveedor:
        self._validar_datos(datos)
        email_limpio = datos.get('email', '').strip().lower()
        if self.db.query(Proveedor).filter_by(email=email_limpio).first():
            raise ValueError(f"El email '{email_limpio}' ya está en uso por otro proveedor.")
        datos_limpios = self._sanitizar_datos(datos)
        nuevo_proveedor = Proveedor(**datos_limpios)
        self.db.add(nuevo_proveedor)
        self.db.commit()
        self.db.refresh(nuevo_proveedor)
        return nuevo_proveedor

    def listar_proveedores(self, filtro: Optional[str] = None) -> List[Proveedor]:
        query = self.db.query(Proveedor)
        if filtro:
            termino_busqueda = f"%{filtro.lower()}%"
            query = query.filter(or_(
                Proveedor.nombre_empresa.ilike(termino_busqueda),
                Proveedor.persona_contacto.ilike(termino_busqueda),
                Proveedor.email.ilike(termino_busqueda)
            ))
        return query.order_by(Proveedor.nombre_empresa).all()
        
    def actualizar_proveedor(self, proveedor_id: int, datos: Dict) -> Optional[Proveedor]:
        self._validar_datos(datos, editando=True)
        proveedor = self.db.get(Proveedor, proveedor_id)
        if proveedor:
            if 'email' in datos:
                email_limpio = datos['email'].strip().lower()
                proveedor_existente = self.db.query(Proveedor).filter_by(email=email_limpio).first()
                if proveedor_existente and proveedor_existente.id != proveedor_id:
                    raise ValueError(f"El email '{email_limpio}' ya está en uso por otro proveedor.")
            datos_limpios = self._sanitizar_datos(datos)
            for key, value in datos_limpios.items():
                setattr(proveedor, key, value)
            self.db.commit()
            self.db.refresh(proveedor)
        return proveedor

    def eliminar_proveedor(self, proveedor_id: int) -> bool:
        proveedor = self.db.get(Proveedor, proveedor_id)
        if not proveedor: return True
        
        # --- INICIO DE LA MODIFICACIÓN LÓGICA ---
        # La relación ahora se llama 'plantillas' y no 'productos'.
        if proveedor.plantillas:
            raise ValueError("No se puede eliminar el proveedor porque tiene productos asociados.")
        # --- FIN DE LA MODIFICACIÓN LÓGICA ---

        self.db.delete(proveedor)
        self.db.commit()
        return True

    def _validar_datos(self, datos: Dict, editando: bool = False):
        if 'nombre_empresa' in datos and not validators.validar_longitud(datos.get('nombre_empresa', ''), minimo=3):
            raise ValueError("El nombre de la empresa es obligatorio (mínimo 3 caracteres).")
        if 'email' in datos and not validators.validar_email(datos.get('email')):
            raise ValueError("El formato del correo electrónico no es válido.")
        if not editando and ('nombre_empresa' not in datos or 'email' not in datos):
            raise ValueError("El nombre de la empresa y el email son obligatorios.")

    def _sanitizar_datos(self, datos: Dict) -> Dict:
        sanitizados = {}
        for key, value in datos.items():
            if key in ['nombre_empresa', 'persona_contacto', 'direccion', 'sitio_web']:
                sanitizados[key] = validators.sanitizar_string(value) if value else value
            elif key == 'email':
                sanitizados[key] = value.strip().lower() if value else ''
            else:
                sanitizados[key] = value
        return sanitizados