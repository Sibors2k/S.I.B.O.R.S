# src/modules/variantes/variantes_ui.py

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, 
    QPushButton, QGroupBox, QMessageBox, QLabel, QInputDialog, QColorDialog, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap, QIcon
from typing import Optional, List

from .variantes_controller import VariantesController
from .variantes_model import Atributo, AtributoValor

class VariantesWidget(QWidget):
    def __init__(self, controller: VariantesController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.atributos_cacheados: List[Atributo] = []
        self.current_atributo: Optional[Atributo] = None
        self.selected_hex_color: str = "#FFFFFF"

        self._setup_ui()
        self.actualizar_vista()

    def actualizar_vista(self):
        self._cargar_lista_atributos()
        self._limpiar_panel_valores()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self._crear_panel_atributos(), 1)
        layout.addWidget(self._crear_panel_valores(), 2)

    def _crear_panel_atributos(self) -> QGroupBox:
        grupo = QGroupBox("Atributos")
        layout = QVBoxLayout(grupo)

        self.lista_atributos = QListWidget()
        self.lista_atributos.itemSelectionChanged.connect(self._on_atributo_seleccionado)
        layout.addWidget(self.lista_atributos)

        botones_layout = QHBoxLayout()
        btn_agregar = QPushButton("➕ Agregar")
        btn_editar = QPushButton("✏️ Editar")
        btn_eliminar = QPushButton("❌ Eliminar")

        btn_agregar.clicked.connect(self._agregar_atributo)
        btn_editar.clicked.connect(self._editar_atributo)
        btn_eliminar.clicked.connect(self._eliminar_atributo)

        botones_layout.addWidget(btn_agregar)
        botones_layout.addWidget(btn_editar)
        botones_layout.addWidget(btn_eliminar)
        layout.addLayout(botones_layout)
        
        return grupo

    def _crear_panel_valores(self) -> QGroupBox:
        self.grupo_valores = QGroupBox("Valores")
        layout = QVBoxLayout(self.grupo_valores)
        self.lista_valores = QListWidget()
        layout.addWidget(self.lista_valores)

        # --- WIDGET PARA VALORES SIMPLES (TALLA, ETC) ---
        self.simple_value_widget = QWidget()
        agregar_layout = QHBoxLayout(self.simple_value_widget)
        agregar_layout.setContentsMargins(0,0,0,0)
        self.input_nuevo_valor_simple = QLineEdit()
        self.input_nuevo_valor_simple.setPlaceholderText("Nuevo valor...")
        btn_agregar_valor_simple = QPushButton("➕ Agregar Valor")
        btn_agregar_valor_simple.clicked.connect(self._agregar_valor)
        agregar_layout.addWidget(self.input_nuevo_valor_simple)
        agregar_layout.addWidget(btn_agregar_valor_simple)
        layout.addWidget(self.simple_value_widget)

        # --- WIDGET PARA VALORES DE COLOR ---
        self.color_value_widget = QWidget()
        form_color_layout = QFormLayout(self.color_value_widget)
        form_color_layout.setContentsMargins(0,0,0,0)
        self.input_nombre_color = QLineEdit()
        self.input_nombre_color.setPlaceholderText("Ej: Azul Cielo")
        
        color_selector_layout = QHBoxLayout()
        self.swatch_label = QLabel()
        self.swatch_label.setFixedSize(24, 24)
        self._update_swatch_color("#FFFFFF")
        
        self.btn_seleccionar_color = QPushButton("Seleccionar Color...")
        self.btn_seleccionar_color.clicked.connect(self._abrir_dialogo_color)
        color_selector_layout.addWidget(self.swatch_label)
        color_selector_layout.addWidget(self.btn_seleccionar_color)
        color_selector_layout.addStretch()
        
        form_color_layout.addRow("Nombre del Color:", self.input_nombre_color)
        form_color_layout.addRow("Muestra:", color_selector_layout)

        btn_agregar_valor_color = QPushButton("➕ Agregar Color")
        btn_agregar_valor_color.clicked.connect(self._agregar_valor)
        form_color_layout.addRow(btn_agregar_valor_color)
        layout.addWidget(self.color_value_widget)

        # --- BOTONES DE EDICIÓN / ELIMINACIÓN ---
        botones_edicion_layout = QHBoxLayout()
        btn_editar_valor = QPushButton("✏️ Editar Valor")
        btn_eliminar_valor = QPushButton("❌ Eliminar Valor")
        btn_editar_valor.clicked.connect(self._editar_valor)
        btn_eliminar_valor.clicked.connect(self._eliminar_valor)
        botones_edicion_layout.addStretch()
        botones_edicion_layout.addWidget(btn_editar_valor)
        botones_edicion_layout.addWidget(btn_eliminar_valor)
        layout.addLayout(botones_edicion_layout)

        return self.grupo_valores

    def _cargar_lista_atributos(self):
        self.atributos_cacheados = self.controller.listar_atributos()
        self.lista_atributos.clear()
        for atributo in self.atributos_cacheados:
            item = QListWidgetItem(atributo.nombre)
            item.setData(Qt.ItemDataRole.UserRole, atributo)
            self.lista_atributos.addItem(item)
        self._limpiar_panel_valores()

    def _limpiar_panel_valores(self):
        self.current_atributo = None
        self.grupo_valores.setTitle("Valores")
        self.lista_valores.clear()
        self.input_nuevo_valor_simple.clear()
        self.input_nombre_color.clear()
        self.grupo_valores.setEnabled(False)
        self.simple_value_widget.hide()
        self.color_value_widget.hide()

    def _on_atributo_seleccionado(self):
        items = self.lista_atributos.selectedItems()
        if not items:
            self._limpiar_panel_valores()
            return
        
        item_seleccionado = items[0]
        self.current_atributo = item_seleccionado.data(Qt.ItemDataRole.UserRole)
        
        if not self.current_atributo:
            self._limpiar_panel_valores()
            return

        self.grupo_valores.setEnabled(True)
        self.grupo_valores.setTitle(f"Valores para '{self.current_atributo.nombre}'")
        
        # Lógica para mostrar el widget de agregar correcto
        if self.current_atributo.nombre.lower() == 'color':
            self.simple_value_widget.hide()
            self.color_value_widget.show()
        else:
            self.simple_value_widget.show()
            self.color_value_widget.hide()

        # Poblar la lista de valores
        self.lista_valores.clear()
        atributo_completo = next((attr for attr in self.atributos_cacheados if attr.id == self.current_atributo.id), None)
        if not atributo_completo: return

        for valor in sorted(atributo_completo.valores, key=lambda v: v.valor):
            item = QListWidgetItem(valor.valor)
            item.setData(Qt.ItemDataRole.UserRole, valor)
            if valor.codigo_color:
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor(valor.codigo_color))
                item.setIcon(QIcon(pixmap))
            self.lista_valores.addItem(item)
            
    def _abrir_dialogo_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.selected_hex_color = color.name().upper()
            self._update_swatch_color(self.selected_hex_color)

    def _update_swatch_color(self, hex_color: str):
        self.swatch_label.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #555;")

    def _agregar_valor(self):
        if not self.current_atributo: return
        
        try:
            if self.current_atributo.nombre.lower() == 'color':
                nombre = self.input_nombre_color.text()
                if not nombre: raise ValueError("El nombre del color es obligatorio.")
                self.controller.agregar_valor_a_atributo(self.current_atributo.id, nombre, self.selected_hex_color)
                self.input_nombre_color.clear()
            else:
                valor = self.input_nuevo_valor_simple.text()
                self.controller.agregar_valor_a_atributo(self.current_atributo.id, valor)
                self.input_nuevo_valor_simple.clear()
            
            self._cargar_lista_atributos()
            for i in range(self.lista_atributos.count()):
                item = self.lista_atributos.item(i)
                if item.data(Qt.ItemDataRole.UserRole).id == self.current_atributo.id:
                    item.setSelected(True)
                    break
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _editar_valor(self):
        items = self.lista_valores.selectedItems()
        if not items:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un valor para editar.")
            return
            
        valor_obj = items[0].data(Qt.ItemDataRole.UserRole)
        
        if self.current_atributo.nombre.lower() == 'color':
            nuevo_nombre, ok = QInputDialog.getText(self, "Editar Nombre del Color", "Nuevo nombre:", text=valor_obj.valor)
            if ok and nuevo_nombre:
                self.controller.actualizar_valor(valor_obj.id, nuevo_nombre, valor_obj.codigo_color) # Se podría añadir opción para cambiar color también
                self._on_atributo_seleccionado()
        else:
            nuevo_valor, ok = QInputDialog.getText(self, "Editar Valor", "Nuevo valor:", text=valor_obj.valor)
            if ok and nuevo_valor:
                self.controller.actualizar_valor(valor_obj.id, nuevo_valor)
                self._on_atributo_seleccionado() 

    def _eliminar_valor(self):
        items = self.lista_valores.selectedItems()
        if not items:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un valor para eliminar.")
            return

        valor_obj = items[0].data(Qt.ItemDataRole.UserRole)
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Seguro que quieres eliminar el valor '{valor_obj.valor}'?")
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_valor(valor_obj.id)
                self._on_atributo_seleccionado()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
    
    # Métodos de Atributos sin cambios
    def _agregar_atributo(self):
        nombre, ok = QInputDialog.getText(self, "Agregar Atributo", "Nombre del nuevo atributo:")
        if ok and nombre:
            try:
                self.controller.crear_atributo(nombre)
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _editar_atributo(self):
        if not self.current_atributo:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un atributo para editar.")
            return

        nuevo_nombre, ok = QInputDialog.getText(self, "Editar Atributo", "Nuevo nombre:", text=self.current_atributo.nombre)
        if ok and nuevo_nombre:
            try:
                self.controller.actualizar_atributo(self.current_atributo.id, nuevo_nombre)
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _eliminar_atributo(self):
        if not self.current_atributo:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un atributo para eliminar.")
            return

        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Seguro que quieres eliminar el atributo '{self.current_atributo.nombre}' y todos sus valores? Esta acción no se puede deshacer.")
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_atributo(self.current_atributo.id)
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))