# src/modules/roles/reasignar_rol_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QMessageBox
)
from typing import List
from .roles_model import Rol

class ReasignarRolDialog(QDialog):
    """
    Un diálogo que se muestra cuando se intenta eliminar un rol en uso.
    Permite al administrador seleccionar un nuevo rol para reasignar a los usuarios.
    """
    def __init__(self, rol_a_eliminar: Rol, roles_disponibles: List[Rol], parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Reasignar Usuarios")
        self.setMinimumWidth(450)
        
        self.rol_seleccionado_id = None
        
        layout = QVBoxLayout(self)

        # Mensaje informativo
        mensaje = QLabel(
            f"El rol <b>'{rol_a_eliminar.nombre}'</b> está en uso por {len(rol_a_eliminar.usuarios)} usuario(s).<br>"
            "Para poder eliminarlo, debe reasignar estos usuarios a otro rol."
        )
        layout.addWidget(mensaje)
        
        layout.addWidget(QLabel("Seleccione el nuevo rol de destino:"))

        # ComboBox con los roles disponibles
        self.combo_roles = QComboBox()
        for rol in roles_disponibles:
            # No mostramos el rol que se va a eliminar en la lista de opciones
            if rol.id != rol_a_eliminar.id:
                self.combo_roles.addItem(rol.nombre, userData=rol.id)
        layout.addWidget(self.combo_roles)
        
        # Botones de Aceptar/Cancelar
        botones_layout = QHBoxLayout()
        btn_ok = QPushButton("Aceptar y Reasignar")
        btn_cancelar = QPushButton("Cancelar")
        
        btn_ok.clicked.connect(self.accept)
        btn_cancelar.clicked.connect(self.reject)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_ok)
        botones_layout.addWidget(btn_cancelar)
        layout.addLayout(botones_layout)

    def accept(self):
        """Se ejecuta al pulsar Aceptar."""
        if self.combo_roles.count() == 0:
            QMessageBox.warning(self, "No hay roles disponibles", "No existen otros roles a los que reasignar los usuarios. Por favor, cree un nuevo rol primero.")
            return
            
        # Guardamos el ID del rol seleccionado antes de cerrar
        self.rol_seleccionado_id = self.combo_roles.currentData()
        super().accept()

    def obtener_rol_seleccionado_id(self) -> int | None:
        """Devuelve el ID del rol que el usuario seleccionó."""
        return self.rol_seleccionado_id