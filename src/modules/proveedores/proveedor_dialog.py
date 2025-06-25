# src/modules/proveedores/proveedor_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from typing import Optional, Dict
from .proveedor_model import Proveedor

class ProveedorDialog(QDialog):
    # El código de la clase no cambia, solo se verifica la importación.
    # Se incluye completo para cumplir la Regla #2.
    def __init__(self, proveedor: Optional[Proveedor] = None, parent=None):
        super().__init__(parent)
        self.proveedor_existente = proveedor
        titulo = "Editar Proveedor" if self.proveedor_existente else "Agregar Nuevo Proveedor"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(450)
        self.setModal(True)
        self._setup_ui()
        if self.proveedor_existente:
            self._cargar_datos()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Nombre Empresa:"), 0, 0)
        self.nombre_input = QLineEdit()
        form_layout.addWidget(self.nombre_input, 0, 1)

        form_layout.addWidget(QLabel("Persona de Contacto:"), 1, 0)
        self.contacto_input = QLineEdit()
        form_layout.addWidget(self.contacto_input, 1, 1)
        
        form_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_input = QLineEdit()
        form_layout.addWidget(self.email_input, 2, 1)

        form_layout.addWidget(QLabel("Teléfono:"), 3, 0)
        self.telefono_input = QLineEdit()
        form_layout.addWidget(self.telefono_input, 3, 1)

        form_layout.addWidget(QLabel("Dirección:"), 4, 0)
        self.direccion_input = QLineEdit()
        form_layout.addWidget(self.direccion_input, 4, 1)

        form_layout.addWidget(QLabel("Sitio Web:"), 5, 0)
        self.website_input = QLineEdit()
        form_layout.addWidget(self.website_input, 5, 1)
        
        layout_principal.addLayout(form_layout)
        
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_guardar = QPushButton("💾 Guardar")
        self.boton_guardar.clicked.connect(self.accept)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        
        layout_principal.addLayout(botones_layout)

    def _cargar_datos(self):
        self.nombre_input.setText(self.proveedor_existente.nombre_empresa)
        self.contacto_input.setText(self.proveedor_existente.persona_contacto or "")
        self.email_input.setText(self.proveedor_existente.email or "")
        self.telefono_input.setText(self.proveedor_existente.telefono or "")
        self.direccion_input.setText(self.proveedor_existente.direccion or "")
        self.website_input.setText(self.proveedor_existente.sitio_web or "")

    def obtener_datos(self) -> Dict:
        nombre = self.nombre_input.text().strip()
        email = self.email_input.text().strip()

        if not nombre or not email:
            QMessageBox.warning(self, "Datos Incompletos", "El nombre de la empresa y el email son obligatorios.")
            return None # Retorna None para indicar que la validación falló

        return {
            "nombre_empresa": nombre,
            "persona_contacto": self.contacto_input.text().strip(),
            "email": email,
            "telefono": self.telefono_input.text().strip(),
            "direccion": self.direccion_input.text().strip(),
            "sitio_web": self.website_input.text().strip()
        }