from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import List
from ..models.reserva import Reserva
from ..models.servicio import Servicio
from ..models.recurso import Recurso
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
    def get_reserva(db: Session, reserva_id: int) -> Reserva:
        db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if db_reserva is None:
            raise HTTPException(status_code=404, detail="Reserva not found")
        return db_reserva
    
    @staticmethod
    def update_reserva(db: Session, reserva_id: int, reserva: ReservaUpdate) -> Reserva:
        db_reserva = ReservaService.get_reserva(db, reserva_id)
        
        # If updating time, check for overlaps
        if reserva.fecha_hora_inicio or reserva.fecha_hora_fin:
            start_time = reserva.fecha_hora_inicio or db_reserva.fecha_hora_inicio
            end_time = reserva.fecha_hora_fin or db_reserva.fecha_hora_fin
            
            if ReservaService._has_overlap(db, db_reserva.recurso_id, start_time, end_time, exclude_id=reserva_id):
                raise HTTPException(status_code=400, detail="Recurso no disponible en ese horario")
        
        update_data = reserva.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_reserva, field, value)
        
        db.commit()
        db.refresh(db_reserva)
        return db_reserva
    
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
