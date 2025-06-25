# src/modules/productos/import_assistant_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDialogButtonBox
)
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Qt
from typing import List, Dict

class ImportAssistantDialog(QDialog):
    def __init__(self, analisis_resultado: List[Dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asistente de Importación de Productos")
        self.setMinimumSize(900, 600)
        self.setModal(True)

        self.resultado = analisis_resultado
        self.filas_validas = [r for r in self.resultado if r['estado'] != 'ERROR']

        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Instrucciones
        info_label = QLabel(
            "Se ha analizado el archivo CSV. Revisa los resultados a continuación.\n"
            "Las filas con errores se marcan en rojo y no se importarán."
        )
        layout.addWidget(info_label)

        # Tabla de Vista Previa
        self.tabla_preview = QTableWidget()
        self.tabla_preview.setColumnCount(5)
        self.tabla_preview.setHorizontalHeaderLabels([
            "N° Fila", "SKU", "Nombre Producto", "Estado", "Detalles / Errores"
        ])
        header = self.tabla_preview.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_preview.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_preview)

        # Resumen
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel()
        summary_layout.addWidget(self.summary_label)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        # Botones
        self.button_box = QDialogButtonBox()
        self.import_button = self.button_box.addButton("Confirmar e Importar", QDialogButtonBox.ButtonRole.AcceptRole)
        self.cancel_button = self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        
        self.import_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(self.button_box)

    def _populate_table(self):
        """Llena la tabla con los resultados del análisis del CSV."""
        self.tabla_preview.setRowCount(len(self.resultado))
        
        error_count = 0
        crear_count = 0
        actualizar_count = 0

        # Colores para los estados
        color_error = QBrush(QColor("#FFDDDD"))  # Rojo claro
        color_ok = QBrush(QColor("#DDFFDD"))     # Verde claro
        color_update = QBrush(QColor("#DDDDFF")) # Azul claro

        for row_index, item in enumerate(self.resultado):
            # Columna 0: Número de Fila en el CSV
            self.tabla_preview.setItem(row_index, 0, QTableWidgetItem(str(item['numero_fila'])))
            
            # Columna 1: SKU
            self.tabla_preview.setItem(row_index, 1, QTableWidgetItem(item['datos'].get('variante_sku', '')))
            
            # Columna 2: Nombre del Producto
            self.tabla_preview.setItem(row_index, 2, QTableWidgetItem(item['datos'].get('plantilla_nombre', '')))
            
            # Columna 3 y 4: Estado y Errores
            estado_item = QTableWidgetItem()
            detalles_item = QTableWidgetItem()
            
            if item['estado'] == 'ERROR':
                estado_item.setText("❌ Error")
                detalles_item.setText(" | ".join(item['error_res']))
                background_color = color_error
                error_count += 1
            elif item['estado'] == 'OK_NUEVO':
                estado_item.setText("✅ OK para Crear")
                background_color = color_ok
                crear_count += 1
            elif item['estado'] == 'OK_ACTUALIZAR':
                estado_item.setText("🔄 OK para Actualizar")
                background_color = color_update
                actualizar_count += 1
            
            self.tabla_preview.setItem(row_index, 3, estado_item)
            self.tabla_preview.setItem(row_index, 4, detalles_item)
            
            # Aplicar color de fondo a toda la fila
            for col_index in range(self.tabla_preview.columnCount()):
                self.tabla_preview.item(row_index, col_index).setBackground(background_color)
        
        # Actualizar el resumen
        summary_text = (
            f"<b>Resumen:</b>   <font color='green'>{crear_count} productos para crear</font> | "
            f"<font color='blue'>{actualizar_count} productos para actualizar</font> | "
            f"<font color='red'>{error_count} filas con errores</font>"
        )
        self.summary_label.setText(summary_text)

        # Deshabilitar el botón de importar si hay errores
        if error_count > 0:
            self.import_button.setEnabled(False)
            self.import_button.setToolTip("No se puede importar porque se encontraron errores en el archivo. Por favor, corrígelos y vuelve a intentarlo.")

    def get_filas_validas(self) -> List[Dict]:
        """Devuelve solo las filas que están listas para ser importadas."""
        return self.filas_validas