# src/modules/clientes/cliente_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QMessageBox)
from typing import Optional, Dict
from .cliente_model import Cliente, EstadoCliente

class ClienteDialog(QDialog):
    # El código de la clase no cambia, solo se verifica la importación.
    # Se incluye completo para cumplir la Regla #2.
    def __init__(self, cliente: Optional[Cliente] = None, parent=None):
        super().__init__(parent)
        self.cliente_existente = cliente
        titulo = "Editar Cliente" if self.cliente_existente else "Agregar Nuevo Cliente"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(450)
        self.setModal(True)
        self._setup_ui()
        if self.cliente_existente:
            self._cargar_datos()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Nombre Completo:"), 0, 0); self.nombre_input = QLineEdit(); form_layout.addWidget(self.nombre_input, 0, 1)
        form_layout.addWidget(QLabel("Razón Social:"), 1, 0); self.razon_social_input = QLineEdit(); form_layout.addWidget(self.razon_social_input, 1, 1)
        form_layout.addWidget(QLabel("RFC:"), 2, 0); self.rfc_input = QLineEdit(); form_layout.addWidget(self.rfc_input, 2, 1)
        form_layout.addWidget(QLabel("Email:"), 3, 0); self.email_input = QLineEdit(); form_layout.addWidget(self.email_input, 3, 1)
        form_layout.addWidget(QLabel("Teléfono:"), 4, 0); self.telefono_input = QLineEdit(); form_layout.addWidget(self.telefono_input, 4, 1)
        form_layout.addWidget(QLabel("Dirección:"), 5, 0); self.direccion_input = QLineEdit(); form_layout.addWidget(self.direccion_input, 5, 1)
        form_layout.addWidget(QLabel("Límite de Crédito:"), 6, 0); self.limite_credito_input = QLineEdit("0"); form_layout.addWidget(self.limite_credito_input, 6, 1)
        form_layout.addWidget(QLabel("Estado:"), 7, 0); self.estado_combo = QComboBox();
        for estado in EstadoCliente: self.estado_combo.addItem(estado.value, userData=estado)
        form_layout.addWidget(self.estado_combo, 7, 1)
        layout_principal.addLayout(form_layout)
        botones_layout = QHBoxLayout(); botones_layout.addStretch(); self.boton_guardar = QPushButton("💾 Guardar"); self.boton_guardar.clicked.connect(self.accept); self.boton_cancelar = QPushButton("Cancelar"); self.boton_cancelar.clicked.connect(self.reject); botones_layout.addWidget(self.boton_guardar); botones_layout.addWidget(self.boton_cancelar); layout_principal.addLayout(botones_layout)

    def _cargar_datos(self):
        self.nombre_input.setText(self.cliente_existente.nombre_completo); self.razon_social_input.setText(self.cliente_existente.razon_social or ""); self.rfc_input.setText(self.cliente_existente.rfc or ""); self.email_input.setText(self.cliente_existente.email or ""); self.telefono_input.setText(self.cliente_existente.telefono or ""); self.direccion_input.setText(self.cliente_existente.direccion or ""); self.limite_credito_input.setText(str(self.cliente_existente.limite_credito));
        index = self.estado_combo.findData(self.cliente_existente.estado)
        if index != -1: self.estado_combo.setCurrentIndex(index)

    def obtener_datos(self) -> Dict:
        nombre = self.nombre_input.text().strip(); email = self.email_input.text().strip()
        if not nombre or not email:
            QMessageBox.warning(self, "Datos Incompletos", "El nombre completo y el email son obligatorios.")
            return None
        try:
            limite = float(self.limite_credito_input.text())
        except ValueError:
            QMessageBox.warning(self, "Dato Inválido", "El límite de crédito debe ser un número.")
            return None
        return {"nombre_completo": nombre, "razon_social": self.razon_social_input.text().strip(), "rfc": self.rfc_input.text().strip(), "email": email, "telefono": self.telefono_input.text().strip(), "direccion": self.direccion_input.text().strip(), "limite_credito": limite, "estado": self.estado_combo.currentData()}