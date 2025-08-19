from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RecursoBase(BaseModel):
    nombre: str
    tipo: str
    disponible: bool = True

class RecursoCreate(RecursoBase):
    pass

class RecursoUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo: Optional[str] = None
    disponible: Optional[bool] = None

class RecursoResponse(RecursoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
