# tests/test_perfil_controller.py

import pytest
from unittest.mock import Mock
from PIL import Image
import os

from modules.perfil.perfil_controller import PerfilController
from modules.usuarios.usuarios_model import Usuario
from modules.perfil.perfil_model import Perfil

@pytest.fixture
def setup_controllers(db_session):
    perfil_ctrl = PerfilController(db_session)
    # Creamos un usuario y un rol para las pruebas
    mock_rol = Mock()
    mock_rol.id = 1
    usuario_test = Usuario(id=1, nombre="Test User", usuario="test", contrasena="-", rol_id=mock_rol.id)
    db_session.add(usuario_test)
    db_session.commit()
    return perfil_ctrl, usuario_test

def test_obtener_o_crear_perfil(setup_controllers):
    """Verifica que un perfil se crea si no existe para un usuario."""
    perfil_ctrl, usuario_test = setup_controllers
    
    # 1. Primera llamada, debe crear el perfil
    perfil = perfil_ctrl.obtener_perfil(usuario_test.id)
    assert perfil is not None
    assert perfil.usuario_id == usuario_test.id
    assert perfil.nombre == "Test User"

    # 2. Segunda llamada, debe devolver el mismo perfil
    perfil_2 = perfil_ctrl.obtener_perfil(usuario_test.id)
    assert perfil_2.id == perfil.id

def test_actualizar_perfil(setup_controllers):
    """Verifica que los datos del perfil se pueden actualizar."""
    perfil_ctrl, usuario_test = setup_controllers
    
    perfil_inicial = perfil_ctrl.obtener_perfil(usuario_test.id)
    
    datos_nuevos = {
        "apellidos": "Probador",
        "cargo": "QA Lead",
        "biografia": "Probando el sistema."
    }
    perfil_actualizado = perfil_ctrl.actualizar_perfil(usuario_test.id, datos_nuevos)

    assert perfil_actualizado.id == perfil_inicial.id
    assert perfil_actualizado.apellidos == "Probador"
    assert perfil_actualizado.cargo == "QA Lead"

def test_guardar_avatar(setup_controllers, tmp_path):
    """Verifica que el avatar se guarda y se actualiza la ruta en la DB."""
    perfil_ctrl, usuario_test = setup_controllers
    
    # Sobrescribimos el directorio de avatares para que use la carpeta temporal de la prueba
    perfil_ctrl.avatares_dir = tmp_path
    
    # Creamos una imagen falsa
    fake_image_path = tmp_path / "fake_avatar.png"
    Image.new('RGB', (100, 100)).save(fake_image_path)
    
    # Acción
    nueva_ruta = perfil_ctrl.guardar_avatar(usuario_test.id, str(fake_image_path))
    
    # Verificación
    assert nueva_ruta is not None
    assert os.path.exists(nueva_ruta) # El archivo debe existir en la carpeta temporal
    
    perfil_actualizado = perfil_ctrl.obtener_perfil(usuario_test.id)
    assert perfil_actualizado.avatar_path == nueva_ruta