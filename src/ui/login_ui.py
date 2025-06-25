# src/ui/login_ui.py

from PySide6.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox)
# --- INICIO DE LA MODIFICACIÓN ---
from PySide6.QtCore import Qt, Signal
# --- FIN DE LA MODIFICACIÓN ---
from PySide6.QtGui import QPixmap
import os
import sys

from modules.usuarios.usuarios_controller import UsuariosController
# --- INICIO DE LA MODIFICACIÓN ---
# Ya no necesita conocer la MainWindow. La eliminamos para un mejor desacoplamiento.
# from ui.main_window import MainWindow 
# --- FIN DE LA MODIFICACIÓN ---

class LoginWindow(QMainWindow):
    # --- INICIO DE LA MODIFICACIÓN ---
    # Creamos una señal que se emitirá cuando el login sea exitoso.
    # Enviará un objeto (el objeto Usuario) como parte de la señal.
    login_success = Signal(object)
    # --- FIN DE LA MODIFICACIÓN ---

    def __init__(self, usuarios_controller: UsuariosController, company_name: str):
        super().__init__()
        self.controller = usuarios_controller
        self.company_name = company_name
        self.setWindowTitle("Iniciar Sesión - S.I.B.O.R.S")
        self.setFixedSize(1200, 600)
        # self.main_window = None # Ya no es necesario
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        left_panel = QWidget()
        left_panel.setObjectName("loginLeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo_sibors_2.png"))
        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation))
        left_layout.addWidget(logo_label)
        
        right_panel = QWidget()
        right_panel.setObjectName("loginRightPanel")
        form_layout = QVBoxLayout(right_panel)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setContentsMargins(80, 80, 80, 80)
        form_layout.setSpacing(15)

        title_label = QLabel(f"Bienvenido a\n{self.company_name}")
        title_label.setObjectName("loginTitle")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self.try_login)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.try_login)

        form_layout.addWidget(title_label)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(self.pass_input)
        form_layout.addSpacing(30)
        form_layout.addWidget(self.login_button)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def try_login(self):
        user = self.user_input.text().strip()
        pwd = self.pass_input.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Campos Requeridos", "Por favor, completa todos los campos.")
            return

        try:
            usuario_obj = self.controller.login(user, pwd)
            if usuario_obj:
                # --- INICIO DE LA MODIFICACIÓN ---
                # En lugar de crear la ventana principal aquí...
                # ...emitimos la señal de éxito con el objeto del usuario.
                self.login_success.emit(usuario_obj)
                self.close() # Cerramos la ventana de login
                # --- FIN DE LA MODIFICACIÓN ---
            else:
                QMessageBox.warning(self, "Login Fallido", "Usuario o contraseña incorrectos.")
                self.pass_input.clear()
                self.pass_input.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", f"Ocurrió un error al intentar iniciar sesión:\n{e}")