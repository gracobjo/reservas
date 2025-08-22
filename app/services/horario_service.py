from sqlalchemy.orm import Session
from sqlalchemy import and_, extract
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from ..models.horario import HorarioRecurso
from ..models.recurso import Recurso
from ..models.reserva import Reserva
from ..models.servicio import Servicio
from ..schemas.horario import HorarioRecursoCreate, HorarioRecursoUpdate, DisponibilidadRequest, SlotDisponibilidad
import calendar

class HorarioService:
    
    @staticmethod
    def create_horario(db: Session, horario: HorarioRecursoCreate) -> HorarioRecurso:
        """Crear un nuevo horario para un recurso"""
        # Validar que el recurso existe
        recurso = db.query(Recurso).filter(Recurso.id == horario.recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        # Validar que no hay solapamiento de horarios para el mismo día
        if HorarioService._has_horario_overlap(db, horario.recurso_id, horario.dia_semana, horario.hora_inicio, horario.hora_fin):
            raise HTTPException(status_code=400, detail="Ya existe un horario que se solapa para este día")
        
        # Validar que la hora de fin es posterior a la de inicio
        if horario.hora_fin <= horario.hora_inicio:
            raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la de inicio")
        
        # Validar formato de hora (HH:MM)
        try:
            datetime.strptime(horario.hora_inicio, "%H:%M")
            datetime.strptime(horario.hora_fin, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de hora inválido. Use HH:MM")
        
        db_horario = HorarioRecurso(**horario.dict())
        db.add(db_horario)
        db.commit()
        db.refresh(db_horario)
        return db_horario
    
    @staticmethod
    def get_horarios_recurso(db: Session, recurso_id: int) -> List[HorarioRecurso]:
        """Obtener todos los horarios de un recurso"""
        return db.query(HorarioRecurso).filter(HorarioRecurso.recurso_id == recurso_id).order_by(HorarioRecurso.dia_semana, HorarioRecurso.hora_inicio).all()
    
    @staticmethod
    def get_horario(db: Session, horario_id: int) -> HorarioRecurso:
        """Obtener un horario específico por ID"""
        horario = db.query(HorarioRecurso).filter(HorarioRecurso.id == horario_id).first()
        if not horario:
            raise HTTPException(status_code=404, detail="Horario no encontrado")
        return horario
    
    @staticmethod
    def update_horario(db: Session, horario_id: int, horario_update: HorarioRecursoUpdate) -> HorarioRecurso:
        """Actualizar un horario existente"""
        db_horario = HorarioService.get_horario(db, horario_id)
        
        # Si se está actualizando el día o las horas, validar que no hay solapamiento
        if horario_update.dia_semana is not None or horario_update.hora_inicio is not None or horario_update.hora_fin is not None:
            dia = horario_update.dia_semana or db_horario.dia_semana
            hora_inicio = horario_update.hora_inicio or db_horario.hora_inicio
            hora_fin = horario_update.hora_fin or db_horario.hora_fin
            
            if HorarioService._has_horario_overlap(db, db_horario.recurso_id, dia, hora_inicio, hora_fin, exclude_id=horario_id):
                raise HTTPException(status_code=400, detail="Ya existe un horario que se solapa para este día")
        
        # Actualizar campos
        update_data = horario_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_horario, field, value)
        
        db.commit()
        db.refresh(db_horario)
        return db_horario
    
    @staticmethod
    def delete_horario(db: Session, horario_id: int) -> bool:
        """Eliminar un horario"""
        db_horario = HorarioService.get_horario(db, horario_id)
        db.delete(db_horario)
        db.commit()
        return True
    
    @staticmethod
    def get_disponibilidad(db: Session, request: DisponibilidadRequest) -> dict:
        """Obtener disponibilidad de un recurso para una fecha específica"""
        # Parsear fecha
        try:
            fecha_obj = datetime.strptime(request.fecha, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        
        # Obtener el día de la semana (0=Lunes, 6=Domingo)
        dia_semana = fecha_obj.weekday()
        
        # Obtener el recurso
        recurso = db.query(Recurso).filter(Recurso.id == request.recurso_id).first()
        if not recurso:
            raise HTTPException(status_code=404, detail="Recurso no encontrado")
        
        # Obtener el horario para ese día
        horario = db.query(HorarioRecurso).filter(
            and_(
                HorarioRecurso.recurso_id == request.recurso_id,
                HorarioRecurso.dia_semana == dia_semana,
                HorarioRecurso.disponible == True
            )
        ).first()
        
        if not horario:
            return {
                "fecha": request.fecha,
                "recurso_id": request.recurso_id,
                "recurso_nombre": recurso.nombre,
                "slots_disponibles": [],
                "total_slots": 0,
                "slots_disponibles_count": 0,
                "mensaje": "No hay horario configurado para este día"
            }
        
        # Generar slots de disponibilidad
        slots = HorarioService._generar_slots_disponibilidad(
            db, request.recurso_id, fecha_obj, horario, request.servicio_id
        )
        
        slots_disponibles = [slot for slot in slots if slot.disponible]
        
        return {
            "fecha": request.fecha,
            "recurso_id": request.recurso_id,
            "recurso_nombre": recurso.nombre,
            "slots_disponibles": slots,
            "total_slots": len(slots),
            "slots_disponibles_count": len(slots_disponibles)
        }
    
    @staticmethod
    def _generar_slots_disponibilidad(db: Session, recurso_id: int, fecha: datetime, horario: HorarioRecurso, servicio_id: Optional[int] = None) -> List[SlotDisponibilidad]:
        """Generar slots de disponibilidad para un día específico"""
        slots = []
        
        # Convertir hora de inicio y fin a datetime para el día específico
        inicio_dia = datetime.combine(fecha.date(), datetime.strptime(horario.hora_inicio, "%H:%M").time())
        fin_dia = datetime.combine(fecha.date(), datetime.strptime(horario.hora_fin, "%H:%M").time())
        
        # Calcular duración del servicio si se proporciona
        duracion_servicio = 60  # Default 1 hora
        if servicio_id:
            servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
            if servicio:
                duracion_servicio = servicio.duracion_minutos
        
        # Generar slots
        current_time = inicio_dia
        while current_time < fin_dia:
            slot_fin = current_time + timedelta(minutes=duracion_servicio)
            
            # Verificar si el slot cabe en el horario
            if slot_fin <= fin_dia:
                # Verificar si hay reservas que se solapan
                disponible = not HorarioService._has_reserva_overlap(
                    db, recurso_id, current_time, slot_fin
                )
                
                slot = SlotDisponibilidad(
                    inicio=current_time.strftime("%H:%M"),
                    fin=slot_fin.strftime("%H:%M"),
                    disponible=disponible,
                    motivo_no_disponible=None if disponible else "Recurso ya reservado"
                )
                slots.append(slot)
            
            # Avanzar al siguiente slot
            current_time += timedelta(minutes=horario.duracion_slot_minutos + horario.pausa_entre_slots)
        
        return slots
    
    @staticmethod
    def _has_horario_overlap(db: Session, recurso_id: int, dia_semana: int, hora_inicio: str, hora_fin: str, exclude_id: Optional[int] = None) -> bool:
        """Verificar si hay solapamiento de horarios para el mismo día"""
        query = db.query(HorarioRecurso).filter(
            and_(
                HorarioRecurso.recurso_id == recurso_id,
                HorarioRecurso.dia_semana == dia_semana,
                HorarioRecurso.disponible == True,
                or_(
                    and_(HorarioRecurso.hora_inicio < hora_fin, HorarioRecurso.hora_fin > hora_inicio),
                    and_(HorarioRecurso.hora_inicio == hora_inicio, HorarioRecurso.hora_fin == hora_fin)
                )
            )
        )
        
        if exclude_id:
            query = query.filter(HorarioRecurso.id != exclude_id)
        
        return query.first() is not None
    
    @staticmethod
    def _has_reserva_overlap(db: Session, recurso_id: int, inicio: datetime, fin: datetime) -> bool:
        """Verificar si hay reservas que se solapan con un horario"""
        return db.query(Reserva).filter(
            and_(
                Reserva.recurso_id == recurso_id,
                Reserva.estado != "cancelada",
                or_(
                    and_(Reserva.fecha_hora_inicio < fin, Reserva.fecha_hora_fin > inicio),
                    and_(Reserva.fecha_hora_inicio == inicio, Reserva.fecha_hora_fin == fin)
                )
            )
        ).first() is not None
