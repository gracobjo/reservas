from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db_sqlite_clean import get_db
from ..services.precio_service import PrecioService
from ..schemas.precio import PrecioCreate, PrecioResponse, PrecioUpdate
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/precios", tags=["precios"])

@router.post("/", response_model=PrecioResponse)
def create_precio(precio: PrecioCreate, db: Session = Depends(get_db)):
    """Crear una nueva regla de precio"""
    return PrecioService.create_precio(db, precio)

@router.get("/servicio/{servicio_id}", response_model=List[PrecioResponse])
def get_precios_by_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener precios por servicio"""
    return PrecioService.get_precios_by_servicio(db, servicio_id)

@router.get("/{precio_id}", response_model=PrecioResponse)
def get_precio(precio_id: int, db: Session = Depends(get_db)):
    """Obtener un precio por ID"""
    return PrecioService.get_precio(db, precio_id)

@router.put("/{precio_id}", response_model=PrecioResponse)
def update_precio(precio_id: int, precio: PrecioUpdate, db: Session = Depends(get_db)):
    """Actualizar un precio"""
    return PrecioService.update_precio(db, precio_id, precio)

@router.delete("/{precio_id}", response_model=BaseResponse)
def delete_precio(precio_id: int, db: Session = Depends(get_db)):
    """Eliminar un precio"""
    PrecioService.delete_precio(db, precio_id)
    return BaseResponse(success=True, message="Precio eliminado exitosamente")
