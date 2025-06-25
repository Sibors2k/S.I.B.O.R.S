# src/modules/roles/roles_ui.py

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QGroupBox, QCheckBox, QMessageBox, QLabel, QGridLayout)
from PySide6.QtCore import Qt
from .roles_controller import RolesController
from .reasignar_rol_dialog import ReasignarRolDialog
import json

# --- INICIO DE LA MODIFICACIÓN ---
MODULOS_DISPONIBLES = ["dashboard", "empresa", "productos", "categorias", "variantes", "ventas", "contabilidad", "reportes", "clientes", "proveedores", "compras", "perfil", "usuarios", "roles"]
# --- FIN DE LA MODIFICACIÓN ---

class RolesWidget(QWidget):
    # ... (El resto del archivo no cambia)
    def __init__(self, controller: RolesController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_rol_id = None
        self.roles_cacheados = []
        self._setup_ui()

    def actualizar_vista(self):
        self._cargar_lista_roles()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        panel_izquierdo = self._crear_panel_lista()
        layout.addWidget(panel_izquierdo, 1)
        panel_derecho = self._crear_panel_detalles()
        layout.addWidget(panel_derecho, 2)
        
    def _crear_panel_lista(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("Roles del Sistema:"))
        self.lista_roles = QListWidget()
        self.lista_roles.itemClicked.connect(self._mostrar_detalles_rol)
        layout.addWidget(self.lista_roles)
        return panel

    def _crear_panel_detalles(self) -> QWidget:
        grupo = QGroupBox("Detalles y Permisos del Rol")
        layout = QVBoxLayout(grupo)
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Nombre del Rol:"))
        self.nombre_rol_input = QLineEdit()
        form_layout.addWidget(self.nombre_rol_input)
        
        permisos_group = QGroupBox("Permisos del Rol")
        permisos_layout = QGridLayout(permisos_group)
        self.checkboxes_permisos = {}
        row, col = 0, 0
        for permiso in MODULOS_DISPONIBLES:
            checkbox = QCheckBox(permiso.capitalize())
            self.checkboxes_permisos[permiso] = checkbox
            permisos_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton("✨ Nuevo")
        self.boton_guardar = QPushButton("💾 Guardar")
        self.boton_eliminar = QPushButton("❌ Eliminar")
        self.boton_nuevo.clicked.connect(self._limpiar_formulario_para_crear)
        self.boton_guardar.clicked.connect(self._guardar_rol)
        self.boton_eliminar.clicked.connect(self._eliminar_rol)
        botones_layout.addWidget(self.boton_nuevo)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_eliminar)

        layout.addLayout(form_layout)
        layout.addWidget(permisos_group)
        layout.addLayout(botones_layout)
        return grupo

    def _cargar_lista_roles(self):
        self.lista_roles.clear()
        self.roles_cacheados = self.controller.listar_roles()
        for rol in self.roles_cacheados:
            item = QListWidgetItem(f"{rol.nombre} ({len(rol.usuarios)} usuarios)")
            item.setData(Qt.ItemDataRole.UserRole, rol.id)
            self.lista_roles.addItem(item)
    
    def _mostrar_detalles_rol(self, item: QListWidgetItem):
        rol_id = item.data(Qt.ItemDataRole.UserRole)
        rol_seleccionado = next((rol for rol in self.roles_cacheados if rol.id == rol_id), None)
        if not rol_seleccionado: return
        
        self.current_rol_id = rol_id
        self.nombre_rol_input.setText(rol_seleccionado.nombre)
        
        permisos_del_rol = rol_seleccionado.obtener_permisos_como_lista()
        for nombre, checkbox in self.checkboxes_permisos.items():
            checkbox.setChecked(nombre in permisos_del_rol)

    def _guardar_rol(self):
        nombre = self.nombre_rol_input.text()
        permisos_seleccionados = [nombre for nombre, cb in self.checkboxes_permisos.items() if cb.isChecked()]
        try:
            if self.current_rol_id:
                self.controller.actualizar_rol(self.current_rol_id, nombre, permisos_seleccionados)
                QMessageBox.information(self, "Éxito", "Rol actualizado correctamente.")
            else:
                self.controller.crear_rol(nombre, permisos_seleccionados)
                QMessageBox.information(self, "Éxito", "Rol creado correctamente.")
            self.actualizar_vista()
        except ValueError as e:
            QMessageBox.warning(self, "Error de Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error Inesperado", f"No se pudo guardar el rol: {e}")

    def _eliminar_rol(self):
        if not self.current_rol_id:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, selecciona un rol de la lista para eliminarlo."); return
        
        rol_a_eliminar = next((rol for rol in self.roles_cacheados if rol.id == self.current_rol_id), None)
        if rol_a_eliminar.nombre.lower() == 'admin':
            QMessageBox.critical(self, "Acción Prohibida", "El rol de 'Admin' no puede ser eliminado."); return
            
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar el rol '{rol_a_eliminar.nombre}'?")
        if confirmacion == QMessageBox.StandardButton.Yes:
            try:
                self.controller.eliminar_rol(self.current_rol_id)
                QMessageBox.information(self, "Éxito", f"Rol '{rol_a_eliminar.nombre}' eliminado.")
            except ValueError as e:
                if "está asignado a" in str(e):
                    dialogo = ReasignarRolDialog(rol_a_eliminar, self.roles_cacheados, self)
                    if dialogo.exec():
                        nuevo_rol_id = dialogo.obtener_rol_seleccionado_id()
                        if nuevo_rol_id:
                            try:
                                self.controller.reasignar_y_eliminar_rol(self.current_rol_id, nuevo_rol_id)
                                QMessageBox.information(self, "Éxito", "Usuarios reasignados y rol eliminado.")
                            except Exception as ex:
                                QMessageBox.critical(self, "Error", f"No se pudo completar la reasignación: {ex}")
                else:
                    QMessageBox.critical(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error Inesperado", f"No se pudo eliminar el rol: {e}")
            
            self.actualizar_vista()
            self._limpiar_formulario_para_crear()

    def _limpiar_formulario_para_crear(self):
        self.current_rol_id = None
        self.nombre_rol_input.clear()
        for checkbox in self.checkboxes_permisos.values():
            checkbox.setChecked(False)
        self.lista_roles.clearSelection()