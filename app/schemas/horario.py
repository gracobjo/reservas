from pydantic import BaseModel, Field, validator
from typing import Optional, List
# No necesitamos importar time
from enum import IntEnum

class DiaSemana(IntEnum):
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6

class HorarioRecursoBase(BaseModel):
    recurso_id: int = Field(..., description="ID del recurso")
    dia_semana: int = Field(..., ge=0, le=6, description="Día de la semana (0=Lunes, 6=Domingo)")
    hora_inicio: str = Field(..., description="Hora de inicio del horario (formato HH:MM)")
    hora_fin: str = Field(..., description="Hora de fin del horario (formato HH:MM)")
    duracion_slot_minutos: int = Field(30, ge=1, le=480, description="Duración de cada slot en minutos")
    pausa_entre_slots: int = Field(0, ge=0, le=60, description="Pausa entre slots en minutos")
    disponible: bool = Field(True, description="Si el horario está disponible")

class HorarioRecursoCreate(HorarioRecursoBase):
    pass

class HorarioRecursoUpdate(BaseModel):
    dia_semana: Optional[int] = Field(None, ge=0, le=6)
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    duracion_slot_minutos: Optional[int] = Field(None, ge=1, le=480)
    pausa_entre_slots: Optional[int] = Field(None, ge=0, le=60)
    disponible: Optional[bool] = None

class HorarioRecursoResponse(HorarioRecursoBase):
    id: int
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

class HorarioRecursoBulkCreate(BaseModel):
    recurso_id: int
    horarios: List[HorarioRecursoBase]

class HorarioSemanal(BaseModel):
    recurso_id: int
    recurso_nombre: str
    horarios: List[HorarioRecursoResponse]

class DisponibilidadRequest(BaseModel):
    recurso_id: int
    fecha: str  # YYYY-MM-DD
    servicio_id: Optional[int] = None

class SlotDisponibilidad(BaseModel):
    inicio: str  # HH:MM
    fin: str     # HH:MM
    disponible: bool
    precio: Optional[float] = None
    motivo_no_disponible: Optional[str] = None

class DisponibilidadResponse(BaseModel):
    fecha: str
    recurso_id: int
    recurso_nombre: str
    slots_disponibles: List[SlotDisponibilidad]
    total_slots: int
    slots_disponibles_count: int
