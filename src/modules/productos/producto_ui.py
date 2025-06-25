# src/modules/productos/producto_ui.py

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView, QLabel,
    QGroupBox, QFormLayout, QComboBox, QStackedWidget, QFileDialog, QDialog
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt
from typing import Optional, List, Tuple
import pprint

from .plantilla_controller import PlantillaController
from .producto_controller import ProductoController
from .producto_editor_dialog import ProductoEditorDialog
from .tipo_producto_dialog import TipoProductoDialog
from .variantes_stock_dialog import VariantesStockDialog
from .import_assistant_dialog import ImportAssistantDialog

from modules.proveedores.proveedor_controller import ProveedorController
from modules.categorias.categoria_controller import CategoriaController
from modules.variantes.variantes_controller import VariantesController
from .models import ProductoPlantilla
from modules.categorias.categoria_model import Categoria


class ProductoWidget(QWidget):
    def __init__(self, plantilla_ctrl: PlantillaController, producto_ctrl: ProductoController, prov_ctrl: ProveedorController, cat_ctrl: CategoriaController, var_ctrl: VariantesController, usuario, parent=None):
        super().__init__(parent)
        self.plantilla_controller = plantilla_ctrl
        self.producto_controller = producto_ctrl
        self.proveedor_controller = prov_ctrl
        self.categoria_controller = cat_ctrl
        self.variantes_controller = var_ctrl
        self.usuario_logueado = usuario
        self.current_plantilla: Optional[ProductoPlantilla] = None
        self.current_image_index = 0
        self.ids_categorias_visibles = set()
        self._setup_ui()
        self.reset_view()

    def _importar_productos(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(self, "Importar Catálogo desde CSV", "", "Archivos CSV (*.csv)")

        if ruta_archivo:
            try:
                resultado_analisis = self.plantilla_controller.analizar_csv_para_importacion(ruta_archivo)
                
                if not resultado_analisis:
                    QMessageBox.information(self, "Archivo Vacío", "El archivo CSV seleccionado está vacío o no tiene datos.")
                    return

                dialogo_asistente = ImportAssistantDialog(resultado_analisis, self)
                
                if dialogo_asistente.exec() == QDialog.Accepted:
                    filas_para_importar = dialogo_asistente.get_filas_validas()
                    
                    self.plantilla_controller.ejecutar_importacion(filas_para_importar, self.usuario_logueado.id)
                    
                    QMessageBox.information(self, "Éxito", "La importación de productos se ha completado correctamente.")
                    self.reset_view()

            except Exception as e:
                QMessageBox.critical(self, "Error de Importación", f"Ocurrió un error al importar los datos:\n{e}")

    # --- INICIO DE LA MODIFICACIÓN ---
    def _actualizar_lista_plantillas(self):
        """
        Refresca la tabla de productos. Ahora calcula el stock de los kits
        directamente con los datos pre-cargados para máxima eficiencia.
        """
        if not self.isEnabled(): return 
        filtro_texto = self.input_busqueda.text()
        categoria_id_seleccionada = self.combo_categorias.currentData()
        try:
            plantillas = self.plantilla_controller.listar_plantillas(filtro=filtro_texto, categoria_id=categoria_id_seleccionada)
            self.tabla_plantillas.setRowCount(len(plantillas))

            for row, p in enumerate(plantillas):
                stock_total_str = ""
                # Si es un kit, calculamos su stock virtual desde el objeto ya cargado.
                if p.componentes:
                    if not p.componentes:
                        stock_calculado = 0
                    else:
                        kits_posibles = []
                        for item_kit in p.componentes:
                            if not item_kit.componente or item_kit.cantidad <= 0:
                                kits_posibles.append(0)
                                break 
                            
                            stock_componente = item_kit.componente.stock
                            cantidad_necesaria = item_kit.cantidad
                            kits_posibles.append(stock_componente // cantidad_necesaria)
                        
                        stock_calculado = min(kits_posibles) if kits_posibles else 0

                    stock_total_str = f"{stock_calculado}*" # Añadimos un asterisco para indicar que es calculado
                else:
                    # Si no es un kit, sumamos el stock de sus variantes como antes.
                    stock_total = sum(v.stock for v in p.variantes)
                    stock_total_str = str(stock_total)

                item_id = QTableWidgetItem(str(p.id))
                item_id.setData(Qt.ItemDataRole.UserRole, p)
                self.tabla_plantillas.setItem(row, 0, item_id)
                self.tabla_plantillas.setItem(row, 1, QTableWidgetItem(p.nombre))
                self.tabla_plantillas.setItem(row, 2, QTableWidgetItem(p.categoria.nombre if p.categoria else "N/A"))
                self.tabla_plantillas.setItem(row, 3, QTableWidgetItem(stock_total_str))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la lista de productos: {e}")
        
        if not self.tabla_plantillas.selectedItems():
            self._limpiar_panel_detalles()
    # --- FIN DE LA MODIFICACIÓN ---

    def _abrir_editor_plantilla(self, mode: str, plantilla: Optional[ProductoPlantilla] = None):
        try:
            proveedores = self.proveedor_controller.listar_proveedores()
            categorias = self.categoria_controller.listar_categorias_jerarquicamente()
            atributos = self.variantes_controller.listar_atributos()
            dialogo = ProductoEditorDialog(
                proveedores, categorias, atributos, 
                self.producto_controller, 
                self.plantilla_controller,
                mode=mode, 
                plantilla_a_editar=plantilla, 
                parent=self
            )
            if dialogo.exec():
                datos_finales = dialogo.obtener_datos_finales()
                if datos_finales:
                    if plantilla: 
                        self.plantilla_controller.actualizar_plantilla_con_variantes(plantilla_id=plantilla.id, datos_plantilla=datos_finales["plantilla"], lista_variantes_ui=datos_finales["variantes"], componentes=datos_finales.get("componentes", []))
                        QMessageBox.information(self, "Éxito", "Producto actualizado correctamente.")
                    else: 
                        self.plantilla_controller.crear_plantilla_con_variantes(datos_plantilla=datos_finales["plantilla"], lista_variantes=datos_finales["variantes"], usuario_id=self.usuario_logueado.id, componentes=datos_finales.get("componentes", []))
                        QMessageBox.information(self, "Éxito", "Producto creado correctamente.")
                    self.reset_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}\n\nConsulta la consola para más detalles.")
            import traceback
            traceback.print_exc()
            
    # El resto de métodos no cambian y se omiten por brevedad, pero se entregan completos.
    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        titulo = QLabel("Gestión de Productos")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)
        toolbar = self._crear_toolbar()
        layout_principal.addWidget(toolbar)
        contenido_layout = QHBoxLayout()
        panel_central = self._crear_panel_central()
        panel_detalles = self._crear_panel_detalles()
        contenido_layout.addWidget(panel_central, 2)
        contenido_layout.addWidget(panel_detalles, 1)
        layout_principal.addLayout(contenido_layout)
        self._init_connections()
    def _init_connections(self):
        self.btn_agregar.clicked.connect(self._abrir_dialogo_seleccion_tipo)
        self.btn_editar.clicked.connect(self._abrir_dialogo_edicion)
        self.btn_eliminar.clicked.connect(self._eliminar_plantilla)
        self.btn_exportar.clicked.connect(self._exportar_productos)
        self.btn_importar.clicked.connect(self._importar_productos)
        self.btn_ver_variantes.clicked.connect(self._abrir_dialogo_stock_variantes)
        self.btn_img_anterior.clicked.connect(lambda: self._navegar_imagen(-1))
        self.btn_img_siguiente.clicked.connect(lambda: self._navegar_imagen(1))
        self.input_busqueda.textChanged.connect(self._actualizar_lista_plantillas)
        self.combo_categorias.currentIndexChanged.connect(self._actualizar_lista_plantillas)
        self.tabla_plantillas.itemSelectionChanged.connect(self._mostrar_detalles_plantilla)
    def reset_view(self):
        self.input_busqueda.clear()
        self._cargar_categorias_filtradas()
        self.combo_categorias.setCurrentIndex(0)
        self._actualizar_lista_plantillas()
        self._limpiar_panel_detalles()
    def _crear_toolbar(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        self.btn_agregar = QPushButton("➕ Agregar Producto")
        self.btn_editar = QPushButton("✏️ Editar Producto")
        self.btn_eliminar = QPushButton("❌ Eliminar Producto")
        layout.addWidget(self.btn_agregar)
        layout.addWidget(self.btn_editar)
        layout.addWidget(self.btn_eliminar)
        self.btn_importar = QPushButton("📥 Importar desde CSV")
        self.btn_exportar = QPushButton("📄 Exportar a CSV")
        layout.addWidget(self.btn_importar)
        layout.addWidget(self.btn_exportar)
        layout.addStretch()
        self.combo_categorias = QComboBox()
        self.combo_categorias.setMinimumWidth(200)
        layout.addWidget(QLabel("Filtrar por categoría:"))
        layout.addWidget(self.combo_categorias)
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre...")
        layout.addWidget(self.input_busqueda)
        return widget
    def _exportar_productos(self):
        default_path = os.path.join(os.path.expanduser("~"), "Downloads", "catalogo_productos.csv")
        ruta_archivo, _ = QFileDialog.getSaveFileName(self, "Exportar Catálogo a CSV", default_path, "Archivos CSV (*.csv)")
        if ruta_archivo:
            try:
                self.plantilla_controller.exportar_plantillas_a_csv(ruta_archivo)
                QMessageBox.information(self, "Exportación Exitosa", f"El catálogo de productos se ha exportado correctamente en:\n{ruta_archivo}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Exportación", f"Ocurrió un error al exportar el archivo:\n{e}")
    def _crear_panel_central(self) -> QGroupBox:
        grupo = QGroupBox("Productos")
        layout = QVBoxLayout(grupo)
        self.tabla_plantillas = QTableWidget()
        self.tabla_plantillas.setColumnCount(4)
        self.tabla_plantillas.setHorizontalHeaderLabels(["ID", "Nombre del Producto", "Categoría", "Stock Total"])
        self.tabla_plantillas.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_plantillas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_plantillas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_plantillas)
        return grupo
    def _crear_panel_detalles(self) -> QGroupBox:
        grupo = QGroupBox("Detalles del Producto")
        main_layout = QVBoxLayout(grupo)
        self.details_stack = QStackedWidget()
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        self.detalle_imagen_visor = QLabel()
        self.detalle_imagen_visor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detalle_imagen_visor.setMinimumHeight(250)
        self.detalle_imagen_visor.setObjectName("imageDetailViewer")
        nav_layout = QHBoxLayout()
        self.btn_img_anterior = QPushButton("<")
        self.btn_img_siguiente = QPushButton(">")
        nav_layout.addWidget(self.btn_img_anterior)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_img_siguiente)
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detalle_nombre = QLabel()
        self.detalle_nombre.setObjectName("detailTitle")
        self.detalle_nombre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detalle_nombre.setWordWrap(True)
        self.detalle_precio = QLabel()
        self.detalle_precio.setObjectName("detailPrice")
        self.detalle_precio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_precio = QFont(); font_precio.setPointSize(14); self.detalle_precio.setFont(font_precio)
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.detalle_categoria = QLabel()
        self.detalle_proveedor = QLabel()
        form_layout.addRow(QLabel("<b>Categoría:</b>"), self.detalle_categoria)
        form_layout.addRow(QLabel("<b>Proveedor:</b>"), self.detalle_proveedor)
        info_layout.addWidget(self.detalle_nombre)
        info_layout.addWidget(self.detalle_precio)
        info_layout.addSpacing(20)
        info_layout.addWidget(form_container)
        self.btn_ver_variantes = QPushButton("📊 Stock y Variantes")
        layout.addWidget(self.detalle_imagen_visor)
        layout.addLayout(nav_layout)
        layout.addWidget(info_container)
        layout.addStretch()
        layout.addWidget(self.btn_ver_variantes)
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_label = QLabel("Selecciona un producto para ver sus detalles.")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setObjectName("placeholderLabel")
        placeholder_layout.addWidget(placeholder_label)
        self.details_stack.addWidget(placeholder_widget)
        self.details_stack.addWidget(content_widget)
        main_layout.addWidget(self.details_stack)
        return grupo
    def _limpiar_panel_detalles(self):
        self.current_plantilla = None
        self.tabla_plantillas.clearSelection()
        self.details_stack.setCurrentIndex(0)
        self._actualizar_estado_botones()
    def _mostrar_detalles_plantilla(self):
        items = self.tabla_plantillas.selectedItems()
        if not items:
            self._limpiar_panel_detalles()
            return
        self.details_stack.setCurrentIndex(1)
        self.current_plantilla = self.tabla_plantillas.item(items[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not self.current_plantilla: return
        self.detalle_nombre.setText(self.current_plantilla.nombre)
        self.detalle_categoria.setText(self.current_plantilla.categoria.nombre if self.current_plantilla.categoria else "N/A")
        self.detalle_proveedor.setText(self.current_plantilla.proveedor.nombre_empresa if self.current_plantilla.proveedor else "N/A")
        precios = [v.precio_venta for v in self.current_plantilla.variantes if v.precio_venta is not None]
        if not precios: self.detalle_precio.setText("N/A")
        elif len(set(precios)) == 1: self.detalle_precio.setText(f"${precios[0]:,.2f}")
        else:
            min_precio = min(precios)
            max_precio = max(precios)
            self.detalle_precio.setText(f"${min_precio:,.2f} - ${max_precio:,.2f}")
        self.current_image_index = 0
        self._mostrar_imagen_actual()
        self._actualizar_estado_botones()
    def _cargar_categorias_filtradas(self):
        self.combo_categorias.blockSignals(True)
        current_selection = self.combo_categorias.currentData()
        self.combo_categorias.clear()
        self.combo_categorias.addItem("Todas las categorías", userData=None)
        self.ids_categorias_visibles = self.plantilla_controller.get_ids_de_categorias_relevantes()
        categorias_raiz = self.categoria_controller.listar_categorias_jerarquicamente()
        for cat in categorias_raiz:
            self._poblar_combo_recursivo(cat, 0)
        index = self.combo_categorias.findData(current_selection)
        if index != -1: self.combo_categorias.setCurrentIndex(index)
        self.combo_categorias.blockSignals(False)
    def _poblar_combo_recursivo(self, categoria: Categoria, indent_level: int):
        if categoria.id not in self.ids_categorias_visibles: return
        self.combo_categorias.addItem(f"{'   ' * indent_level}{categoria.nombre}", userData=categoria.id)
        for sub_cat in sorted(categoria.subcategorias, key=lambda x: x.nombre):
             self._poblar_combo_recursivo(sub_cat, indent_level + 1)

    def _mostrar_imagen_actual(self):
        if not self.current_plantilla or not self.current_plantilla.imagenes:
            self.detalle_imagen_visor.setText("Sin Imagen")
            self.detalle_imagen_visor.setPixmap(QPixmap())
            self.btn_img_anterior.setVisible(False)
            self.btn_img_siguiente.setVisible(False)
            return
        num_imagenes = len(self.current_plantilla.imagenes)
        self.btn_img_anterior.setVisible(self.current_image_index > 0)
        self.btn_img_siguiente.setVisible(self.current_image_index < num_imagenes - 1)
        ruta_imagen = self.current_plantilla.imagenes[self.current_image_index].ruta_imagen
        if os.path.exists(ruta_imagen):
            pixmap = QPixmap(ruta_imagen)
            self.detalle_imagen_visor.setPixmap(pixmap.scaled(self.detalle_imagen_visor.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.detalle_imagen_visor.setText("Imagen no encontrada")
            self.detalle_imagen_visor.setPixmap(QPixmap())
    def _navegar_imagen(self, direccion: int):
        if not self.current_plantilla: return
        num_imagenes = len(self.current_plantilla.imagenes)
        nuevo_indice = self.current_image_index + direccion
        if 0 <= nuevo_indice < num_imagenes:
            self.current_image_index = nuevo_indice
            self._mostrar_imagen_actual()
    def _actualizar_estado_botones(self):
        hay_seleccion = self.current_plantilla is not None
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)
        self.btn_ver_variantes.setEnabled(hay_seleccion)
        self.btn_exportar.setEnabled(True)
        self.btn_importar.setEnabled(True)
    def _abrir_dialogo_seleccion_tipo(self):
        dialogo_seleccion = TipoProductoDialog(self)
        if dialogo_seleccion.exec():
            modo = dialogo_seleccion.get_selection()
            if modo:
                self._abrir_editor_plantilla(mode=modo)
    def _abrir_dialogo_edicion(self):
        if not self.current_plantilla:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un producto para editar.")
            return
        self._abrir_editor_plantilla(mode="edit", plantilla=self.current_plantilla)
    def _abrir_dialogo_stock_variantes(self):
        if not self.current_plantilla: return
        dialogo = VariantesStockDialog(self.current_plantilla, self.producto_controller, self.usuario_logueado, self)
        dialogo.exec()
        self._actualizar_lista_plantillas()
    def _eliminar_plantilla(self):
        if not self.current_plantilla:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un producto de la lista para eliminar.")
            return
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Estás seguro de eliminar '{self.current_plantilla.nombre}' y todas sus variantes?\n" "Esta acción no se puede deshacer.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.plantilla_controller.eliminar_plantilla(self.current_plantilla.id)
                QMessageBox.information(self, "Éxito", "Producto eliminado.")
                self.reset_view()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))