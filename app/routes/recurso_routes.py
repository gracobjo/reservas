from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db_sqlite_clean import get_db
from ..services.recurso_service import RecursoService
from ..schemas.recurso import RecursoCreate, RecursoResponse, RecursoUpdate
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/recursos", tags=["recursos"])

@router.post("/", response_model=RecursoResponse)
def create_recurso(recurso: RecursoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo recurso"""
    return RecursoService.create(db, recurso)

@router.get("/", response_model=List[RecursoResponse])
def get_recursos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de recursos"""
    return RecursoService.get_all(db, skip=skip, limit=limit)

@router.get("/disponibles", response_model=List[RecursoResponse])
def get_recursos_disponibles(db: Session = Depends(get_db)):
    """Obtener recursos disponibles"""
    return RecursoService.get_disponibles(db)

@router.get("/{recurso_id}", response_model=RecursoResponse)
def get_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener un recurso por ID"""
    recurso = RecursoService.get_by_id(db, recurso_id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso

@router.put("/{recurso_id}", response_model=RecursoResponse)
def update_recurso(recurso_id: int, recurso: RecursoUpdate, db: Session = Depends(get_db)):
    """Actualizar un recurso"""
    updated_recurso = RecursoService.update(db, recurso_id, recurso)
    if not updated_recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return updated_recurso

@router.put("/{recurso_id}/toggle-disponibilidad", response_model=RecursoResponse)
def toggle_disponibilidad(recurso_id: int, db: Session = Depends(get_db)):
    """Cambiar la disponibilidad de un recurso"""
    recurso = RecursoService.toggle_disponibilidad(db, recurso_id)
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return recurso

@router.delete("/{recurso_id}", response_model=BaseResponse)
def delete_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Eliminar un recurso"""
    success = RecursoService.delete(db, recurso_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    return BaseResponse(success=True, message="Recurso eliminado exitosamente")
