# src/modules/compras/compra_ui.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, 
    QAbstractItemView, QLabel, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt
from .compra_controller import CompraController
from modules.proveedores.proveedor_controller import ProveedorController
from modules.productos.producto_controller import ProductoController
from .compra_model import EstadoOrdenCompra

class CompraWidget(QWidget):
    # El código de la clase no cambia, solo la lista de importación.
    # Se incluye completo para cumplir la Regla #2.
    def __init__(self, compra_controller: CompraController, proveedor_controller: ProveedorController, producto_controller: ProductoController, parent=None):
        super().__init__(parent)
        self.controller = compra_controller
        self.proveedor_ctrl = proveedor_controller
        self.producto_ctrl = producto_controller
        self.detalles_orden_actual = []
        self._setup_ui()

    def actualizar_vista(self):
        self._poblar_combos()
        self._cargar_historial_ordenes()
        self._limpiar_formulario_nueva_orden()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        titulo = QLabel("Gestión de Órdenes de Compra")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)
        main_layout = QHBoxLayout()
        panel_izquierdo = self._crear_panel_nueva_orden()
        main_layout.addWidget(panel_izquierdo, 1)
        panel_derecho = self._crear_panel_historial()
        main_layout.addWidget(panel_derecho, 2)
        layout_principal.addLayout(main_layout)

    def _crear_panel_nueva_orden(self) -> QGroupBox:
        grupo = QGroupBox("Nueva Orden de Compra")
        layout = QVBoxLayout(grupo)
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Proveedor:"), 0, 0)
        self.combo_proveedores = QComboBox()
        form_layout.addWidget(self.combo_proveedores, 0, 1)
        form_layout.addWidget(QLabel("Producto:"), 1, 0)
        self.combo_productos = QComboBox()
        form_layout.addWidget(self.combo_productos, 1, 1)
        form_layout.addWidget(QLabel("Cantidad:"), 2, 0)
        self.input_cantidad = QLineEdit("1")
        form_layout.addWidget(self.input_cantidad, 2, 1)
        form_layout.addWidget(QLabel("Costo Unitario:"), 3, 0)
        self.input_costo = QLineEdit()
        self.input_costo.setPlaceholderText("Costo de compra por unidad")
        form_layout.addWidget(self.input_costo, 3, 1)
        boton_agregar_producto = QPushButton("➕ Agregar a la Orden")
        boton_agregar_producto.clicked.connect(self._agregar_detalle_a_orden)
        form_layout.addWidget(boton_agregar_producto, 4, 0, 1, 2)
        layout.addLayout(form_layout)
        self.tabla_nueva_orden = QTableWidget()
        self.tabla_nueva_orden.setColumnCount(4)
        self.tabla_nueva_orden.setHorizontalHeaderLabels(["ID Prod.", "Producto", "Cantidad", "Costo Unit."])
        layout.addWidget(self.tabla_nueva_orden)
        boton_crear_orden = QPushButton("✅ Crear Orden de Compra")
        boton_crear_orden.clicked.connect(self._crear_orden_de_compra)
        layout.addWidget(boton_crear_orden)
        return grupo

    def _crear_panel_historial(self) -> QGroupBox:
        grupo = QGroupBox("Historial de Órdenes")
        layout = QVBoxLayout(grupo)
        self.tabla_historial_ordenes = QTableWidget()
        self.tabla_historial_ordenes.setColumnCount(5)
        self.tabla_historial_ordenes.setHorizontalHeaderLabels(["ID Orden", "Fecha Emisión", "Proveedor", "Total", "Estado"])
        self.tabla_historial_ordenes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_historial_ordenes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_historial_ordenes)
        boton_marcar_recibida = QPushButton("📦 Marcar como Recibida")
        boton_marcar_recibida.clicked.connect(self._marcar_orden_recibida)
        layout.addWidget(boton_marcar_recibida)
        return grupo

    def _poblar_combos(self):
        self.combo_proveedores.clear()
        try:
            for p in self.proveedor_ctrl.listar_proveedores():
                self.combo_proveedores.addItem(p.nombre_empresa, userData=p.id)
        except Exception as e:
            print(f"Error al poblar proveedores: {e}")
        self.combo_productos.clear()
        try:
            for p in self.producto_ctrl.listar_productos():
                self.combo_productos.addItem(f"{p.nombre} (Costo: ${p.costo_compra or 0:.2f})", userData=p.id)
        except Exception as e:
            print(f"Error al poblar productos: {e}")

    def _cargar_historial_ordenes(self):
        try:
            ordenes = self.controller.listar_ordenes_compra()
            self.tabla_historial_ordenes.setRowCount(len(ordenes))
            for row, orden in enumerate(ordenes):
                self.tabla_historial_ordenes.setItem(row, 0, QTableWidgetItem(str(orden.id)))
                self.tabla_historial_ordenes.setItem(row, 1, QTableWidgetItem(orden.fecha_emision.strftime('%Y-%m-%d')))
                self.tabla_historial_ordenes.setItem(row, 2, QTableWidgetItem(orden.proveedor.nombre_empresa if orden.proveedor else "N/A"))
                self.tabla_historial_ordenes.setItem(row, 3, QTableWidgetItem(f"${orden.total:,.2f}"))
                self.tabla_historial_ordenes.setItem(row, 4, QTableWidgetItem(orden.estado.value))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el historial de compras: {e}")

    def _agregar_detalle_a_orden(self):
        producto_id = self.combo_productos.currentData()
        producto_texto = self.combo_productos.currentText()
        if producto_id is None:
            QMessageBox.warning(self, "Error", "Debe seleccionar un producto.")
            return
        try:
            cantidad = int(self.input_cantidad.text())
            costo = float(self.input_costo.text())
            if cantidad <= 0 or costo <= 0: raise ValueError()
        except (ValueError, TypeError):
            QMessageBox.warning(self, "Datos Inválidos", "La cantidad y el costo deben ser números válidos y positivos.")
            return
        self.detalles_orden_actual.append({"producto_id": producto_id, "producto_nombre": producto_texto.split(' (')[0], "cantidad": cantidad, "costo_unitario": costo})
        self._refrescar_tabla_nueva_orden()

    def _refrescar_tabla_nueva_orden(self):
        self.tabla_nueva_orden.setRowCount(len(self.detalles_orden_actual))
        for row, item in enumerate(self.detalles_orden_actual):
            self.tabla_nueva_orden.setItem(row, 0, QTableWidgetItem(str(item["producto_id"])))
            self.tabla_nueva_orden.setItem(row, 1, QTableWidgetItem(item["producto_nombre"]))
            self.tabla_nueva_orden.setItem(row, 2, QTableWidgetItem(str(item["cantidad"])))
            self.tabla_nueva_orden.setItem(row, 3, QTableWidgetItem(f"${item['costo_unitario']:.2f}"))

    def _crear_orden_de_compra(self):
        proveedor_id = self.combo_proveedores.currentData()
        if not self.detalles_orden_actual or proveedor_id is None:
            QMessageBox.warning(self, "Datos Incompletos", "Debe seleccionar un proveedor y agregar al menos un producto a la orden.")
            return
        try:
            detalles_limpios = [{"producto_id": d["producto_id"], "cantidad": d["cantidad"], "costo_unitario": d["costo_unitario"]} for d in self.detalles_orden_actual]
            self.controller.crear_orden_compra(proveedor_id, detalles_limpios)
            QMessageBox.information(self, "Éxito", "Orden de compra creada correctamente.")
            self.actualizar_vista()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear la orden de compra: {e}")

    def _marcar_orden_recibida(self):
        selected_items = self.tabla_historial_ordenes.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona una orden del historial.")
            return
        orden_id = int(self.tabla_historial_ordenes.item(selected_items[0].row(), 0).text())
        confirmacion = QMessageBox.question(self, "Confirmar Recepción", f"¿Estás seguro de que deseas marcar la orden #{orden_id} como recibida?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.marcar_orden_como_recibida(orden_id)
                QMessageBox.information(self, "Éxito", "Orden procesada.")
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo procesar la recepción: {e}")
                
    def _limpiar_formulario_nueva_orden(self):
        self.detalles_orden_actual.clear()
        self._refrescar_tabla_nueva_orden()
        if self.combo_proveedores.count() > 0: self.combo_proveedores.setCurrentIndex(0)
        if self.combo_productos.count() > 0: self.combo_productos.setCurrentIndex(0)
        self.input_cantidad.setText("1")
        self.input_costo.clear()