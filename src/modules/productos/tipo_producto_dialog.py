# src/modules/productos/tipo_producto_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class TipoProductoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection = None
        self.setWindowTitle("Seleccionar Tipo de Producto")
        self.setMinimumWidth(650)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        titulo = QLabel("¿Qué tipo de producto deseas crear?")
        font_titulo = QFont()
        font_titulo.setPointSize(14)
        font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)

        opciones_layout = QHBoxLayout()
        opciones_layout.setSpacing(15)
        
        desc_layout = QGridLayout()
        desc_layout.setSpacing(15)

        # Opción 1: Producto Simple
        btn_simple = QPushButton("📦\nProducto Simple")
        btn_simple.setFixedSize(200, 120)
        btn_simple.clicked.connect(self._select_simple)
        desc_simple = QLabel("Un producto único con su\npropio SKU y stock.\nEj: Un monitor de 24 pulgadas.")
        desc_simple.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Opción 2: Producto con Variantes
        btn_variantes = QPushButton("🧬\nProducto con Variantes")
        btn_variantes.setFixedSize(200, 120)
        btn_variantes.clicked.connect(self._select_variantes)
        desc_variantes = QLabel("Un producto 'molde' que tiene\nmúltiples opciones como talla o color.\nEj: Una camiseta.")
        desc_variantes.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Opción 3: Producto Compuesto (Kit)
        btn_kit = QPushButton("🎁\nProducto Compuesto (Kit)")
        btn_kit.setFixedSize(200, 120)
        btn_kit.clicked.connect(self._select_kit)
        desc_kit = QLabel("Un paquete que se vende como\nun solo item pero descuenta el\nstock de varios productos.\nEj: Una canasta de regalo.")
        desc_kit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        opciones_layout.addWidget(btn_simple)
        opciones_layout.addWidget(btn_variantes)
        opciones_layout.addWidget(btn_kit)
        
        desc_layout.addWidget(desc_simple, 0, 0)
        desc_layout.addWidget(desc_variantes, 0, 1)
        desc_layout.addWidget(desc_kit, 0, 2)
        
        layout_principal.addLayout(opciones_layout)
        layout_principal.addLayout(desc_layout)

    def _select_simple(self):
        self.selection = "simple"
        self.accept()

    def _select_variantes(self):
        self.selection = "variants"
        self.accept()

    def _select_kit(self):
        self.selection = "kit"
        self.accept()

    def get_selection(self) -> str | None:
        return self.selection