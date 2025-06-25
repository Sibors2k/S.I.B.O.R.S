# src/ui/components/main_sidebar.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class MainSidebar(QWidget):
    """
    La barra de navegación lateral. Ahora solo crea botones y le dice al stack qué widget mostrar.
    """
    def __init__(self, modulos_permitidos: list, stack: QStackedWidget, parent=None):
        super().__init__(parent)
        self.modulos = modulos_permitidos
        self.stack = stack
        
        self.setObjectName("mainSidebar")
        self.setFixedWidth(240)

        self._setup_ui()
        
        if self.stack:
            self.stack.currentChanged.connect(self.on_view_changed)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- INICIO DE LA CORRECCIÓN ---
        # El bucle ahora desempaca 4 valores. Usamos '_' para ignorar el último, que no se usa aquí.
        for nombre, icono, index, _nombre_interno in self.modulos:
        # --- FIN DE LA CORRECCIÓN ---
            button = QPushButton(f"  {icono} {nombre}")
            button.setObjectName("sidebarButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, idx=index: self.stack.setCurrentIndex(idx))
            layout.addWidget(button)
            
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def on_view_changed(self, index: int):
        """
        Cada vez que el usuario cambia de módulo, llama al método 'actualizar_vista' del widget
        correspondiente si este existe.
        """
        widget_actual = self.stack.widget(index)
        if hasattr(widget_actual, 'actualizar_vista'):
            print(f"Refrescando vista para: {widget_actual.__class__.__name__}")
            widget_actual.actualizar_vista()