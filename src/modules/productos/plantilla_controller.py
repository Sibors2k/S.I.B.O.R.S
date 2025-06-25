# src/modules/productos/plantilla_controller.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import distinct
from typing import List, Dict, Any, Optional, Set, Tuple
import os
import shutil
import csv
from datetime import datetime
from collections import defaultdict
import math

from .models import (
    ProductoPlantilla, Producto, MovimientoStock, TipoAjusteStock,
    ProductoImagen, KitComponente
)
from modules.variantes.variantes_model import Atributo, AtributoValor
from modules.categorias.categoria_model import Categoria
from modules.proveedores.proveedor_model import Proveedor
from utils import validators

class PlantillaController:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.imagenes_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "product_images"))
        os.makedirs(self.imagenes_dir, exist_ok=True)

    def calcular_stock_disponible_kit(self, plantilla_id: int) -> int:
        plantilla = self.db.query(ProductoPlantilla).options(
            joinedload(ProductoPlantilla.componentes).joinedload(KitComponente.componente)
        ).filter(ProductoPlantilla.id == plantilla_id).first()

        if not plantilla or not plantilla.componentes:
            return 0

        kits_posibles = []
        for item_kit in plantilla.componentes:
            if not item_kit.componente or item_kit.cantidad <= 0:
                return 0
            
            stock_componente = item_kit.componente.stock
            cantidad_necesaria = item_kit.cantidad
            
            kits_posibles.append(stock_componente // cantidad_necesaria)

        return min(kits_posibles) if kits_posibles else 0

    def listar_plantillas(self, filtro: Optional[str] = None, categoria_id: Optional[int] = None) -> List[ProductoPlantilla]:
        query = self.db.query(ProductoPlantilla).options(
            joinedload(ProductoPlantilla.categoria), 
            joinedload(ProductoPlantilla.proveedor), 
            joinedload(ProductoPlantilla.variantes), 
            joinedload(ProductoPlantilla.imagenes),
            joinedload(ProductoPlantilla.componentes).joinedload(KitComponente.componente)
        )
        if filtro:
            termino_busqueda = f"%{filtro.lower()}%"
            query = query.filter(ProductoPlantilla.nombre.ilike(termino_busqueda))
        if categoria_id:
            ids_a_filtrar = self._get_all_child_category_ids(categoria_id)
            query = query.filter(ProductoPlantilla.categoria_id.in_(ids_a_filtrar))
            
        return query.order_by(ProductoPlantilla.nombre).all()

    def crear_plantilla_con_variantes(self, datos_plantilla: Dict[str, Any], lista_variantes: List[Dict[str, Any]], usuario_id: int, componentes: List[Dict] = []):
        if not datos_plantilla.get("nombre"): raise ValueError("El nombre del producto es obligatorio.")
        if self.db.query(ProductoPlantilla).filter(ProductoPlantilla.nombre.ilike(datos_plantilla["nombre"])).first(): raise ValueError(f"Ya existe un producto con el nombre '{datos_plantilla['nombre']}'.")
        try:
            imagenes_a_agregar = datos_plantilla.pop("imagenes_a_agregar", [])
            imagenes_a_eliminar = datos_plantilla.pop("imagenes_a_eliminar", [])
            nueva_plantilla = ProductoPlantilla(nombre=datos_plantilla["nombre"], categoria_id=datos_plantilla.get("categoria_id"), proveedor_id=datos_plantilla.get("proveedor_id"))
            self.db.add(nueva_plantilla)
            self.db.flush() 
            if imagenes_a_agregar or imagenes_a_eliminar: self._gestionar_imagenes(nueva_plantilla, imagenes_a_agregar, imagenes_a_eliminar)
            for datos_variante in lista_variantes:
                sku = datos_variante.get("sku")
                if not sku: raise ValueError("Todas las variantes activadas deben tener un SKU.")
                if self.db.query(Producto).filter(Producto.sku.ilike(sku)).first(): raise ValueError(f"El SKU '{sku}' ya está en uso.")
                stock_inicial = int(datos_variante.get("stock", 0))

                nueva_variante = Producto(
                    plantilla_id=nueva_plantilla.id, 
                    sku=sku, 
                    precio_venta=float(datos_variante.get("precio_venta", 0.0)), 
                    stock=stock_inicial, 
                    costo_compra=datos_variante.get("costo_compra")
                )

                ids_valores = datos_variante.get("ids_valores", [])
                if ids_valores:
                    valores_obj = self.db.query(AtributoValor).filter(AtributoValor.id.in_(ids_valores)).all()
                    if len(valores_obj) != len(ids_valores): raise ValueError("Uno o más valores de atributo no son válidos.")
                    nueva_variante.valores.extend(valores_obj)
                self.db.add(nueva_variante)
                if stock_inicial > 0:
                    self.db.flush()
                    movimiento = MovimientoStock(producto_id=nueva_variante.id, usuario_id=usuario_id, tipo_ajuste=TipoAjusteStock.ENTRADA_MANUAL, cantidad=stock_inicial, motivo="Stock Inicial de Creación de Producto", stock_anterior=0, stock_nuevo=stock_inicial)
                    self.db.add(movimiento)
            if componentes:
                for comp_data in componentes:
                    componente = KitComponente(kit_plantilla_id=nueva_plantilla.id, componente_id=comp_data["componente_id"], cantidad=comp_data["cantidad"])
                    self.db.add(componente)
            self.db.commit()
            self.db.refresh(nueva_plantilla)
            return nueva_plantilla
        except Exception as e:
            self.db.rollback()
            raise e

    def exportar_plantillas_a_csv(self, ruta_archivo: str):
        try:
            plantillas = self.db.query(ProductoPlantilla).options(
                joinedload(ProductoPlantilla.categoria),
                joinedload(ProductoPlantilla.proveedor),
                joinedload(ProductoPlantilla.variantes).joinedload(Producto.valores).joinedload(AtributoValor.atributo),
                joinedload(ProductoPlantilla.componentes).joinedload(KitComponente.componente)
            ).order_by(ProductoPlantilla.nombre).all()

            with open(ruta_archivo, 'w', newline='', encoding='utf-8-sig') as archivo_csv:
                escritor = csv.writer(archivo_csv)
                encabezado = [
                    'plantilla_nombre', 'categoria_ruta', 'proveedor_nombre', 'tipo_producto',
                    'variante_sku', 'variante_precio', 'variante_costo', 'variante_stock',
                    'variante_atributos', 'kit_componentes'
                ]
                escritor.writerow(encabezado)

                for p in plantillas:
                    for v in p.variantes:
                        if p.componentes: tipo_producto = "Kit"
                        elif len(p.variantes) > 1: tipo_producto = "Variante"
                        else: tipo_producto = "Simple"

                        categoria_ruta = self._get_ruta_categoria(p.categoria) if p.categoria else ""
                        atributos = " | ".join(sorted([f"{val.atributo.nombre}:{val.valor}" for val in v.valores]))
                        
                        componentes_kit = " | ".join(sorted([f"{comp.componente.sku}:{comp.cantidad}" for comp in p.componentes if comp.componente is not None])) if tipo_producto == "Kit" else ""

                        fila = [
                            p.nombre,
                            categoria_ruta,
                            p.proveedor.nombre_empresa if p.proveedor else "",
                            tipo_producto,
                            v.sku,
                            v.precio_venta,
                            v.costo_compra if v.costo_compra is not None else "",
                            v.stock,
                            atributos,
                            componentes_kit
                        ]
                        escritor.writerow(fila)
            print(f"Exportación completada exitosamente en: {ruta_archivo}")

        except Exception as e:
            print(f"Error durante la exportación a CSV: {e}")
            raise

    def analizar_csv_para_importacion(self, ruta_archivo: str) -> List[Dict]:
        resultados = []
        try:
            with open(ruta_archivo, mode='r', encoding='utf-8-sig') as archivo_csv:
                lector = csv.DictReader(archivo_csv)
                
                categorias_db = self.db.query(Categoria).all()
                proveedores_db = self.db.query(Proveedor).all()
                
                cache = {
                    'categorias': {cat.nombre.lower(): cat for cat in categorias_db},
                    'proveedores': {prov.nombre_empresa.lower(): prov for prov in proveedores_db},
                    'skus': {p.sku.lower() for p in self.db.query(Producto).all()},
                    'atributos': {attr.nombre.lower(): attr for attr in self.db.query(Atributo).options(joinedload(Atributo.valores)).all()}
                }
                
                for i, fila in enumerate(lector):
                    datos_fila, errores = self._validar_fila_importacion(fila, cache)
                    estado = 'ERROR'
                    if not errores:
                        sku_lower = datos_fila.get('variante_sku', '').lower()
                        if sku_lower in cache['skus']:
                            estado = 'OK_ACTUALIZAR'
                        else:
                            estado = 'OK_NUEVO'
                    
                    resultados.append({"numero_fila": i + 2, "datos": datos_fila, "estado": estado, "errores": errores})
            return resultados
        except Exception as e:
            raise ValueError(f"Error al leer o procesar el archivo CSV: {e}")

    def _validar_fila_importacion(self, fila: Dict, cache: Dict) -> Tuple[Dict, List[str]]:
        errores = []
        
        nombre_plantilla = fila.get('plantilla_nombre', '').strip()
        sku_variante = fila.get('variante_sku', '').strip()
        
        fila['plantilla_nombre'] = nombre_plantilla
        fila['variante_sku'] = sku_variante

        if not nombre_plantilla: errores.append("El 'plantilla_nombre' es obligatorio.")
        if not sku_variante: errores.append("El 'variante_sku' es obligatorio.")
        
        try:
            fila['variante_precio'] = float(fila.get('variante_precio', 0.0))
            fila['variante_stock'] = int(fila.get('variante_stock', 0))
            costo_str = fila.get('variante_costo')
            fila['variante_costo'] = float(costo_str) if costo_str else None
        except (ValueError, TypeError):
            errores.append("Precio, costo o stock tienen un formato numérico inválido.")
            
        ruta_cat = fila.get('categoria_ruta', '').strip()
        if ruta_cat:
            nombre_cat_final = ruta_cat.split('/')[-1].strip().lower()
            if nombre_cat_final not in cache['categorias']:
                errores.append(f"La categoría '{ruta_cat.split('/')[-1].strip()}' no fue encontrada.")

        nombre_prov = fila.get('proveedor_nombre', '').strip()
        if nombre_prov and nombre_prov.lower() not in cache['proveedores']:
            errores.append(f"El proveedor '{nombre_prov}' no fue encontrado.")
            
        atributos_str = fila.get('variante_atributos', '').strip()
        if atributos_str:
            pares = [par.strip() for par in atributos_str.split('|')]
            for par in pares:
                if ':' not in par:
                    errores.append(f"El formato del atributo '{par}' es inválido (debe ser 'Nombre:Valor').")
                    continue
                nombre_attr, valor_attr = [p.strip() for p in par.split(':', 1)]
                
                if nombre_attr.lower() not in cache['atributos']:
                    errores.append(f"El atributo '{nombre_attr}' no existe.")
                else:
                    attr_obj = cache['atributos'][nombre_attr.lower()]
                    valores_existentes = {v.valor.lower() for v in attr_obj.valores}
                    if valor_attr.lower() not in valores_existentes:
                        errores.append(f"El valor '{valor_attr}' no existe para el atributo '{nombre_attr}'.")

        return fila, errores
    
    def _find_category_by_path(self, ruta_completa: str) -> Optional[Categoria]:
        nombre_final = ruta_completa.split('/')[-1].strip()
        return self.db.query(Categoria).filter(Categoria.nombre.ilike(nombre_final)).first()

    def _find_provider_by_name(self, nombre: str) -> Optional[Proveedor]:
        if not nombre:
            return None
        return self.db.query(Proveedor).filter(Proveedor.nombre_empresa.ilike(nombre)).first()
        
    def ejecutar_importacion(self, filas_validadas: List[Dict], usuario_id: int):
        plantillas_a_procesar = defaultdict(list)
        for fila in filas_validadas:
            plantillas_a_procesar[fila['datos']['plantilla_nombre']].append(fila)
        try:
            for nombre_plantilla, filas_variantes in plantillas_a_procesar.items():
                primera_fila = filas_variantes[0]['datos']
                plantilla_existente = self.db.query(ProductoPlantilla).filter(ProductoPlantilla.nombre.ilike(nombre_plantilla)).first()
                if not plantilla_existente:
                    categoria_obj = self._find_category_by_path(primera_fila['categoria_ruta'])
                    proveedor_obj = self._find_provider_by_name(primera_fila['proveedor_nombre'])
                    plantilla_obj = ProductoPlantilla(nombre=nombre_plantilla, categoria_id=categoria_obj.id if categoria_obj else None, proveedor_id=proveedor_obj.id if proveedor_obj else None)
                    self.db.add(plantilla_obj)
                    self.db.flush()
                else:
                    plantilla_obj = plantilla_existente
                
                for fila_variante_data in filas_variantes:
                    if fila_variante_data['datos']['plantilla_nombre'] != nombre_plantilla:
                        continue

                    estado = fila_variante_data['estado']
                    datos = fila_variante_data['datos']
                    sku = datos['variante_sku']
                    if estado == 'OK_NUEVO':
                        nueva_variante = Producto(plantilla_id=plantilla_obj.id, sku=sku, precio_venta=datos['variante_precio'], costo_compra=datos['variante_costo'], stock=datos['variante_stock'])
                        self.db.add(nueva_variante)
                        if datos['variante_stock'] > 0:
                            self.db.flush()
                            mov = MovimientoStock(producto_id=nueva_variante.id, usuario_id=usuario_id, tipo_ajuste=TipoAjusteStock.ENTRADA_MANUAL, cantidad=datos['variante_stock'], motivo=f"Importación masiva desde CSV", stock_anterior=0, stock_nuevo=datos['variante_stock'])
                            self.db.add(mov)
                    elif estado == 'OK_ACTUALIZAR':
                        variante_a_actualizar = self.db.query(Producto).filter(Producto.sku.ilike(sku)).one()
                        stock_anterior = variante_a_actualizar.stock
                        nuevo_stock = datos['variante_stock']
                        variante_a_actualizar.precio_venta = datos['variante_precio']
                        variante_a_actualizar.costo_compra = datos['variante_costo']
                        if nuevo_stock != stock_anterior:
                            variante_a_actualizar.stock = nuevo_stock
                            mov = MovimientoStock(producto_id=variante_a_actualizar.id, usuario_id=usuario_id, tipo_ajuste=TipoAjusteStock.AJUSTE_CONTEO_POSITIVO, cantidad=(nuevo_stock - stock_anterior), motivo=f"Ajuste por importación masiva desde CSV", stock_anterior=stock_anterior, stock_nuevo=nuevo_stock)
                            self.db.add(mov)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"ERROR FATAL DURANTE LA IMPORTACIÓN, SE HA HECHO ROLLBACK: {e}")
            raise ValueError(f"No se pudo completar la importación. Error: {e}")

    def get_ids_de_categorias_relevantes(self) -> Set[int]:
        categorias_con_productos_directos = self.db.query(distinct(ProductoPlantilla.categoria_id)).filter(ProductoPlantilla.categoria_id.isnot(None)).all()
        ids_con_productos = {id[0] for id in categorias_con_productos_directos}
        todas_las_categorias = self.db.query(Categoria).all()
        mapa_categorias = {cat.id: cat for cat in todas_las_categorias}
        ids_relevantes = set(ids_con_productos)
        for cat_id in ids_con_productos:
            actual = mapa_categorias.get(cat_id)
            while actual and actual.categoria_padre_id:
                ids_relevantes.add(actual.categoria_padre_id)
                actual = mapa_categorias.get(actual.categoria_padre_id)
        return ids_relevantes
        
    def _get_all_child_category_ids(self, categoria_id: int) -> List[int]:
        ids = {categoria_id}
        categoria = self.db.query(Categoria).options(joinedload(Categoria.subcategorias)).get(categoria_id)
        if categoria:
            for sub_cat in categoria.subcategorias:
                ids.update(self._get_all_child_category_ids(sub_cat.id))
        return list(ids)
    
    def actualizar_plantilla_con_variantes(self, plantilla_id: int, datos_plantilla: Dict[str, Any], lista_variantes_ui: List[Dict[str, Any]], componentes: List[Dict] = []):
        try:
            plantilla = self.db.query(ProductoPlantilla).options(joinedload(ProductoPlantilla.variantes), joinedload(ProductoPlantilla.componentes)).filter_by(id=plantilla_id).first()
            if not plantilla: raise ValueError("La plantilla del producto no fue encontrada.")
            
            plantilla.nombre = datos_plantilla["nombre"]
            plantilla.categoria_id = datos_plantilla.get("categoria_id")
            plantilla.proveedor_id = datos_plantilla.get("proveedor_id")
            
            imagenes_a_agregar = datos_plantilla.pop("imagenes_a_agregar", [])
            imagenes_a_eliminar = datos_plantilla.pop("imagenes_a_eliminar", [])
            if imagenes_a_agregar or imagenes_a_eliminar: self._gestionar_imagenes(plantilla, imagenes_a_agregar, imagenes_a_eliminar)

            variantes_en_db_map = {v.id: v for v in plantilla.variantes}
            ids_variantes_ui = {v['id'] for v in lista_variantes_ui if v.get('id')}

            for datos_variante in lista_variantes_ui:
                variante_id = datos_variante.get("id")
                sku = datos_variante["sku"]
                if not sku: raise ValueError("El SKU es obligatorio para todas las variantes.")
                
                conflicting_sku = self.db.query(Producto).filter(Producto.sku.ilike(sku), Producto.id != variante_id).first()
                if conflicting_sku: raise ValueError(f"El SKU '{sku}' ya está en uso por otro producto.")

                if variante_id in variantes_en_db_map:
                    variante_a_actualizar = variantes_en_db_map[variante_id]
                    variante_a_actualizar.sku = sku
                    variante_a_actualizar.precio_venta = float(datos_variante["precio_venta"])
                    variante_a_actualizar.costo_compra = datos_variante.get("costo_compra")
                else: 
                    nueva_variante = Producto(plantilla_id=plantilla.id, sku=sku, precio_venta=float(datos_variante["precio_venta"]), costo_compra=datos_variante.get("costo_compra"), stock=int(datos_variante["stock"]))
                    ids_valores = datos_variante.get("ids_valores", [])
                    if ids_valores:
                        valores_obj = self.db.query(AtributoValor).filter(AtributoValor.id.in_(ids_valores)).all()
                        nueva_variante.valores.extend(valores_obj)
                    self.db.add(nueva_variante)

            for id_db, variante_db in variantes_en_db_map.items():
                if id_db not in ids_variantes_ui:
                    if variante_db.stock > 0: raise ValueError(f"No se puede eliminar la variante con SKU '{variante_db.sku}' porque tiene stock.")
                    self.db.delete(variante_db)

            plantilla.componentes.clear()
            self.db.flush()
            if componentes:
                for comp_data in componentes:
                    componente_obj = KitComponente(kit_plantilla_id=plantilla.id, componente_id=comp_data["componente_id"], cantidad=comp_data["cantidad"])
                    self.db.add(componente_obj)
            
            self.db.commit()
            self.db.refresh(plantilla)
            return plantilla
        except Exception as e:
            self.db.rollback()
            raise e
            
    def _gestionar_imagenes(self, plantilla: ProductoPlantilla, agregar: List[str], eliminar: List[ProductoImagen]):
        for img_obj in eliminar:
            img_a_borrar = self.db.merge(img_obj)
            if img_a_borrar.ruta_imagen and os.path.exists(img_a_borrar.ruta_imagen): os.remove(img_a_borrar.ruta_imagen)
            self.db.delete(img_a_borrar)
        self.db.flush()
        for i, ruta_origen in enumerate(agregar):
            if not os.path.exists(ruta_origen): continue
            try:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                _root, extension = os.path.splitext(ruta_origen)
                contador_img = len(plantilla.imagenes) + i + 1
                nombre_base = f"plantilla_{plantilla.id}_{timestamp}_{contador_img}"
                nuevo_nombre_archivo = f"{nombre_base}{extension}"
                ruta_destino = os.path.join(self.imagenes_dir, nuevo_nombre_archivo)
                shutil.copy2(ruta_origen, ruta_destino)
                nueva_imagen = ProductoImagen(plantilla_id=plantilla.id, ruta_imagen=ruta_destino, orden=contador_img)
                self.db.add(nueva_imagen)
                self.db.flush()
            except Exception as e:
                print(f"Error crítico al procesar la imagen {ruta_origen}: {e}")
                continue
                
    def eliminar_plantilla(self, plantilla_id: int) -> bool:
        plantilla = self.db.query(ProductoPlantilla).options(joinedload(ProductoPlantilla.variantes)).filter_by(id=plantilla_id).first()
        if not plantilla: return True
        
        # --- INICIO DE LA MODIFICACIÓN ---
        # Se corrige la referencia de self.componentes a plantilla.componentes
        stock_total = 0
        if plantilla.componentes: # Si es un kit, el stock es calculado.
            stock_total = self.calcular_stock_disponible_kit(plantilla.id)
        else: # Si no es un kit, es la suma del stock de sus variantes
            stock_total = sum(variante.stock for variante in plantilla.variantes)
        # --- FIN DE LA MODIFICACIÓN ---
        
        if stock_total > 0: raise ValueError("No se puede eliminar el producto porque una o más de sus variantes (o componentes de kit) tienen existencias en el inventario.")
        
        for img in plantilla.imagenes:
            if img.ruta_imagen and os.path.exists(img.ruta_imagen):
                try:
                    os.remove(img.ruta_imagen)
                except OSError as e:
                    print(f"No se pudo eliminar la imagen {img.ruta_imagen}: {e}")

        self.db.delete(plantilla)
        self.db.commit()
        return True

    def _get_ruta_categoria(self, categoria: Categoria) -> str:
        partes_ruta = []
        actual = categoria
        while actual:
            partes_ruta.append(actual.nombre)
            actual = actual.padre
        return " / ".join(reversed(partes_ruta))