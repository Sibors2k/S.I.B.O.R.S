# src/core/base_controller.py

from typing import Optional

class BaseController:
    """
    Clase base para todos los controladores del sistema.
    En el futuro, podría centralizar la gestión de la sesión de la base de datos
    o un sistema de logging más avanzado.
    """

    def __init__(self, db_session: Optional[object] = None):
        """
        Inicializa el controlador. Opcionalmente, puede recibir una sesión
        de base de datos para facilitar las pruebas unitarias.
        
        :param db_session: Una sesión activa de SQLAlchemy.
        """
        self.db = db_session

    def log(self, message: str) -> None:
        """
        Un método simple para imprimir mensajes de log en la consola.
        Ideal para depuración rápida durante el desarrollo.
        
        :param message: El mensaje a imprimir.
        """
        print(f"[LOG] {self.__class__.__name__}: {message}")