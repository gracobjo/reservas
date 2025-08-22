from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..db_sqlite_clean import get_db
from ..services.horario_service import HorarioService
from ..schemas.horario import (
    HorarioRecursoCreate, 
    HorarioRecursoUpdate, 
    HorarioRecursoResponse,
    HorarioRecursoBulkCreate,
    DisponibilidadRequest,
    DisponibilidadResponse
)

router = APIRouter(prefix="/horarios", tags=["Horarios"])

@router.post("/", response_model=HorarioRecursoResponse)
async def crear_horario(
    horario: HorarioRecursoCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo horario para un recurso.
    
    - **recurso_id**: ID del recurso
    - **dia_semana**: Día de la semana (0=Lunes, 6=Domingo)
    - **hora_inicio**: Hora de inicio (HH:MM)
    - **hora_fin**: Hora de fin (HH:MM)
    - **duracion_slot_minutos**: Duración de cada slot en minutos
    - **pausa_entre_slots**: Pausa entre slots en minutos
    """
    return HorarioService.create_horario(db, horario)

@router.post("/bulk", response_model=List[HorarioRecursoResponse])
async def crear_horarios_masivos(
    horarios_bulk: HorarioRecursoBulkCreate,
    db: Session = Depends(get_db)
):
    """
    Crear múltiples horarios para un recurso de una vez.
    Útil para configurar toda la semana de un recurso.
    """
    horarios_creados = []
    for horario_data in horarios_bulk.horarios:
        horario_data.recurso_id = horarios_bulk.recurso_id
        horario = HorarioService.create_horario(db, horario_data)
        horarios_creados.append(horario)
    return horarios_creados

@router.get("/recurso/{recurso_id}", response_model=List[HorarioRecursoResponse])
async def obtener_horarios_recurso(
    recurso_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todos los horarios configurados para un recurso específico.
    Los horarios se devuelven ordenados por día de la semana y hora de inicio.
    """
    return HorarioService.get_horarios_recurso(db, recurso_id)

@router.get("/{horario_id}", response_model=HorarioRecursoResponse)
async def obtener_horario(
    horario_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un horario específico por su ID.
    """
    return HorarioService.get_horario(db, horario_id)

@router.put("/{horario_id}", response_model=HorarioRecursoResponse)
async def actualizar_horario(
    horario_id: int,
    horario_update: HorarioRecursoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un horario existente.
    Solo se actualizan los campos proporcionados.
    """
    return HorarioService.update_horario(db, horario_id, horario_update)

@router.delete("/{horario_id}")
async def eliminar_horario(
    horario_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un horario específico.
    """
    HorarioService.delete_horario(db, horario_id)
    return {"message": "Horario eliminado correctamente"}

@router.post("/disponibilidad", response_model=DisponibilidadResponse)
async def obtener_disponibilidad(
    request: DisponibilidadRequest,
    db: Session = Depends(get_db)
):
    """
    Obtener la disponibilidad de un recurso para una fecha específica.
    
    - **recurso_id**: ID del recurso
    - **fecha**: Fecha en formato YYYY-MM-DD
    - **servicio_id**: ID del servicio (opcional, para calcular duración del slot)
    
    Retorna:
    - Slots disponibles y no disponibles
    - Horarios de cada slot
    - Motivo por el que un slot no está disponible
    """
    return HorarioService.get_disponibilidad(db, request)

@router.get("/disponibilidad/{recurso_id}")
async def obtener_disponibilidad_get(
    recurso_id: int,
    fecha: str = Query(..., description="Fecha en formato YYYY-MM-DD"),
    servicio_id: int = Query(None, description="ID del servicio (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Obtener disponibilidad usando GET (más fácil para testing).
    
    - **recurso_id**: ID del recurso
    - **fecha**: Fecha en formato YYYY-MM-DD
    - **servicio_id**: ID del servicio (opcional)
    """
    request = DisponibilidadRequest(
        recurso_id=recurso_id,
        fecha=fecha,
        servicio_id=servicio_id
    )
    return HorarioService.get_disponibilidad(db, request)

@router.get("/semana/{recurso_id}")
async def obtener_horario_semanal(
    recurso_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener el horario completo de la semana para un recurso.
    Útil para mostrar un calendario semanal.
    """
    horarios = HorarioService.get_horarios_recurso(db, recurso_id)
    
    # Agrupar por día de la semana
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    horarios_por_dia = {i: [] for i in range(7)}
    
    for horario in horarios:
        horarios_por_dia[horario.dia_semana].append(horario)
    
    # Crear respuesta estructurada
    respuesta = {
        "recurso_id": recurso_id,
        "horarios_semana": {}
    }
    
    for dia_num, dia_nombre in enumerate(dias_semana):
        respuesta["horarios_semana"][dia_nombre] = [
            {
                "id": h.id,
                "hora_inicio": h.hora_inicio.strftime("%H:%M"),
                "hora_fin": h.hora_fin.strftime("%H:%M"),
                "duracion_slot_minutos": h.duracion_slot_minutos,
                "pausa_entre_slots": h.pausa_entre_slots,
                "disponible": h.disponible
            }
            for h in horarios_por_dia[dia_num]
        ]
    
    return respuesta
