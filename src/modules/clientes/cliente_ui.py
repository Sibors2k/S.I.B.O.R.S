# src/modules/clientes/cliente_ui.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView, QLabel, QGroupBox, QStackedWidget
)
from PySide6.QtCore import Qt
from typing import List, Optional

from .cliente_controller import ClienteController
from .cliente_model import Cliente, EstadoCliente
from .cliente_dialog import ClienteDialog
from modules.ventas.ventas_model import Venta

class ClienteWidget(QWidget):
    def __init__(self, controller: ClienteController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def actualizar_vista(self):
        self._filtrar_tabla()
        self._actualizar_botones()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Gestión de Clientes")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)

        toolbar_layout = QHBoxLayout()
        self.boton_agregar = QPushButton("➕ Agregar Cliente")
        self.boton_agregar.clicked.connect(self._abrir_dialogo_agregar)
        self.boton_editar = QPushButton("✏️ Editar Seleccionado")
        self.boton_editar.clicked.connect(self._abrir_dialogo_editar)
        self.boton_eliminar = QPushButton("🗑️ Eliminar Seleccionado")
        self.boton_eliminar.clicked.connect(self._eliminar_cliente)
        
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar por nombre, RFC o email...")
        self.input_busqueda.textChanged.connect(self._filtrar_tabla)
        
        toolbar_layout.addWidget(self.boton_agregar)
        toolbar_layout.addWidget(self.boton_editar)
        toolbar_layout.addWidget(self.boton_eliminar)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.input_busqueda)
        layout_principal.addLayout(toolbar_layout)

        main_content_layout = QHBoxLayout()
        
        clientes_group = QGroupBox("Clientes")
        clientes_layout = QVBoxLayout(clientes_group)
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(5) # Reducimos para dar más espacio
        self.tabla_clientes.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Estado", "Límite Crédito"])
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_clientes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_clientes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_clientes.itemSelectionChanged.connect(self._on_cliente_selected)
        clientes_layout.addWidget(self.tabla_clientes)
        main_content_layout.addWidget(clientes_group, 2)

        # --- INICIO DE LA NUEVA FUNCIONALIDAD ---
        historial_group = QGroupBox("Historial de Compras del Cliente")
        historial_layout = QVBoxLayout(historial_group)
        
        self.stack_historial = QStackedWidget()
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(4)
        self.tabla_ventas.setHorizontalHeaderLabels(["Fecha", "Producto", "Cantidad", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.label_sin_compras = QLabel("Este cliente no ha realizado compras.")
        self.label_sin_compras.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.stack_historial.addWidget(self.tabla_ventas)
        self.stack_historial.addWidget(self.label_sin_compras)
        
        historial_layout.addWidget(self.stack_historial)
        main_content_layout.addWidget(historial_group, 1)
        # --- FIN DE LA NUEVA FUNCIONALIDAD ---

        layout_principal.addLayout(main_content_layout)
        
    def _filtrar_tabla(self):
        termino = self.input_busqueda.text()
        try:
            clientes = self.controller.buscar_clientes(termino)
            self._cargar_tabla_clientes(clientes)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo filtrar la lista: {e}")

    def _cargar_tabla_clientes(self, clientes: List[Cliente]):
        self.tabla_clientes.setRowCount(len(clientes))
        for row, cliente in enumerate(clientes):
            self.tabla_clientes.setItem(row, 0, QTableWidgetItem(str(cliente.id)))
            self.tabla_clientes.setItem(row, 1, QTableWidgetItem(cliente.nombre_completo))
            self.tabla_clientes.setItem(row, 2, QTableWidgetItem(cliente.email))
            estado_item = QTableWidgetItem(cliente.estado.value)
            color = Qt.GlobalColor.darkGreen if cliente.estado == EstadoCliente.ACTIVO else Qt.GlobalColor.red
            estado_item.setForeground(color)
            self.tabla_clientes.setItem(row, 3, estado_item)
            limite_item = QTableWidgetItem(f"${cliente.limite_credito:,.2f}")
            limite_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_clientes.setItem(row, 4, limite_item)
        self._actualizar_botones()

    def _on_cliente_selected(self):
        cliente = self._obtener_cliente_seleccionado()
        self._actualizar_botones()
        if cliente:
            try:
                ventas = self.controller.obtener_ventas_de_cliente(cliente.id)
                self._cargar_tabla_ventas(ventas)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudieron cargar las ventas: {e}")
        else:
            self._cargar_tabla_ventas([])

    def _cargar_tabla_ventas(self, ventas: List[Venta]):
        if not ventas:
            self.stack_historial.setCurrentWidget(self.label_sin_compras)
            return
        
        self.stack_historial.setCurrentWidget(self.tabla_ventas)
        self.tabla_ventas.setRowCount(len(ventas))
        for row, venta in enumerate(ventas):
            self.tabla_ventas.setItem(row, 0, QTableWidgetItem(venta.fecha_venta.strftime('%Y-%m-%d')))
            self.tabla_ventas.setItem(row, 1, QTableWidgetItem(venta.producto.nombre if venta.producto else "N/A"))
            self.tabla_ventas.setItem(row, 2, QTableWidgetItem(str(venta.cantidad)))
            total_item = QTableWidgetItem(f"${venta.total_venta:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_ventas.setItem(row, 3, total_item)

    # El resto de los métodos (_obtener_cliente_seleccionado, _actualizar_botones,
    # _abrir_dialogo_agregar, _abrir_dialogo_editar, _eliminar_cliente)
    # no necesitan cambios funcionales.
    def _obtener_cliente_seleccionado(self) -> Optional[Cliente]:
        selected_items = self.tabla_clientes.selectedItems()
        if not selected_items: return None
        cliente_id = int(self.tabla_clientes.item(selected_items[0].row(), 0).text())
        return self.controller.db.get(Cliente, cliente_id)

    def _actualizar_botones(self):
        estado = self._obtener_cliente_seleccionado() is not None
        self.boton_editar.setEnabled(estado)
        self.boton_eliminar.setEnabled(estado)

    def _abrir_dialogo_agregar(self):
        dialogo = ClienteDialog(parent=self)
        if dialogo.exec():
            datos = dialogo.obtener_datos()
            try:
                self.controller.agregar_cliente(datos)
                QMessageBox.information(self, "Éxito", "Cliente agregado.")
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar: {e}")
                
    def _abrir_dialogo_editar(self):
        cliente = self._obtener_cliente_seleccionado()
        if not cliente:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona un cliente para editar.")
            return
        dialogo = ClienteDialog(cliente=cliente, parent=self)
        if dialogo.exec():
            datos = dialogo.obtener_datos()
            try:
                self.controller.actualizar_cliente(cliente.id, datos)
                QMessageBox.information(self, "Éxito", "Cliente actualizado.")
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar: {e}")

    def _eliminar_cliente(self):
        cliente = self._obtener_cliente_seleccionado()
        if not cliente: return
        confirm = QMessageBox.question(self, "Confirmar", f"¿Eliminar al cliente '{cliente.nombre_completo}'?")
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_cliente(cliente.id)
                QMessageBox.information(self, "Éxito", "Cliente eliminado.")
                self.actualizar_vista()
            except ValueError as e:
                QMessageBox.warning(self, "Acción no permitida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")