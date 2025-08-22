from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db_sqlite_clean import get_db
from ..services.precio_dinamico_service import PrecioDinamicoService
from ..schemas.precio_dinamico import (
    ReglaPrecioCreate, ReglaPrecioUpdate, ReglaPrecioResponse,
    CalculoPrecioRequest, CalculoPrecioResponse,
    ConfiguracionPrecioCreate, ConfiguracionPrecioUpdate, ConfiguracionPrecioResponse,
    HistorialPrecioResponse, ReglaRapida
)

router = APIRouter(prefix="/precios-dinamicos", tags=["Precios Dinámicos"])

# Endpoints para reglas de precios
@router.post("/reglas", response_model=ReglaPrecioResponse)
async def crear_regla_precio(
    regla: ReglaPrecioCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva regla de precio dinámico.
    
    Las reglas permiten configurar modificadores de precio basados en:
    - Día de la semana
    - Hora del día
    - Temporadas (alta/baja)
    - Días festivos
    - Anticipación de la reserva
    - Duración del servicio
    - Número de participantes
    """
    return PrecioDinamicoService.create_regla(db, regla)

@router.get("/reglas", response_model=List[ReglaPrecioResponse])
async def obtener_reglas_precio(
    activas_solo: bool = Query(False, description="Solo reglas activas"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de reglas de precio dinámico.
    """
    return PrecioDinamicoService.get_reglas(db, activas_solo, skip, limit)

@router.get("/reglas/{regla_id}", response_model=ReglaPrecioResponse)
async def obtener_regla_precio(
    regla_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener una regla específica por ID.
    """
    return PrecioDinamicoService.get_regla(db, regla_id)

@router.put("/reglas/{regla_id}", response_model=ReglaPrecioResponse)
async def actualizar_regla_precio(
    regla_id: int,
    regla_update: ReglaPrecioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar una regla de precio existente.
    """
    return PrecioDinamicoService.update_regla(db, regla_id, regla_update)

@router.delete("/reglas/{regla_id}")
async def eliminar_regla_precio(
    regla_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar una regla de precio.
    """
    PrecioDinamicoService.delete_regla(db, regla_id)
    return {"message": "Regla eliminada correctamente"}

# Endpoint principal para cálculo de precios
@router.post("/calcular", response_model=CalculoPrecioResponse)
async def calcular_precio_dinamico(
    request: CalculoPrecioRequest,
    db: Session = Depends(get_db)
):
    """
    Calcular el precio dinámico para una reserva.
    
    Este endpoint aplica todas las reglas de precio activas y aplicables
    para calcular el precio final, mostrando los descuentos y recargos aplicados.
    """
    return PrecioDinamicoService.calcular_precio(db, request)

@router.get("/calcular/{servicio_id}")
async def calcular_precio_get(
    servicio_id: int,
    recurso_id: int = Query(..., description="ID del recurso"),
    fecha_hora_inicio: str = Query(..., description="Fecha y hora de inicio (ISO format)"),
    fecha_hora_fin: str = Query(..., description="Fecha y hora de fin (ISO format)"),
    participantes: int = Query(1, ge=1, description="Número de participantes"),
    cliente_id: Optional[int] = Query(None, description="ID del cliente"),
    tipo_cliente: str = Query("regular", description="Tipo de cliente"),
    db: Session = Depends(get_db)
):
    """
    Calcular precio usando GET para testing más fácil.
    """
    from datetime import datetime
    
    try:
        fecha_inicio = datetime.fromisoformat(fecha_hora_inicio.replace('Z', '+00:00'))
        fecha_fin = datetime.fromisoformat(fecha_hora_fin.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use formato ISO")
    
    request = CalculoPrecioRequest(
        servicio_id=servicio_id,
        recurso_id=recurso_id,
        fecha_hora_inicio=fecha_inicio,
        fecha_hora_fin=fecha_fin,
        participantes=participantes,
        cliente_id=cliente_id,
        tipo_cliente=tipo_cliente
    )
    
    return PrecioDinamicoService.calcular_precio(db, request)

# Endpoints para reglas rápidas predefinidas
@router.post("/reglas-rapidas/hora-pico", response_model=ReglaPrecioResponse)
async def crear_regla_hora_pico(
    regla: ReglaRapida,
    db: Session = Depends(get_db)
):
    """
    Crear una regla de hora pico de forma rápida.
    """
    if regla.tipo != "hora_pico":
        raise HTTPException(status_code=400, detail="Tipo de regla debe ser 'hora_pico'")
    
    config = regla.configuracion
    hora_inicio = config.get("hora_inicio")
    hora_fin = config.get("hora_fin")
    porcentaje_recargo = config.get("porcentaje_recargo")
    dias_semana = config.get("dias_semana", [])
    
    if not all([hora_inicio, hora_fin, porcentaje_recargo, dias_semana]):
        raise HTTPException(status_code=400, detail="Faltan parámetros requeridos")
    
    return PrecioDinamicoService.crear_regla_hora_pico(
        db, regla.nombre or "Hora Pico", hora_inicio, hora_fin, porcentaje_recargo, dias_semana
    )

@router.post("/reglas-rapidas/descuento-anticipacion", response_model=ReglaPrecioResponse)
async def crear_regla_descuento_anticipacion(
    regla: ReglaRapida,
    db: Session = Depends(get_db)
):
    """
    Crear una regla de descuento por anticipación.
    """
    if regla.tipo != "descuento_anticipacion":
        raise HTTPException(status_code=400, detail="Tipo de regla debe ser 'descuento_anticipacion'")
    
    config = regla.configuracion
    dias_minimos = config.get("dias_minimos")
    porcentaje_descuento = config.get("porcentaje_descuento")
    
    if not all([dias_minimos, porcentaje_descuento]):
        raise HTTPException(status_code=400, detail="Faltan parámetros requeridos")
    
    return PrecioDinamicoService.crear_regla_descuento_anticipacion(
        db, regla.nombre or "Descuento Anticipación", dias_minimos, porcentaje_descuento
    )

@router.post("/reglas-rapidas/fin-de-semana", response_model=ReglaPrecioResponse)
async def crear_regla_fin_de_semana(
    regla: ReglaRapida,
    db: Session = Depends(get_db)
):
    """
    Crear una regla de recargo por fin de semana.
    """
    if regla.tipo != "fin_de_semana":
        raise HTTPException(status_code=400, detail="Tipo de regla debe ser 'fin_de_semana'")
    
    config = regla.configuracion
    porcentaje_recargo = config.get("porcentaje_recargo")
    prioridad = config.get("prioridad", 15)
    dias_semana = config.get("dias_semana", [5, 6])  # Por defecto sábado y domingo
    
    if not porcentaje_recargo:
        raise HTTPException(status_code=400, detail="Falta el porcentaje de recargo")
    
    return PrecioDinamicoService.crear_regla_fin_de_semana(
        db, regla.nombre or "Recargo Fin de Semana", porcentaje_recargo, prioridad, dias_semana
    )

@router.post("/reglas-rapidas/temporada-alta", response_model=ReglaPrecioResponse)
async def crear_regla_temporada_alta(
    regla: ReglaRapida,
    db: Session = Depends(get_db)
):
    """
    Crear una regla de temporada alta.
    """
    if regla.tipo != "temporada_alta":
        raise HTTPException(status_code=400, detail="Tipo de regla debe ser 'temporada_alta'")
    
    config = regla.configuracion
    fecha_inicio = config.get("fecha_inicio")
    fecha_fin = config.get("fecha_fin")
    porcentaje_recargo = config.get("porcentaje_recargo")
    
    if not all([fecha_inicio, fecha_fin, porcentaje_recargo]):
        raise HTTPException(status_code=400, detail="Faltan parámetros requeridos")
    
    return PrecioDinamicoService.crear_regla_temporada_alta(
        db, regla.nombre or "Temporada Alta", fecha_inicio, fecha_fin, porcentaje_recargo
    )

# Endpoints para simulación
@router.get("/simular/{servicio_id}")
async def simular_precios_semana(
    servicio_id: int,
    recurso_id: int = Query(..., description="ID del recurso"),
    fecha_inicio: str = Query(..., description="Fecha de inicio de la semana (YYYY-MM-DD)"),
    hora_servicio: str = Query("10:00", description="Hora del servicio (HH:MM)"),
    duracion_horas: int = Query(1, ge=1, description="Duración en horas"),
    participantes: int = Query(1, ge=1, description="Número de participantes"),
    db: Session = Depends(get_db)
):
    """
    Simular precios para una semana completa.
    Útil para ver cómo varían los precios día a día.
    """
    from datetime import datetime, timedelta
    
    try:
        fecha_base = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
    
    resultados = {}
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    for i in range(7):
        fecha_dia = fecha_base + timedelta(days=i)
        fecha_hora_inicio = datetime.combine(
            fecha_dia.date(), 
            datetime.strptime(hora_servicio, "%H:%M").time()
        )
        fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)
        
        request = CalculoPrecioRequest(
            servicio_id=servicio_id,
            recurso_id=recurso_id,
            fecha_hora_inicio=fecha_hora_inicio,
            fecha_hora_fin=fecha_hora_fin,
            participantes=participantes,
            tipo_cliente="regular"
        )
        
        try:
            calculo = PrecioDinamicoService.calcular_precio(db, request)
            resultados[dias_semana[i]] = {
                "fecha": fecha_dia.strftime("%Y-%m-%d"),
                "precio_base": calculo.precio_base,
                "precio_final": calculo.precio_final,
                "descuento_total": calculo.descuento_total,
                "recargo_total": calculo.recargo_total,
                "ahorro": calculo.ahorro_total,
                "reglas_aplicadas": len(calculo.reglas_aplicadas)
            }
        except Exception as e:
            resultados[dias_semana[i]] = {
                "error": str(e)
            }
    
    return {
        "servicio_id": servicio_id,
        "recurso_id": recurso_id,
        "fecha_inicio": fecha_inicio,
        "simulacion_semanal": resultados
    }

# Endpoints para estadísticas
@router.get("/estadisticas/reglas")
async def obtener_estadisticas_reglas(
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas sobre las reglas de precio.
    """
    reglas = PrecioDinamicoService.get_reglas(db, limit=1000)
    
    estadisticas = {
        "total_reglas": len(reglas),
        "reglas_activas": len([r for r in reglas if r.activa]),
        "reglas_inactivas": len([r for r in reglas if not r.activa]),
        "por_tipo": {},
        "por_modificador": {}
    }
    
    # Estadísticas por tipo de regla
    for regla in reglas:
        tipo = regla.tipo_regla
        if tipo not in estadisticas["por_tipo"]:
            estadisticas["por_tipo"][tipo] = 0
        estadisticas["por_tipo"][tipo] += 1
        
        # Estadísticas por tipo de modificador
        modificador = regla.tipo_modificador
        if modificador not in estadisticas["por_modificador"]:
            estadisticas["por_modificador"][modificador] = 0
        estadisticas["por_modificador"][modificador] += 1
    
    return estadisticas
