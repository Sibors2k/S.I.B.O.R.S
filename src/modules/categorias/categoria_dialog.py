# src/modules/categorias/categoria_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox
)
from typing import Optional, Dict, List
from .categoria_model import Categoria

class CategoriaDialog(QDialog):
    def __init__(self, todas_las_categorias: List[Categoria], categoria_a_editar: Optional[Categoria] = None, parent=None):
        super().__init__(parent)
        
        self.todas_las_categorias = todas_las_categorias
        self.categoria_existente = categoria_a_editar

        titulo = "Editar Categoría" if self.categoria_existente else "Agregar Nueva Categoría"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self._setup_ui()
        if self.categoria_existente:
            self._cargar_datos_existentes()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.input_nombre = QLineEdit()
        self.combo_padre = QComboBox()
        
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Categoría Padre:", self.combo_padre)
        
        self._poblar_combo_padre()

        layout.addLayout(form_layout)

        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_guardar = QPushButton("💾 Guardar")
        self.boton_guardar.clicked.connect(self.accept)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.reject)
        
        botones_layout.addWidget(self.boton_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        
        layout.addLayout(botones_layout)

    def _cargar_datos_existentes(self):
        """Si estamos editando, llena el formulario con los datos existentes."""
        if not self.categoria_existente: return
        
        self.input_nombre.setText(self.categoria_existente.nombre)
        
        index = self.combo_padre.findData(self.categoria_existente.categoria_padre_id)
        if index != -1:
            self.combo_padre.setCurrentIndex(index)
        else:
            self.combo_padre.setCurrentIndex(0) # "Ninguna"

    def _obtener_descendientes(self, categoria_id: int) -> List[int]:
        """Obtiene una lista de todos los IDs de las subcategorías de una categoría."""
        descendientes = []
        hijos = [c for c in self.todas_las_categorias if c.categoria_padre_id == categoria_id]
        for hijo in hijos:
            descendientes.append(hijo.id)
            descendientes.extend(self._obtener_descendientes(hijo.id))
        return descendientes

    def _poblar_combo_padre(self):
        """Puebla el ComboBox de padres, excluyendo la categoría actual y sus descendientes."""
        self.combo_padre.addItem("Ninguna (Categoría Principal)", userData=None)
        
        ids_excluidos = []
        if self.categoria_existente:
            ids_excluidos.append(self.categoria_existente.id)
            ids_excluidos.extend(self._obtener_descendientes(self.categoria_existente.id))

        # Crear un diccionario para un acceso rápido por ID
        categorias_por_id = {c.id: c for c in self.todas_las_categorias}
        
        # Obtener solo las categorías raíz para iniciar el recorrido
        categorias_raiz = [c for c in self.todas_las_categorias if c.categoria_padre_id is None]
        
        for cat in sorted(categorias_raiz, key=lambda x: x.nombre):
            if cat.id not in ids_excluidos:
                self._poblar_combo_recursivo(cat, 1, ids_excluidos, categorias_por_id)

    def _poblar_combo_recursivo(self, categoria: Categoria, indent_level: int, ids_excluidos: List[int], categorias_por_id: dict):
        self.combo_padre.addItem(f"{'—' * (indent_level - 1)} {categoria.nombre}", userData=categoria.id)
        
        # Obtenemos los hijos desde el diccionario
        hijos = [c for c in categorias_por_id.values() if c.categoria_padre_id == categoria.id]

        for sub_cat in sorted(hijos, key=lambda x: x.nombre):
            if sub_cat.id not in ids_excluidos:
                self._poblar_combo_recursivo(sub_cat, indent_level + 1, ids_excluidos, categorias_por_id)

    def obtener_datos(self) -> Optional[Dict]:
        """Valida y devuelve los datos del formulario en un diccionario."""
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Dato Requerido", "El nombre de la categoría es obligatorio.")
            return None
        
        return {
            "nombre": nombre,
            "padre_id": self.combo_padre.currentData()
        }