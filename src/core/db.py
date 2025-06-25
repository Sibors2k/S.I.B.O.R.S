# src/core/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
import traceback

DB_FILENAME = "sibors.db"
DB_URL = f"sqlite:///{DB_FILENAME}"
engine = create_engine(DB_URL, echo=False)
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- INICIO DE LA MODIFICACIÓN ---
def seed_initial_data(db: Session):
    """
    Puebla la base de datos con datos iniciales si no existen,
    como atributos y valores predefinidos.
    """
    from modules.variantes.variantes_model import Atributo, AtributoValor

    # --- Atributo: Color ---
    attr_color_nombre = "Color"
    attr_color = db.query(Atributo).filter_by(nombre=attr_color_nombre).first()
    if not attr_color:
        print("🌱 Sembrando atributo 'Color' y sus valores...")
        attr_color = Atributo(nombre=attr_color_nombre)
        db.add(attr_color)
        db.flush() # Para obtener el ID del nuevo atributo

        colores = [
            {"valor": "Rojo", "codigo_color": "#FF0000"},
            {"valor": "Verde", "codigo_color": "#008000"},
            {"valor": "Azul", "codigo_color": "#0000FF"},
            {"valor": "Negro", "codigo_color": "#000000"},
            {"valor": "Blanco", "codigo_color": "#FFFFFF"},
            {"valor": "Amarillo", "codigo_color": "#FFFF00"},
            {"valor": "Gris", "codigo_color": "#808080"},
        ]
        for color in colores:
            db.add(AtributoValor(atributo_id=attr_color.id, **color))

    # --- Atributo: Talla ---
    attr_talla_nombre = "Talla"
    attr_talla = db.query(Atributo).filter_by(nombre=attr_talla_nombre).first()
    if not attr_talla:
        print("🌱 Sembrando atributo 'Talla' y sus valores...")
        attr_talla = Atributo(nombre=attr_talla_nombre)
        db.add(attr_talla)
        db.flush()

        tallas = ["XS", "S", "M", "L", "XL", "XXL"]
        for talla in tallas:
            db.add(AtributoValor(valor=talla, atributo_id=attr_talla.id))
    
    db.commit()

def init_db() -> None:
    try:
        from modules.empresa.empresa_model import Empresa
        from modules.usuarios.usuarios_model import Usuario
        from modules.perfil.perfil_model import Perfil
        from modules.productos.models import (
            ProductoPlantilla, Producto, ProductoImagen, KitComponente, MovimientoStock
        )
        from modules.variantes.variantes_model import Atributo, AtributoValor
        from modules.ventas.ventas_model import Venta
        from modules.contabilidad.contabilidad_model import MovimientoContable
        from modules.clientes.cliente_model import Cliente
        from modules.proveedores.proveedor_model import Proveedor
        from modules.compras.compra_model import OrdenCompra, DetalleCompra
        from modules.roles.roles_model import Rol
        from modules.categorias.categoria_model import Categoria
        from modules.auditorias.auditoria_model import Auditoria, AuditoriaDetalle
        
        Base.metadata.create_all(bind=engine)
        print(f"📦 Base de datos inicializada en: {os.path.abspath(DB_FILENAME)}")
        
        # Llamamos a la función de sembrado después de crear las tablas
        db = DBSession()
        seed_initial_data(db)
        db.close()

    except Exception as e:
        print(f"❌ Error CRÍTICO al inicializar la base de datos. El programa se detendrá.")
        print("Error original:", str(e))
        traceback.print_exc()
        os._exit(1)
# --- FIN DE LA MODIFICACIÓN ---