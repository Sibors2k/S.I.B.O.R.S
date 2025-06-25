# src/modules/perfil/perfil_controller.py

import os
from PIL import Image
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session

from modules.usuarios.usuarios_model import Usuario
from .perfil_model import Perfil

class PerfilController:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.avatares_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "assets", "avatares"
        ))
        os.makedirs(self.avatares_dir, exist_ok=True)

    def obtener_perfil(self, usuario_id: int) -> Optional[Perfil]:
        perfil = self.db.query(Perfil).filter_by(usuario_id=usuario_id).first()
        if not perfil:
            usuario = self.db.get(Usuario, usuario_id)
            if not usuario: return None
            
            perfil = Perfil(
                usuario_id=usuario_id,
                nombre=usuario.nombre,
            )
            self.db.add(perfil)
            self.db.commit()
            self.db.refresh(perfil)
        return perfil

    def actualizar_perfil(self, usuario_id: int, datos: Dict) -> Perfil:
        perfil = self.obtener_perfil(usuario_id)
        if not perfil:
            raise ValueError("No se pudo encontrar o crear el perfil para este usuario.")

        for key, value in datos.items():
            if hasattr(perfil, key):
                setattr(perfil, key, value)
        
        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def guardar_avatar(self, usuario_id: int, archivo_origen: str) -> Optional[str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = os.path.splitext(archivo_origen)[1].lower() or '.jpg'
        nombre_archivo = f"avatar_{usuario_id}_{timestamp}{extension}"
        ruta_destino = os.path.join(self.avatares_dir, nombre_archivo)

        with Image.open(archivo_origen) as img:
            img.thumbnail((250, 250), Image.Resampling.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(ruta_destino, 'JPEG', quality=85)

        perfil = self.obtener_perfil(usuario_id)
        if perfil:
            if perfil.avatar_path and os.path.exists(perfil.avatar_path):
                os.remove(perfil.avatar_path)
            
            perfil.avatar_path = ruta_destino
            self.db.commit()
            return ruta_destino
        return None