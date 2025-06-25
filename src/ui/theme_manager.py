# src/ui/theme_manager.py

import os
import json
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream

class ThemeManager:
    CONFIG_FILE = "config.json"
    
    def __init__(self, app: QApplication):
        self.app = app
        self.current_theme = self.load_theme_preference()
        self.apply_theme()

    def load_stylesheet(self, theme_name: str) -> str:
        """Carga el contenido de un archivo QSS desde la carpeta de assets principal."""
        
        # --- INICIO DE LA CORRECCIÓN ---
        # La ruta base ahora apunta a la raíz del proyecto, saliendo de 'src/ui'
        # __file__ es '.../src/ui/theme_manager.py'
        # os.path.dirname(__file__) es '.../src/ui'
        # os.path.join(..., '..', '..') nos lleva a la raíz del proyecto
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        qss_path = os.path.join(base_path, "assets", "styles", f"{theme_name}.qss")
        # --- FIN DE LA CORRECCIÓN ---
        
        print(f"Buscando hoja de estilos en: {qss_path}") # Mensaje de depuración
        
        file = QFile(qss_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            stylesheet = stream.readAll()
            file.close()
            return stylesheet
        else:
            print(f"⚠️ No se pudo encontrar o abrir el archivo de estilos: {qss_path}")
        return ""

    def apply_theme(self):
        """Aplica el tema actual a la aplicación."""
        print(f"🎨 Aplicando tema: '{self.current_theme}'")
        stylesheet = self.load_stylesheet(self.current_theme)
        if stylesheet:
            self.app.setStyleSheet(stylesheet)
        else:
            print(f"No se aplicó ningún estilo porque el archivo para el tema '{self.current_theme}' está vacío o no se encontró.")


    def toggle_theme(self):
        """Cambia entre el tema claro y oscuro."""
        if self.current_theme == "global":
            self.current_theme = "dark"
        else:
            self.current_theme = "global"
        
        self.apply_theme()
        self.save_theme_preference()

    def save_theme_preference(self):
        """Guarda el tema seleccionado en un archivo de configuración."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"Error al guardar la preferencia de tema: {e}")

    def load_theme_preference(self) -> str:
        """Carga la preferencia de tema desde el archivo de configuración."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get("theme", "global")
        except Exception as e:
            print(f"Error al cargar la preferencia de tema: {e}")
        return "global"