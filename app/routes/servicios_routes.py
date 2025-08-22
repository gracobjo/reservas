from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_sqlite_clean import get_db
from ..models.servicio import Servicio
from ..schemas.servicio import ServicioCreate, ServicioUpdate, ServicioResponse
from ..services.servicio_service import ServicioService

router = APIRouter(prefix="/servicios", tags=["servicios"])

@router.get("/", response_model=List[ServicioResponse])
async def get_servicios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obtener todos los servicios"""
    return ServicioService.get_all(db, skip=skip, limit=limit)

@router.get("/{servicio_id}", response_model=ServicioResponse)
async def get_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener un servicio específico por ID"""
    servicio = ServicioService.get_by_id(db, servicio_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

@router.post("/", response_model=ServicioResponse, status_code=201)
async def create_servicio(
    servicio: ServicioCreate, 
    db: Session = Depends(get_db)
):
    """Crear un nuevo servicio"""
    return ServicioService.create(db, servicio)

@router.put("/{servicio_id}", response_model=ServicioResponse)
async def update_servicio(
    servicio_id: int, 
    servicio: ServicioUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un servicio existente"""
    updated_servicio = ServicioService.update(db, servicio_id, servicio)
    if not updated_servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return updated_servicio

@router.delete("/{servicio_id}")
async def delete_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    success = ServicioService.delete(db, servicio_id)
    if not success:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": "Servicio eliminado correctamente"}
