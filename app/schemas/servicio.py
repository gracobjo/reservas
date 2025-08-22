from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ServicioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del servicio")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del servicio")
    duracion_minutos: int = Field(..., gt=0, description="Duración en minutos")
    precio_base: float = Field(..., gt=0, description="Precio base del servicio")

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    duracion_minutos: Optional[int] = Field(None, gt=0)
    precio_base: Optional[float] = Field(None, gt=0)

class ServicioResponse(ServicioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
