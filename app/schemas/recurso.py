from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RecursoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del recurso")
    tipo: str = Field(..., min_length=1, max_length=50, description="Tipo de recurso (habitación, sala, etc.)")
    capacidad: int = Field(1, ge=1, description="Capacidad del recurso (número de personas)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional del recurso")
    disponible: bool = Field(True, description="Si el recurso está disponible")
    precio_base: float = Field(0.0, ge=0.0, description="Precio base por hora del recurso")

class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    capacidad: Optional[int] = Field(None, ge=1)
    descripcion: Optional[str] = Field(None, max_length=500)
    disponible: Optional[bool] = None
    precio_base: Optional[float] = Field(None, ge=0.0)

class RecursoResponse(RecursoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
