# src/modules/ventas/producto_selection_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QComboBox, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal
from typing import List, Optional

from modules.productos.producto_controller import ProductoController
from modules.categorias.categoria_controller import CategoriaController
from modules.productos.models import Producto, ProductoPlantilla

class ProductoSelectionDialog(QDialog):
    producto_seleccionado = Signal(Producto)

    def __init__(self, producto_ctrl: ProductoController, categoria_ctrl: CategoriaController, parent=None):
        super().__init__(parent)
        self.producto_controller = producto_ctrl
        self.categoria_controller = categoria_ctrl
        
        self.setWindowTitle("Seleccionar Producto para la Venta")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        self._setup_ui()
        self._cargar_categorias()
        self._actualizar_lista_productos()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        filter_layout = QHBoxLayout()
        self.combo_categorias = QComboBox()
        self.combo_categorias.addItem("Todas las categorías", userData=None)
        
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre o SKU...")
        
        filter_layout.addWidget(self.combo_categorias, 1)
        filter_layout.addWidget(self.input_busqueda, 2)
        layout.addLayout(filter_layout)
        
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels(["SKU", "Producto", "Precio", "Stock"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_productos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_productos.doubleClicked.connect(self._aceptar_seleccion)
        layout.addWidget(self.tabla_productos)
        
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._aceptar_seleccion)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.combo_categorias.currentIndexChanged.connect(self._actualizar_lista_productos)
        self.input_busqueda.textChanged.connect(self._actualizar_lista_productos)

    def _cargar_categorias(self):
        categorias = self.categoria_controller.obtener_todas_las_categorias()
        for cat in sorted(categorias, key=lambda x: x.nombre):
            self.combo_categorias.addItem(cat.nombre, userData=cat.id)

    def _actualizar_lista_productos(self):
        filtro_texto = self.input_busqueda.text()
        cat_id = self.combo_categorias.currentData()
        
        productos_raw = self.producto_controller.listar_todas_las_variantes(filtro=filtro_texto)
        
        productos_filtrados = []
        if cat_id is not None:
            # Si se selecciona una categoría, filtramos los productos
            ids_categorias_hijas = self.categoria_controller._get_all_child_category_ids(cat_id)
            for p in productos_raw:
                if p.plantilla.categoria_id in ids_categorias_hijas:
                    productos_filtrados.append(p)
        else:
            productos_filtrados = productos_raw

        self.tabla_productos.setRowCount(len(productos_filtrados))
        for row, p in enumerate(productos_filtrados):
            item_sku = QTableWidgetItem(p.sku)
            item_sku.setData(Qt.ItemDataRole.UserRole, p)
            self.tabla_productos.setItem(row, 0, item_sku)

            nombre_variante = " / ".join(v.valor for v in p.valores)
            nombre_display = f"{p.plantilla.nombre} ({nombre_variante})" if nombre_variante else p.plantilla.nombre
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(nombre_display))
            
            self.tabla_productos.setItem(row, 2, QTableWidgetItem(f"${p.precio_venta:,.2f}"))
            self.tabla_productos.setItem(row, 3, QTableWidgetItem(str(p.stock)))

    def _aceptar_seleccion(self):
        selected_items = self.tabla_productos.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un producto de la lista.")
            return
            
        producto_obj = self.tabla_productos.item(selected_items[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        self.producto_seleccionado.emit(producto_obj)
        self.accept()