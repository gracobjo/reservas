from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..services.cliente_service import ClienteService
from ..schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("/", response_model=ClienteResponse)
def create_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crear un nuevo cliente"""
    return ClienteService.create_cliente(db, cliente)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtener un cliente por ID"""
    return ClienteService.get_cliente(db, cliente_id)

@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(cliente_id: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    """Actualizar un cliente"""
    return ClienteService.update_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}", response_model=BaseResponse)
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Eliminar un cliente"""
    ClienteService.delete_cliente(db, cliente_id)
    return BaseResponse(success=True, message="Cliente eliminado exitosamente")
