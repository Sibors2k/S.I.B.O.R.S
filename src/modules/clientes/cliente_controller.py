# src/modules/clientes/cliente_controller.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from .cliente_model import Cliente, EstadoCliente
from modules.ventas.ventas_model import Venta # Importamos Venta
from utils import validators

class ClienteController:
    def __init__(self, db_session: Session):
        self.db = db_session

    # ... (métodos agregar, actualizar, listar, eliminar, buscar no cambian) ...
    def agregar_cliente(self, datos: Dict) -> Cliente:
        self._validar_datos(datos)
        email = datos.get('email', '').strip().lower()
        if email and self.db.query(Cliente).filter(Cliente.email == email).first():
            raise ValueError(f"El email '{email}' ya está registrado.")
        rfc = datos.get('rfc', '').strip().upper()
        if rfc and self.db.query(Cliente).filter(Cliente.rfc == rfc).first():
            raise ValueError(f"El RFC '{rfc}' ya está registrado.")
        datos_limpios = self._sanitizar_datos(datos)
        nuevo_cliente = Cliente(**datos_limpios)
        self.db.add(nuevo_cliente)
        self.db.commit()
        self.db.refresh(nuevo_cliente)
        return nuevo_cliente

    def actualizar_cliente(self, cliente_id: int, datos: Dict) -> Optional[Cliente]:
        cliente = self.db.get(Cliente, cliente_id)
        if not cliente: return None
        self._validar_datos(datos, editando=True)
        datos_limpios = self._sanitizar_datos(datos)
        for key, value in datos_limpios.items():
            setattr(cliente, key, value)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente
        
    def listar_clientes(self) -> List[Cliente]:
        return self.db.query(Cliente).order_by(Cliente.nombre_completo).all()

    def eliminar_cliente(self, cliente_id: int) -> bool:
        cliente = self.db.get(Cliente, cliente_id)
        if not cliente: return False
        if cliente.ventas:
            raise ValueError("No se puede eliminar el cliente porque tiene ventas asociadas.")
        self.db.delete(cliente)
        self.db.commit()
        return True
    
    def buscar_clientes(self, termino: str) -> List[Cliente]:
        if not termino or not termino.strip():
            return self.listar_clientes()
        termino_busqueda = f"%{termino.strip()}%"
        return self.db.query(Cliente).filter(
            or_(
                Cliente.nombre_completo.ilike(termino_busqueda),
                Cliente.rfc.ilike(termino_busqueda),
                Cliente.email.ilike(termino_busqueda)
            )
        ).order_by(Cliente.nombre_completo).all()

    # --- INICIO DE LA NUEVA FUNCIONALIDAD ---
    def obtener_ventas_de_cliente(self, cliente_id: int) -> List[Venta]:
        """
        Devuelve la lista de ventas asociadas a un cliente específico,
        cargando también la información del producto de cada venta.
        """
        cliente = self.db.query(Cliente).options(
            joinedload(Cliente.ventas).joinedload(Venta.producto)
        ).filter(Cliente.id == cliente_id).first()
        
        if cliente:
            return sorted(cliente.ventas, key=lambda venta: venta.fecha_venta, reverse=True)
        return []
    # --- FIN DE LA NUEVA FUNCIONALIDAD ---

    def _validar_datos(self, datos: Dict, editando: bool = False):
        # ... (sin cambios)
        if 'nombre_completo' in datos and not validators.validar_longitud(datos.get('nombre_completo', ''), minimo=3):
            raise ValueError("El nombre completo es obligatorio (mínimo 3 caracteres).")
        if 'email' in datos and not validators.validar_email(datos.get('email')):
            raise ValueError("El formato del correo electrónico no es válido.")
        if not editando and ('nombre_completo' not in datos or 'email' not in datos):
            raise ValueError("El nombre completo y el email son obligatorios.")
        if 'rfc' in datos and datos.get('rfc') and not validators.validar_rfc(datos.get('rfc')):
            raise ValueError("El formato del RFC no es válido.")
        if 'limite_credito' in datos and datos.get('limite_credito') is not None:
            try:
                if float(datos['limite_credito']) < 0:
                    raise ValueError("El límite de crédito no puede ser negativo.")
            except (ValueError, TypeError):
                raise ValueError("El límite de crédito debe ser un número válido.")

    def _sanitizar_datos(self, datos: Dict) -> Dict:
        # ... (sin cambios)
        sanitizados = {}
        for key, value in datos.items():
            if key in ['nombre_completo', 'razon_social', 'direccion']:
                sanitizados[key] = validators.sanitizar_string(value)
            elif key == 'email':
                sanitizados[key] = value.strip().lower() if value else ''
            elif key == 'rfc':
                sanitizados[key] = value.strip().upper() if value else ''
            elif key == 'telefono':
                sanitizados[key] = validators.sanitizar_telefono(value) if value else ''
            elif key == 'estado':
                 sanitizados[key] = EstadoCliente(value) if isinstance(value, str) else value
            elif key == 'limite_credito':
                sanitizados[key] = float(value or 0.0)
        return sanitizados