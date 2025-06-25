# tests/test_validators.py

import pytest
from utils import validators

# --- Pruebas para validar_email ---
@pytest.mark.parametrize("email, esperado", [
    ("test@example.com", True),
    ("user.name+tag@domain.co.uk", True),
    ("email.valido-123@sub.dominio.org", True),
    ("invalido", False),
    ("sin_arroba.com", False),
    ("sin_dominio@", False),
    ("@sin_usuario.com", False),
    ("espacios @ email.com", False),
    ("", False),
    (None, False)
])
def test_validar_email(email, esperado):
    """Verifica la validación de emails con varios casos."""
    assert validators.validar_email(email) == esperado

# --- Pruebas para validar_rfc (México) ---
@pytest.mark.parametrize("rfc, esperado", [
    ("GODE880101HMA", True),      # Persona Física (13 caracteres)
    ("GOME8801011A1", True),      # Persona Física con Homoclave (13)
    # --- INICIO DE LA CORRECCIÓN ---
    # Este RFC tiene un formato válido de 12 caracteres para Persona Moral.
    # La prueba original estaba incorrecta al esperar False.
    ("PME8801011A1", True),       # Persona Moral (12 caracteres)
    # --- FIN DE LA CORRECCIÓN ---
    ("PEM991231AB1", True),       # Persona Moral (12 caracteres)
    ("INVALIDO", False),
    ("ABC1234567890", False),     # Formato incorrecto
    ("gode880101hma", True),      # Debe aceptar minúsculas
    ("", False)
])
def test_validar_rfc(rfc, esperado):
    """Verifica la validación de RFCs."""
    assert validators.validar_rfc(rfc) == esperado

# --- Pruebas para sanitizar_telefono ---
def test_sanitizar_telefono():
    """Verifica que solo queden dígitos en el teléfono."""
    assert validators.sanitizar_telefono("(55) 1234-5678") == "5512345678"
    assert validators.sanitizar_telefono("  +52 987 654 3210  ") == "529876543210"
    assert validators.sanitizar_telefono("SinNumeros") == ""
    assert validators.sanitizar_telefono("") == ""