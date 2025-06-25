# src/modules/empresa/empresa_ui.py
import os
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QGroupBox, QScrollArea, QFileDialog, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from .empresa_controller import EmpresaController, EmpresaValidationError
from .empresa_model import EmpresaData

class EmpresaWidget(QWidget):
    def __init__(self, controller: EmpresaController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.ruta_logo_actual = ""
        self._init_ui()

    def actualizar_vista(self):
        self._cargar_datos_existentes()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        titulo = QLabel("Gestión de Datos de la Empresa")
        titulo.setObjectName("viewTitle")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(titulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        form_layout = QGridLayout(content_widget)
        
        # --- Grupo de Datos Fiscales ---
        fiscal_group = QGroupBox("Información Fiscal y de Contacto")
        fiscal_layout = QGridLayout(fiscal_group)
        self.nombre_input = QLineEdit()
        self.rfc_input = QLineEdit()
        self.correo_input = QLineEdit()
        self.telefono_input = QLineEdit()
        fiscal_layout.addWidget(QLabel("Nombre o Razón Social:"), 0, 0)
        fiscal_layout.addWidget(self.nombre_input, 0, 1)
        fiscal_layout.addWidget(QLabel("RFC:"), 1, 0)
        fiscal_layout.addWidget(self.rfc_input, 1, 1)
        fiscal_layout.addWidget(QLabel("Correo Principal:"), 2, 0)
        fiscal_layout.addWidget(self.correo_input, 2, 1)
        fiscal_layout.addWidget(QLabel("Teléfono Principal:"), 3, 0)
        fiscal_layout.addWidget(self.telefono_input, 3, 1)
        form_layout.addWidget(fiscal_group, 0, 0)

        # --- Grupo de Dirección Fiscal ---
        direccion_group = QGroupBox("Dirección Fiscal")
        direccion_layout = QGridLayout(direccion_group)
        self.calle_input = QLineEdit()
        self.numero_input = QLineEdit()
        self.colonia_input = QLineEdit()
        self.cp_input = QLineEdit()
        self.ciudad_input = QLineEdit()
        self.estado_input = QLineEdit()
        direccion_layout.addWidget(QLabel("Calle:"), 0, 0)
        direccion_layout.addWidget(self.calle_input, 0, 1)
        direccion_layout.addWidget(QLabel("Número Ext/Int:"), 1, 0)
        direccion_layout.addWidget(self.numero_input, 1, 1)
        direccion_layout.addWidget(QLabel("Colonia:"), 2, 0)
        direccion_layout.addWidget(self.colonia_input, 2, 1)
        direccion_layout.addWidget(QLabel("Código Postal:"), 3, 0)
        direccion_layout.addWidget(self.cp_input, 3, 1)
        direccion_layout.addWidget(QLabel("Ciudad:"), 4, 0)
        direccion_layout.addWidget(self.ciudad_input, 4, 1)
        direccion_layout.addWidget(QLabel("Estado:"), 5, 0)
        direccion_layout.addWidget(self.estado_input, 5, 1)
        form_layout.addWidget(direccion_group, 1, 0)

        # --- Grupo de Representante Legal y Logo ---
        rep_logo_group = QGroupBox("Representante y Logo")
        rep_logo_layout = QGridLayout(rep_logo_group)
        self.rep_nombre_input = QLineEdit()
        self.rep_curp_input = QLineEdit()
        self.logo_label = QLabel("Sin logo")
        self.logo_label.setFixedSize(150, 150)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setObjectName("logoPreview")
        self.boton_logo = QPushButton("Seleccionar Logo...")
        self.boton_logo.clicked.connect(self._seleccionar_logo)
        rep_logo_layout.addWidget(QLabel("Nombre Rep. Legal:"), 0, 0)
        rep_logo_layout.addWidget(self.rep_nombre_input, 0, 1)
        rep_logo_layout.addWidget(QLabel("CURP Rep. Legal:"), 1, 0)
        rep_logo_layout.addWidget(self.rep_curp_input, 1, 1)
        rep_logo_layout.addWidget(self.logo_label, 0, 2, 2, 1)
        rep_logo_layout.addWidget(self.boton_logo, 2, 2)
        form_layout.addWidget(rep_logo_group, 0, 1, 2, 1)
        
        # --- Botón de Guardar ---
        self.boton_guardar = QPushButton("💾 Guardar Datos de la Empresa")
        form_layout.addWidget(self.boton_guardar, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        self.boton_guardar.clicked.connect(self._guardar_datos)
        
    def _cargar_datos_existentes(self):
        datos = self.controller.obtener_datos_empresa()
        if datos:
            self.nombre_input.setText(datos.nombre or "")
            self.rfc_input.setText(datos.rfc or "")
            self.correo_input.setText(datos.correo_principal or "")
            self.telefono_input.setText(datos.telefono_principal or "")
            self.calle_input.setText(datos.calle_fiscal or "")
            self.numero_input.setText(datos.numero_fiscal or "")
            self.colonia_input.setText(datos.colonia_fiscal or "")
            self.cp_input.setText(datos.cp_fiscal or "")
            self.ciudad_input.setText(datos.ciudad_fiscal or "")
            self.estado_input.setText(datos.estado_fiscal or "")
            self.rep_nombre_input.setText(datos.nombre_representante or "")
            self.rep_curp_input.setText(datos.curp_representante or "")
            self.ruta_logo_actual = datos.ruta_logo or ""
            if self.ruta_logo_actual and os.path.exists(self.ruta_logo_actual):
                self._mostrar_logo(self.ruta_logo_actual)

    def _obtener_datos_formulario(self) -> EmpresaData:
        return EmpresaData(
            id=1,
            nombre=self.nombre_input.text(),
            rfc=self.rfc_input.text(),
            correo_principal=self.correo_input.text(),
            telefono_principal=self.telefono_input.text(),
            calle_fiscal=self.calle_input.text(),
            numero_fiscal=self.numero_input.text(),
            colonia_fiscal=self.colonia_input.text(),
            cp_fiscal=self.cp_input.text(),
            ciudad_fiscal=self.ciudad_input.text(),
            estado_fiscal=self.estado_input.text(),
            nombre_representante=self.rep_nombre_input.text(),
            curp_representante=self.rep_curp_input.text(),
            ruta_logo=self.ruta_logo_actual
        )

    def _guardar_datos(self):
        datos_a_guardar = self._obtener_datos_formulario()
        try:
            self.controller.guardar_datos_empresa(datos_a_guardar)
            QMessageBox.information(self, "Éxito", "Los datos de la empresa se han guardado.")
        except EmpresaValidationError as e:
            QMessageBox.warning(self, "Error de Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar los datos: {e}")

    def _seleccionar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg)")
        if archivo:
            self.ruta_logo_actual = archivo
            self._mostrar_logo(archivo)
    
    def _mostrar_logo(self, ruta_archivo):
        pixmap = QPixmap(ruta_archivo)
        self.logo_label.setPixmap(pixmap.scaled(
            self.logo_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))