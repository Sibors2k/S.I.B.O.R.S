# tests/test_roles_controller.py

import pytest
from modules.roles.roles_controller import RolesController
from modules.roles.roles_model import Rol

# --- INICIO DE LA CORRECCIÓN ---
def test_crear_rol_exitoso(db_session):
    """Verifica que se puede crear un nuevo rol con datos válidos."""
    controller = RolesController(db_session)  # Inyectamos la sesión
    nombre_rol = "Vendedor"
    permisos = ["ventas", "clientes"]
    
    rol = controller.crear_rol(nombre_rol, permisos)
    
    assert rol.id is not None
    assert rol.nombre == nombre_rol
    assert rol.obtener_permisos_como_lista() == permisos
    
    rol_en_db = db_session.query(Rol).filter_by(nombre=nombre_rol).first()
    assert rol_en_db is not None
    assert rol_en_db.id == rol.id

def test_crear_rol_duplicado_falla(db_session):
    """Verifica que no se puede crear un rol con un nombre que ya existe."""
    controller = RolesController(db_session) # Inyectamos la sesión
    
    controller.crear_rol("Tester", ["dashboard"])
    
    with pytest.raises(ValueError, match="El rol 'Tester' ya existe."):
        controller.crear_rol("Tester", ["inventario"])

def test_listar_roles(db_session):
    """Verifica que se listen correctamente los roles creados."""
    controller = RolesController(db_session) # Inyectamos la sesión
    
    # 1. Verificamos que la DB empieza vacía
    roles_iniciales = controller.listar_roles()
    assert len(roles_iniciales) == 0
    
    # 2. Creamos datos
    controller.crear_rol("Admin", ["todos"])
    controller.crear_rol("Cajero", ["ventas"])
    
    # 3. Verificamos que ahora hay 2 roles
    roles_finales = controller.listar_roles()
    assert len(roles_finales) == 2
    nombres_roles = {rol.nombre for rol in roles_finales}
    assert {"Admin", "Cajero"} == nombres_roles
# --- FIN DE LA CORRECCIÓN ---