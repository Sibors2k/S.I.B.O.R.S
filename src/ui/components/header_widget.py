# src/ui/components/header_widget.py

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu
from PySide6.QtGui import QPixmap, QPainter, QBitmap, QAction
from PySide6.QtCore import Qt, QSize, Signal

from modules.empresa.empresa_model import get_company_data

class HeaderWidget(QWidget):
    perfil_clicked = Signal()
    logout_clicked = Signal()
    usuarios_clicked = Signal()
    roles_clicked = Signal()

    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.setObjectName("headerWidget")
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(10)

        # Lado Izquierdo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(40, 40)
        self.empresa_label = QLabel("Cargando...")
        self.empresa_label.setObjectName("headerEmpresaLabel")
        
        layout.addWidget(self.logo_label)
        layout.addWidget(self.empresa_label)
        layout.addStretch()

        # --- INICIO DE LA CORRECCIÓN DE ORDEN ---
        # Lado Derecho: FOTO, luego NOMBRE, luego MENÚ
        self.perfil_foto_label = QLabel()
        self.perfil_foto_label.setFixedSize(40, 40)
        
        self.perfil_nombre_label = QLabel("Cargando...")
        self.perfil_nombre_label.setObjectName("headerUserLabel")
        
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("headerMenuButton")
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._crear_menu_hamburguesa()

        layout.addWidget(self.perfil_foto_label) # FOTO PRIMERO
        layout.addWidget(self.perfil_nombre_label) # NOMBRE DESPUÉS
        layout.addWidget(self.menu_button)
        # --- FIN DE LA CORRECCIÓN DE ORDEN ---
        
        self.actualizar_info()

    # El resto del archivo (_crear_menu_hamburguesa, actualizar_info, etc.) no cambia
    # ... (pegar el resto del archivo desde la versión anterior)
    def _crear_menu_hamburguesa(self):
        self.menu = QMenu(self)
        action_perfil = QAction("Mi Perfil", self)
        action_logout = QAction("Cerrar Sesión", self)
        action_perfil.triggered.connect(self.perfil_clicked)
        action_logout.triggered.connect(self.logout_clicked)
        self.menu.addAction(action_perfil)
        if self.usuario.rol_asignado:
            permisos = self.usuario.rol_asignado.obtener_permisos_como_lista()
            if "usuarios" in permisos:
                action_usuarios = QAction("Panel de Usuarios", self)
                action_usuarios.triggered.connect(self.usuarios_clicked)
                self.menu.addAction(action_usuarios)
            if "roles" in permisos:
                action_roles = QAction("Panel de Roles", self)
                action_roles.triggered.connect(self.roles_clicked)
                self.menu.addAction(action_roles)
        self.menu.addSeparator()
        self.menu.addAction(action_logout)
        self.menu_button.setMenu(self.menu)

    def actualizar_info(self):
        empresa_data = get_company_data()
        if empresa_data and empresa_data.nombre:
            self.empresa_label.setText(empresa_data.nombre)
            pixmap = self._cargar_pixmap(empresa_data.ruta_logo, es_circular=False)
            self.logo_label.setPixmap(pixmap)
        else:
            self.empresa_label.setText("S.I.B.O.R.S.")
        if self.usuario and self.usuario.perfil:
            nombre_perfil = self.usuario.perfil.nombre or self.usuario.nombre
            self.perfil_nombre_label.setText(nombre_perfil)
            pixmap = self._cargar_pixmap(self.usuario.perfil.avatar_path, es_circular=True)
            self.perfil_foto_label.setPixmap(pixmap)

    def _cargar_pixmap(self, ruta_archivo, es_circular=False, tamano=40):
        if ruta_archivo and os.path.exists(ruta_archivo):
            pixmap = QPixmap(ruta_archivo)
        else:
            pixmap = QPixmap(tamano, tamano)
            pixmap.fill(Qt.GlobalColor.gray)
        pixmap = pixmap.scaled(tamano, tamano, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        if es_circular:
            mask = QBitmap(pixmap.size())
            mask.fill(Qt.GlobalColor.white)
            painter = QPainter(mask)
            painter.setBrush(Qt.GlobalColor.black)
            painter.drawEllipse(0, 0, mask.width(), mask.height())
            painter.end()
            pixmap.setMask(mask)
        return pixmap