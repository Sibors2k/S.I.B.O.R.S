# src/ui/components/main_header.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QApplication
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
import os

# Importamos el ThemeManager
from ui.theme_manager import ThemeManager

class MainHeader(QWidget):
    def __init__(self, usuario, on_profile_click, on_logout_click, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.on_profile_click = on_profile_click
        self.on_logout_click = on_logout_click
        
        self.setObjectName("mainHeader")
        self.setFixedHeight(60)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        welcome_text = f"Bienvenido, <b>{self.usuario.nombre}</b>"
        self.welcome_label = QLabel(welcome_text)
        self.welcome_label.setObjectName("welcomeLabel")

        # --- INICIO DEL CAMBIO ---
        # 1. Creamos el botón para cambiar de tema
        self.theme_toggle_button = QPushButton("🌙") # Icono simple de luna
        self.theme_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_toggle_button.setObjectName("headerButton")
        self.theme_toggle_button.setToolTip("Cambiar Tema (Claro/Oscuro)")
        self.theme_toggle_button.setFixedSize(40, 40)
        
        # Esta conexión es temporal, la mejoraremos
        self.theme_toggle_button.clicked.connect(self.toggle_theme_action)
        # --- FIN DEL CAMBIO ---

        self.profile_button = QPushButton("👤 Perfil")
        self.profile_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.profile_button.setObjectName("headerButton")
        self.profile_button.clicked.connect(self.on_profile_click)
        
        self.logout_button = QPushButton("🚪 Cerrar Sesión")
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.setObjectName("headerButton")
        self.logout_button.clicked.connect(self.on_logout_click)

        layout.addWidget(self.welcome_label)
        layout.addStretch() 
        layout.addWidget(self.theme_toggle_button) # 2. Añadimos el botón al layout
        layout.addWidget(self.profile_button)
        layout.addWidget(self.logout_button)

    # --- INICIO DEL CAMBIO ---
    # 3. Creamos la acción que se ejecutará al hacer clic
    def toggle_theme_action(self):
        """
        Esta función necesita una forma de acceder al ThemeManager.
        La forma más limpia es no instanciarlo aquí, sino tener una referencia
        o un método para acceder a él. Por ahora, lo crearemos aquí para que funcione,
        luego lo refactorizaremos si es necesario.
        """
        app_instance = QApplication.instance()
        if hasattr(app_instance, 'theme_manager'):
            app_instance.theme_manager.toggle_theme()
    # --- FIN DEL CAMBIO ---