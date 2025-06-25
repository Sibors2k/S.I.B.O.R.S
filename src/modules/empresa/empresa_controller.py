# src/modules/empresa/empresa_controller.py

from typing import Optional
from sqlalchemy.orm import Session
from .empresa_model import EmpresaData, Empresa
from utils import validators

class EmpresaValidationError(ValueError):
    pass

class EmpresaController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def obtener_datos_empresa(self) -> Optional[EmpresaData]:
        empresa_orm = self.db.query(Empresa).first()
        if empresa_orm:
            return EmpresaData(**{c.name: getattr(empresa_orm, c.name) for c in empresa_orm.__table__.columns})
        return None

    def guardar_datos_empresa(self, datos: EmpresaData) -> EmpresaData:
        self._validar_datos(datos)
        datos_sanitizados = self._sanitizar_datos(datos)
        
        empresa_orm = self.db.query(Empresa).first()
        if empresa_orm:
            # --- INICIO DE LA CORRECCIÓN ---
            # Al actualizar, solo modificamos los campos que no son None
            # para no borrar datos existentes con valores vacíos.
            for key, value in datos_sanitizados.__dict__.items():
                if key != 'id' and value is not None and hasattr(empresa_orm, key):
                    setattr(empresa_orm, key, value)
            # --- FIN DE LA CORRECCIÓN ---
        else:
            empresa_orm = Empresa(**datos_sanitizados.__dict__)
            self.db.add(empresa_orm)
        
        self.db.commit()
        self.db.refresh(empresa_orm)
        return EmpresaData(**{c.name: getattr(empresa_orm, c.name) for c in empresa_orm.__table__.columns})

    def _validar_datos(self, datos: EmpresaData):
        # La validación existente es correcta. No necesita cambios.
        if not validators.validar_longitud(datos.nombre, minimo=3):
            raise EmpresaValidationError("El nombre de la empresa es obligatorio (mínimo 3 caracteres).")
        if datos.rfc and not validators.validar_rfc(datos.rfc):
            raise EmpresaValidationError("El formato del RFC no es válido.")
        if datos.correo_principal and not validators.validar_email(datos.correo_principal):
            raise EmpresaValidationError("El formato del correo electrónico principal no es válido.")
        if datos.curp_representante and not validators.validar_curp(datos.curp_representante):
            raise EmpresaValidationError("El CURP del representante no tiene un formato válido.")

    def _sanitizar_datos(self, datos: EmpresaData) -> EmpresaData:
        # La sanitización existente es correcta.
        if datos.nombre:
            datos.nombre = validators.sanitizar_string(datos.nombre)
        if datos.rfc:
            datos.rfc = validators.sanitizar_a_mayusculas(datos.rfc)
        if datos.curp_representante:
            datos.curp_representante = validators.sanitizar_a_mayusculas(datos.curp_representante)
        return datos