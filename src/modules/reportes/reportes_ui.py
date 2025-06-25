# src/modules/reportes/reportes_ui.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QPushButton, QMessageBox,
    QLabel, QGroupBox, QComboBox, QFileDialog, QDateEdit, QHBoxLayout
)
from PySide6.QtCore import QDate, Qt
from .reportes_controller import ReportesController
from utils.reporter import generar_reporte_ventas_pdf
from utils.excel_reporter import generar_reporte_excel

class ReportesWidget(QWidget):
    def __init__(self, controller: ReportesController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()
    
    def actualizar_vista(self):
        pass

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Centro de Reportes")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)

        config_group = QGroupBox("Configuración del Reporte")
        config_layout = QGridLayout(config_group)

        config_layout.addWidget(QLabel("Tipo de Reporte:"), 0, 0)
        self.combo_tipo_reporte = QComboBox()
        self.combo_tipo_reporte.addItem("Reporte de Ventas", "ventas")
        self.combo_tipo_reporte.addItem("Reporte de Inventario", "inventario")
        config_layout.addWidget(self.combo_tipo_reporte, 0, 1)

        config_layout.addWidget(QLabel("Desde:"), 1, 0)
        self.fecha_desde = QDateEdit(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setCalendarPopup(True)
        config_layout.addWidget(self.fecha_desde, 1, 1)

        config_layout.addWidget(QLabel("Hasta:"), 2, 0)
        self.fecha_hasta = QDateEdit(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        config_layout.addWidget(self.fecha_hasta, 2, 1)
        
        botones_group = QGroupBox("Generar Reporte")
        botones_layout = QHBoxLayout(botones_group)
        self.boton_pdf = QPushButton("📄 Exportar a PDF")
        self.boton_excel = QPushButton("📊 Exportar a Excel")
        self.boton_pdf.clicked.connect(self._exportar_a_pdf)
        self.boton_excel.clicked.connect(self._exportar_a_excel)
        botones_layout.addWidget(self.boton_pdf)
        botones_layout.addWidget(self.boton_excel)

        layout_principal.addWidget(config_group)
        layout_principal.addWidget(botones_group)
        layout_principal.addStretch()

    def _obtener_configuracion_reporte(self):
        tipo_reporte = self.combo_tipo_reporte.currentData()
        filtros = {
            "fecha_inicio": self.fecha_desde.date().toString("yyyy-MM-dd"),
            "fecha_fin": self.fecha_hasta.date().toString("yyyy-MM-dd"),
        }
        return tipo_reporte, filtros

    def _exportar_a_pdf(self):
        tipo_reporte, filtros = self._obtener_configuracion_reporte()
        if tipo_reporte != "ventas":
            QMessageBox.information(self, "Función no disponible", f"La exportación a PDF para '{tipo_reporte}' aún no está implementada.")
            return

        ruta_sugerida = f"reporte_ventas_{QDate.currentDate().toString('yyyyMMdd')}.pdf"
        ruta_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte en PDF", ruta_sugerida, "Archivos PDF (*.pdf)")
        if not ruta_archivo: return
        
        try:
            reporte_data = self.controller.obtener_datos_para_reporte(tipo_reporte, filtros)
            empresa_data = self.controller.empresa_ctrl.obtener_datos_empresa()
            empresa_dict = empresa_data.__dict__ if empresa_data else {}

            generar_reporte_ventas_pdf(ruta_archivo, reporte_data["data"], empresa_dict)
            QMessageBox.information(self, "Éxito", f"Reporte PDF guardado en:\n{ruta_archivo}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el PDF: {e}")

    def _exportar_a_excel(self):
        tipo_reporte, filtros = self._obtener_configuracion_reporte()
        ruta_sugerida = f"reporte_{tipo_reporte}_{QDate.currentDate().toString('yyyyMMdd')}.xlsx"
        ruta_archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte en Excel", ruta_sugerida, "Archivos Excel (*.xlsx)")
        if not ruta_archivo: return

        try:
            reporte_data = self.controller.obtener_datos_para_reporte(tipo_reporte, filtros)
            generar_reporte_excel(ruta_archivo, reporte_data["titulo"], reporte_data["headers"], reporte_data["data"])
            QMessageBox.information(self, "Éxito", f"Reporte Excel guardado en:\n{ruta_archivo}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el reporte Excel: {e}")