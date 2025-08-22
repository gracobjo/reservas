from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db_sqlite_clean import get_db
from ..services.reserva_service import ReservaService
from ..schemas.reserva import ReservaCreate, ReservaResponse, ReservaUpdate, DisponibilidadResponse
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/reservas", tags=["reservas"])

@router.post("/", response_model=ReservaResponse)
def create_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    """Crear una nueva reserva"""
    return ReservaService.create_reserva(db, reserva)

@router.get("/listar", response_model=List[ReservaResponse])
def listar_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar todas las reservas"""
    return ReservaService.get_all_reservas(db, skip=skip, limit=limit)

@router.get("/disponibilidad", response_model=DisponibilidadResponse)
def get_disponibilidad(servicio_id: int, fecha: str, db: Session = Depends(get_db)):
    """Obtener disponibilidad de un servicio para una fecha específica"""
    return ReservaService.get_disponibilidad(db, servicio_id, fecha)

@router.get("/{reserva_id}", response_model=ReservaResponse)
def get_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Obtener una reserva por ID"""
    return ReservaService.get_reserva(db, reserva_id)

@router.put("/{reserva_id}", response_model=ReservaResponse)
def update_reserva(reserva_id: int, reserva: ReservaUpdate, db: Session = Depends(get_db)):
    """Actualizar una reserva"""
    return ReservaService.update_reserva(db, reserva_id, reserva)

@router.delete("/{reserva_id}", response_model=BaseResponse)
def delete_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Eliminar una reserva"""
    ReservaService.delete_reserva(db, reserva_id)
    return BaseResponse(success=True, message="Reserva eliminada exitosamente")

@router.post("/{reserva_id}/cancelar", response_model=ReservaResponse)
def cancel_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Cancelar una reserva"""
    return ReservaService.cancel_reserva(db, reserva_id)

