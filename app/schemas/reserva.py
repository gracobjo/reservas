from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ReservaBase(BaseModel):
    cliente_id: int
    servicio_id: int
    recurso_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str = "pendiente"

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    fecha_hora_inicio: Optional[datetime] = None
    fecha_hora_fin: Optional[datetime] = None
    estado: Optional[str] = None

class ReservaResponse(ReservaBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DisponibilidadResponse(BaseModel):
    fecha: str
    servicio_id: int
    horarios_disponibles: List[dict]
    
    class Config:
        from_attributes = True
