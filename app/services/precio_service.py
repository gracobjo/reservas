from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ..models.precio import Precio, TipoPrecio, Moneda
from ..models.servicio import Servicio
from ..models.recurso import Recurso
from ..schemas.precio import (
    PrecioCreate, PrecioUpdate, CalculoPrecioRequest, 
    CalculoPrecioResponse, FiltroPrecios
)

class PrecioService:
    """Servicio para gestión completa de precios"""
    
    @staticmethod
    def create_precio(db: Session, precio: PrecioCreate) -> Precio:
        """Crear un nuevo precio"""
        try:
            # Validar que se especifique servicio_id o recurso_id
            if not precio.servicio_id and not precio.recurso_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Debe especificar servicio_id o recurso_id"
                )
            
            # Validar que no se especifiquen ambos
            if precio.servicio_id and precio.recurso_id:
                raise HTTPException(
                    status_code=400, 
                    detail="No puede especificar servicio_id y recurso_id al mismo tiempo"
                )
            
            # Verificar que el servicio o recurso existe
            if precio.servicio_id:
                servicio = db.query(Servicio).filter(Servicio.id == precio.servicio_id).first()
                if not servicio:
                    raise HTTPException(status_code=404, detail="Servicio no encontrado")
            
            if precio.recurso_id:
                recurso = db.query(Recurso).filter(Recurso.id == precio.recurso_id).first()
                if not recurso:
                    raise HTTPException(status_code=404, detail="Recurso no encontrado")
            
            # Convertir el modelo a dict y crear el precio
            precio_data = precio.dict()
            db_precio = Precio(**precio_data)
            db.add(db_precio)
            db.commit()
            db.refresh(db_precio)
            return db_precio
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    @staticmethod
    def get_precio(db: Session, precio_id: int) -> Precio:
        """Obtener un precio por ID"""
        db_precio = db.query(Precio).filter(Precio.id == precio_id).first()
        if db_precio is None:
            raise HTTPException(status_code=404, detail="Precio no encontrado")
        return db_precio
    
    @staticmethod
    def get_precios_by_servicio(db: Session, servicio_id: int) -> List[Precio]:
        """Obtener todos los precios de un servicio"""
        return db.query(Precio).filter(
            and_(
                Precio.servicio_id == servicio_id,
                Precio.activo == True
            )
        ).order_by(Precio.prioridad.desc(), Precio.created_at.desc()).all()
    
    @staticmethod
    def get_precios_by_recurso(db: Session, recurso_id: int) -> List[Precio]:
        """Obtener todos los precios de un recurso"""
        return db.query(Precio).filter(
            and_(
                Precio.recurso_id == recurso_id,
                Precio.activo == True
            )
        ).order_by(Precio.prioridad.desc(), Precio.created_at.desc()).all()
    
    @staticmethod
    def get_precio_base_servicio(db: Session, servicio_id: int) -> Optional[Precio]:
        """Obtener el precio base de un servicio"""
        return db.query(Precio).filter(
            and_(
                Precio.servicio_id == servicio_id,
                Precio.tipo_precio == 'base',
                Precio.activo == True
            )
        ).first()
    
    @staticmethod
    def get_precio_base_recurso(db: Session, recurso_id: int) -> Optional[Precio]:
        """Obtener el precio base de un recurso"""
        return db.query(Precio).filter(
            and_(
                Precio.recurso_id == recurso_id,
                Precio.tipo_precio == 'base',
                Precio.activo == True
            )
        ).first()
    
    @staticmethod
    def update_precio(db: Session, precio_id: int, precio: PrecioUpdate) -> Precio:
        """Actualizar un precio existente"""
        try:
            db_precio = PrecioService.get_precio(db, precio_id)
            
            update_data = precio.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_precio, field, value)
            
            db_precio.updated_at = datetime.now()
            db.commit()
            db.refresh(db_precio)
            return db_precio
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    @staticmethod
    def delete_precio(db: Session, precio_id: int) -> bool:
        """Eliminar un precio"""
        try:
            db_precio = PrecioService.get_precio(db, precio_id)
            db.delete(db_precio)
            db.commit()
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
    @staticmethod
    def listar_precios(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filtros: Optional[FiltroPrecios] = None
    ) -> List[Precio]:
        """Listar precios con filtros opcionales"""
        query = db.query(Precio)
        
        if filtros:
            if filtros.servicio_id:
                query = query.filter(Precio.servicio_id == filtros.servicio_id)
            if filtros.recurso_id:
                query = query.filter(Precio.recurso_id == filtros.recurso_id)
            if filtros.tipo_precio:
                query = query.filter(Precio.tipo_precio == filtros.tipo_precio)
            if filtros.moneda:
                query = query.filter(Precio.moneda == filtros.moneda)
            if filtros.activo is not None:
                query = query.filter(Precio.activo == filtros.activo)
            if filtros.precio_minimo:
                query = query.filter(Precio.precio_base >= filtros.precio_minimo)
            if filtros.precio_maximo:
                query = query.filter(Precio.precio_base <= filtros.precio_maximo)
            if filtros.fecha_desde:
                query = query.filter(Precio.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(Precio.fecha_fin <= filtros.fecha_hasta)
        
        return query.order_by(Precio.prioridad.desc(), Precio.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def calcular_precio(
        db: Session, 
        calculo_request: CalculoPrecioRequest
    ) -> CalculoPrecioResponse:
        """Calcular el precio final para una reserva"""
        try:
            precio_base = 0.0
            descuentos = []
            recargos = []
            reglas_aplicadas = []
            
            # Obtener precio base
            if calculo_request.servicio_id:
                precio_base = PrecioService._calcular_precio_servicio(
                    db, calculo_request.servicio_id, 
                    calculo_request.fecha_inicio, calculo_request.fecha_fin,
                    calculo_request.cantidad
                )
            elif calculo_request.recurso_id:
                precio_base = PrecioService._calcular_precio_recurso(
                    db, calculo_request.recurso_id,
                    calculo_request.fecha_inicio, calculo_request.fecha_fin,
                    calculo_request.cantidad
                )
            
            # Aplicar reglas de precio dinámico
            precio_final, descuentos, recargos, reglas_aplicadas = PrecioService._aplicar_reglas_precio(
                db, calculo_request, precio_base
            )
            
            # Crear desglose
            desglose = {
                "precio_base": precio_base,
                "descuentos_total": sum(d.get('monto', 0) for d in descuentos),
                "recargos_total": sum(r.get('monto', 0) for r in recargos),
                "precio_final": precio_final,
                "duracion_horas": (calculo_request.fecha_fin - calculo_request.fecha_inicio).total_seconds() / 3600
            }
            
            return CalculoPrecioResponse(
                precio_base=precio_base,
                precio_final=precio_final,
                descuentos=descuentos,
                recargos=recargos,
                reglas_aplicadas=reglas_aplicadas,
                desglose=desglose
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculando precio: {str(e)}")
    
    @staticmethod
    def _calcular_precio_servicio(
        db: Session, 
        servicio_id: int, 
        fecha_inicio: datetime, 
        fecha_fin: datetime, 
        cantidad: int
    ) -> float:
        """Calcular precio base de un servicio"""
        servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Obtener precio base del servicio
        precio_base = servicio.precio_base
        
        # Calcular duración en horas
        duracion_horas = (fecha_fin - fecha_inicio).total_seconds() / 3600
        
        # Para servicios, el precio base ya incluye la duración
        return precio_base * cantidad
    
    @staticmethod
    def _calcular_precio_recurso(
        db: Session, 
        recurso_id: int, 
        fecha_inicio: datetime, 
        fecha_fin: datetime, 
        cantidad: int
    ) -> float:
        """Calcular precio base de un recurso"""
        recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        # Obtener precio base del recurso
        precio_base = recurso.precio_base
        
        # Calcular duración en horas
        duracion_horas = (fecha_fin - fecha_inicio).total_seconds() / 3600
        
        # Para recursos, el precio es por hora
        return precio_base * duracion_horas * cantidad
    
    @staticmethod
    def _aplicar_reglas_precio(
        db: Session, 
        calculo_request: CalculoPrecioRequest, 
        precio_base: float
    ) -> tuple:
        """Aplicar reglas de precio dinámico"""
        descuentos = []
        recargos = []
        reglas_aplicadas = []
        precio_final = precio_base
        
        # Obtener precios aplicables
        precios_aplicables = []
        
        if calculo_request.servicio_id:
            precios = db.query(Precio).filter(
                and_(
                    Precio.servicio_id == calculo_request.servicio_id,
                    Precio.activo == True,
                    Precio.tipo_precio.in_(['descuento', 'recargo'])
                )
            ).order_by(Precio.prioridad.desc()).all()
        else:
            precios = db.query(Precio).filter(
                and_(
                    Precio.recurso_id == calculo_request.recurso_id,
                    Precio.activo == True,
                    Precio.tipo_precio.in_(['descuento', 'recargo'])
                )
            ).order_by(Precio.prioridad.desc()).all()
        
        # Aplicar cada precio
        for precio in precios:
            if PrecioService._es_precio_aplicable(precio, calculo_request):
                if precio.tipo_precio == 'descuento':
                    monto_descuento = precio.precio_base
                    descuentos.append({
                        "nombre": precio.nombre,
                        "monto": monto_descuento,
                        "descripcion": precio.descripcion
                    })
                    precio_final -= monto_descuento
                elif precio.tipo_precio == 'recargo':
                    monto_recargo = precio.precio_base
                    recargos.append({
                        "nombre": precio.nombre,
                        "monto": monto_recargo,
                        "descripcion": precio.descripcion
                    })
                    precio_final += monto_recargo
                
                reglas_aplicadas.append({
                    "id": precio.id,
                    "nombre": precio.nombre,
                    "tipo": precio.tipo_precio,
                    "monto": precio.precio_base
                })
        
        # Asegurar que el precio final no sea negativo
        precio_final = max(0, precio_final)
        
        return precio_final, descuentos, recargos, reglas_aplicadas
    
    @staticmethod
    def _es_precio_aplicable(precio: Precio, calculo_request: CalculoPrecioRequest) -> bool:
        """Verificar si un precio es aplicable a una solicitud de cálculo"""
        # Verificar fechas
        if not precio.es_valido_en_fecha(calculo_request.fecha_inicio):
            return False
        
        # Verificar cantidad
        if not precio.es_valido_para_cantidad(calculo_request.cantidad):
            return False
        
        # Verificar días de la semana
        if precio.dias_semana:
            dia_semana = str(calculo_request.fecha_inicio.isoweekday())
            if dia_semana not in precio.dias_semana.split(','):
                return False
        
        # Verificar hora
        if not precio.es_valido_en_hora(calculo_request.fecha_inicio):
            return False
        
        return True
    
    @staticmethod
    def obtener_estadisticas(db: Session) -> Dict[str, Any]:
        """Obtener estadísticas de precios"""
        total_precios = db.query(Precio).count()
        precios_activos = db.query(Precio).filter(Precio.activo == True).count()
        precios_inactivos = total_precios - precios_activos
        
        # Estadísticas de precios
        stats = db.query(
            func.avg(Precio.precio_base).label('promedio'),
            func.min(Precio.precio_base).label('minimo'),
            func.max(Precio.precio_base).label('maximo')
        ).filter(Precio.activo == True).first()
        
        # Monedas utilizadas
        monedas = db.query(Precio.moneda).distinct().all()
        monedas_utilizadas = [m[0] for m in monedas]
        
        # Tipos de precio
        tipos = db.query(Precio.tipo_precio).distinct().all()
        tipos_precio = [t[0] for t in tipos]
        
        return {
            "total_precios": total_precios,
            "precios_activos": precios_activos,
            "precios_inactivos": precios_inactivos,
            "precio_promedio": float(stats.promedio) if stats.promedio else 0.0,
            "precio_minimo": float(stats.minimo) if stats.minimo else 0.0,
            "precio_maximo": float(stats.maximo) if stats.maximo else 0.0,
            "monedas_utilizadas": monedas_utilizadas,
            "tipos_precio": tipos_precio
        }
