# src/modules/productos/producto_editor_dialog.py

import os
from itertools import product
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QComboBox,
    QTabWidget, QWidget, QListWidget, QListWidgetItem, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QFileDialog, QSpinBox
)
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor
from PySide6.QtCore import Qt, QSize
from typing import Optional, List, Dict, Set

from modules.proveedores.proveedor_model import Proveedor
from modules.categorias.categoria_model import Categoria
from modules.variantes.variantes_model import Atributo, AtributoValor
from .models import ProductoPlantilla, ProductoImagen, Producto
from .producto_controller import ProductoController
from .plantilla_controller import PlantillaController

class ProductoEditorDialog(QDialog):
    def __init__(self, proveedores: List[Proveedor], categorias: List[Categoria], atributos: List[Atributo], producto_controller: ProductoController, plantilla_controller: PlantillaController, mode: str = "variantes", plantilla_a_editar: Optional[ProductoPlantilla] = None, parent=None):
        super().__init__(parent)
        
        self.proveedores = proveedores
        self.categorias_raiz = categorias
        self.atributos = atributos
        self.producto_controller = producto_controller
        self.plantilla_controller = plantilla_controller 
        self.plantilla_existente = plantilla_a_editar
        
        self.mode = "edit" if self.plantilla_existente else mode
        
        self.atributos_seleccionados: Dict[int, Set[int]] = {} 
        self.mapa_valores: Dict[int, AtributoValor] = {val.id: val for attr in atributos for val in attr.valores}
        
        self.imagenes_a_agregar = []
        self.imagenes_a_eliminar = []

        titulo = self._determinar_titulo()
        self.setWindowTitle(titulo)
        self.setMinimumSize(900, 600)
        self.setModal(True)

        self._setup_ui()
        if self.plantilla_existente:
            self._cargar_datos_existentes()

    def _agregar_componente_al_kit(self):
        item_seleccionado = self.lista_resultados_comp.currentItem()
        if not item_seleccionado: return
        variante = item_seleccionado.data(Qt.ItemDataRole.UserRole)
        for row in range(self.tabla_componentes.rowCount()):
            if self.tabla_componentes.item(row, 0).data(Qt.ItemDataRole.UserRole) == variante.id:
                return
        row = self.tabla_componentes.rowCount()
        self.tabla_componentes.insertRow(row)

        self.tabla_componentes.setRowHeight(row, 40)

        item_sku = QTableWidgetItem(variante.sku)
        item_sku.setData(Qt.ItemDataRole.UserRole, variante.id)
        nombre_variante = " / ".join(sorted([v.valor for v in variante.valores]))
        texto_item = f"{variante.plantilla.nombre} ({nombre_variante})" if nombre_variante else variante.plantilla.nombre
        item_nombre = QTableWidgetItem(texto_item)
        spin_cantidad = QSpinBox()
        spin_cantidad.setMinimum(1)
        spin_cantidad.setMaximum(9999)
        self.tabla_componentes.setItem(row, 0, item_sku)
        self.tabla_componentes.setItem(row, 1, item_nombre)
        self.tabla_componentes.setCellWidget(row, 2, spin_cantidad)

    def _cargar_datos_existentes(self):
        if not self.plantilla_existente: return
        
        self.input_nombre_plantilla.setText(self.plantilla_existente.nombre)
        
        cat_index = self.combo_categorias.findData(self.plantilla_existente.categoria_id)
        if cat_index != -1: self.combo_categorias.setCurrentIndex(cat_index)
        
        prov_index = self.combo_proveedores.findData(self.plantilla_existente.proveedor_id)
        if prov_index != -1: self.combo_proveedores.setCurrentIndex(prov_index)
        
        if self.plantilla_existente.componentes:
            self.grupo_simple_producto.setVisible(True)
            if self.plantilla_existente.variantes:
                variante_kit = self.plantilla_existente.variantes[0]
                self.input_sku_simple.setText(variante_kit.sku)
                self.input_precio_simple.setText(f"{variante_kit.precio_venta:.2f}")
                self.input_costo_simple.setText(f"{variante_kit.costo_compra:.2f}" if variante_kit.costo_compra is not None else "0.00")
                
                stock_calculado = self.plantilla_controller.calcular_stock_disponible_kit(self.plantilla_existente.id)
                self.input_stock_simple.setText(str(stock_calculado))
                self.input_stock_simple.setReadOnly(True)
                self.input_stock_simple.setToolTip("El stock de los kits es virtual y se calcula automáticamente en base al stock de sus componentes.")

            for comp in self.plantilla_existente.componentes:
                row = self.tabla_componentes.rowCount()
                self.tabla_componentes.insertRow(row)
                self.tabla_componentes.setRowHeight(row, 40)
                item_sku = QTableWidgetItem(comp.componente.sku)
                item_sku.setData(Qt.ItemDataRole.UserRole, comp.componente.id)
                nombre_variante = " / ".join(sorted([v.valor for v in comp.componente.valores]))
                texto_item = f"{comp.componente.plantilla.nombre} ({nombre_variante})" if nombre_variante else comp.componente.plantilla.nombre
                item_nombre = QTableWidgetItem(texto_item)
                spin_cantidad = QSpinBox()
                spin_cantidad.setMinimum(1)
                spin_cantidad.setMaximum(9999)
                spin_cantidad.setValue(comp.cantidad)
                self.tabla_componentes.setItem(row, 0, item_sku)
                self.tabla_componentes.setItem(row, 1, item_nombre)
                self.tabla_componentes.setCellWidget(row, 2, spin_cantidad)
        else:
            es_simple = len(self.plantilla_existente.variantes) == 1 and not self.plantilla_existente.variantes[0].valores
            if es_simple:
                 variante_simple = self.plantilla_existente.variantes[0]
                 self.input_sku_simple.setText(variante_simple.sku)
                 self.input_precio_simple.setText(f"{variante_simple.precio_venta:.2f}")
                 self.input_costo_simple.setText(f"{variante_simple.costo_compra:.2f}" if variante_simple.costo_compra is not None else "0.00")
                 self.input_stock_simple.setText(str(variante_simple.stock))
                 self.input_stock_simple.setReadOnly(True)
                 self.input_stock_simple.setToolTip("El stock se modifica desde 'Ajustar Stock'.")

            else:
                for variante in self.plantilla_existente.variantes:
                    for valor in variante.valores:
                        if valor.atributo_id not in self.atributos_seleccionados:
                            self.atributos_seleccionados[valor.atributo_id] = set()
                        self.atributos_seleccionados[valor.atributo_id].add(valor.id)
                for i in range(self.lista_atributos.count()):
                    item = self.lista_atributos.item(i)
                    atributo = item.data(Qt.ItemDataRole.UserRole)
                    if atributo.id in self.atributos_seleccionados:
                        item.setCheckState(Qt.CheckState.Checked)
                self._poblar_matriz_con_existentes()
        
        self._actualizar_galeria()
    
    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab_general = self._crear_tab_general()
        self.tab_atributos = self._crear_tab_atributos()
        self.tab_variantes = self._crear_tab_variantes()
        self.tab_componentes = self._crear_tab_componentes()
        self.tab_galeria = self._crear_tab_galeria()
        self.tabs.addTab(self.tab_general, "Información General")
        self.tabs.addTab(self.tab_atributos, "Atributos y Opciones")
        self.tabs.addTab(self.tab_variantes, "Generación de Variantes")
        self.tabs.addTab(self.tab_componentes, "Componentes del Kit")
        self.tabs.addTab(self.tab_galeria, "Galería de Imágenes")
        if self.mode == "simple":
            self.tabs.setTabVisible(1, False)
            self.tabs.setTabVisible(2, False)
            self.tabs.setTabVisible(3, False)
            self.grupo_simple_producto.setVisible(True)
        elif self.mode == "kit":
            self.tabs.setTabVisible(1, False)
            self.tabs.setTabVisible(2, False)
            self.grupo_simple_producto.setVisible(True)
        elif self.mode == "variants":
            self.tabs.setTabVisible(3, False)
        elif self.mode == "edit":
            if self.plantilla_existente.componentes: 
                self.tabs.setTabVisible(1, False)
                self.tabs.setTabVisible(2, False)
            else: 
                self.tabs.setTabVisible(3, False)
                if len(self.plantilla_existente.variantes) == 1 and not self.plantilla_existente.variantes[0].valores:
                    self.tabs.setTabVisible(1, False)
                    self.tabs.setTabVisible(2, False)
                    self.grupo_simple_producto.setVisible(True)
        layout_principal.addWidget(self.tabs)
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_guardar = QPushButton("💾 Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_guardar.clicked.connect(self.accept)
        self.boton_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.boton_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        layout_principal.addLayout(botones_layout)

    def _crear_tab_general(self) -> QWidget:
        widget = QWidget()
        layout_principal_tab = QVBoxLayout(widget)
        info_general_group = QGroupBox("Información del Producto")
        form_layout = QFormLayout(info_general_group)
        self.input_nombre_plantilla = QLineEdit()
        self.combo_categorias = QComboBox()
        self.combo_proveedores = QComboBox()
        form_layout.addRow("Nombre del Producto:", self.input_nombre_plantilla)
        form_layout.addRow("Categoría:", self.combo_categorias)
        form_layout.addRow("Proveedor Principal:", self.combo_proveedores)
        layout_principal_tab.addWidget(info_general_group)
        self.grupo_simple_producto = QGroupBox("Datos del Producto (SKU, Precios y Stock)")
        layout_simple = QFormLayout(self.grupo_simple_producto)
        self.input_sku_simple = QLineEdit()
        self.input_precio_simple = QLineEdit("0.00")
        self.input_costo_simple = QLineEdit("0.00")
        self.input_stock_simple = QLineEdit("0")
        layout_simple.addRow("SKU (Código Interno):", self.input_sku_simple)
        layout_simple.addRow("Costo de Compra:", self.input_costo_simple)
        layout_simple.addRow("Precio de Venta:", self.input_precio_simple)
        layout_simple.addRow("Stock Inicial:", self.input_stock_simple)
        self.grupo_simple_producto.setVisible(False)
        layout_principal_tab.addWidget(self.grupo_simple_producto)
        layout_principal_tab.addStretch()
        self._poblar_combo_categorias()
        self._poblar_combo_proveedores()
        return widget
        
    def _crear_tab_atributos(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        grupo_atributos = QGroupBox("Atributos Disponibles")
        layout_atributos = QVBoxLayout(grupo_atributos)
        self.lista_atributos = QListWidget()
        self.lista_atributos.itemChanged.connect(self._on_atributo_check_changed)
        self.lista_atributos.currentItemChanged.connect(self._on_atributo_selection_changed)
        for atributo in self.atributos:
            item = QListWidgetItem(atributo.nombre)
            item.setData(Qt.ItemDataRole.UserRole, atributo)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista_atributos.addItem(item)
        layout_atributos.addWidget(self.lista_atributos)
        self.grupo_valores = QGroupBox("Valores del Atributo")
        layout_valores = QVBoxLayout(self.grupo_valores)
        self.lista_valores = QListWidget()
        self.lista_valores.itemChanged.connect(self._on_valor_check_changed)
        layout_valores.addWidget(self.lista_valores)
        self.grupo_valores.setEnabled(False) 
        layout.addWidget(grupo_atributos, 1)
        layout.addWidget(self.grupo_valores, 1)
        return widget
        
    def _crear_tab_variantes(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        btn_generar = QPushButton("🚀 Generar / Actualizar Variantes")
        btn_generar.clicked.connect(self._generar_matriz_variantes)
        layout.addWidget(btn_generar, 0, Qt.AlignmentFlag.AlignRight)
        self.tabla_variantes = QTableWidget()
        self.tabla_variantes.setColumnCount(6)
        header_label = "Stock" if self.mode == "edit" else "Stock Inicial"
        self.tabla_variantes.setHorizontalHeaderLabels(["Activar", "Variante", "SKU", "Costo de Compra", "Precio de Venta", header_label])
        header = self.tabla_variantes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_variantes.setAlternatingRowColors(True)
        layout.addWidget(self.tabla_variantes)
        return widget

    def _crear_tab_componentes(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        panel_busqueda = QGroupBox("Añadir Componente")
        layout_busqueda = QVBoxLayout(panel_busqueda)
        self.input_busqueda_comp = QLineEdit()
        self.input_busqueda_comp.setPlaceholderText("Buscar por SKU o nombre...")
        self.input_busqueda_comp.textChanged.connect(self._buscar_componentes)
        self.lista_resultados_comp = QListWidget()
        btn_agregar_comp = QPushButton("Añadir Seleccionado al Kit →")
        btn_agregar_comp.clicked.connect(self._agregar_componente_al_kit)
        layout_busqueda.addWidget(self.input_busqueda_comp)
        layout_busqueda.addWidget(self.lista_resultados_comp)
        layout_busqueda.addWidget(btn_agregar_comp)
        panel_componentes = QGroupBox("Componentes Actuales del Kit")
        layout_componentes = QVBoxLayout(panel_componentes)
        self.tabla_componentes = QTableWidget()
        self.tabla_componentes.setColumnCount(3)
        self.tabla_componentes.setHorizontalHeaderLabels(["SKU", "Producto", "Cantidad"])
        self.tabla_componentes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        btn_quitar_comp = QPushButton("Quitar Componente Seleccionado")
        btn_quitar_comp.clicked.connect(self._quitar_componente_del_kit)
        layout_componentes.addWidget(self.tabla_componentes)
        layout_componentes.addWidget(btn_quitar_comp)
        layout.addWidget(panel_busqueda, 1)
        layout.addWidget(panel_componentes, 2)
        return widget

    def _crear_tab_galeria(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.galeria_widget = QListWidget()
        self.galeria_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.galeria_widget.setIconSize(QSize(128, 128))
        self.galeria_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.galeria_widget.setMovement(QListWidget.Movement.Static)
        layout.addWidget(self.galeria_widget)
        botones_galeria_layout = QHBoxLayout()
        boton_agregar_img = QPushButton("➕ Agregar Imágenes...")
        boton_eliminar_img = QPushButton("❌ Eliminar Seleccionada")
        boton_agregar_img.clicked.connect(self._agregar_imagenes)
        boton_eliminar_img.clicked.connect(self._eliminar_imagen_seleccionada)
        botones_galeria_layout.addStretch()
        botones_galeria_layout.addWidget(boton_agregar_img)
        botones_galeria_layout.addWidget(boton_eliminar_img)
        layout.addLayout(botones_galeria_layout)
        return widget
    
    def _poblar_combo_proveedores(self):
        self.combo_proveedores.addItem("Sin Proveedor", userData=None)
        for prov in self.proveedores:
            self.combo_proveedores.addItem(prov.nombre_empresa, userData=prov.id)
            
    def _poblar_combo_categorias(self):
        self.combo_categorias.addItem("Sin Categoría", userData=None)
        for cat in self.categorias_raiz:
            self._poblar_categorias_recursivo(cat, 1)
            
    def _poblar_categorias_recursivo(self, categoria: Categoria, indent_level: int):
        self.combo_categorias.addItem(f"{'—' * (indent_level - 1)} {categoria.nombre}", userData=categoria.id)
        for sub_cat in sorted(categoria.subcategorias, key=lambda x: x.nombre):
            self._poblar_categorias_recursivo(sub_cat, indent_level + 1)
            
    def _buscar_componentes(self):
        filtro = self.input_busqueda_comp.text()
        self.lista_resultados_comp.clear()
        if len(filtro) < 1: return
        resultados = self.producto_controller.listar_todas_las_variantes(filtro)
        for variante in resultados:
            if self.plantilla_existente and self.plantilla_existente.id == variante.plantilla_id:
                continue
            nombre_variante = " / ".join(sorted([v.valor for v in variante.valores]))
            texto_item = f"{variante.plantilla.nombre} ({nombre_variante})" if nombre_variante else variante.plantilla.nombre
            item = QListWidgetItem(f"{variante.sku} - {texto_item}")
            item.setData(Qt.ItemDataRole.UserRole, variante)
            self.lista_resultados_comp.addItem(item)
            
    def _quitar_componente_del_kit(self):
        fila_seleccionada = self.tabla_componentes.currentRow()
        if fila_seleccionada >= 0:
            self.tabla_componentes.removeRow(fila_seleccionada)

    def _determinar_titulo(self) -> str:
        if self.plantilla_existente: return "Editar Producto"
        if self.mode == "simple": return "Agregar Producto Simple"
        if self.mode == "kit": return "Agregar Nuevo Kit"
        return "Asistente para Nuevo Producto con Variantes"

    def _poblar_matriz_con_existentes(self):
        variantes_existentes = sorted(self.plantilla_existente.variantes, key=lambda v: v.id)
        self.tabla_variantes.setRowCount(len(variantes_existentes))
        input_style = "QLineEdit { padding: 4px; }"
        for row, variante in enumerate(variantes_existentes):
            self.tabla_variantes.setRowHeight(row, 40)
            chk_activar = QCheckBox()
            chk_activar.setChecked(True)
            chk_activar.setStyleSheet("margin-left: 20px;")
            self.tabla_variantes.setCellWidget(row, 0, chk_activar)
            nombres_valores = sorted([v.valor for v in variante.valores])
            nombre_variante = " / ".join(nombres_valores)
            item_variante = QTableWidgetItem(nombre_variante)
            item_variante.setData(Qt.ItemDataRole.UserRole, tuple(sorted([v.id for v in variante.valores])))
            self.tabla_variantes.setItem(row, 1, item_variante)
            input_sku = QLineEdit(variante.sku)
            input_sku.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 2, input_sku)
            input_costo = QLineEdit(f"{variante.costo_compra:.2f}" if variante.costo_compra is not None else "0.00")
            input_costo.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 3, input_costo)
            input_precio = QLineEdit(f"{variante.precio_venta:.2f}")
            input_precio.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 4, input_precio)
            input_stock = QLineEdit(str(variante.stock))
            input_stock.setStyleSheet(input_style)
            input_stock.setProperty("variante_id", variante.id)
            if self.mode == 'edit':
                input_stock.setReadOnly(True)
                input_stock.setToolTip("El stock de variantes existentes se debe modificar desde el diálogo de 'Ajustar Stock'.")
            self.tabla_variantes.setCellWidget(row, 5, input_stock)

    def _actualizar_galeria(self):
        self.galeria_widget.clear()
        if self.plantilla_existente:
            for img_obj in self.plantilla_existente.imagenes: 
                if img_obj not in self.imagenes_a_eliminar and os.path.exists(img_obj.ruta_imagen):
                    item = QListWidgetItem(QIcon(img_obj.ruta_imagen), "")
                    item.setData(Qt.ItemDataRole.UserRole, img_obj)
                    self.galeria_widget.addItem(item)
        for ruta_nueva in self.imagenes_a_agregar:
            item = QListWidgetItem(QIcon(ruta_nueva), "(Nueva)")
            item.setData(Qt.ItemDataRole.UserRole, ruta_nueva)
            self.galeria_widget.addItem(item)

    def _agregar_imagenes(self):
        rutas_archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar Imágenes", "", "Imágenes (*.png *.jpg *.jpeg)")
        if rutas_archivos:
            self.imagenes_a_agregar.extend(rutas_archivos)
            self._actualizar_galeria()

    def _eliminar_imagen_seleccionada(self):
        items_seleccionados = self.galeria_widget.selectedItems()
        if not items_seleccionados: return
        item = items_seleccionados[0]
        data = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(data, ProductoImagen):
            if data not in self.imagenes_a_eliminar:
                self.imagenes_a_eliminar.append(data)
        elif isinstance(data, str):
            if data in self.imagenes_a_agregar:
                self.imagenes_a_agregar.remove(data)
        self._actualizar_galeria()
        
    def obtener_datos_finales(self) -> Optional[Dict]:
        datos_plantilla = {
            "nombre": self.input_nombre_plantilla.text().strip(),
            "descripcion": "", 
            "categoria_id": self.combo_categorias.currentData(),
            "proveedor_id": self.combo_proveedores.currentData(),
            "imagenes_a_agregar": self.imagenes_a_agregar,
            "imagenes_a_eliminar": self.imagenes_a_eliminar
        }
        if not datos_plantilla["nombre"]:
            QMessageBox.warning(self, "Información Requerida", "El nombre del producto es obligatorio.")
            return None
            
        lista_variantes = []
        es_kit_en_edicion = self.mode == 'edit' and self.plantilla_existente and self.plantilla_existente.componentes
        es_simple_en_edicion = self.mode == 'edit' and not es_kit_en_edicion and len(self.plantilla_existente.variantes) == 1 and not self.plantilla_existente.variantes[0].valores

        if self.mode in ["simple", "kit"] or es_simple_en_edicion or es_kit_en_edicion:
            sku = self.input_sku_simple.text().strip()
            precio_str = self.input_precio_simple.text().strip()
            costo_str = self.input_costo_simple.text().strip()
            stock_str = self.input_stock_simple.text().strip()

            if not sku:
                QMessageBox.warning(self, "Dato Obligatorio", "El SKU es obligatorio.")
                return None
            try:
                precio_float = float(precio_str)
                costo_float = float(costo_str) if costo_str else None
                stock_int = 0 if self.mode == "kit" or es_kit_en_edicion else int(stock_str)
            except (ValueError, TypeError):
                QMessageBox.warning(self, "Dato Inválido", "El precio, costo y stock deben ser números.")
                return None
            
            variante_id = self.plantilla_existente.variantes[0].id if (es_simple_en_edicion or es_kit_en_edicion) else None
            lista_variantes.append({
                "id": variante_id, "sku": sku, "precio_venta": precio_float, "stock": stock_int, 
                "costo_compra": costo_float, "ids_valores": []
            })
        else: 
            for row in range(self.tabla_variantes.rowCount()):
                chk_activar = self.tabla_variantes.cellWidget(row, 0)
                if chk_activar and chk_activar.isChecked():
                    item_variante = self.tabla_variantes.item(row, 1)
                    ids_valores = item_variante.data(Qt.ItemDataRole.UserRole)
                    sku = self.tabla_variantes.cellWidget(row, 2).text().strip()
                    costo_str = self.tabla_variantes.cellWidget(row, 3).text().strip()
                    precio_str = self.tabla_variantes.cellWidget(row, 4).text().strip()
                    stock_widget = self.tabla_variantes.cellWidget(row, 5)
                    stock_str = stock_widget.text().strip()
                    variante_id = stock_widget.property("variante_id")

                    if not sku:
                        QMessageBox.warning(self, "Dato Requerido", f"El SKU es obligatorio para la variante '{item_variante.text()}'.")
                        return None
                    try:
                        precio_float = float(precio_str)
                        stock_int = int(stock_str)
                        costo_float = float(costo_str) if costo_str else None
                    except (ValueError, TypeError):
                        QMessageBox.warning(self, "Dato Inválido", f"El precio, costo y stock deben ser números para la variante '{item_variante.text()}'.")
                        return None
                    
                    datos_una_variante = {
                        "id": variante_id, "sku": sku, "precio_venta": precio_float, "stock": stock_int,
                        "costo_compra": costo_float, "ids_valores": ids_valores
                    }
                    lista_variantes.append(datos_una_variante)
        
        datos_completos = {"plantilla": datos_plantilla, "variantes": lista_variantes}
        if self.mode == "kit" or (self.plantilla_existente and self.plantilla_existente.componentes):
            componentes = []
            for row in range(self.tabla_componentes.rowCount()):
                componente_id = self.tabla_componentes.item(row, 0).data(Qt.ItemDataRole.UserRole)
                cantidad = self.tabla_componentes.cellWidget(row, 2).value()
                componentes.append({"componente_id": componente_id, "cantidad": cantidad})
            if not componentes:
                QMessageBox.warning(self, "Componentes Requeridos", "Un kit debe tener al menos un componente.")
                return None
            datos_completos["componentes"] = componentes
            
        if not lista_variantes:
            QMessageBox.warning(self, "Variantes Requeridas", "Debes configurar al menos una variante activa.")
            return None
            
        return datos_completos
        
    def _generar_matriz_variantes(self):
        nombre_plantilla_base = self.input_nombre_plantilla.text().strip()
        if not nombre_plantilla_base:
            QMessageBox.warning(self, "Información Requerida", "Por favor, define un nombre para el producto en la Pestaña 1.")
            return
        atributos_con_valores = { attr_id: sorted(list(val_ids)) for attr_id, val_ids in self.atributos_seleccionados.items() if val_ids }
        if not atributos_con_valores:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona al menos un atributo y un valor en la Pestaña 2.")
            return
        grupos_de_valores = list(atributos_con_valores.values())
        combinaciones = list(product(*grupos_de_valores))
        datos_existentes = {}
        for row in range(self.tabla_variantes.rowCount()):
            item_variante = self.tabla_variantes.item(row, 1)
            combo_ids = item_variante.data(Qt.ItemDataRole.UserRole)
            if combo_ids:
                datos_existentes[combo_ids] = {
                    "sku": self.tabla_variantes.cellWidget(row, 2).text(),
                    "costo": self.tabla_variantes.cellWidget(row, 3).text(),
                    "precio": self.tabla_variantes.cellWidget(row, 4).text(),
                    "stock": self.tabla_variantes.cellWidget(row, 5).text(),
                    "id": self.tabla_variantes.cellWidget(row, 5).property("variante_id")
                }
        self.tabla_variantes.setRowCount(len(combinaciones))
        input_style = "QLineEdit { padding: 4px; }"
        for row, combo in enumerate(combinaciones):
            self.tabla_variantes.setRowHeight(row, 40)
            combo = tuple(sorted(combo))
            chk_activar = QCheckBox()
            chk_activar.setChecked(True)
            chk_activar.setStyleSheet("margin-left: 20px;")
            self.tabla_variantes.setCellWidget(row, 0, chk_activar)
            nombres_valores = [self.mapa_valores[val_id].valor for val_id in combo]
            nombre_variante = " / ".join(nombres_valores)
            item_variante = QTableWidgetItem(nombre_variante)
            item_variante.setData(Qt.ItemDataRole.UserRole, combo)
            self.tabla_variantes.setItem(row, 1, item_variante)
            datos_previos = datos_existentes.get(combo)
            sku_texto = datos_previos["sku"] if datos_previos else f"{nombre_plantilla_base[:5].upper().replace(' ','-')}-{''.join([n[:2] for n in nombres_valores]).upper()}"
            costo_texto = datos_previos["costo"] if datos_previos else "0.00"
            precio_texto = datos_previos["precio_venta"] if datos_previos else "0.00"
            stock_texto = datos_previos["stock"] if datos_previos else "0"
            variante_id = datos_previos["id"] if datos_previos else None
            input_sku = QLineEdit(sku_texto)
            input_sku.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 2, input_sku)
            input_costo = QLineEdit(costo_texto)
            input_costo.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 3, input_costo)
            input_precio = QLineEdit(precio_texto)
            input_precio.setStyleSheet(input_style)
            self.tabla_variantes.setCellWidget(row, 4, input_precio)
            input_stock = QLineEdit(stock_texto)
            input_stock.setStyleSheet(input_style)
            input_stock.setProperty("variante_id", variante_id)
            if self.mode == 'edit':
                input_stock.setReadOnly(True)
                input_stock.setToolTip("El stock de variantes existentes se debe modificar desde el diálogo de 'Ajustar Stock'.")
            self.tabla_variantes.setCellWidget(row, 5, input_stock)
            
    def _on_atributo_check_changed(self, item: QListWidgetItem):
        atributo = item.data(Qt.ItemDataRole.UserRole)
        is_checked = item.checkState() == Qt.CheckState.Checked
        if is_checked:
            if atributo.id not in self.atributos_seleccionados:
                self.atributos_seleccionados[atributo.id] = set()
        else:
            if atributo.id in self.atributos_seleccionados:
                del self.atributos_seleccionados[atributo.id]
        
    def _on_atributo_selection_changed(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        if not current_item:
            self.grupo_valores.setEnabled(False)
            self.grupo_valores.setTitle("Valores del Atributo")
            self.lista_valores.clear()
            return
        atributo = current_item.data(Qt.ItemDataRole.UserRole)
        self.grupo_valores.setEnabled(True)
        self.grupo_valores.setTitle(f"Valores para '{atributo.nombre}'")
        self._poblar_lista_valores(atributo)
        
    def _poblar_lista_valores(self, atributo: Atributo):
        self.lista_valores.blockSignals(True)
        self.lista_valores.clear()
        valores_seleccionados = self.atributos_seleccionados.get(atributo.id, set())
        for valor in sorted(atributo.valores, key=lambda v: v.valor):
            item = QListWidgetItem(valor.valor)
            item.setData(Qt.ItemDataRole.UserRole, valor)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if valor.codigo_color:
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor(valor.codigo_color))
                item.setIcon(QIcon(pixmap))
            check_state = Qt.CheckState.Checked if valor.id in valores_seleccionados else Qt.CheckState.Unchecked
            item.setCheckState(check_state)
            self.lista_valores.addItem(item)
        self.lista_valores.blockSignals(False)
        
    def _on_valor_check_changed(self, item: QListWidgetItem):
        valor = item.data(Qt.ItemDataRole.UserRole)
        atributo_id = valor.atributo_id
        is_checked = item.checkState() == Qt.CheckState.Checked
        if is_checked:
            if atributo_id in self.atributos_seleccionados:
                self.atributos_seleccionados[atributo_id].add(valor.id)
        else:
            if atributo_id in self.atributos_seleccionados and valor.id in self.atributos_seleccionados[atributo_id]:
                self.atributos_seleccionados[atributo_id].remove(valor.id)
        self._actualizar_estado_tab_variantes()
        
    def _actualizar_estado_tab_variantes(self):
        if self.mode == 'edit':
            self.tabs.setTabEnabled(2, True)
            return
        
        puede_generar = any(valores for valores in self.atributos_seleccionados.values())
        self.tabs.setTabEnabled(2, puede_generar)