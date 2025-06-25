# src/modules/dashboard/dashboard_ui.py

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, 
    QLabel, QFrame, QMessageBox
)
from PySide6.QtCharts import (
    QChartView, QChart, QBarSeries, QBarSet, 
    QBarCategoryAxis, QValueAxis
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPainter

from .dashboard_controller import DashboardController

class DashboardUI(QWidget):
    def __init__(self, controller: DashboardController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Dashboard")
        self._setup_ui()

    def actualizar_vista(self):
        print("Actualizando vista del Dashboard...")
        self._actualizar_kpis()
        self._actualizar_grafico()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        titulo = QLabel("Dashboard Principal")
        titulo.setObjectName("viewTitle")
        main_layout.addWidget(titulo)

        # Panel de KPIs
        kpi_layout = QGridLayout()
        self.kpi_ingresos = self._crear_kpi_box("Ingresos Totales", "$0.00")
        self.kpi_ventas = self._crear_kpi_box("Ventas Totales (Unidades)", "0")
        self.kpi_stock = self. _crear_kpi_box("Productos en Stock", "0")
        
        kpi_layout.addWidget(self.kpi_ingresos, 0, 0)
        kpi_layout.addWidget(self.kpi_ventas, 0, 1)
        kpi_layout.addWidget(self.kpi_stock, 0, 2)
        main_layout.addLayout(kpi_layout)

        # Gráfico
        chart_group = QFrame()
        chart_group.setObjectName("chartGroup")
        chart_layout = QVBoxLayout(chart_group)
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        main_layout.addWidget(chart_group)

    def _crear_kpi_box(self, titulo: str, valor_inicial: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("kpiBox")
        layout = QVBoxLayout(frame)
        
        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("kpiTitle")
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        valor_label = QLabel(valor_inicial)
        valor_label.setObjectName("kpiValue")
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)
        
        return frame

    def _actualizar_kpis(self):
        try:
            kpis = self.controller.obtener_kpis_principales()
            self.kpi_ingresos.findChild(QLabel, "kpiValue").setText(f"${kpis['ingresos_totales']:,.2f}")
            self.kpi_ventas.findChild(QLabel, "kpiValue").setText(f"{kpis['ventas_totales']:,}")
            self.kpi_stock.findChild(QLabel, "kpiValue").setText(f"{kpis['productos_en_stock']:,}")
        except Exception as e:
            QMessageBox.warning(self, "Error de KPIs", f"No se pudieron cargar los indicadores: {e}")

    def _actualizar_grafico(self):
        try:
            datos_grafico = self.controller.obtener_datos_grafico_financiero(dias=15)
        except Exception as e:
            QMessageBox.warning(self, "Error de Gráfico", f"No se pudieron cargar los datos del gráfico: {e}")
            return

        set_ingresos = QBarSet("Ingresos")
        set_egresos = QBarSet("Egresos")
        
        categorias_fechas = []
        max_valor = 0

        for item in datos_grafico:
            ingreso = item.get("total_ingresos", 0)
            egreso = item.get("total_egresos", 0)
            set_ingresos.append(ingreso)
            set_egresos.append(egreso)
            categorias_fechas.append(item["dia"])
            max_valor = max(max_valor, ingreso, egreso)

        series = QBarSeries()
        series.append(set_ingresos)
        series.append(set_egresos)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Resumen Financiero de los Últimos 15 Días")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        axis_x = QBarCategoryAxis()
        axis_x.append(categorias_fechas)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setLabelFormat("$%.2f")
        axis_y.setRange(0, max_valor * 1.1 if max_valor > 0 else 100) 
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        self.chart_view.setChart(chart)