# src/ui/components/content_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt

class ContentWidget(QWidget):
    """
    El widget de contenido principal. Contiene el QStackedWidget
    que gestiona y muestra las vistas de los diferentes módulos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("contentWidget") # ID para aplicar estilos QSS

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) # Margen interno para que el contenido no pegue a los bordes
        
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)

    def get_stack(self) -> QStackedWidget:
        """
        Devuelve la referencia al 'mazo de cartas' para que la ventana
        principal pueda añadirle los módulos.
        """
        return self.stack