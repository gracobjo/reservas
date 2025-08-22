from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func as sql_func
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.reserva import Reserva
from ..models.servicio import Servicio
from ..models.recurso import Recurso
from ..models.cliente import Cliente
from ..schemas.reserva import ReservaCreate, ReservaUpdate

class ReservaService:
    @staticmethod
    def create_reserva(db: Session, reserva: ReservaCreate) -> Reserva:
        # Validate service exists
        servicio = db.query(Servicio).filter(Servicio.id == reserva.servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio not found")
        
        # Validate resource exists and is available
        recurso = db.query(Recurso).filter(Recurso.id == reserva.recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso not found")
        if not recurso.disponible:
            raise HTTPException(status_code=400, detail="Recurso no disponible")
        
        # Check for overlapping reservations
        if ReservaService._has_overlap(db, reserva.recurso_id, reserva.fecha_hora_inicio, reserva.fecha_hora_fin):
            raise HTTPException(status_code=400, detail="Recurso no disponible en ese horario")
        
        # Validate time consistency with service duration
        expected_end = reserva.fecha_hora_inicio + timedelta(minutes=servicio.duracion_minutos)
        if abs((expected_end - reserva.fecha_hora_fin).total_seconds()) > 60:  # Allow 1 minute tolerance
            raise HTTPException(status_code=400, detail="La duración de la reserva no coincide con el servicio")
        
        db_reserva = Reserva(**reserva.dict())
        db.add(db_reserva)
        db.commit()
        db.refresh(db_reserva)
        return db_reserva
    
    @staticmethod
    def get_all_reservas(db: Session, skip: int = 0, limit: int = 100) -> List[Reserva]:
        """Obtener todas las reservas con paginación"""
        return db.query(Reserva).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_reserva(db: Session, reserva_id: int) -> Reserva:
        db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if db_reserva is None:
            raise HTTPException(status_code=404, detail="Reserva not found")
        return db_reserva
    
    @staticmethod
    def update_reserva(db: Session, reserva_id: int, reserva: ReservaUpdate) -> Reserva:
        db_reserva = ReservaService.get_reserva(db, reserva_id)
        
        # Validate estado if it's being updated
        if reserva.estado is not None:
            estados_validos = ['pendiente', 'confirmada', 'cancelada']
            if reserva.estado not in estados_validos:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
                )
        
        # If updating time, check for overlaps
        if reserva.fecha_hora_inicio or reserva.fecha_hora_fin:
            start_time = reserva.fecha_hora_inicio or db_reserva.fecha_hora_inicio
            end_time = reserva.fecha_hora_fin or db_reserva.fecha_hora_fin
            
            if ReservaService._has_overlap(db, db_reserva.recurso_id, start_time, end_time, exclude_id=reserva_id):
                raise HTTPException(status_code=400, detail="Recurso no disponible en ese horario")
        
        update_data = reserva.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reserva, field, value)
        
        try:
            db.commit()
            db.refresh(db_reserva)
            return db_reserva
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar la reserva: {str(e)}")
    
    @staticmethod
    def delete_reserva(db: Session, reserva_id: int) -> bool:
        db_reserva = ReservaService.get_reserva(db, reserva_id)
        db.delete(db_reserva)
        db.commit()
        return True
    
    @staticmethod
    def cancel_reserva(db: Session, reserva_id: int) -> Reserva:
        db_reserva = ReservaService.get_reserva(db, reserva_id)
        db_reserva.estado = "cancelada"
        db.commit()
        db.refresh(db_reserva)
        return db_reserva
    
    @staticmethod
    def get_disponibilidad(db: Session, servicio_id: int, fecha: str) -> dict:
        # Parse date
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Get service
        servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio not found")
        
        # Get available resources for this service type
        recursos = db.query(Recurso).filter(Recurso.disponible == True).all()
        
        # Generate time slots (9 AM to 6 PM, every 30 minutes)
        horarios = []
        start_time = fecha_obj.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = fecha_obj.replace(hour=18, minute=0, second=0, microsecond=0)
        
        current_time = start_time
        while current_time <= end_time:
            slot_end = current_time + timedelta(minutes=servicio.duracion_minutos)
            if slot_end <= end_time:
                # Check if any resource is available for this time slot
                disponible = not ReservaService._has_overlap(db, None, current_time, slot_end)
                horarios.append({
                    "inicio": current_time.strftime("%H:%M"),
                    "fin": slot_end.strftime("%H:%M"),
                    "disponible": disponible
                })
            current_time += timedelta(minutes=30)
        
        return {
            "fecha": fecha,
            "servicio_id": servicio_id,
            "horarios_disponibles": horarios
        }
    
    @staticmethod
    def _has_overlap(db: Session, recurso_id: int, start_time: datetime, end_time: datetime, exclude_id: int = None) -> bool:
        query = db.query(Reserva).filter(
            and_(
                Reserva.estado != "cancelada",
                or_(
                    and_(Reserva.fecha_hora_inicio < end_time, Reserva.fecha_hora_fin > start_time),
                    and_(Reserva.fecha_hora_inicio == start_time, Reserva.fecha_hora_fin == end_time)
                )
            )
        )
        
        if recurso_id:
            query = query.filter(Reserva.recurso_id == recurso_id)
        
        if exclude_id:
            query = query.filter(Reserva.id != exclude_id)
        
        return query.first() is not None

    @staticmethod
    def get_disponibilidad_avanzada(db: Session, fecha: str, hora: Optional[str] = None, 
                                  servicio_id: Optional[int] = None, recurso_id: Optional[int] = None) -> dict:
        """Búsqueda avanzada de disponibilidad para el calendario"""
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Si se especifica hora, buscar slots específicos
        if hora:
            try:
                hora_obj = datetime.strptime(hora, "%H:%M")
                hora_inicio = fecha_obj.replace(hour=hora_obj.hour, minute=hora_obj.minute, second=0, microsecond=0)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM")
        else:
            # Si no se especifica hora, buscar todo el día
            hora_inicio = fecha_obj.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Obtener recursos disponibles
        query_recursos = db.query(Recurso).filter(Recurso.disponible == True)
        if recurso_id:
            query_recursos = query_recursos.filter(Recurso.id == recurso_id)
        recursos = query_recursos.all()
        
        # Obtener servicios disponibles
        query_servicios = db.query(Servicio)
        if servicio_id:
            query_servicios = query_servicios.filter(Servicio.id == servicio_id)
        servicios = query_servicios.all()
        
        slots_disponibles = []
        
        # Generar slots de tiempo
        if hora:
            # Buscar solo en la hora específica
            slots_disponibles = ReservaService._generar_slots_hora_especifica(
                db, fecha_obj, hora_inicio, servicios, recursos
            )
        else:
            # Buscar en todo el día
            slots_disponibles = ReservaService._generar_slots_dia_completo(
                db, fecha_obj, servicios, recursos
            )
        
        return {
            "fecha": fecha,
            "hora": hora,
            "servicio_id": servicio_id,
            "recurso_id": recurso_id,
            "slots_disponibles": slots_disponibles
        }
    
    @staticmethod
    def _generar_slots_hora_especifica(db: Session, fecha: datetime, hora_inicio: datetime, 
                                      servicios: List, recursos: List) -> List[dict]:
        """Genera slots disponibles para una hora específica"""
        slots = []
        
        for servicio in servicios:
            for recurso in recursos:
                # Verificar si el recurso está disponible para este servicio
                if not ReservaService._recurso_compatible_servicio(recurso, servicio):
                    continue
                
                # Calcular fin del slot basado en duración del servicio
                slot_fin = hora_inicio + timedelta(minutes=servicio.duracion_minutos)
                
                # Verificar disponibilidad
                if not ReservaService._has_overlap(db, recurso.id, hora_inicio, slot_fin):
                    slots.append({
                        "hora_inicio": hora_inicio.strftime("%H:%M"),
                        "hora_fin": slot_fin.strftime("%H:%M"),
                        "recurso_id": recurso.id,
                        "recurso_nombre": recurso.nombre,
                        "servicio_id": servicio.id,
                        "servicio_nombre": servicio.nombre,
                        "precio_base": servicio.precio_base,
                        "duracion_minutos": servicio.duracion_minutos
                    })
        
        return slots
    
    @staticmethod
    def _generar_slots_dia_completo(db: Session, fecha: datetime, servicios: List, recursos: List) -> List[dict]:
        """Genera slots disponibles para todo el día"""
        slots = []
        
        # Horario de trabajo: 9 AM a 6 PM
        hora_inicio_dia = fecha.replace(hour=9, minute=0, second=0, microsecond=0)
        hora_fin_dia = fecha.replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Intervalo de 30 minutos
        current_time = hora_inicio_dia
        while current_time <= hora_fin_dia:
            for servicio in servicios:
                for recurso in recursos:
                    # Verificar compatibilidad
                    if not ReservaService._recurso_compatible_servicio(recurso, servicio):
                        continue
                    
                    # Calcular fin del slot
                    slot_fin = current_time + timedelta(minutes=servicio.duracion_minutos)
                    if slot_fin > hora_fin_dia:
                        continue
                    
                    # Verificar disponibilidad
                    if not ReservaService._has_overlap(db, recurso.id, current_time, slot_fin):
                        slots.append({
                            "hora_inicio": current_time.strftime("%H:%M"),
                            "hora_fin": slot_fin.strftime("%H:%M"),
                            "recurso_id": recurso.id,
                            "recurso_nombre": recurso.nombre,
                            "servicio_id": servicio.id,
                            "servicio_nombre": servicio.nombre,
                            "precio_base": servicio.precio_base,
                            "duracion_minutos": servicio.duracion_minutos
                        })
            
            current_time += timedelta(minutes=30)
        
        return slots
    
    @staticmethod
    def _recurso_compatible_servicio(recurso, servicio) -> bool:
        """Verifica si un recurso es compatible con un servicio"""
        # Por ahora, asumimos que todos los recursos son compatibles con todos los servicios
        # En el futuro, esto podría ser más sofisticado basado en categorías
        return True

    # ===== MÉTODOS PARA EXPLOTACIÓN DE DATOS =====

    @staticmethod
    def get_estadisticas_periodo(db: Session, fecha_inicio: str, fecha_fin: str) -> dict:
        """Obtener estadísticas de reservas en un período específico"""
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Total de reservas en el período
        total_reservas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj
            )
        ).count()
        
        # Reservas por estado
        reservas_por_estado = db.query(Reserva.estado, sql_func.count(Reserva.id)).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj
            )
        ).group_by(Reserva.estado).all()
        
        # Reservas por servicio
        reservas_por_servicio = db.query(
            Servicio.nombre, 
            sql_func.count(Reserva.id)
        ).join(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj
            )
        ).group_by(Servicio.id, Servicio.nombre).all()
        
        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "total_reservas": total_reservas,
            "reservas_por_estado": dict(reservas_por_estado),
            "reservas_por_servicio": dict(reservas_por_servicio),
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_estadisticas_servicio(db: Session, servicio_id: int) -> dict:
        """Obtener estadísticas de reservas por servicio"""
        # Verificar que el servicio existe
        servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio not found")
        
        # Total de reservas para este servicio
        total_reservas = db.query(Reserva).filter(Reserva.servicio_id == servicio_id).count()
        
        # Reservas por estado
        reservas_por_estado = db.query(Reserva.estado, sql_func.count(Reserva.id)).filter(
            Reserva.servicio_id == servicio_id
        ).group_by(Reserva.estado).all()
        
        # Reservas por mes (últimos 12 meses)
        from datetime import date
        hoy = date.today()
        reservas_por_mes = []
        
        for i in range(12):
            mes = (hoy.month - i - 1) % 12 + 1
            año = hoy.year - ((i + 1) // 12)
            
            inicio_mes = datetime(año, mes, 1)
            if mes == 12:
                fin_mes = datetime(año + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin_mes = datetime(año, mes + 1, 1) - timedelta(seconds=1)
            
            count = db.query(Reserva).filter(
                and_(
                    Reserva.servicio_id == servicio_id,
                    Reserva.fecha_hora_inicio >= inicio_mes,
                    Reserva.fecha_hora_inicio <= fin_mes
                )
            ).count()
            
            reservas_por_mes.append({
                "mes": f"{año}-{mes:02d}",
                "total": count
            })
        
        return {
            "servicio": {
                "id": servicio.id,
                "nombre": servicio.nombre,
                "descripcion": servicio.descripcion
            },
            "total_reservas": total_reservas,
            "reservas_por_estado": dict(reservas_por_estado),
            "reservas_por_mes": reservas_por_mes,
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_estadisticas_recurso(db: Session, recurso_id: int) -> dict:
        """Obtener estadísticas de reservas por recurso"""
        # Verificar que el recurso existe
        recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso not found")
        
        # Total de reservas para este recurso
        total_reservas = db.query(Reserva).filter(Reserva.recurso_id == recurso_id).count()
        
        # Reservas por estado
        reservas_por_estado = db.query(Reserva.estado, sql_func.count(Reserva.id)).filter(
            Reserva.recurso_id == recurso_id
        ).group_by(Reserva.estado).all()
        
        # Tasa de ocupación (últimos 30 días)
        from datetime import date
        hoy = date.today()
        inicio_periodo = datetime(hoy.year, hoy.month, hoy.day) - timedelta(days=30)
        
        reservas_periodo = db.query(Reserva).filter(
            and_(
                Reserva.recurso_id == recurso_id,
                Reserva.fecha_hora_inicio >= inicio_periodo,
                Reserva.estado != "cancelada"
            )
        ).all()
        
        # Calcular horas ocupadas
        horas_ocupadas = 0
        for reserva in reservas_periodo:
            duracion = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
            horas_ocupadas += duracion
        
        # 30 días * 24 horas = 720 horas totales
        horas_totales = 720
        tasa_ocupacion = (horas_ocupadas / horas_totales) * 100 if horas_totales > 0 else 0
        
        return {
            "recurso": {
                "id": recurso.id,
                "nombre": recurso.nombre,
                "tipo": recurso.tipo
            },
            "total_reservas": total_reservas,
            "reservas_por_estado": dict(reservas_por_estado),
            "tasa_ocupacion_30_dias": round(tasa_ocupacion, 2),
            "horas_ocupadas_30_dias": round(horas_ocupadas, 2),
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_reporte_ocupacion(db: Session, fecha: str) -> dict:
        """Obtener reporte de ocupación para una fecha específica"""
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Obtener todas las reservas para esa fecha
        reservas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_obj,
                Reserva.fecha_hora_inicio < fecha_obj + timedelta(days=1),
                Reserva.estado != "cancelada"
            )
        ).all()
        
        # Agrupar por recurso
        ocupacion_por_recurso = {}
        recursos = db.query(Recurso).all()
        
        for recurso in recursos:
            ocupacion_por_recurso[recurso.id] = {
                "nombre": recurso.nombre,
                "tipo": recurso.tipo,
                "reservas": [],
                "horas_ocupadas": 0
            }
        
        # Calcular ocupación para cada recurso
        for reserva in reservas:
            recurso_id = reserva.recurso_id
            if recurso_id in ocupacion_por_recurso:
                duracion = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
                ocupacion_por_recurso[recurso_id]["reservas"].append({
                    "id": reserva.id,
                    "cliente_id": reserva.cliente_id,
                    "servicio_id": reserva.servicio_id,
                    "inicio": reserva.fecha_hora_inicio.strftime("%H:%M"),
                    "fin": reserva.fecha_hora_fin.strftime("%H:%M"),
                    "estado": reserva.estado
                })
                ocupacion_por_recurso[recurso_id]["horas_ocupadas"] += duracion
        
        return {
            "fecha": fecha,
            "total_recursos": len(recursos),
            "total_reservas": len(reservas),
            "ocupacion_por_recurso": ocupacion_por_recurso,
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_tendencias(db: Session, meses_atras: int = 6) -> dict:
        """Obtener análisis de tendencias de reservas"""
        from datetime import date
        hoy = date.today()
        
        # Calcular fecha de inicio
        if hoy.month <= meses_atras:
            año_inicio = hoy.year - ((meses_atras - hoy.month) // 12 + 1)
            mes_inicio = 12 - ((meses_atras - hoy.month) % 12)
        else:
            año_inicio = hoy.year
            mes_inicio = hoy.month - meses_atras
        
        inicio_periodo = datetime(año_inicio, mes_inicio, 1)
        
        # Reservas por mes
        reservas_por_mes = []
        for i in range(meses_atras):
            mes = (mes_inicio + i - 1) % 12 + 1
            año = año_inicio + ((mes_inicio + i - 1) // 12)
            
            if mes == 12:
                fin_mes = datetime(año + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin_mes = datetime(año, mes + 1, 1) - timedelta(seconds=1)
            
            inicio_mes = datetime(año, mes, 1)
            
            count = db.query(Reserva).filter(
                and_(
                    Reserva.fecha_hora_inicio >= inicio_mes,
                    Reserva.fecha_hora_inicio <= fin_mes
                )
            ).count()
            
            reservas_por_mes.append({
                "mes": f"{año}-{mes:02d}",
                "total": count
            })
        
        # Reservas por día de la semana (últimos 3 meses)
        inicio_3_meses = datetime(hoy.year, hoy.month - 3, 1) if hoy.month > 3 else datetime(hoy.year - 1, hoy.month + 9, 1)
        
        reservas_por_dia = []
        for dia in range(7):
            count = db.query(Reserva).filter(
                and_(
                    Reserva.fecha_hora_inicio >= inicio_3_meses,
                    Reserva.fecha_hora_inicio < datetime.now(),
                    sql_func.extract('dow', Reserva.fecha_hora_inicio) == dia
                )
            ).count()
            
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            reservas_por_dia.append({
                "dia": dias[dia],
                "total": count
            })
        
        return {
            "periodo_analisis": meses_atras,
            "fecha_inicio": inicio_periodo.strftime("%Y-%m-%d"),
            "reservas_por_mes": reservas_por_mes,
            "reservas_por_dia_semana": reservas_por_dia,
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_kpis_negocio(db: Session, fecha_inicio: str, fecha_fin: str) -> dict:
        """Obtener KPIs de negocio (ocupación, ingresos, etc.)"""
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Total de reservas confirmadas
        total_reservas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj,
                Reserva.estado == "confirmada"
            )
        ).count()
        
        # Reservas canceladas
        reservas_canceladas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj,
                Reserva.estado == "cancelada"
            )
        ).count()
        
        # Tasa de cancelación
        tasa_cancelacion = (reservas_canceladas / (total_reservas + reservas_canceladas)) * 100 if (total_reservas + reservas_canceladas) > 0 else 0
        
        # Ingresos estimados (usando precio base de servicios)
        reservas_con_precio = db.query(
            Servicio.precio_base
        ).join(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj,
                Reserva.estado == "confirmada"
            )
        ).all()
        
        ingresos_totales = sum(precio[0] for precio in reservas_con_precio)
        
        # Ocupación promedio por día
        dias_periodo = (fecha_fin_obj - fecha_inicio_obj).days + 1
        ocupacion_promedio = total_reservas / dias_periodo if dias_periodo > 0 else 0
        
        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "total_reservas_confirmadas": total_reservas,
            "reservas_canceladas": reservas_canceladas,
            "tasa_cancelacion": round(tasa_cancelacion, 2),
            "ingresos_estimados": round(ingresos_totales, 2),
            "ocupacion_promedio_por_dia": round(ocupacion_promedio, 2),
            "dias_periodo": dias_periodo,
            "fecha_generacion": datetime.now().isoformat()
        }

    # ===== MÉTODOS AVANZADOS PARA EXPLOTACIÓN DE DATOS =====

    @staticmethod
    def get_reservas_filtradas(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        cliente_id: Optional[int] = None,
        servicio_id: Optional[int] = None,
        recurso_id: Optional[int] = None,
        estado: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> List[Reserva]:
        """Obtener reservas con filtros avanzados"""
        query = db.query(Reserva)
        
        # Aplicar filtros
        if cliente_id:
            query = query.filter(Reserva.cliente_id == cliente_id)
        if servicio_id:
            query = query.filter(Reserva.servicio_id == servicio_id)
        if recurso_id:
            query = query.filter(Reserva.recurso_id == recurso_id)
        if estado:
            query = query.filter(Reserva.estado == estado)
        if fecha_inicio and fecha_fin:
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
                # Incluir reservas que se solapan con el rango de fechas
                # Una reserva se solapa si:
                # - Empieza antes del fin del rango Y termina después del inicio del rango
                query = query.filter(
                    and_(
                        Reserva.fecha_hora_inicio < fecha_fin_obj + timedelta(days=1),
                        Reserva.fecha_hora_fin > fecha_inicio_obj
                    )
                )
            except ValueError:
                pass
        elif fecha_inicio:
            try:
                fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                query = query.filter(Reserva.fecha_hora_inicio >= fecha_inicio_obj)
            except ValueError:
                pass
        elif fecha_fin:
            try:
                fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
                query = query.filter(Reserva.fecha_hora_fin <= fecha_fin_obj + timedelta(days=1))
            except ValueError:
                pass
        
        # Ordenar por fecha de inicio (más recientes primero)
        query = query.order_by(Reserva.fecha_hora_inicio.desc())
        
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_analisis_rendimiento(db: Session, fecha_inicio: str, fecha_fin: str) -> dict:
        """Obtener análisis de rendimiento detallado"""
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Obtener todas las reservas en el período
        reservas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj
            )
        ).all()
        
        # Calcular métricas de rendimiento
        total_reservas = len(reservas)
        reservas_confirmadas = len([r for r in reservas if r.estado == "confirmada"])
        reservas_canceladas = len([r for r in reservas if r.estado == "cancelada"])
        reservas_pendientes = len([r for r in reservas if r.estado == "pendiente"])
        
        # Calcular tiempo promedio de confirmación (si hay datos suficientes)
        tiempo_confirmacion = 0
        if reservas_confirmadas > 0:
            confirmadas = [r for r in reservas if r.estado == "confirmada"]
            tiempo_total = sum(
                (r.updated_at - r.created_at).total_seconds() 
                for r in confirmadas if r.updated_at
            )
            tiempo_confirmacion = tiempo_total / reservas_confirmadas / 3600  # en horas
        
        # Calcular eficiencia por recurso
        eficiencia_recursos = {}
        recursos = db.query(Recurso).all()
        
        for recurso in recursos:
            reservas_recurso = [r for r in reservas if r.recurso_id == recurso.id]
            if reservas_recurso:
                horas_ocupadas = sum(
                    (r.fecha_hora_fin - r.fecha_hora_inicio).total_seconds() / 3600
                    for r in reservas_recurso if r.estado != "cancelada"
                )
                horas_totales = (fecha_fin_obj - fecha_inicio_obj).days * 24
                eficiencia = (horas_ocupadas / horas_totales) * 100 if horas_totales > 0 else 0
                
                eficiencia_recursos[recurso.nombre] = {
                    "tipo": recurso.tipo,
                    "reservas": len(reservas_recurso),
                    "eficiencia": round(eficiencia, 2),
                    "horas_ocupadas": round(horas_ocupadas, 2)
                }
        
        return {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "metricas_generales": {
                "total_reservas": total_reservas,
                "reservas_confirmadas": reservas_confirmadas,
                "reservas_canceladas": reservas_canceladas,
                "reservas_pendientes": reservas_pendientes,
                "tasa_confirmacion": round((reservas_confirmadas / total_reservas) * 100, 2) if total_reservas > 0 else 0,
                "tiempo_promedio_confirmacion_horas": round(tiempo_confirmacion, 2)
            },
            "eficiencia_por_recurso": eficiencia_recursos,
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def get_predicciones(db: Session, dias_futuros: int = 30) -> dict:
        """Obtener predicciones de demanda futura basadas en datos históricos"""
        from datetime import date
        
        hoy = date.today()
        
        # Obtener datos históricos de los últimos 90 días
        inicio_historico = datetime(hoy.year, hoy.month, hoy.day) - timedelta(days=90)
        
        # Obtener reservas históricas
        reservas_historicas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= inicio_historico,
                Reserva.estado != "cancelada"
            )
        ).all()
        
        # Agrupar por día de la semana
        reservas_por_dia = {}
        for i in range(7):
            reservas_por_dia[i] = []
        
        for reserva in reservas_historicas:
            dia_semana = reserva.fecha_hora_inicio.weekday()
            reservas_por_dia[dia_semana].append(reserva)
        
        # Calcular promedio de reservas por día de la semana
        promedios_por_dia = {}
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for dia, reservas in reservas_por_dia.items():
            if reservas:
                # Calcular promedio por semana
                semanas = 90 // 7
                promedio = len(reservas) / semanas
                promedios_por_dia[dias[dia]] = round(promedio, 2)
            else:
                promedios_por_dia[dias[dia]] = 0
        
        # Generar predicciones para los próximos días
        predicciones = []
        for i in range(dias_futuros):
            fecha_prediccion = hoy + timedelta(days=i)
            dia_semana = fecha_prediccion.weekday()
            dia_nombre = dias[dia_semana]
            
            # Ajustar predicción según tendencias estacionales
            prediccion_base = promedios_por_dia[dia_nombre]
            
            # Factor de ajuste simple (podría ser más sofisticado)
            factor_ajuste = 1.0
            if fecha_prediccion.month in [7, 8]:  # Verano
                factor_ajuste = 1.2
            elif fecha_prediccion.month in [12, 1]:  # Navidad
                factor_ajuste = 1.3
            
            prediccion_ajustada = round(prediccion_base * factor_ajuste, 2)
            
            predicciones.append({
                "fecha": fecha_prediccion.strftime("%Y-%m-%d"),
                "dia_semana": dia_nombre,
                "prediccion_reservas": prediccion_ajustada,
                "factor_ajuste": factor_ajuste
            })
        
        return {
            "periodo_prediccion": dias_futuros,
            "datos_historicos": {
                "dias_analizados": 90,
                "total_reservas": len(reservas_historicas),
                "promedios_por_dia_semana": promedios_por_dia
            },
            "predicciones": predicciones,
            "fecha_generacion": datetime.now().isoformat()
        }

    @staticmethod
    def exportar_reservas(db: Session, fecha_inicio: str, fecha_fin: str, formato: str = "csv") -> dict:
        """Exportar reservas en formato CSV"""
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            fecha_fin_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Obtener reservas con información completa
        reservas = db.query(
            Reserva, Cliente.nombre.label('cliente_nombre'), 
            Servicio.nombre.label('servicio_nombre'),
            Recurso.nombre.label('recurso_nombre')
        ).join(Cliente).join(Servicio).join(Recurso).filter(
            and_(
                Reserva.fecha_hora_inicio >= fecha_inicio_obj,
                Reserva.fecha_hora_inicio <= fecha_fin_obj
            )
        ).all()
        
        # Preparar datos para exportación
        datos_exportacion = []
        for reserva, cliente_nombre, servicio_nombre, recurso_nombre in reservas:
            datos_exportacion.append({
                "id": reserva.id,
                "cliente": cliente_nombre,
                "servicio": servicio_nombre,
                "recurso": recurso_nombre,
                "fecha_inicio": reserva.fecha_hora_inicio.strftime("%Y-%m-%d %H:%M"),
                "fecha_fin": reserva.fecha_hora_fin.strftime("%Y-%m-%d %H:%M"),
                "estado": reserva.estado,
                "created_at": reserva.created_at.strftime("%Y-%m-%d %H:%M") if reserva.created_at else "",
                "updated_at": reserva.updated_at.strftime("%Y-%m-%d %H:%M") if reserva.updated_at else ""
            })
        
        # Generar CSV (simulado)
        if formato.lower() == "csv":
            csv_content = "ID,Cliente,Servicio,Recurso,Fecha Inicio,Fecha Fin,Estado,Creado,Actualizado\n"
            for dato in datos_exportacion:
                csv_content += f"{dato['id']},{dato['cliente']},{dato['servicio']},{dato['recurso']},"
                csv_content += f"{dato['fecha_inicio']},{dato['fecha_fin']},{dato['estado']},"
                csv_content += f"{dato['created_at']},{dato['updated_at']}\n"
            
            return {
                "formato": "csv",
                "periodo": {"inicio": fecha_inicio, "fecha_fin": fecha_fin},
                "total_registros": len(datos_exportacion),
                "contenido_csv": csv_content,
                "fecha_generacion": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Use 'csv'")
    
    @staticmethod
    def get_metricas_tiempo_real(db: Session) -> dict:
        """Obtener métricas en tiempo real"""
        ahora = datetime.now()
        
        # Reservas de hoy
        hoy = ahora.date()
        reservas_hoy = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= datetime(hoy.year, hoy.month, hoy.day),
                Reserva.fecha_hora_inicio < datetime(hoy.year, hoy.month, hoy.day + 1)
            )
        ).count()
        
        # Reservas confirmadas de hoy
        reservas_confirmadas_hoy = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= datetime(hoy.year, hoy.month, hoy.day),
                Reserva.fecha_hora_inicio < datetime(hoy.year, hoy.month, hoy.day + 1),
                Reserva.estado == "confirmada"
            )
        ).count()
        
        # Reservas pendientes de hoy
        reservas_pendientes_hoy = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= datetime(hoy.year, hoy.month, hoy.day),
                Reserva.fecha_hora_inicio < datetime(hoy.year, hoy.month, hoy.day + 1),
                Reserva.estado == "pendiente"
            )
        ).count()
        
        # Próximas reservas (próximas 2 horas)
        proximas_2_horas = ahora + timedelta(hours=2)
        proximas_reservas = db.query(Reserva).filter(
            and_(
                Reserva.fecha_hora_inicio >= ahora,
                Reserva.fecha_hora_inicio <= proximas_2_horas,
                Reserva.estado == "confirmada"
            )
        ).count()
        
        # Recursos ocupados actualmente
        recursos_ocupados = 0
        recursos = db.query(Recurso).all()
        
        for recurso in recursos:
            reserva_activa = db.query(Reserva).filter(
                and_(
                    Reserva.recurso_id == recurso.id,
                    Reserva.fecha_hora_inicio <= ahora,
                    Reserva.fecha_hora_fin >= ahora,
                    Reserva.estado == "confirmada"
                )
            ).first()
            
            if reserva_activa:
                recursos_ocupados += 1
        
        return {
            "timestamp": ahora.isoformat(),
            "metricas_hoy": {
                "total_reservas": reservas_hoy,
                "confirmadas": reservas_confirmadas_hoy,
                "pendientes": reservas_pendientes_hoy,
                "tasa_confirmacion": round((reservas_confirmadas_hoy / reservas_hoy) * 100, 2) if reservas_hoy > 0 else 0
            },
            "metricas_tiempo_real": {
                "proximas_2_horas": proximas_reservas,
                "recursos_ocupados": recursos_ocupados,
                "recursos_disponibles": len(recursos) - recursos_ocupados,
                "tasa_ocupacion_actual": round((recursos_ocupados / len(recursos)) * 100, 2) if recursos else 0
            },
            "fecha_generacion": ahora.isoformat()
        }
