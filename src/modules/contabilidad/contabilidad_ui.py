# src/modules/contabilidad/contabilidad_ui.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel,
    QComboBox, QTabWidget, QFrame, QHeaderView, QGridLayout,
    QAbstractItemView  # <-- AÑADIDO AQUÍ
)
from PySide6.QtCore import Qt
from .contabilidad_controller import ContabilidadController
from .contabilidad_model import TipoMovimiento

class ContabilidadWidget(QWidget):
    def __init__(self, controller: ContabilidadController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def actualizar_vista(self):
        print("Actualizando vista de contabilidad...")
        self._actualizar_resumen()
        self._cargar_tabla_movimientos()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Panel de Contabilidad")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)

        resumen_panel = self._crear_panel_resumen()
        layout_principal.addWidget(resumen_panel)

        tabs = QTabWidget()
        historial_tab = self._crear_tab_historial()
        agregar_tab = self._crear_tab_agregar_movimiento()
        
        tabs.addTab(historial_tab, "📊 Historial de Movimientos")
        tabs.addTab(agregar_tab, "➕ Agregar Movimiento Manual")
        
        layout_principal.addWidget(tabs)

    def _crear_panel_resumen(self):
        panel = QFrame()
        panel.setObjectName("resumenPanel")
        layout = QHBoxLayout(panel)
        
        self.label_ingresos = QLabel("Ingresos Totales: $0.00")
        self.label_egresos = QLabel("Egresos Totales: $0.00")
        self.label_balance = QLabel("Balance: $0.00")
        
        for label in [self.label_ingresos, self.label_egresos, self.label_balance]:
            label.setObjectName("resumenLabel")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            
        return panel
        
    def _crear_tab_historial(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(6)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Tipo", "Concepto", "Descripción", "Categoría", "Monto"])
        self.tabla_movimientos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_movimientos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Esta línea ahora es válida
        layout.addWidget(self.tabla_movimientos)
        return widget

    def _crear_tab_agregar_movimiento(self):
        widget = QWidget()
        layout = QGridLayout(widget)
        
        layout.addWidget(QLabel("Tipo de Movimiento:"), 0, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Ingreso", userData=TipoMovimiento.INGRESO)
        self.combo_tipo.addItem("Egreso", userData=TipoMovimiento.EGRESO)
        layout.addWidget(self.combo_tipo, 0, 1)

        layout.addWidget(QLabel("Concepto:"), 1, 0)
        self.input_concepto = QLineEdit()
        self.input_concepto.setPlaceholderText("Ej: Venta de producto X, Pago de nómina")
        layout.addWidget(self.input_concepto, 1, 1)

        layout.addWidget(QLabel("Monto ($):"), 2, 0)
        self.input_monto = QLineEdit()
        self.input_monto.setPlaceholderText("Ej: 1500.50")
        layout.addWidget(self.input_monto, 2, 1)

        layout.addWidget(QLabel("Descripción (Opcional):"), 3, 0)
        self.input_descripcion = QLineEdit()
        layout.addWidget(self.input_descripcion, 3, 1)

        layout.addWidget(QLabel("Categoría (Opcional):"), 4, 0)
        self.input_categoria = QLineEdit()
        self.input_categoria.setPlaceholderText("Ej: Ventas, Sueldos, Marketing")
        layout.addWidget(self.input_categoria, 4, 1)
        
        self.boton_guardar_movimiento = QPushButton("💾 Guardar Movimiento")
        self.boton_guardar_movimiento.clicked.connect(self._guardar_movimiento_manual)
        layout.addWidget(self.boton_guardar_movimiento, 5, 1, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.setColumnStretch(1, 2)
        layout.setRowStretch(6, 1)
        
        return widget

    def _actualizar_resumen(self):
        try:
            resumen = self.controller.obtener_resumen()
            self.label_ingresos.setText(f"Ingresos Totales: ${resumen['total_ingresos']:,.2f}")
            self.label_egresos.setText(f"Egresos Totales: ${resumen['total_egresos']:,.2f}")
            self.label_balance.setText(f"Balance: ${resumen['balance']:,.2f}")
        except Exception as e:
            print(f"Error al actualizar resumen contable: {e}")

    def _cargar_tabla_movimientos(self):
        try:
            movimientos = self.controller.obtener_todos_movimientos()
            self.tabla_movimientos.setRowCount(len(movimientos))
            for fila, mov in enumerate(movimientos):
                fecha_str = mov.fecha.strftime('%Y-%m-%d %H:%M')
                tipo_str = mov.tipo.value.capitalize()
                monto_str = f"${mov.monto:,.2f}"
                color = Qt.GlobalColor.darkGreen if mov.tipo == TipoMovimiento.INGRESO else Qt.GlobalColor.red
                
                items = [
                    QTableWidgetItem(fecha_str), QTableWidgetItem(tipo_str),
                    QTableWidgetItem(mov.concepto), QTableWidgetItem(mov.descripcion or ""),
                    QTableWidgetItem(mov.categoria or ""), QTableWidgetItem(monto_str)
                ]
                
                items[1].setForeground(color)
                items[5].setForeground(color)
                items[5].setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                for col, item in enumerate(items):
                    self.tabla_movimientos.setItem(fila, col, item)
        except Exception as e:
             QMessageBox.critical(self, "Error", f"No se pudo cargar la tabla de movimientos: {e}")

    def _guardar_movimiento_manual(self):
        try:
            tipo = self.combo_tipo.currentData()
            concepto = self.input_concepto.text()
            monto = float(self.input_monto.text())
            descripcion = self.input_descripcion.text()
            categoria = self.input_categoria.text()

            self.controller.agregar_movimiento(tipo, concepto, monto, descripcion, categoria)
            QMessageBox.information(self, "Éxito", "Movimiento registrado correctamente.")
            self._limpiar_formulario()
            self.actualizar_vista()
        except ValueError as ve:
            QMessageBox.warning(self, "Datos Inválidos", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el movimiento: {e}")

    def _limpiar_formulario(self):
        self.input_concepto.clear()
        self.input_monto.clear()
        self.input_descripcion.clear()
        self.input_categoria.clear()
        self.input_concepto.setFocus()