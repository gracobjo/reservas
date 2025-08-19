from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PrecioBase(BaseModel):
    servicio_id: int
    tipo_regla: str
    valor: float
    descripcion: Optional[str] = None

class PrecioCreate(PrecioBase):
    pass

class PrecioUpdate(BaseModel):
    tipo_regla: Optional[str] = None
    valor: Optional[float] = None
    descripcion: Optional[str] = None

class PrecioResponse(PrecioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
