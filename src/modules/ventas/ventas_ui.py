# src/modules/ventas/ventas_ui.py (v2.2 - Sincronización Forzada)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView, QLabel,
    QGroupBox, QFormLayout, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from modules.ventas.ventas_controller import VentasController
from modules.clientes.cliente_controller import ClienteController
from modules.productos.producto_controller import ProductoController
from modules.categorias.categoria_controller import CategoriaController
from .producto_selection_dialog import ProductoSelectionDialog
from modules.productos.models import Producto

class VentasWidget(QWidget):
    def __init__(self, ventas_ctrl: VentasController, cliente_ctrl: ClienteController, producto_ctrl: ProductoController, categoria_ctrl: CategoriaController, usuario, parent=None):
        super().__init__(parent)
        self.ventas_controller = ventas_ctrl
        self.cliente_controller = cliente_ctrl
        self.producto_controller = producto_ctrl
        self.categoria_controller = categoria_ctrl
        self.usuario_logueado = usuario
        self.current_venta = None
        
        self._setup_ui()
        self.actualizar_vista()

    def actualizar_vista(self):
        """Punto de entrada para refrescar toda la UI. Carga la venta activa y actualiza los componentes."""
        self.current_venta = self.ventas_controller.obtener_venta_activa(self.usuario_logueado.id)
        self._refrescar_carrito()
        self._refrescar_totales()
        self._actualizar_estado_botones()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        carrito_group = self._crear_grupo_carrito()
        left_layout.addWidget(carrito_group)
        right_panel = QWidget()
        right_panel.setFixedWidth(350)
        right_layout = QVBoxLayout(right_panel)
        acciones_group = self._crear_grupo_acciones()
        cliente_group = self._crear_grupo_cliente()
        totales_group = self._crear_grupo_totales()
        right_layout.addWidget(acciones_group)
        right_layout.addWidget(cliente_group)
        right_layout.addWidget(totales_group)
        right_layout.addStretch()
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel)

    def _crear_grupo_carrito(self) -> QGroupBox:
        grupo = QGroupBox("Ticket de Venta Actual")
        layout = QVBoxLayout(grupo)
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["SKU", "Producto", "Cantidad", "Precio Unitario", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_carrito.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_carrito.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla_carrito)
        return grupo
        
    def _crear_grupo_cliente(self) -> QGroupBox:
        grupo = QGroupBox("Cliente")
        layout = QVBoxLayout(grupo)
        self.label_cliente = QLabel("Público General")
        layout.addWidget(self.label_cliente)
        return grupo

    def _crear_grupo_totales(self) -> QGroupBox:
        grupo = QGroupBox("Resumen")
        layout = QFormLayout(grupo)
        self.label_subtotal = QLabel("$0.00")
        self.label_descuentos = QLabel("$0.00")
        self.label_impuestos = QLabel("$0.00")
        self.label_total = QLabel("$0.00")
        font_total = QFont(); font_total.setPointSize(18); font_total.setBold(True)
        self.label_total.setFont(font_total); self.label_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addRow("Subtotal:", self.label_subtotal)
        layout.addRow("Descuentos:", self.label_descuentos)
        layout.addRow("Impuestos:", self.label_impuestos)
        layout.addRow(QLabel("<b>TOTAL:</b>"), self.label_total)
        return grupo

    def _crear_grupo_acciones(self) -> QGroupBox:
        grupo = QGroupBox("Acciones")
        grid_layout = QGridLayout(grupo)
        self.btn_nueva_venta = QPushButton("➕ Nueva Venta")
        self.btn_anadir_producto = QPushButton("📦 Añadir Producto...")
        self.btn_quitar_producto = QPushButton("➖ Quitar Producto")
        self.btn_cancelar_venta = QPushButton("❌ Cancelar Venta")
        self.btn_cobrar = QPushButton("💵 Cobrar")
        self.btn_cobrar.setObjectName("cobrarButton")
        self.btn_nueva_venta.clicked.connect(self._iniciar_nueva_venta)
        self.btn_anadir_producto.clicked.connect(self._abrir_dialogo_seleccion_producto)
        self.btn_quitar_producto.clicked.connect(self._quitar_producto_del_carrito)
        self.btn_cancelar_venta.clicked.connect(self._cancelar_venta_actual)
        self.btn_cobrar.clicked.connect(self._finalizar_venta)
        grid_layout.addWidget(self.btn_nueva_venta, 0, 0)
        grid_layout.addWidget(self.btn_cancelar_venta, 0, 1)
        grid_layout.addWidget(self.btn_anadir_producto, 1, 0)
        grid_layout.addWidget(self.btn_quitar_producto, 1, 1)
        grid_layout.addWidget(self.btn_cobrar, 2, 0, 1, 2)
        return grupo

    def _iniciar_nueva_venta(self):
        self.current_venta = self.ventas_controller.crear_nueva_venta(self.usuario_logueado.id)
        self.actualizar_vista()

    def _refrescar_carrito(self):
        self.tabla_carrito.setRowCount(0)
        if not self.current_venta or not self.current_venta.detalles: return
        detalles_ordenados = sorted(self.current_venta.detalles, key=lambda d: d.id if d.id is not None else -1)
        self.tabla_carrito.setRowCount(len(detalles_ordenados))
        for row, detalle in enumerate(detalles_ordenados):
            p = detalle.producto
            nombre_variante = " / ".join(v.valor for v in p.valores)
            nombre_display = f"{p.plantilla.nombre} ({nombre_variante})" if nombre_variante else p.plantilla.nombre
            item_sku = QTableWidgetItem(p.sku)
            item_sku.setData(Qt.ItemDataRole.UserRole, detalle.id)
            self.tabla_carrito.setItem(row, 0, item_sku)
            self.tabla_carrito.setItem(row, 1, QTableWidgetItem(nombre_display))
            self.tabla_carrito.setItem(row, 2, QTableWidgetItem(str(detalle.cantidad)))
            self.tabla_carrito.setItem(row, 3, QTableWidgetItem(f"${detalle.precio_unitario:,.2f}"))
            self.tabla_carrito.setItem(row, 4, QTableWidgetItem(f"${detalle.subtotal_linea:,.2f}"))

    def _refrescar_totales(self):
        if self.current_venta:
            self.label_subtotal.setText(f"${self.current_venta.subtotal or 0:,.2f}")
            self.label_descuentos.setText(f"- ${self.current_venta.descuento_total or 0:,.2f}")
            self.label_impuestos.setText(f"+ ${self.current_venta.impuestos or 0:,.2f}")
            self.label_total.setText(f"${self.current_venta.total or 0:,.2f}")
        else:
            self.label_subtotal.setText("$0.00"); self.label_descuentos.setText("$0.00")
            self.label_impuestos.setText("$0.00"); self.label_total.setText("$0.00")

    def _actualizar_estado_botones(self):
        hay_transaccion_activa = self.current_venta is not None
        self.btn_anadir_producto.setEnabled(hay_transaccion_activa)
        self.btn_cancelar_venta.setEnabled(hay_transaccion_activa)
        hay_items = hay_transaccion_activa and len(self.current_venta.detalles) > 0
        self.btn_quitar_producto.setEnabled(hay_items)
        self.btn_cobrar.setEnabled(hay_items)

    def _abrir_dialogo_seleccion_producto(self):
        if not self.current_venta:
            QMessageBox.information(self, "Nueva Venta", "Iniciando una nueva venta antes de añadir productos.")
            self._iniciar_nueva_venta()
        if not self.current_venta: return # Si la creación falla o es cancelada por alguna razón
        dialog = ProductoSelectionDialog(self.producto_controller, self.categoria_controller, self)
        dialog.producto_seleccionado.connect(self._producto_seleccionado_del_dialogo)
        dialog.exec()

    def _producto_seleccionado_del_dialogo(self, producto):
        try:
            self.current_venta = self.ventas_controller.agregar_item(self.current_venta, producto.id, 1)
            self.actualizar_vista()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _quitar_producto_del_carrito(self):
        selected_items = self.tabla_carrito.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un producto del carrito para quitarlo.")
            return
        detalle_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not detalle_id: return
        try:
            self.current_venta = self.ventas_controller.quitar_item(self.current_venta, detalle_id)
            self.actualizar_vista()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _cancelar_venta_actual(self):
        if self.current_venta:
            reply = QMessageBox.question(self, "Cancelar Venta", "¿Estás seguro?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.ventas_controller.cancelar_venta(self.current_venta)
                self.current_venta = None
                self.actualizar_vista()

    def _finalizar_venta(self):
        if self.current_venta:
            total = self.current_venta.total
            reply = QMessageBox.question(self, "Confirmar Venta", f"El total a cobrar es de <b>${total:,.2f}</b>. ¿Proceder?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    pagos = [{"metodo": "Efectivo", "monto": total}]
                    self.ventas_controller.finalizar_venta(self.current_venta, pagos)
                    QMessageBox.information(self, "Venta Completada", "Venta registrada exitosamente.")
                    self.current_venta = None
                    self.actualizar_vista()
                except Exception as e:
                    QMessageBox.critical(self, "Error al Finalizar Venta", str(e))