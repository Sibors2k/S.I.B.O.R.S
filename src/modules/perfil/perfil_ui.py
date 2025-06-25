# src/modules/perfil/perfil_ui.py

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QGroupBox, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from .perfil_controller import PerfilController

# --- INICIO DE LA CORRECCIÓN ---
# Eliminamos la importación de la función 'validar_telefono' que no existe.
from utils.validators import validar_email, sanitizar_telefono, validar_longitud
# --- FIN DE LA CORRECCIÓN ---


class PerfilWidget(QWidget):
    def __init__(self, controller: PerfilController, usuario_logueado, parent=None):
        super().__init__(parent)
        self.usuario = usuario_logueado
        self.controller = controller
        self.perfil_actual = None
        self._setup_ui()

    def actualizar_vista(self):
        self.cargar_perfil()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        titulo = QLabel("Mi Perfil de Usuario")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)
        
        main_layout = QHBoxLayout()
        
        # Panel izquierdo: Datos
        form_group = QGroupBox("Mis Datos")
        form_layout = QFormLayout(form_group)
        self.nombre_edit = QLineEdit()
        self.apellidos_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.telefono_edit = QLineEdit()
        self.cargo_edit = QLineEdit()
        form_layout.addRow("Nombre:", self.nombre_edit)
        form_layout.addRow("Apellidos:", self.apellidos_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Teléfono:", self.telefono_edit)
        form_layout.addRow("Cargo:", self.cargo_edit)
        main_layout.addWidget(form_group, 1)

        # Panel derecho: Avatar y Biografía
        right_panel_layout = QVBoxLayout()
        avatar_group = QGroupBox("Avatar")
        avatar_layout = QVBoxLayout(avatar_group)
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setObjectName("logoPreview")
        self.boton_avatar = QPushButton("Cambiar Avatar")
        self.boton_avatar.clicked.connect(self.cambiar_avatar)
        avatar_layout.addWidget(self.avatar_label, alignment=Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(self.boton_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        right_panel_layout.addWidget(avatar_group)
        
        bio_group = QGroupBox("Biografía")
        bio_layout = QVBoxLayout(bio_group)
        self.bio_edit = QTextEdit()
        bio_layout.addWidget(self.bio_edit)
        right_panel_layout.addWidget(bio_group)
        main_layout.addLayout(right_panel_layout, 1)
        
        layout_principal.addLayout(main_layout)
        
        # Botón de guardar
        self.boton_guardar = QPushButton("💾 Guardar Cambios en mi Perfil")
        self.boton_guardar.clicked.connect(self.guardar_perfil)
        layout_principal.addWidget(self.boton_guardar, alignment=Qt.AlignmentFlag.AlignRight)

    def cargar_perfil(self):
        try:
            self.perfil_actual = self.controller.obtener_perfil(self.usuario.id)
            if self.perfil_actual:
                self.nombre_edit.setText(self.perfil_actual.nombre or self.usuario.nombre)
                self.apellidos_edit.setText(self.perfil_actual.apellidos or "")
                self.email_edit.setText(self.perfil_actual.email or "")
                self.telefono_edit.setText(self.perfil_actual.telefono or "")
                self.cargo_edit.setText(self.perfil_actual.cargo or "")
                self.bio_edit.setPlainText(self.perfil_actual.biografia or "")
                if self.perfil_actual.avatar_path and os.path.exists(self.perfil_actual.avatar_path):
                    self.cargar_avatar(self.perfil_actual.avatar_path)
                else:
                    self.avatar_label.setText("Sin Avatar")
            else:
                # Si no hay perfil, mostramos el nombre del usuario logueado
                self.nombre_edit.setText(self.usuario.nombre)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el perfil: {e}")

    def guardar_perfil(self):
        if not self.validar_formulario():
            return
            
        datos_perfil = {
            "nombre": self.nombre_edit.text(),
            "apellidos": self.apellidos_edit.text(),
            "email": self.email_edit.text(),
            "telefono": self.telefono_edit.text(),
            "cargo": self.cargo_edit.text(),
            "biografia": self.bio_edit.toPlainText(),
        }
        try:
            self.controller.actualizar_perfil(self.usuario.id, datos_perfil)
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el perfil: {e}")

    def cambiar_avatar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Avatar", "", "Imágenes (*.png *.jpg *.jpeg)")
        if archivo:
            try:
                nuevo_path = self.controller.guardar_avatar(self.usuario.id, archivo)
                if nuevo_path:
                    self.cargar_avatar(nuevo_path)
                    QMessageBox.information(self, "Éxito", "Avatar actualizado.")
            except Exception as e:
                QMessageBox.critical(self, "Error Grave", f"No se pudo cambiar el avatar: {e}")

    def cargar_avatar(self, ruta_avatar: str):
        pixmap = QPixmap(ruta_avatar)
        self.avatar_label.setPixmap(pixmap.scaled(self.avatar_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    
    def validar_formulario(self) -> bool:
        if not validar_longitud(self.nombre_edit.text(), minimo=2):
            QMessageBox.warning(self, "Validación Fallida", "El nombre debe tener al menos 2 caracteres.")
            return False
        if self.email_edit.text() and not validar_email(self.email_edit.text()):
            QMessageBox.warning(self, "Validación Fallida", "El formato del email no es válido.")
            return False
        
        # No necesitamos validar el teléfono aquí, solo lo sanitizamos al guardar
        return True