# src/utils/validators.py

import re
from datetime import datetime
from typing import Any

# ... (Las demás funciones no cambian) ...
def validar_email(email: str) -> bool:
    if not email: return False
    return bool(re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()))

# --- INICIO DE LA CORRECCIÓN ---
def validar_rfc(rfc: str) -> bool:
    """Valida si el string es un RFC mexicano válido (persona física o moral)."""
    if not rfc: return False
    # Corregido: Se usa un solo backslash \d para los dígitos.
    return bool(re.match(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", rfc.strip(), re.IGNORECASE))
# --- FIN DE LA CORRECCIÓN ---

def validar_curp(curp: str) -> bool:
    if not curp: return False
    return bool(re.match(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$", curp.strip(), re.IGNORECASE))

# ... (El resto del archivo no cambia) ...
def validar_clabe(clabe: str) -> bool:
    if not clabe: return False
    return bool(re.match(r"^\d{18}$", clabe.strip()))

def validar_fecha(fecha: str, formato: str = "%Y-%m-%d") -> bool:
    if not fecha: return False
    try:
        datetime.strptime(fecha.strip(), formato)
        return True
    except ValueError:
        return False

def validar_longitud(texto: str, minimo: int = 1, maximo: int = -1) -> bool:
    if texto is None: return False
    longitud = len(texto.strip())
    if maximo == -1:
        return longitud >= minimo
    else:
        return minimo <= longitud <= maximo

def validar_numero_entero(valor: Any) -> bool:
    try:
        int(valor)
        return True
    except (TypeError, ValueError):
        return False

def sanitizar_telefono(telefono: str) -> str:
    if not telefono: return ""
    return re.sub(r"\D", "", telefono)

def sanitizar_string(texto: str) -> str:
    if not texto: return ""
    return " ".join(texto.strip().split())

def sanitizar_a_mayusculas(texto: str) -> str:
    if not texto: return ""
    return sanitizar_string(texto).upper()