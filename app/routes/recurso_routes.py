from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..services.recurso_service import RecursoService
from ..schemas.recurso import RecursoCreate, RecursoResponse, RecursoUpdate
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/recursos", tags=["recursos"])

@router.post("/", response_model=RecursoResponse)
def create_recurso(recurso: RecursoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo recurso"""
    return RecursoService.create_recurso(db, recurso)

@router.get("/", response_model=List[RecursoResponse])
def get_recursos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener lista de recursos"""
    return RecursoService.get_recursos(db, skip=skip, limit=limit)

@router.get("/disponibles", response_model=List[RecursoResponse])
def get_recursos_disponibles(db: Session = Depends(get_db)):
    """Obtener recursos disponibles"""
    return RecursoService.get_recursos_disponibles(db)

@router.get("/{recurso_id}", response_model=RecursoResponse)
def get_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener un recurso por ID"""
    return RecursoService.get_recurso(db, recurso_id)

@router.put("/{recurso_id}", response_model=RecursoResponse)
def update_recurso(recurso_id: int, recurso: RecursoUpdate, db: Session = Depends(get_db)):
    """Actualizar un recurso"""
    return RecursoService.update_recurso(db, recurso_id, recurso)

@router.delete("/{recurso_id}", response_model=BaseResponse)
def delete_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Eliminar un recurso"""
    RecursoService.delete_recurso(db, recurso_id)
    return BaseResponse(success=True, message="Recurso eliminado exitosamente")
