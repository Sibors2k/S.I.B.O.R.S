# src/modules/proveedores/proveedor_ui.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView, QLabel, QGroupBox, QStackedWidget)
from PySide6.QtCore import Qt
from typing import Optional, List

from .proveedor_controller import ProveedorController
from .proveedor_model import Proveedor
from .proveedor_dialog import ProveedorDialog

# --- INICIO DE LA MODIFICACIÓN ---
# 1. Se corrige la importación para apuntar al nuevo 'models.py'.
# 2. Se importa 'ProductoPlantilla' porque ahora es la relación directa.
from modules.productos.models import Producto, ProductoPlantilla
# --- FIN DE LA MODIFICACIÓN ---

class ProveedorWidget(QWidget):
    def __init__(self, controller: ProveedorController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()
    
    def actualizar_vista(self):
        self._filtrar_tabla()
        self._actualizar_botones()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        titulo = QLabel("Gestión de Proveedores")
        titulo.setObjectName("viewTitle")
        layout.addWidget(titulo)

        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Agregar")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_del = QPushButton("❌ Eliminar")
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_del)
        toolbar.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre, contacto o email...")
        toolbar.addWidget(self.search_input)
        layout.addLayout(toolbar)

        content = QHBoxLayout()
        tabla_grp = QGroupBox("Proveedores")
        tabla_layout = QVBoxLayout(tabla_grp)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre Empresa", "Contacto", "Email"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabla_layout.addWidget(self.tabla)
        content.addWidget(tabla_grp, 2)

        self.stack_detalles = QStackedWidget()
        self.pag_vacia = QLabel("Selecciona un proveedor para ver sus detalles.")
        self.pag_vacia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pag_vacia.setObjectName("placeholderLabel")
        self.pag_detalles = self._crear_panel_detalles()
        self.stack_detalles.addWidget(self.pag_vacia)
        self.stack_detalles.addWidget(self.pag_detalles)
        content.addWidget(self.stack_detalles, 1)
        layout.addLayout(content)

        self.btn_add.clicked.connect(self._abrir_dialogo_agregar)
        self.btn_edit.clicked.connect(self._abrir_dialogo_editar)
        self.btn_del.clicked.connect(self._eliminar_proveedor)
        self.search_input.textChanged.connect(self._filtrar_tabla)
        self.tabla.itemSelectionChanged.connect(self._actualizar_vista_detalle)
        self.actualizar_vista()

    def _crear_panel_detalles(self) -> QWidget:
        widget = QGroupBox("Detalles del Proveedor")
        layout = QVBoxLayout(widget)
        
        self.lbl_nombre_detalle = QLabel()
        self.lbl_nombre_detalle.setObjectName("detailTitle")
        self.lbl_tel = QLabel()
        self.lbl_dir = QLabel()
        self.lbl_web = QLabel()
        
        layout.addWidget(self.lbl_nombre_detalle)
        layout.addWidget(self.lbl_tel)
        layout.addWidget(self.lbl_dir)
        layout.addWidget(self.lbl_web)
        layout.addSpacing(15)

        prod_grp = QGroupBox("Productos Suministrados")
        prod_layout = QVBoxLayout(prod_grp)
        self.tabla_prod = QTableWidget()
        self.tabla_prod.setColumnCount(3)
        self.tabla_prod.setHorizontalHeaderLabels(["SKU", "Producto (Variante)", "Stock Actual"])
        self.tabla_prod.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_prod.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        prod_layout.addWidget(self.tabla_prod)
        layout.addWidget(prod_grp)
        return widget

    def _filtrar_tabla(self):
        try:
            proveedores = self.controller.listar_proveedores(self.search_input.text())
            self.tabla.setRowCount(len(proveedores))
            for row, p in enumerate(proveedores):
                self.tabla.setItem(row, 0, QTableWidgetItem(str(p.id)))
                self.tabla.setItem(row, 1, QTableWidgetItem(p.nombre_empresa))
                self.tabla.setItem(row, 2, QTableWidgetItem(p.persona_contacto or ''))
                self.tabla.setItem(row, 3, QTableWidgetItem(p.email))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar proveedores: {e}")

    def _actualizar_vista_detalle(self):
        prov = self._obtener_proveedor_seleccionado()
        if prov:
            self.lbl_nombre_detalle.setText(prov.nombre_empresa)
            self.lbl_tel.setText(f"<b>Teléfono:</b> {prov.telefono or 'N/A'}")
            self.lbl_dir.setText(f"<b>Dirección:</b> {prov.direccion or 'N/A'}")
            self.lbl_web.setText(f"<b>Sitio Web:</b> {prov.sitio_web or 'N/A'}")
            
            # --- INICIO DE LA MODIFICACIÓN LÓGICA ---
            # 3. La lógica se reescribe para manejar la nueva estructura de datos.
            variantes_del_proveedor: List[Producto] = []
            if prov.plantillas:
                for plantilla in prov.plantillas:
                    variantes_del_proveedor.extend(plantilla.variantes)
            
            self.tabla_prod.setRowCount(len(variantes_del_proveedor))
            for r, variante in enumerate(variantes_del_proveedor):
                nombre_variante = " / ".join(sorted([val.valor for val in variante.valores]))
                nombre_display = f"{variante.plantilla.nombre} ({nombre_variante})" if nombre_variante else variante.plantilla.nombre
                
                self.tabla_prod.setItem(r, 0, QTableWidgetItem(variante.sku))
                self.tabla_prod.setItem(r, 1, QTableWidgetItem(nombre_display))
                self.tabla_prod.setItem(r, 2, QTableWidgetItem(str(variante.stock)))
            # --- FIN DE LA MODIFICACIÓN LÓGICA ---

            self.stack_detalles.setCurrentWidget(self.pag_detalles)
        else:
            self.stack_detalles.setCurrentWidget(self.pag_vacia)
        self._actualizar_botones()

    def _obtener_proveedor_seleccionado(self) -> Optional[Proveedor]:
        items = self.tabla.selectedItems()
        if not items:
            return None
        proveedor_id = int(items[0].text())
        # Usamos el controlador para asegurar que las relaciones estén cargadas.
        # Esto es más robusto que un simple .get() si no se cargaron las relaciones previamente.
        return next((p for p in self.controller.listar_proveedores() if p.id == proveedor_id), None)

    def _actualizar_botones(self):
        sel = self.tabla.selectedItems() is not None and len(self.tabla.selectedItems()) > 0
        self.btn_edit.setEnabled(sel)
        self.btn_del.setEnabled(sel)

    def _abrir_dialogo_agregar(self):
        d = ProveedorDialog(parent=self)
        if d.exec():
            try:
                self.controller.agregar_proveedor(d.obtener_datos())
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar el proveedor: {e}")

    def _abrir_dialogo_editar(self):
        prov = self._obtener_proveedor_seleccionado()
        if not prov:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un proveedor de la tabla.")
            return
        d = ProveedorDialog(proveedor=prov, parent=self)
        if d.exec():
            try:
                self.controller.actualizar_proveedor(prov.id, d.obtener_datos())
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el proveedor: {e}")

    def _eliminar_proveedor(self):
        prov = self._obtener_proveedor_seleccionado()
        if not prov:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un proveedor de la tabla.")
            return
        
        confirm_msg = f"¿Estás seguro de que quieres eliminar al proveedor '{prov.nombre_empresa}'?\nEsta acción no se puede deshacer."
        reply = QMessageBox.question(self, "Confirmar Eliminación", confirm_msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_proveedor(prov.id)
                self.actualizar_vista()
                QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente.")
            except ValueError as e:
                QMessageBox.warning(self, "Acción no permitida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error Inesperado", f"No se pudo eliminar el proveedor: {e}")