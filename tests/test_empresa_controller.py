# tests/test_empresa_controller.py

import pytest
from modules.empresa.empresa_controller import EmpresaController, EmpresaValidationError
from modules.empresa.empresa_model import EmpresaData, Empresa

def test_guardar_y_obtener_datos_empresa(db_session):
    """
    Prueba el flujo de guardar y luego obtener los datos de la empresa.
    """
    controller = EmpresaController(db_session)
    
    # 1. Guardar datos por primera vez (creación)
    datos_iniciales = EmpresaData(
        nombre="Mi Empresa de Prueba S.A.",
        rfc="MEP250620ABC",
        correo_principal="contacto@empresa.com"
    )
    controller.guardar_datos_empresa(datos_iniciales)
    
    # 2. Obtener los datos y verificar
    datos_obtenidos = controller.obtener_datos_empresa()
    assert datos_obtenidos is not None
    assert datos_obtenidos.nombre == "Mi Empresa de Prueba S.A."
    assert datos_obtenidos.rfc == "MEP250620ABC"

    # 3. Guardar datos por segunda vez (actualización)
    datos_actualizados = EmpresaData(
        nombre="Mi Gran Empresa de Prueba S.A. de C.V."
    )
    controller.guardar_datos_empresa(datos_actualizados)
    
    # 4. Obtener y verificar la actualización
    datos_finales = controller.obtener_datos_empresa()
    assert datos_finales.nombre == "Mi Gran Empresa de Prueba S.A. de C.V."
    assert datos_finales.rfc == "MEP250620ABC" # El RFC no se envió, no debe cambiar

def test_guardar_datos_con_validacion_fallida(db_session):
    """Prueba que el controlador rechaza datos inválidos."""
    controller = EmpresaController(db_session)
    datos_invalidos = EmpresaData(
        nombre="OK", # Nombre muy corto
        rfc="123" # RFC inválido
    )
    
    with pytest.raises(EmpresaValidationError, match="El nombre de la empresa es obligatorio"):
        controller.guardar_datos_empresa(datos_invalidos)