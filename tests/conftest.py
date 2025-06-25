# tests/conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from core.db import Base
# --- INICIO DE LA MODIFICACIÓN ---
# Importamos todos los modelos relacionados con productos desde la nueva ubicación.
from modules.productos.models import (
    ProductoPlantilla, Producto, ProductoImagen, KitComponente, MovimientoStock
)
# --- FIN DE LA MODIFICACIÓN ---
from modules.roles.roles_model import Rol
from modules.usuarios.usuarios_model import Usuario
from modules.perfil.perfil_model import Perfil
from modules.empresa.empresa_model import Empresa
from modules.clientes.cliente_model import Cliente
from modules.proveedores.proveedor_model import Proveedor
from modules.variantes.variantes_model import Atributo, AtributoValor
from modules.ventas.ventas_model import Venta
from modules.compras.compra_model import OrdenCompra, DetalleCompra
from modules.contabilidad.contabilidad_model import MovimientoContable
from modules.categorias.categoria_model import Categoria
from modules.auditorias.auditoria_model import Auditoria, AuditoriaDetalle


TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Crea un motor de base de datos en memoria para toda la sesión de pruebas."""
    return create_engine(TEST_DB_URL)

@pytest.fixture(scope="function")
def tables(engine):
    """Crea todas las tablas antes de cada prueba y las elimina después."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine, tables) -> Generator[Session, None, None]:
    """Crea una nueva sesión de base de datos para cada prueba."""
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def test_usuario(db_session: Session) -> Usuario:
    """Fixture que crea un usuario y un rol básicos para usar en las pruebas."""
    rol_tester = db_session.query(Rol).filter_by(nombre="Tester").first()
    if not rol_tester:
        rol_tester = Rol(nombre="Tester", permisos='["dashboard"]')
        db_session.add(rol_tester)
        db_session.commit()

    usuario = Usuario(
        nombre="Test User",
        usuario="testuser",
        contrasena=Usuario.hash_contrasena("test"),
        rol_id=rol_tester.id
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    return usuario

@pytest.fixture
def setup_atributos(db_session: Session):
    """Fixture para crear atributos y valores comunes para las pruebas de productos."""
    from modules.variantes.variantes_controller import VariantesController
    var_ctrl = VariantesController(db_session)

    # Crear Atributo Talla
    attr_talla = var_ctrl.crear_atributo("Talla")
    val_s = var_ctrl.agregar_valor_a_atributo(attr_talla.id, "S")
    val_m = var_ctrl.agregar_valor_a_atributo(attr_talla.id, "M")

    # Crear Atributo Color
    attr_color = var_ctrl.crear_atributo("Color")
    val_rojo = var_ctrl.agregar_valor_a_atributo(attr_color.id, "Rojo", "#FF0000")
    val_azul = var_ctrl.agregar_valor_a_atributo(attr_color.id, "Azul", "#0000FF")

    return val_s.id, val_m.id, val_rojo.id, val_azul.id