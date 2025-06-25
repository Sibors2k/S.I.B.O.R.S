# src/modules/productos/variantes_stock_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QHBoxLayout, QHeaderView, QAbstractItemView, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from typing import Optional

# --- INICIO DE LA MODIFICACIÓN ---
# Se actualizan las importaciones para apuntar al nuevo archivo de modelos unificado.
from .models import ProductoPlantilla, Producto
# --- FIN DE LA MODIFICACIÓN ---

from .producto_controller import ProductoController
from .stock_adjustment_dialog import StockAdjustmentDialog

class VariantesStockDialog(QDialog):
    def __init__(self, plantilla: ProductoPlantilla, producto_controller: ProductoController, usuario_logueado, parent=None):
        super().__init__(parent)
        self.plantilla = plantilla
        self.producto_controller = producto_controller
        self.usuario_logueado = usuario_logueado

        self.setWindowTitle(f"Stock y Variantes para: {self.plantilla.nombre}")
        self.setMinimumSize(700, 400)
        self.setModal(True)

        self._setup_ui()
        self._poblar_tabla()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        titulo = QLabel(f"<b>Producto:</b> {self.plantilla.nombre}")
        layout.addWidget(titulo)
        
        self.tabla_variantes = QTableWidget()
        self.tabla_variantes.setColumnCount(5)
        self.tabla_variantes.setHorizontalHeaderLabels(["ID Variante", "SKU", "Variante (Atributos)", "Precio Venta", "Stock Actual"])
        self.tabla_variantes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.tabla_variantes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_variantes.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_variantes.itemSelectionChanged.connect(self._actualizar_estado_botones)
        layout.addWidget(self.tabla_variantes)

        botones_layout = QHBoxLayout()
        self.btn_ajustar_stock = QPushButton("📊 Ajustar Stock de Variante")
        self.btn_ajustar_stock.setEnabled(False) # Deshabilitado hasta que se seleccione una fila
        self.btn_ajustar_stock.clicked.connect(self._abrir_dialogo_ajuste_stock)
        
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)

        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_ajustar_stock)
        botones_layout.addWidget(btn_cerrar)
        layout.addLayout(botones_layout)

    def _poblar_tabla(self):
        """Llena la tabla con las variantes de la plantilla."""
        self.tabla_variantes.setRowCount(0) # Limpiar por si se refresca
        
        variantes = sorted(self.plantilla.variantes, key=lambda v: v.sku)
        self.tabla_variantes.setRowCount(len(variantes))
        
        for row, v in enumerate(variantes):
            nombre_variante = " / ".join(sorted([valor.valor for valor in v.valores]))
            
            # Guardamos el objeto completo en el item de la primera columna para fácil acceso
            item_id = QTableWidgetItem(str(v.id))
            item_id.setData(Qt.ItemDataRole.UserRole, v)

            self.tabla_variantes.setItem(row, 0, item_id)
            self.tabla_variantes.setItem(row, 1, QTableWidgetItem(v.sku))
            self.tabla_variantes.setItem(row, 2, QTableWidgetItem(nombre_variante))
            self.tabla_variantes.setItem(row, 3, QTableWidgetItem(f"${v.precio_venta:,.2f}"))
            self.tabla_variantes.setItem(row, 4, QTableWidgetItem(str(v.stock)))

    def _actualizar_estado_botones(self):
        """Habilita o deshabilita botones según la selección en la tabla."""
        hay_seleccion = bool(self.tabla_variantes.selectedItems())
        self.btn_ajustar_stock.setEnabled(hay_seleccion)

    def _obtener_variante_seleccionada(self) -> Optional[Producto]:
        """Obtiene el objeto Producto de la fila seleccionada."""
        items_seleccionados = self.tabla_variantes.selectedItems()
        if not items_seleccionados:
            return None
        # El objeto variante está en la data del item de la primera columna
        return self.tabla_variantes.item(items_seleccionados[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def _abrir_dialogo_ajuste_stock(self):
        variante_seleccionada = self._obtener_variante_seleccionada()
        if not variante_seleccionada:
            QMessageBox.warning(self, "Selección Requerida", "Selecciona una variante de la lista para ajustar su stock.")
            return
            
        dialogo = StockAdjustmentDialog(variante_seleccionada, self)
        if dialogo.exec():
            datos_ajuste = dialogo.obtener_datos()
            if datos_ajuste:
                try:
                    self.producto_controller.ajustar_stock(
                        producto_id=variante_seleccionada.id, 
                        usuario_id=self.usuario_logueado.id, 
                        **datos_ajuste
                    )
                    QMessageBox.information(self, "Éxito", "Stock ajustado.")
                    # Refrescar la tabla para mostrar el nuevo stock
                    self._poblar_tabla()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo ajustar el stock: {e}")