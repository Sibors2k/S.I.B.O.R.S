# src/ui/components/footer_widget.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class FooterWidget(QWidget):
    """
    El widget del pie de página.
    Mostrará información simple como copyright o la versión de la app.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footerWidget") # ID para aplicar estilos QSS
        self.setFixedHeight(30) # Altura delgada como pediste

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        copyright_label = QLabel("© 2025 S.I.B.O.R.S. | Todos los derechos reservados")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(copyright_label)