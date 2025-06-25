# src/modules/categorias/categoria_ui.py

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTreeView, QGroupBox,
    QLineEdit, QPushButton, QMessageBox, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from typing import Optional
from .categoria_controller import CategoriaController
from .categoria_model import Categoria
from .categoria_dialog import CategoriaDialog

class CategoriaWidget(QWidget):
    def __init__(self, categoria_controller: CategoriaController, parent=None):
        super().__init__(parent)
        self.controller = categoria_controller
        self._setup_ui()
        self.actualizar_vista()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        toolbar_widget = self._crear_toolbar()
        layout_principal.addWidget(toolbar_widget)
        contenido_layout = QHBoxLayout()
        panel_izquierdo = self._crear_panel_izquierdo()
        panel_derecho = self._crear_panel_derecho()
        contenido_layout.addWidget(panel_izquierdo, 1)
        contenido_layout.addWidget(panel_derecho, 2)
        layout_principal.addLayout(contenido_layout)

    def actualizar_vista(self):
        self._cargar_categorias()
        self._limpiar_panel_derecho()

    def _crear_toolbar(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.boton_agregar = QPushButton("➕ Agregar Categoría")
        self.boton_editar = QPushButton("✏️ Editar Seleccionada")
        self.boton_eliminar = QPushButton("❌ Eliminar Seleccionada")
        self.boton_agregar.clicked.connect(self._abrir_dialogo_agregar)
        self.boton_editar.clicked.connect(self._abrir_dialogo_editar)
        self.boton_eliminar.clicked.connect(self._eliminar_categoria)
        layout.addWidget(self.boton_agregar)
        layout.addWidget(self.boton_editar)
        layout.addWidget(self.boton_eliminar)
        layout.addStretch()
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar categoría...")
        self.input_busqueda.textChanged.connect(self._filtrar_arbol)
        layout.addWidget(self.input_busqueda)
        return widget

    def _crear_panel_izquierdo(self) -> QGroupBox:
        grupo = QGroupBox("Jerarquía de Categorías")
        layout = QVBoxLayout(grupo)
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.selectionModel().selectionChanged.connect(self._actualizar_panel_derecho)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tree_view)
        return grupo

    def _crear_panel_derecho(self) -> QGroupBox:
        grupo = QGroupBox("Productos en la Categoría Seleccionada")
        layout = QVBoxLayout(grupo)
        self.tabla_productos = QTableWidget()
        # MODIFICADO: Añadimos columna para el tipo de producto
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["ID Plantilla", "Nombre Producto", "Tipo", "Stock Total"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.tabla_productos)
        return grupo

    def _cargar_categorias(self):
        self.tree_model.clear()
        categorias_raiz = self.controller.listar_categorias_jerarquicamente()
        for cat in categorias_raiz:
            item_raiz = QStandardItem(cat.nombre)
            item_raiz.setData(cat, Qt.ItemDataRole.UserRole)
            self.tree_model.appendRow(item_raiz)
            self._poblar_recursivamente(item_raiz, cat)
        self.tree_view.expandAll()

    def _poblar_recursivamente(self, item_padre: QStandardItem, categoria_padre: Categoria):
        for sub_cat in sorted(categoria_padre.subcategorias, key=lambda x: x.nombre):
            item_hijo = QStandardItem(sub_cat.nombre)
            item_hijo.setData(sub_cat, Qt.ItemDataRole.UserRole)
            item_padre.appendRow(item_hijo)
            self._poblar_recursivamente(item_hijo, sub_cat)

    def _obtener_categoria_seleccionada(self) -> Optional[Categoria]:
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
        item = self.tree_model.itemFromIndex(indexes[0])
        return item.data(Qt.ItemDataRole.UserRole)

    def _actualizar_panel_derecho(self):
        categoria = self._obtener_categoria_seleccionada()
        self.tabla_productos.setRowCount(0)
        if not categoria:
            return
            
        # MODIFICADO (Solución #4): Se usa la relación correcta 'plantillas'
        categoria_con_plantillas = self.controller.obtener_categoria_por_id(categoria.id)
        if not categoria_con_plantillas or not categoria_con_plantillas.plantillas:
            return
            
        self.tabla_productos.setRowCount(len(categoria_con_plantillas.plantillas))
        for row, plantilla in enumerate(categoria_con_plantillas.plantillas):
            # Calculamos el stock total sumando el de todas sus variantes
            stock_total = sum(v.stock for v in plantilla.variantes)
            
            # Determinamos el tipo de producto
            if plantilla.componentes:
                tipo = "Kit / Compuesto"
            elif len(plantilla.variantes) > 1:
                tipo = "Con Variantes"
            else:
                tipo = "Simple"

            self.tabla_productos.setItem(row, 0, QTableWidgetItem(str(plantilla.id)))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(plantilla.nombre))
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(tipo))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(stock_total)))

    def _limpiar_panel_derecho(self):
        self.tree_view.clearSelection()
        self.tabla_productos.setRowCount(0)

    def _abrir_dialogo_agregar(self):
        todas_las_categorias = self.controller.obtener_todas_las_categorias()
        dialogo = CategoriaDialog(todas_las_categorias, parent=self)
        if dialogo.exec():
            datos = dialogo.obtener_datos()
            if datos:
                try:
                    self.controller.crear_categoria(datos["nombre"], datos["padre_id"])
                    QMessageBox.information(self, "Éxito", "Categoría creada.")
                    self.actualizar_vista()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def _abrir_dialogo_editar(self):
        categoria_seleccionada = self._obtener_categoria_seleccionada()
        if not categoria_seleccionada:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona una categoría del árbol para editarla.")
            return
        todas_las_categorias = self.controller.obtener_todas_las_categorias()
        dialogo = CategoriaDialog(todas_las_categorias, categoria_a_editar=categoria_seleccionada, parent=self)
        if dialogo.exec():
            datos = dialogo.obtener_datos()
            if datos:
                try:
                    self.controller.actualizar_categoria(categoria_seleccionada.id, datos["nombre"], datos["padre_id"])
                    QMessageBox.information(self, "Éxito", "Categoría actualizada.")
                    self.actualizar_vista()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
    
    def _eliminar_categoria(self):
        categoria_seleccionada = self._obtener_categoria_seleccionada()
        if not categoria_seleccionada:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona una categoría del árbol para eliminarla.")
            return
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                            f"¿Estás seguro de eliminar '{categoria_seleccionada.nombre}'?\n"
                                            "Esto solo funcionará si no tiene subcategorías ni productos asociados.",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_categoria(categoria_seleccionada.id)
                QMessageBox.information(self, "Éxito", "Categoría eliminada.")
                self.actualizar_vista()
            except ValueError as e:
                QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error: {e}")

    def _filtrar_arbol(self, texto: str):
        texto_busqueda = texto.strip().lower()
        root = self.tree_model.invisibleRootItem()
        for i in range(root.rowCount()):
            self._filtrar_item(root.child(i), texto_busqueda)

    def _filtrar_item(self, item: QStandardItem, texto: str) -> bool:
        coincide_item_actual = texto in item.text().lower()
        visible = coincide_item_actual
        for i in range(item.rowCount()):
            hijo = item.child(i)
            if self._filtrar_item(hijo, texto):
                visible = True
        self.tree_view.setRowHidden(item.row(), item.parent().index() if item.parent() else self.tree_model.invisibleRootItem().index(), not visible)
        if not coincide_item_actual and visible:
            self.tree_view.expand(item.index())
        elif not texto:
            self.tree_view.expand(item.index())
        return visible