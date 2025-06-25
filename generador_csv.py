import sys
import os
import csv

# Añadimos la ruta de la carpeta 'src' al path de Python
try:
    ruta_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
    if ruta_src not in sys.path:
        sys.path.append(ruta_src)
except NameError:
    sys.path.append(os.path.abspath('src'))

# --- INICIO DE LA MODIFICACIÓN ---
# Se importan TODOS los modelos al principio para que SQLAlchemy
# tenga el mapa completo de relaciones antes de cualquier consulta.
from core.db import DBSession
from modules.categorias.categoria_model import Categoria
from modules.proveedores.proveedor_model import Proveedor
from modules.productos.models import Producto, ProductoPlantilla
from modules.usuarios.usuarios_model import Usuario
from modules.perfil.perfil_model import Perfil
from modules.roles.roles_model import Rol
# (Se podrían añadir más si hicieran falta, pero estos cubren las dependencias conocidas)
# --- FIN DE LA MODIFICACIÓN ---

# --- CONFIGURACIÓN ---
NOMBRE_ARCHIVO_SALIDA = "muestra_para_importar.csv"

def generar_csv_de_prueba():
    """
    Se conecta a la base de datos, lee datos existentes y genera un archivo CSV
    100% compatible para la importación.
    """
    print("🤖 Iniciando generador de datos de prueba...")
    db = DBSession()
    
    # 1. Obtenemos datos reales de la base de datos
    try:
        # Esta consulta ahora funcionará sin problemas.
        categorias_existentes = db.query(Categoria).all()
        proveedores_existentes = db.query(Proveedor).all()
        print(f"🔍 Encontrados {len(categorias_existentes)} categorías y {len(proveedores_existentes)} proveedores.")
    finally:
        db.close()

    # 2. Preparamos los datos para el CSV
    filas_csv = []
    encabezado = [
        'plantilla_nombre', 'categoria_ruta', 'proveedor_nombre', 'tipo_producto',
        'variante_sku', 'variante_precio', 'variante_costo', 'variante_stock',
        'variante_atributos', 'kit_componentes'
    ]
    filas_csv.append(encabezado)

    # --- Producto Simple con datos existentes ---
    cat_nombre = categorias_existentes[0].nombre if categorias_existentes else ""
    prov_nombre = proveedores_existentes[0].nombre_empresa if proveedores_existentes else ""
    filas_csv.append([
        "Laptop Pro X1", cat_nombre, prov_nombre, "Simple", "LP-X1", 1999.99, 1500, 10, "", ""
    ])

    # --- Producto con Variantes ---
    cat_nombre_ropa = next((c.nombre for c in categorias_existentes if "ropa" in c.nombre.lower()), "")
    tallas = ["S", "M", "L"]
    colores = ["Negro", "Blanco"]
    for talla in tallas:
        for color in colores:
            filas_csv.append([
                "Camiseta Basica Premium", cat_nombre_ropa, prov_nombre, "Variante",
                f"TSH-PREM-{talla}-{color[:3]}", 29.99, 12.50, 50,
                f"Talla:{talla} | Color:{color}", ""
            ])
            
    # --- Kit (usando SKUs que sabemos que existirán después de la importación) ---
    filas_csv.append([
        "Kit de Oficina Esencial", "Kits", prov_nombre, "Kit", "KIT-OFC-01", 
        2025.00, 1560, 0, "", "LP-X1:1"
    ])
    
    print(f"✍️  Generando {len(filas_csv) - 1} filas de datos...")

    # 3. Escribimos el archivo CSV
    try:
        with open(NOMBRE_ARCHIVO_SALIDA, 'w', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerows(filas_csv)
        print(f"✅ ¡Éxito! Archivo '{NOMBRE_ARCHIVO_SALIDA}' creado en la raíz de tu proyecto.")
    except Exception as e:
        print(f"❌ Error al escribir el archivo: {e}")

if __name__ == "__main__":
    generar_csv_de_prueba()