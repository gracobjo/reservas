from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
import logging
from ..models.precio_dinamico import ReglaPrecio, HistorialPrecio, ConfiguracionPrecio, TipoRegla, TipoModificador
from ..models.servicio import Servicio
from ..models.recurso import Recurso
from ..models.cliente import Cliente
from ..schemas.precio_dinamico import (
    ReglaPrecioCreate, ReglaPrecioUpdate, CalculoPrecioRequest, 
    CalculoPrecioResponse, ReglaAplicada, ConfiguracionPrecioCreate, ConfiguracionPrecioUpdate
)

logger = logging.getLogger(__name__)

class PrecioDinamicoService:
    
    @staticmethod
    def create_regla(db: Session, regla: ReglaPrecioCreate) -> ReglaPrecio:
        """Crear una nueva regla de precio"""
        # Validar que la condición sea JSON válido
        try:
            json.loads(regla.condicion)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="La condición debe ser un JSON válido")
        
        db_regla = ReglaPrecio(**regla.dict())
        db.add(db_regla)
        db.commit()
        db.refresh(db_regla)
        return db_regla
    
    @staticmethod
    def get_reglas(db: Session, activas_solo: bool = False, skip: int = 0, limit: int = 100) -> List[ReglaPrecio]:
        """Obtener reglas de precio"""
        query = db.query(ReglaPrecio)
        if activas_solo:
            query = query.filter(ReglaPrecio.activa == True)
        return query.order_by(ReglaPrecio.prioridad.desc(), ReglaPrecio.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_regla(db: Session, regla_id: int) -> ReglaPrecio:
        """Obtener una regla específica"""
        regla = db.query(ReglaPrecio).filter(ReglaPrecio.id == regla_id).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regla no encontrada")
        return regla
    
    @staticmethod
    def update_regla(db: Session, regla_id: int, regla_update: ReglaPrecioUpdate) -> ReglaPrecio:
        """Actualizar una regla existente"""
        db_regla = PrecioDinamicoService.get_regla(db, regla_id)
        
        # Validar condición si se está actualizando
        if regla_update.condicion:
            try:
                json.loads(regla_update.condicion)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="La condición debe ser un JSON válido")
        
        update_data = regla_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_regla, field, value)
        
        db.commit()
        db.refresh(db_regla)
        return db_regla
    
    @staticmethod
    def delete_regla(db: Session, regla_id: int) -> bool:
        """Eliminar una regla"""
        db_regla = PrecioDinamicoService.get_regla(db, regla_id)
        db.delete(db_regla)
        db.commit()
        return True
    
    @staticmethod
    def calcular_precio(db: Session, request: CalculoPrecioRequest) -> CalculoPrecioResponse:
        """Calcular precio dinámico basado en las reglas"""
        
        # Obtener precio base del servicio
        servicio = db.query(Servicio).filter(Servicio.id == request.servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Obtener recurso
        recurso = db.query(Recurso).filter(Recurso.id == request.recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        precio_base = servicio.precio_base
        precio_actual = precio_base
        reglas_aplicadas = []
        descuento_total = 0.0
        recargo_total = 0.0
        
        # Obtener reglas aplicables
        reglas = PrecioDinamicoService._get_reglas_aplicables(
            db, request.servicio_id, request.recurso_id, request.fecha_hora_inicio
        )
        
        # Aplicar cada regla en orden de prioridad
        for regla in reglas:
            if PrecioDinamicoService._evaluar_condicion(regla, request):
                precio_anterior = precio_actual
                precio_actual = PrecioDinamicoService._aplicar_modificador(
                    precio_actual, precio_base, regla.tipo_modificador, regla.valor_modificador
                )
                
                # Calcular el cambio
                cambio = precio_actual - precio_anterior
                
                regla_aplicada = ReglaAplicada(
                    regla_id=regla.id,
                    nombre=regla.nombre,
                    tipo_regla=regla.tipo_regla,
                    tipo_modificador=regla.tipo_modificador,
                    valor_modificador=regla.valor_modificador,
                    descuento=abs(cambio) if cambio < 0 else 0.0,
                    recargo=cambio if cambio > 0 else 0.0,
                    precio_resultado=precio_actual
                )
                reglas_aplicadas.append(regla_aplicada)
                
                if cambio < 0:
                    descuento_total += abs(cambio)
                else:
                    recargo_total += cambio
        
        # Calcular ahorro total
        ahorro_total = precio_base - precio_actual if precio_actual < precio_base else 0.0
        
        return CalculoPrecioResponse(
            precio_base=precio_base,
            precio_final=max(0, precio_actual),  # No permitir precios negativos
            descuento_total=descuento_total,
            recargo_total=recargo_total,
            ahorro_total=ahorro_total,
            reglas_aplicadas=reglas_aplicadas,
            detalles={
                "servicio_nombre": servicio.nombre,
                "recurso_nombre": recurso.nombre,
                "duracion_minutos": servicio.duracion_minutos,
                "participantes": request.participantes,
                "fecha_calculo": datetime.now().isoformat()
            }
        )
    
    @staticmethod
    def _get_reglas_aplicables(db: Session, servicio_id: int, recurso_id: int, fecha: datetime) -> List[ReglaPrecio]:
        """Obtener reglas aplicables ordenadas por prioridad"""
        query = db.query(ReglaPrecio).filter(
            and_(
                ReglaPrecio.activa == True,
                or_(
                    ReglaPrecio.fecha_inicio.is_(None),
                    ReglaPrecio.fecha_inicio <= fecha
                ),
                or_(
                    ReglaPrecio.fecha_fin.is_(None),
                    ReglaPrecio.fecha_fin >= fecha
                )
            )
        )
        
        reglas = query.order_by(ReglaPrecio.prioridad.desc()).all()
        
        # Filtrar por servicios y recursos aplicables
        reglas_filtradas = []
        for regla in reglas:
            if PrecioDinamicoService._es_regla_aplicable(regla, servicio_id, recurso_id):
                reglas_filtradas.append(regla)
        
        return reglas_filtradas
    
    @staticmethod
    def _es_regla_aplicable(regla: ReglaPrecio, servicio_id: int, recurso_id: int) -> bool:
        """Verificar si una regla es aplicable al servicio/recurso"""
        # Verificar servicios aplicables
        if regla.servicios_aplicables:
            try:
                servicios = json.loads(regla.servicios_aplicables)
                if servicios and servicio_id not in servicios:
                    return False
            except:
                pass
        
        # Verificar recursos aplicables
        if regla.recursos_aplicables:
            try:
                recursos = json.loads(regla.recursos_aplicables)
                if recursos and recurso_id not in recursos:
                    return False
            except:
                pass
        
        return True
    
    @staticmethod
    def _evaluar_condicion(regla: ReglaPrecio, request: CalculoPrecioRequest) -> bool:
        """Evaluar si se cumple la condición de la regla"""
        try:
            condicion = json.loads(regla.condicion)
        except:
            return False
        
        if regla.tipo_regla == TipoRegla.DIA_SEMANA:
            dia_semana = request.fecha_hora_inicio.weekday()  # 0=Lunes, 6=Domingo
            return dia_semana in condicion.get("dias", [])
        
        elif regla.tipo_regla == TipoRegla.HORA:
            hora = request.fecha_hora_inicio.time()
            hora_inicio = datetime.strptime(condicion.get("hora_inicio", "00:00"), "%H:%M").time()
            hora_fin = datetime.strptime(condicion.get("hora_fin", "23:59"), "%H:%M").time()
            return hora_inicio <= hora <= hora_fin
        
        elif regla.tipo_regla == TipoRegla.TEMPORADA:
            fecha = request.fecha_hora_inicio.date()
            fecha_inicio = datetime.strptime(condicion.get("fecha_inicio"), "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(condicion.get("fecha_fin"), "%Y-%m-%d").date()
            return fecha_inicio <= fecha <= fecha_fin
        
        elif regla.tipo_regla == TipoRegla.ANTICIPACION:
            # Cambiar lógica: basar en duración total de la reserva, no en anticipación desde hoy
            duracion_horas = (request.fecha_hora_fin - request.fecha_hora_inicio).total_seconds() / 3600
            duracion_dias = duracion_horas / 24
            
            dias_minimos = condicion.get("dias_minimos", 0)
            
            # Para reglas de anticipación, ahora se basan en la duración total
            # Ejemplo: regla de 7+ días se aplica a reservas de 7+ días de duración
            return duracion_dias >= dias_minimos
        
        elif regla.tipo_regla == TipoRegla.DURACION:
            duracion_minutos = (request.fecha_hora_fin - request.fecha_hora_inicio).total_seconds() / 60
            duracion_minima = condicion.get("duracion_minima", 0)
            duracion_maxima = condicion.get("duracion_maxima", float('inf'))
            return duracion_minima <= duracion_minutos <= duracion_maxima
        
        elif regla.tipo_regla == TipoRegla.PARTICIPANTES:
            participantes_min = condicion.get("participantes_min", 1)
            participantes_max = condicion.get("participantes_max", float('inf'))
            return participantes_min <= request.participantes <= participantes_max
        
        elif regla.tipo_regla == TipoRegla.CLIENTE_TIPO:
            tipos_aplicables = condicion.get("tipos", [])
            return request.tipo_cliente in tipos_aplicables
        
        elif regla.tipo_regla == TipoRegla.FESTIVO:
            # Implementar lógica de días festivos
            return PrecioDinamicoService._es_dia_festivo(request.fecha_hora_inicio.date())
        
        return False
    
    @staticmethod
    def _aplicar_modificador(precio_actual: float, precio_base: float, tipo: TipoModificador, valor: float) -> float:
        """Aplicar modificador de precio"""
        if tipo == TipoModificador.PORCENTAJE:
            return precio_actual * (1 + valor / 100)
        elif tipo == TipoModificador.MONTO_FIJO:
            return precio_actual + valor
        elif tipo == TipoModificador.PRECIO_FIJO:
            return valor
        return precio_actual
    
    @staticmethod
    def _es_dia_festivo(fecha: datetime.date) -> bool:
        """Verificar si una fecha es día festivo (implementación básica)"""
        # Lista básica de días festivos (se puede expandir)
        festivos_fijos = [
            (1, 1),   # Año Nuevo
            (12, 25), # Navidad
            (12, 31), # Fin de Año
        ]
        
        return (fecha.month, fecha.day) in festivos_fijos
    
    @staticmethod
    def guardar_historial(db: Session, reserva_id: int, calculo: CalculoPrecioResponse) -> HistorialPrecio:
        """Guardar historial de cálculo de precios"""
        reglas_json = json.dumps([regla.dict() for regla in calculo.reglas_aplicadas])
        
        historial = HistorialPrecio(
            reserva_id=reserva_id,
            servicio_id=calculo.detalles.get("servicio_id"),
            recurso_id=calculo.detalles.get("recurso_id"),
            precio_base=calculo.precio_base,
            precio_final=calculo.precio_final,
            descuento_total=calculo.descuento_total,
            recargo_total=calculo.recargo_total,
            reglas_aplicadas=reglas_json
        )
        
        db.add(historial)
        db.commit()
        db.refresh(historial)
        return historial
    
    # Métodos para crear reglas predefinidas
    @staticmethod
    def crear_regla_hora_pico(db: Session, nombre: str, hora_inicio: str, hora_fin: str, 
                             porcentaje_recargo: float, dias_semana: List[int]) -> ReglaPrecio:
        """Crear regla de hora pico"""
        condicion = {
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "dias": dias_semana
        }
        
        regla = ReglaPrecioCreate(
            nombre=nombre,
            descripcion=f"Recargo de {porcentaje_recargo}% durante horas pico",
            tipo_regla=TipoRegla.HORA,
            condicion=json.dumps(condicion),
            tipo_modificador=TipoModificador.PORCENTAJE,
            valor_modificador=porcentaje_recargo,
            prioridad=10
        )
        
        return PrecioDinamicoService.create_regla(db, regla)
    
    @staticmethod
    def crear_regla_descuento_anticipacion(db: Session, nombre: str, dias_minimos: int, 
                                         porcentaje_descuento: float) -> ReglaPrecio:
        """Crear regla de descuento por anticipación"""
        condicion = {
            "dias_minimos": dias_minimos
        }
        
        regla = ReglaPrecioCreate(
            nombre=nombre,
            descripcion=f"Descuento de {porcentaje_descuento}% por reservar con {dias_minimos} días de anticipación",
            tipo_regla=TipoRegla.ANTICIPACION,
            condicion=json.dumps(condicion),
            tipo_modificador=TipoModificador.PORCENTAJE,
            valor_modificador=-porcentaje_descuento,
            prioridad=5
        )
        
        return PrecioDinamicoService.create_regla(db, regla)
    
    @staticmethod
    def crear_regla_fin_de_semana(db: Session, nombre: str, porcentaje_recargo: float, 
                                 prioridad: int, dias_semana: List[int]) -> ReglaPrecio:
        """Crear regla de recargo por fin de semana"""
        condicion = {
            "dias": dias_semana
        }
        
        regla = ReglaPrecioCreate(
            nombre=nombre,
            descripcion=f"Recargo de {porcentaje_recargo}% durante fines de semana",
            tipo_regla=TipoRegla.DIA_SEMANA,
            condicion=json.dumps(condicion),
            tipo_modificador=TipoModificador.PORCENTAJE,
            valor_modificador=porcentaje_recargo,
            prioridad=prioridad
        )
        
        return PrecioDinamicoService.create_regla(db, regla)
    
    @staticmethod
    def crear_regla_temporada_alta(db: Session, nombre: str, fecha_inicio: str, fecha_fin: str, 
                                  porcentaje_recargo: float) -> ReglaPrecio:
        """Crear regla de temporada alta"""
        condicion = {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
        
        regla = ReglaPrecioCreate(
            nombre=nombre,
            descripcion=f"Recargo de {porcentaje_recargo}% durante temporada alta",
            tipo_regla=TipoRegla.TEMPORADA,
            condicion=json.dumps(condicion),
            tipo_modificador=TipoModificador.PORCENTAJE,
            valor_modificador=porcentaje_recargo,
            prioridad=15
        )
        
        return PrecioDinamicoService.create_regla(db, regla)
