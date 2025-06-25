# src/main.py
import sys
import os
import json

print("🚀 Iniciando S.I.B.O.R.S, por favor espere...")

try:
    # Aseguramos que la carpeta 'src' esté en el path para que las importaciones funcionen
    ruta_src = os.path.dirname(os.path.abspath(__file__))
    if ruta_src not in sys.path:
        sys.path.append(ruta_src)
except NameError:
    # Fallback para algunos entornos
    sys.path.append(os.path.abspath('.'))

from PySide6.QtWidgets import QApplication

# --- INICIO DE LA MODIFICACIÓN ---
# El 'orm' y la 'Session' para type-hinting vienen de sqlalchemy, no de PySide6.
from sqlalchemy.orm import Session as SQLAlchemySession
# --- FIN DE LA MODIFICACIÓN ---

from core.db import init_db, DBSession 
from modules.usuarios.usuarios_model import Usuario
from modules.roles.roles_model import Rol
from modules.roles.roles_ui import MODULOS_DISPONIBLES
from ui.theme_manager import ThemeManager
from modules.usuarios.usuarios_controller import UsuariosController
from ui.login_ui import LoginWindow
from modules.empresa.empresa_model import Empresa
from ui.main_window import MainWindow

def crear_admin_si_no_existe(db: SQLAlchemySession) -> None:
    """
    Ahora esta función RECIBE una credencial activa, no crea una propia.
    """
    rol_admin = db.query(Rol).filter_by(nombre="Admin").first()
    permisos_actuales_json = json.dumps(MODULOS_DISPONIBLES, sort_keys=True)
    if not rol_admin:
        print("👤 Creando rol 'Admin' por primera vez.")
        rol_admin = Rol(nombre="Admin", permisos=permisos_actuales_json)
        db.add(rol_admin)
        # Hacemos commit aquí para asegurar que el rol tenga un ID antes de asignarlo
        db.commit() 
        db.refresh(rol_admin)
    else:
        # Comparamos los permisos y actualizamos si es necesario
        permisos_guardados = sorted(rol_admin.obtener_permisos_como_lista())
        permisos_actuales = sorted(MODULOS_DISPONIBLES)
        if permisos_guardados != permisos_actuales:
            print("🔄 Actualizando permisos del rol 'Admin'.")
            rol_admin.permisos = permisos_actuales_json
            db.commit()
    
    usuario_admin = db.query(Usuario).filter_by(usuario="admin").first()
    if not usuario_admin:
        print("👤 Creando usuario 'admin' por primera vez. Contraseña por defecto: admin123")
        admin = Usuario(nombre="Administrador", usuario="admin", contrasena=Usuario.hash_contrasena("admin123"), rol_id=rol_admin.id, activo=True)
        db.add(admin)
        db.commit()

def main():
    app = QApplication(sys.argv)
    app.theme_manager = ThemeManager(app)
    
    # 1. Inicializa la estructura de la DB (crea las tablas si no existen)
    init_db()
    
    # 2. Creamos UNA SOLA credencial de base de datos para todas las operaciones de arranque
    db_session = DBSession()
    
    try:
        # 3. Le pasamos esa credencial a la función que crea el admin
        crear_admin_si_no_existe(db_session)
        
        # 4. Usamos la misma credencial para las demás tareas
        usuarios_controller = UsuariosController(db_session)
        empresa = db_session.query(Empresa).first()
        nombre_empresa = empresa.nombre if empresa else "S.I.B.O.R.S"
        
        main_window_instance = None

        def open_main_window(usuario_autenticado):
            nonlocal main_window_instance
            if usuario_autenticado:
                # La ventana principal también podría necesitar la sesión en el futuro
                main_window_instance = MainWindow(usuario_autenticado, db_session)
                main_window_instance.showMaximized()
        
        login_window = LoginWindow(usuarios_controller, nombre_empresa)
        login_window.login_success.connect(open_main_window)
        
        print("✅ Sistema listo. Mostrando ventana de login.")
        login_window.show()
        
        app.exec()

    finally:
        # 5. Al final de todo, cerramos la credencial.
        print("🚪 Cerrando sesión de base de datos.")
        db_session.close()
        sys.exit()

if __name__ == "__main__":
    main()