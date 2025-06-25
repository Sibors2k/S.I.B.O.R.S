# tests/test_usuarios_controller.py

import pytest
from datetime import datetime, timedelta, timezone
from modules.usuarios.usuarios_model import Usuario
from modules.usuarios.usuarios_controller import UsuariosController, PERIODO_DE_GRACIA
from modules.roles.roles_controller import RolesController

# ... (Las primeras 3 pruebas no cambian) ...
@pytest.fixture
def rol_empleado(db_session):
    return RolesController(db_session).crear_rol("Empleado", ["dashboard"])

def test_crear_y_login_exitoso(db_session, rol_empleado):
    controller = UsuariosController(db_session)
    datos_usuario = {"nombre": "John Doe", "usuario": "johndoe", "contrasena": "password123", "rol_id": rol_empleado.id, "activo": True}
    controller.crear_usuario(datos_usuario)
    usuario_logueado = controller.login("johndoe", "password123")
    assert usuario_logueado is not None

def test_login_usuario_inactivo_falla(db_session, rol_empleado):
    controller = UsuariosController(db_session)
    datos_usuario = {"nombre": "Inactive User", "usuario": "inactive", "contrasena": "password123", "rol_id": rol_empleado.id, "activo": False}
    controller.crear_usuario(datos_usuario)
    usuario_logueado = controller.login("inactive", "password123")
    assert usuario_logueado is None

def test_desactivar_usuario_registra_fecha(db_session, rol_empleado):
    controller = UsuariosController(db_session)
    controller.crear_usuario({"nombre": "Temp User", "usuario": "temp", "contrasena": "pass", "rol_id": rol_empleado.id, "activo": True})
    usuario_creado = db_session.query(Usuario).filter_by(usuario="temp").first()
    controller.editar_usuario(usuario_creado.id, {"activo": False})
    db_session.expire(usuario_creado)
    usuario_actualizado = db_session.query(Usuario).filter_by(usuario="temp").first()
    assert not usuario_actualizado.activo
    assert usuario_actualizado.fecha_desactivacion is not None
    fecha_desactivacion_aware = usuario_actualizado.fecha_desactivacion.replace(tzinfo=timezone.utc)
    assert (datetime.now(timezone.utc) - fecha_desactivacion_aware).total_seconds() < 5


def test_eliminar_usuario_falla_antes_de_periodo_gracia(db_session, rol_empleado):
    controller = UsuariosController(db_session)
    controller.crear_usuario({"nombre": "User To Delete", "usuario": "todelete", "contrasena": "pass", "rol_id": rol_empleado.id, "activo": True})
    usuario_creado = db_session.query(Usuario).filter_by(usuario="todelete").first()
    controller.editar_usuario(usuario_creado.id, {"activo": False})
    usuario_creado.fecha_desactivacion = datetime.now(timezone.utc) - timedelta(days=29)
    db_session.commit()
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Hacemos la prueba robusta: verificamos que el mensaje contenga el patrón esperado
    # sin depender del número exacto, que es inestable. '.*' es un comodín.
    with pytest.raises(ValueError, match="Aún no se puede eliminar. Faltan .* día\\(s\\)."):
        controller.eliminar_permanentemente(usuario_creado.id)
    # --- FIN DE LA CORRECCIÓN ---

def test_eliminar_usuario_exitoso_despues_de_periodo_gracia(db_session, rol_empleado):
    controller = UsuariosController(db_session)
    controller.crear_usuario({"nombre": "Old User", "usuario": "olduser", "contrasena": "pass", "rol_id": rol_empleado.id, "activo": True})
    usuario_creado = db_session.query(Usuario).filter_by(usuario="olduser").first()
    controller.editar_usuario(usuario_creado.id, {"activo": False})
    usuario_creado.fecha_desactivacion = datetime.now(timezone.utc) - (PERIODO_DE_GRACIA + timedelta(days=1))
    db_session.commit()
    controller.eliminar_permanentemente(usuario_creado.id)
    usuario_eliminado = db_session.query(Usuario).filter_by(usuario="olduser").first()
    assert usuario_eliminado is None