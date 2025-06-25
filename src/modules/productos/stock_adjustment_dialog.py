# src/modules/productos/stock_adjustment_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QPushButton, QHBoxLayout, QComboBox, QTextEdit, QMessageBox
)
from typing import Optional, Dict

# --- INICIO DE LA MODIFICACIÓN ---
from .models import TipoAjusteStock, Producto
# --- FIN DE LA MODIFICACIÓN ---

class StockAdjustmentDialog(QDialog):
    def __init__(self, producto: Producto, parent=None):
        super().__init__(parent)
        self.producto = producto
        
        nombre_variante = " / ".join(valor.valor for valor in self.producto.valores)
        titulo_completo = f"{self.producto.plantilla.nombre} ({nombre_variante})" if nombre_variante else self.producto.plantilla.nombre
        self.setWindowTitle(f"Ajustar Stock de: {titulo_completo}")

        self.setMinimumWidth(450)
        self.setModal(True)
        
        self._setup_widgets()

    def _setup_widgets(self):
        """Construye y organiza todos los widgets del diálogo."""
        layout_principal = QVBoxLayout(self)
        
        nombre_variante = " / ".join(valor.valor for valor in self.producto.valores)
        nombre_display = f" ({nombre_variante})" if nombre_variante else ""

        info_label = QLabel(f"<b>Producto:</b> {self.producto.plantilla.nombre}{nombre_display}<br>"
                            f"<b>SKU:</b> {self.producto.sku}<br>"
                            f"<b>Stock Actual:</b> {self.producto.stock} unidades")

        layout_principal.addWidget(info_label)

        form_layout = QFormLayout()
        
        self.combo_tipo_ajuste = QComboBox()
        self._poblar_combo_tipo_ajuste()
        form_layout.addRow("Tipo de Ajuste:", self.combo_tipo_ajuste)
        
        self.input_cantidad = QLineEdit()
        self.input_cantidad.setPlaceholderText("Ej: 5 para sumar, -3 para restar")
        form_layout.addRow("Cantidad a Ajustar:", self.input_cantidad)

        self.input_motivo = QTextEdit()
        self.input_motivo.setPlaceholderText("Describe brevemente el motivo del ajuste.")
        self.input_motivo.setFixedHeight(80)
        form_layout.addRow("Motivo del Ajuste:", self.input_motivo)
        
        layout_principal.addLayout(form_layout)
        
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_aceptar = QPushButton("💾 Aceptar y Ajustar")
        self.boton_aceptar.clicked.connect(self.accept)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        
        botones_layout.addWidget(self.boton_aceptar)
        botones_layout.addWidget(self.boton_cancelar)
        
        layout_principal.addLayout(botones_layout)

    def _poblar_combo_tipo_ajuste(self):
        """Puebla el ComboBox con los valores del Enum TipoAjusteStock."""
        for tipo in TipoAjusteStock:
            if tipo not in [TipoAjusteStock.SALIDA_VENTA, TipoAjusteStock.ENTRADA_COMPRA]:
                 self.combo_tipo_ajuste.addItem(tipo.value, userData=tipo)

    def obtener_datos(self) -> Optional[Dict]:
        """Valida y devuelve los datos del formulario en un diccionario."""
        try:
            cantidad = int(self.input_cantidad.text())
            if cantidad == 0:
                QMessageBox.warning(self, "Dato Inválido", "La cantidad a ajustar no puede ser cero.")
                return None
        except ValueError:
            QMessageBox.warning(self, "Dato Inválido", "La cantidad a ajustar debe ser un número entero.")
            return None

        motivo = self.input_motivo.toPlainText().strip()
        if not motivo:
            QMessageBox.warning(self, "Dato Requerido", "El motivo del ajuste es obligatorio.")
            return None
            
        tipo_ajuste = self.combo_tipo_ajuste.currentData()

        return {
            "cantidad_ajuste": cantidad,
            "tipo_ajuste": tipo_ajuste,
            "motivo": motivo
        }