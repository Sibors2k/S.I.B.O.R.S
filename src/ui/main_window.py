# src/ui/main_window.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from sqlalchemy.orm import Session as SQLAlchemySession

from modules.categorias.categoria_controller import CategoriaController
from modules.roles.roles_controller import RolesController
from modules.usuarios.usuarios_controller import UsuariosController
from modules.proveedores.proveedor_controller import ProveedorController
from modules.clientes.cliente_controller import ClienteController
from modules.productos.producto_controller import ProductoController
from modules.productos.plantilla_controller import PlantillaController
from modules.contabilidad.contabilidad_controller import ContabilidadController
from modules.ventas.ventas_controller import VentasController
# --- INICIO DE LA MODIFICACIÓN ---
# Se añade la importación que faltaba para el CompraController
from modules.compras.compra_controller import CompraController
# --- FIN DE LA MODIFICACIÓN ---
from modules.dashboard.dashboard_controller import DashboardController
from modules.empresa.empresa_controller import EmpresaController
from modules.perfil.perfil_controller import PerfilController
from modules.reportes.reportes_controller import ReportesController
from modules.variantes.variantes_controller import VariantesController

from modules.categorias.categoria_ui import CategoriaWidget
from modules.dashboard.dashboard_ui import DashboardUI
from modules.proveedores.proveedor_ui import ProveedorWidget
from modules.clientes.cliente_ui import ClienteWidget
from modules.productos.producto_ui import ProductoWidget
from modules.ventas.ventas_ui import VentasWidget
from modules.compras.compra_ui import CompraWidget
from modules.contabilidad.contabilidad_ui import ContabilidadWidget
from modules.usuarios.usuarios_ui import UsuariosWindow
from modules.roles.roles_ui import RolesWidget, MODULOS_DISPONIBLES
from modules.empresa.empresa_ui import EmpresaWidget
from modules.perfil.perfil_ui import PerfilWidget
from modules.reportes.reportes_ui import ReportesWidget
from modules.variantes.variantes_ui import VariantesWidget
from ui.components.main_sidebar import MainSidebar
from ui.components.main_header import MainHeader
from ui.components.main_content import MainContent

class MainWindow(QWidget):
    def __init__(self, usuario, db_session: SQLAlchemySession):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("S.I.B.O.R.S. - Sistema Integral de Operaciones")
        self.db_session = db_session
        
        self._inicializar_controladores()
        self._setup_ui()
        
    def _inicializar_controladores(self):
        self.categoria_ctrl = CategoriaController(self.db_session)
        self.roles_ctrl = RolesController(self.db_session)
        self.usuario_ctrl = UsuariosController(self.db_session)
        self.proveedor_ctrl = ProveedorController(self.db_session)
        self.cliente_ctrl = ClienteController(self.db_session)
        self.producto_ctrl = ProductoController(self.db_session)
        self.plantilla_ctrl = PlantillaController(self.db_session)
        self.variantes_ctrl = VariantesController(self.db_session)
        self.contabilidad_ctrl = ContabilidadController(self.db_session)
        self.ventas_ctrl = VentasController(self.db_session, self.producto_ctrl, self.contabilidad_ctrl, self.cliente_ctrl)
        self.compra_ctrl = CompraController(self.db_session, self.producto_ctrl, self.contabilidad_ctrl)
        self.dashboard_ctrl = DashboardController(self.contabilidad_ctrl, self.ventas_ctrl, self.producto_ctrl)
        self.empresa_ctrl = EmpresaController(self.db_session)
        self.perfil_ctrl = PerfilController(self.db_session)
        self.reportes_ctrl = ReportesController(self.ventas_ctrl, self.producto_ctrl, self.empresa_ctrl)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.content_area = MainContent(self)
        self.stack = self.content_area.get_stack()
        
        self.vistas_permitidas = []
        self.vistas_creadas = {}
        
        self.stack.currentChanged.connect(self._on_view_changed)

        self._crear_vistas_modulos()
        
        self.sidebar = MainSidebar(self.vistas_permitidas, self.stack, self)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.header = MainHeader(self.usuario, on_profile_click=lambda: self.cambiar_vista_a("perfil"), on_logout_click=self.close, parent=self)
        
        right_layout.addWidget(self.header)
        right_layout.addWidget(self.content_area)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_panel, 1)

    def _crear_vistas_modulos(self):
        permisos_usuario = self.usuario.rol_asignado.obtener_permisos_como_lista()
        modulos_config = {
            "dashboard": {"label": "📊 Dashboard", "creator": lambda: DashboardUI(self.dashboard_ctrl)},
            "categorias": {"label": "🗂️ Categorías", "creator": lambda: CategoriaWidget(self.categoria_ctrl)},
            "variantes": {"label": "🧬 Atributos y Variantes", "creator": lambda: VariantesWidget(self.variantes_ctrl)},
            "proveedores": {"label": "🚚 Proveedores", "creator": lambda: ProveedorWidget(self.proveedor_ctrl)},
            "clientes": {"label": "👥 Clientes", "creator": lambda: ClienteWidget(self.cliente_ctrl)},
            "productos": {"label": "📦 Productos", "creator": lambda: ProductoWidget(self.plantilla_ctrl, self.producto_ctrl, self.proveedor_ctrl, self.categoria_ctrl, self.variantes_ctrl, self.usuario)},
            "ventas": {"label": "🛒 Ventas", "creator": lambda: VentasWidget(self.ventas_ctrl, self.cliente_ctrl, self.producto_ctrl, self.categoria_ctrl, self.usuario)},
            "compras": {"label": "🛍️ Compras", "creator": lambda: CompraWidget(self.compra_ctrl, self.proveedor_ctrl, self.producto_ctrl)},
            "contabilidad": {"label": "🧾 Contabilidad", "creator": lambda: ContabilidadWidget(self.contabilidad_ctrl)},
            "reportes": {"label": "📈 Reportes", "creator": lambda: ReportesWidget(self.reportes_ctrl)},
            "usuarios": {"label": "👤 Usuarios", "creator": lambda: UsuariosWindow(self.usuario_ctrl, self.roles_ctrl)},
            "roles": {"label": "🔑 Roles", "creator": lambda: RolesWidget(self.roles_ctrl)},
            "empresa": {"label": "🏢 Empresa", "creator": lambda: EmpresaWidget(self.empresa_ctrl)},
            "perfil": {"label": "👤 Mi Perfil", "creator": lambda: PerfilWidget(self.perfil_ctrl, self.usuario)},
        }
        
        for nombre_permiso in MODULOS_DISPONIBLES:
            if nombre_permiso in permisos_usuario and nombre_permiso in modulos_config:
                config = modulos_config[nombre_permiso]
                if nombre_permiso not in self.vistas_creadas:
                    vista_widget = config["creator"]()
                    self.vistas_creadas[nombre_permiso] = {"widget": vista_widget, "nombre": nombre_permiso}
                    index = self.stack.addWidget(vista_widget)
                    self.vistas_permitidas.append((config["label"], "", index, nombre_permiso))

    def cambiar_vista_a(self, nombre_modulo: str):
        for _label, _icono, index, nombre in self.vistas_permitidas:
            if nombre == nombre_modulo:
                self.stack.setCurrentIndex(index)
                return

    def _on_view_changed(self, index):
        widget_actual_info = None
        for info in self.vistas_creadas.values():
            if self.stack.widget(index) == info["widget"]:
                widget_actual_info = info
                break
        
        if widget_actual_info:
            nombre_modulo = widget_actual_info["nombre"]
            widget = widget_actual_info["widget"]
            
            if hasattr(widget, 'reset_view'):
                print(f"INFO: Reseteando vista para el módulo '{nombre_modulo}'.")
                widget.reset_view()
            elif hasattr(widget, 'actualizar_vista'):
                print(f"INFO: Actualizando vista para el módulo '{nombre_modulo}'.")
                widget.actualizar_vista()

    def closeEvent(self, event):
        print("INFO: MainWindow cerrándose.")
        super().closeEvent(event)