# src/modules/usuarios/usuario_creator.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QGroupBox, QMessageBox, QWidget, QHBoxLayout, QRadioButton, QComboBox)
from PySide6.QtCore import Qt
from modules.roles.roles_controller import RolesController

class UsuarioDialog(QDialog):
    def __init__(self, roles_controller: RolesController, usuario_existente=None, on_submit_callback=None, parent=None):
        super().__init__(parent)
        self.usuario_existente = usuario_existente
        self.on_submit_callback = on_submit_callback
        self.roles_controller = roles_controller # Recibimos el controlador
        titulo = "Editar Usuario" if self.usuario_existente else "Crear Nuevo Usuario"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(400)
        self._build_ui()
        self._cargar_roles_en_combo()
        if self.usuario_existente:
            self._cargar_datos_existentes()

    def _build_ui(self):
        layout_principal = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.nombre_input = QLineEdit()
        self.usuario_input = QLineEdit()
        self.rol_combo = QComboBox()
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmar_input = QLineEdit()
        self.confirmar_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.radio_activo = QRadioButton("Activo")
        self.radio_inactivo = QRadioButton("Inactivo")
        self.radio_activo.setChecked(True)
        
        form_layout.addRow("Nombre Completo:", self.nombre_input)
        form_layout.addRow("Nombre de Usuario:", self.usuario_input)
        form_layout.addRow("Rol:", self.rol_combo)
        
        grupo_estado = QGroupBox("Estado")
        layout_estado = QHBoxLayout()
        layout_estado.addWidget(self.radio_activo)
        layout_estado.addWidget(self.radio_inactivo)
        grupo_estado.setLayout(layout_estado)
        form_layout.addRow(grupo_estado)
        
        if self.usuario_existente:
            form_layout.addRow(QLabel("Nueva Contraseña (dejar en blanco para no cambiar):"))
        form_layout.addRow("Contraseña:", self.contrasena_input)
        form_layout.addRow("Confirmar Contraseña:", self.confirmar_input)

        layout_principal.addLayout(form_layout)
        
        botones_layout = QHBoxLayout()
        self.boton_aceptar = QPushButton("Aceptar")
        self.boton_aceptar.clicked.connect(self.submit)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        botones_layout.addStretch()
        botones_layout.addWidget(self.boton_aceptar)
        botones_layout.addWidget(self.boton_cancelar)
        layout_principal.addLayout(botones_layout)

    def _cargar_roles_en_combo(self):
        try:
            roles = self.roles_controller.listar_roles()
            for rol in roles:
                self.rol_combo.addItem(rol.nombre, userData=rol.id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los roles: {e}")

    def _cargar_datos_existentes(self):
        self.nombre_input.setText(self.usuario_existente.nombre)
        self.usuario_input.setText(self.usuario_existente.usuario)
        self.usuario_input.setEnabled(False)
        
        if self.usuario_existente.rol_id:
            index = self.rol_combo.findData(self.usuario_existente.rol_id)
            self.rol_combo.setCurrentIndex(index if index >= 0 else 0)

        if self.usuario_existente.activo:
            self.radio_activo.setChecked(True)
        else:
            self.radio_inactivo.setChecked(True)

    def submit(self):
        nombre = self.nombre_input.text().strip()
        usuario = self.usuario_input.text().strip()
        contrasena = self.contrasena_input.text()
        confirmar = self.confirmar_input.text()
        rol_id_seleccionado = self.rol_combo.currentData()
        
        if not nombre or not usuario or rol_id_seleccionado is None:
            QMessageBox.warning(self, "Campos Incompletos", "El nombre, usuario y rol son obligatorios.")
            return
            
        if contrasena != confirmar:
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            return
            
        if not self.usuario_existente and not contrasena:
            QMessageBox.warning(self, "Contraseña Requerida", "Para un usuario nuevo, la contraseña es obligatoria.")
            return

        datos = {
            "nombre": nombre, "usuario": usuario,
            "rol_id": rol_id_seleccionado,
            "activo": self.radio_activo.isChecked()
        }
        
        if contrasena:
            clave_contrasena = "nueva_contrasena" if self.usuario_existente else "contrasena"
            datos[clave_contrasena] = contrasena

        if self.on_submit_callback:
            try:
                id_usuario = self.usuario_existente.id if self.usuario_existente else None
                self.on_submit_callback(datos, id_usuario)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error al Guardar", str(e))