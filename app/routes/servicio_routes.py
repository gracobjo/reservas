from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..services.servicio_service import ServicioService
from ..schemas.servicio import ServicioCreate, ServicioResponse, ServicioUpdate
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/servicios", tags=["servicios"])

@router.post("/", response_model=ServicioResponse)
def create_servicio(servicio: ServicioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo servicio"""
    return ServicioService.create_servicio(db, servicio)

@router.get("/", response_model=List[ServicioResponse])
def get_servicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de servicios"""
    return ServicioService.get_servicios(db, skip=skip, limit=limit)

@router.get("/{servicio_id}", response_model=ServicioResponse)
def get_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener un servicio por ID"""
    return ServicioService.get_servicio(db, servicio_id)

@router.put("/{servicio_id}", response_model=ServicioResponse)
def update_servicio(servicio_id: int, servicio: ServicioUpdate, db: Session = Depends(get_db)):
    """Actualizar un servicio"""
    return ServicioService.update_servicio(db, servicio_id, servicio)

@router.delete("/{servicio_id}", response_model=BaseResponse)
def delete_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    ServicioService.delete_servicio(db, servicio_id)
    return BaseResponse(success=True, message="Servicio eliminado exitosamente")
