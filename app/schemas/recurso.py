from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RecursoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del recurso")
    tipo: str = Field(..., min_length=1, max_length=50, description="Tipo de recurso (habitación, sala, etc.)")
    disponible: bool = Field(True, description="Si el recurso está disponible")

class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=50)
    disponible: Optional[bool] = None

class RecursoResponse(RecursoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
