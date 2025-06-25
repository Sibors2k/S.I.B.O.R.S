# src/ui/components/main_content.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt

class MainContent(QWidget):
    """
    El widget de contenido principal. Actúa como el contenedor para
    el QStackedWidget, que gestiona las diferentes vistas de los módulos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainContent") # Asignamos un ID para el estilo

        # El layout principal de este widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # El QStackedWidget es el "mazo de cartas" que contendrá
        # y mostrará una a una las interfaces de los módulos.
        self.stack = QStackedWidget(self)
        
        # Creamos una página de bienvenida por defecto
        self.pagina_bienvenida = self._crear_pagina_bienvenida()
        self.stack.addWidget(self.pagina_bienvenida)
        
        # Añadimos el mazo de cartas al layout de este widget
        layout.addWidget(self.stack)

    def _crear_pagina_bienvenida(self) -> QWidget:
        """Crea un widget simple para mostrar como página de inicio."""
        widget_bienvenida = QWidget()
        layout = QVBoxLayout(widget_bienvenida)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje de bienvenida
        mensaje = QLabel("Bienvenido a S.I.B.O.R.S\n\nSelecciona un módulo en el menú de la izquierda para comenzar.")
        mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mensaje.setStyleSheet("font-size: 18px; color: #888;") # Estilo simple
        
        layout.addWidget(mensaje)
        
        return widget_bienvenida

    def get_stack(self) -> QStackedWidget:
        """
        Método público para que otros widgets (como MainWindow) puedan
        acceder al QStackedWidget y añadirle las vistas de los módulos.
        """
        return self.stack