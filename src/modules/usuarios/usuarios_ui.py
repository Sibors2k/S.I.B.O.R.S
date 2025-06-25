# src/modules/usuarios/usuarios_ui.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QHeaderView,
    QAbstractItemView, QStackedWidget
)
from PySide6.QtCore import Qt
from typing import Optional

# Importamos los controladores y modelos necesarios
from .usuarios_controller import UsuariosController
from modules.roles.roles_controller import RolesController
from .usuario_creator import UsuarioDialog
from .usuarios_model import Usuario
from modules.roles.roles_ui import RolesWidget


class UsuariosWindow(QWidget):
    def __init__(self, usuarios_controller: UsuariosController, roles_controller: RolesController, parent=None):
        super().__init__(parent)
        self.controller = usuarios_controller
        self.roles_controller = roles_controller # Guardamos la referencia para pasarla al diálogo
        self.lista_usuarios_actual = []
        
        self.setWindowTitle("Gestión de Usuarios y Roles")
        self._build_ui()

    def actualizar_vista(self):
        """Refresca la tabla de usuarios cuando la vista se muestra."""
        self.cargar_usuarios()
        self._actualizar_estado_botones()

    def _build_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        titulo = QLabel("Usuarios Registrados en el Sistema")
        titulo.setObjectName("viewTitle")
        layout_principal.addWidget(titulo)
        
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton("➕ Agregar Usuario")
        self.boton_agregar.clicked.connect(self._abrir_dialogo_usuario)
        botones_layout.addWidget(self.boton_agregar)
        
        self.boton_editar = QPushButton("✏️ Editar Seleccionado")
        self.boton_editar.clicked.connect(self._editar_usuario_seleccionado)
        self.boton_editar.setEnabled(False)
        botones_layout.addWidget(self.boton_editar)
        
        self.boton_desactivar = QPushButton("❌ Desactivar/Activar")
        self.boton_desactivar.clicked.connect(self._desactivar_usuario_seleccionado)
        self.boton_desactivar.setEnabled(False)
        botones_layout.addWidget(self.boton_desactivar)
        
        self.boton_eliminar_perm = QPushButton("🗑️ Eliminar Permanentemente")
        self.boton_eliminar_perm.clicked.connect(self._eliminar_usuario_permanentemente)
        self.boton_eliminar_perm.setEnabled(False)
        botones_layout.addWidget(self.boton_eliminar_perm)
        
        botones_layout.addStretch()
        
        self.boton_gestionar_roles = QPushButton("🔑 Gestionar Roles")
        # Esta conexión se manejará en la MainWindow para cambiar de vista
        # self.boton_gestionar_roles.clicked.connect(self.abrir_gestion_roles)
        botones_layout.addWidget(self.boton_gestionar_roles)
        
        layout_principal.addLayout(botones_layout)
        
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(5)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Nombre", "Usuario", "Rol", "Activo"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_usuarios.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_usuarios.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_usuarios.itemSelectionChanged.connect(self._actualizar_estado_botones)
        
        layout_principal.addWidget(self.tabla_usuarios)

    def _get_usuario_seleccionado(self) -> Optional[Usuario]:
        selected_items = self.tabla_usuarios.selectedItems()
        if not selected_items:
            return None
        user_id = int(self.tabla_usuarios.item(selected_items[0].row(), 0).text())
        return next((u for u in self.lista_usuarios_actual if u.id == user_id), None)

    def _actualizar_estado_botones(self):
        usuario_seleccionado = self._get_usuario_seleccionado()
        estado = usuario_seleccionado is not None
        self.boton_editar.setEnabled(estado)
        self.boton_desactivar.setEnabled(estado)
        
        es_admin = usuario_seleccionado.rol_asignado.nombre == "Admin" if (usuario_seleccionado and usuario_seleccionado.rol_asignado) else False
        self.boton_eliminar_perm.setEnabled(estado and not usuario_seleccionado.activo and not es_admin)
        
        if estado:
            texto_desactivar = "✔️ Activar" if not usuario_seleccionado.activo else "❌ Desactivar"
            self.boton_desactivar.setText(texto_desactivar)
        else:
            self.boton_desactivar.setText("❌ Desactivar/Activar")

    def cargar_usuarios(self):
        try:
            self.lista_usuarios_actual = self.controller.listar_usuarios()
            self.tabla_usuarios.setRowCount(len(self.lista_usuarios_actual))
            for fila, usuario in enumerate(self.lista_usuarios_actual):
                self.tabla_usuarios.setItem(fila, 0, QTableWidgetItem(str(usuario.id)))
                self.tabla_usuarios.setItem(fila, 1, QTableWidgetItem(usuario.nombre))
                self.tabla_usuarios.setItem(fila, 2, QTableWidgetItem(usuario.usuario))
                rol_nombre = usuario.rol_asignado.nombre if usuario.rol_asignado else "N/A"
                self.tabla_usuarios.setItem(fila, 3, QTableWidgetItem(rol_nombre))
                estado_item = QTableWidgetItem("Sí" if usuario.activo else "No")
                estado_item.setForeground(Qt.GlobalColor.darkGreen if usuario.activo else Qt.GlobalColor.red)
                self.tabla_usuarios.setItem(fila, 4, estado_item)
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudo cargar la lista de usuarios: {e}")

    def _abrir_dialogo_usuario(self, usuario_existente=None):
        dialog = UsuarioDialog(self.roles_controller, usuario_existente, self._on_dialog_submit)
        if dialog.exec():
            self.actualizar_vista()

    def _editar_usuario_seleccionado(self):
        usuario = self._get_usuario_seleccionado()
        if usuario:
            self._abrir_dialogo_usuario(usuario)

    def _on_dialog_submit(self, datos_usuario, id_usuario_existente=None):
        try:
            if id_usuario_existente:
                self.controller.editar_usuario(id_usuario_existente, datos_usuario)
                QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
            else:
                self.controller.crear_usuario(datos_usuario)
                QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error al Guardar", str(e))
            raise e 

    def _desactivar_usuario_seleccionado(self):
        usuario = self._get_usuario_seleccionado()
        if not usuario: return
        
        accion = "activar" if not usuario.activo else "desactivar"
        confirmacion = QMessageBox.question(self, f"Confirmar {accion.capitalize()}",
                                          f"¿Estás seguro de que deseas {accion} al usuario '{usuario.nombre}'?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.editar_usuario(usuario.id, {'activo': not usuario.activo})
                self.actualizar_vista()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el estado del usuario: {e}")

    def _eliminar_usuario_permanentemente(self):
        usuario = self._get_usuario_seleccionado()
        if not usuario: return
        
        advertencia = "Esta acción es IRREVERSIBLE y eliminará permanentemente al usuario y todos sus datos asociados del sistema.\n\n¿Estás ABSOLUTAMENTE SEGURO de que deseas continuar?"
        confirmacion = QMessageBox.critical(self, "¡ADVERTENCIA MÁXIMA!", advertencia, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_permanentemente(usuario.id)
                QMessageBox.information(self, "Éxito", f"El usuario '{usuario.nombre}' ha sido eliminado permanentemente.")
                self.actualizar_vista()
            except ValueError as e:
                QMessageBox.warning(self, "Acción no permitida", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar al usuario: {e}")