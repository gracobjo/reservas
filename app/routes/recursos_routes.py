from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_sqlite_clean import get_db
from ..models.recurso import Recurso
from ..schemas.recurso import RecursoCreate, RecursoUpdate, RecursoResponse
from ..services.recurso_service import RecursoService

router = APIRouter(prefix="/recursos", tags=["recursos"])

@router.get("/", response_model=List[RecursoResponse])
async def get_recursos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Obtener todos los recursos"""
    return RecursoService.get_all(db, skip=skip, limit=limit)

@router.get("/{recurso_id}", response_model=RecursoResponse)
async def get_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener un recurso específico por ID"""
    recurso = RecursoService.get_by_id(db, recurso_id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso

@router.post("/", response_model=RecursoResponse, status_code=201)
async def create_recurso(
    recurso: RecursoCreate, 
    db: Session = Depends(get_db)
):
    """Crear un nuevo recurso"""
    return RecursoService.create(db, recurso)

@router.put("/{recurso_id}", response_model=RecursoResponse)
async def update_recurso(
    recurso_id: int, 
    recurso: RecursoUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar un recurso existente"""
    updated_recurso = RecursoService.update(db, recurso_id, recurso)
    if not updated_recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return updated_recurso

@router.delete("/{recurso_id}")
async def delete_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Eliminar un recurso"""
    success = RecursoService.delete(db, recurso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return {"message": "Recurso eliminado correctamente"}

@router.put("/{recurso_id}/toggle-disponibilidad")
async def toggle_disponibilidad(recurso_id: int, db: Session = Depends(get_db)):
    """Cambiar la disponibilidad de un recurso"""
    recurso = RecursoService.toggle_disponibilidad(db, recurso_id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso
