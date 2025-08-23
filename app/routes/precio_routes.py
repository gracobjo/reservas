from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..db_sqlite_clean import get_db
from ..services.precio_service import PrecioService
from ..schemas.precio import (
    PrecioCreate, PrecioUpdate, PrecioResponse, PrecioCompletoResponse,
    CalculoPrecioRequest, CalculoPrecioResponse, FiltroPrecios,
    EstadisticasPreciosResponse
)
from ..schemas.base import BaseResponse

router = APIRouter(prefix="/api/precios", tags=["precios"])

# ============================================================================
# RUTAS CRUD PARA PRECIOS
# ============================================================================

@router.post("/", response_model=PrecioResponse, status_code=status.HTTP_201_CREATED)
def crear_precio(precio: PrecioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo precio"""
    try:
        return PrecioService.create_precio(db, precio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno: {str(e)}"
        )

@router.get("/", response_model=List[PrecioResponse])
def listar_precios(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """Listar todos los precios"""
    try:
        precios = PrecioService.listar_precios(db, skip=skip, limit=limit, filtros=None)
        return precios
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando precios: {str(e)}"
        )

@router.get("/{precio_id}", response_model=PrecioCompletoResponse)
def obtener_precio(precio_id: int, db: Session = Depends(get_db)):
    """Obtener un precio por ID con información completa"""
    try:
        precio = PrecioService.get_precio(db, precio_id)
        
        # Crear respuesta completa
        response_data = precio.__dict__.copy()
        
        # Agregar información del servicio si existe
        if precio.servicio_id and precio.servicio:
            response_data["servicio"] = {
                "id": precio.servicio.id,
                "nombre": precio.servicio.nombre,
                "descripcion": precio.servicio.descripcion
            }
        
        # Agregar información del recurso si existe
        if precio.recurso_id and precio.recurso:
            response_data["recurso"] = {
                "id": precio.recurso.id,
                "nombre": precio.recurso.nombre,
                "tipo": precio.recurso.tipo
            }
        
        return PrecioCompletoResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo precio: {str(e)}"
        )

@router.put("/{precio_id}", response_model=PrecioResponse)
def actualizar_precio(precio_id: int, precio: PrecioUpdate, db: Session = Depends(get_db)):
    """Actualizar un precio existente"""
    try:
        return PrecioService.update_precio(db, precio_id, precio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando precio: {str(e)}"
        )

@router.delete("/{precio_id}", response_model=BaseResponse)
def eliminar_precio(precio_id: int, db: Session = Depends(get_db)):
    """Eliminar un precio"""
    try:
        PrecioService.delete_precio(db, precio_id)
        return BaseResponse(success=True, message="Precio eliminado exitosamente")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando precio: {str(e)}"
        )

# ============================================================================
# RUTAS PARA PRECIOS POR SERVICIO
# ============================================================================

@router.get("/servicio/{servicio_id}", response_model=List[PrecioResponse])
def obtener_precios_por_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener todos los precios de un servicio específico"""
    try:
        return PrecioService.get_precios_by_servicio(db, servicio_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo precios del servicio: {str(e)}"
        )

@router.get("/servicio/{servicio_id}/base", response_model=PrecioResponse)
def obtener_precio_base_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener el precio base de un servicio"""
    try:
        precio = PrecioService.get_precio_base_servicio(db, servicio_id)
        if not precio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Precio base no encontrado para este servicio"
            )
        return precio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo precio base: {str(e)}"
        )

# ============================================================================
# RUTAS PARA PRECIOS POR RECURSO
# ============================================================================

@router.get("/recurso/{recurso_id}", response_model=List[PrecioResponse])
def obtener_precios_por_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener todos los precios de un recurso específico"""
    try:
        return PrecioService.get_precios_by_recurso(db, recurso_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo precios del recurso: {str(e)}"
        )

@router.get("/recurso/{recurso_id}/base", response_model=PrecioResponse)
def obtener_precio_base_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener el precio base de un recurso"""
    try:
        precio = PrecioService.get_precio_base_recurso(db, recurso_id)
        if not precio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Precio base no encontrado para este recurso"
            )
        return precio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo precio base: {str(e)}"
        )

# ============================================================================
# RUTAS PARA CÁLCULO DE PRECIOS
# ============================================================================

@router.post("/calcular", response_model=CalculoPrecioResponse)
def calcular_precio(calculo_request: CalculoPrecioRequest, db: Session = Depends(get_db)):
    """Calcular el precio final para una reserva"""
    try:
        return PrecioService.calcular_precio(db, calculo_request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando precio: {str(e)}"
        )

@router.post("/calcular/servicio/{servicio_id}", response_model=CalculoPrecioResponse)
def calcular_precio_servicio(
    servicio_id: int,
    fecha_inicio: datetime = Query(..., description="Fecha y hora de inicio"),
    fecha_fin: datetime = Query(..., description="Fecha y hora de fin"),
    cantidad: int = Query(1, ge=1, description="Cantidad de unidades"),
    cliente_id: Optional[int] = Query(None, description="ID del cliente para descuentos"),
    db: Session = Depends(get_db)
):
    """Calcular precio para un servicio específico"""
    try:
        calculo_request = CalculoPrecioRequest(
            servicio_id=servicio_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cantidad=cantidad,
            cliente_id=cliente_id
        )
        return PrecioService.calcular_precio(db, calculo_request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando precio del servicio: {str(e)}"
        )

@router.post("/calcular/recurso/{recurso_id}", response_model=CalculoPrecioResponse)
def calcular_precio_recurso(
    recurso_id: int,
    fecha_inicio: datetime = Query(..., description="Fecha y hora de inicio"),
    fecha_fin: datetime = Query(..., description="Fecha y hora de fin"),
    cantidad: int = Query(1, ge=1, description="Cantidad de unidades"),
    cliente_id: Optional[int] = Query(None, description="ID del cliente para descuentos"),
    db: Session = Depends(get_db)
):
    """Calcular precio para un recurso específico"""
    try:
        calculo_request = CalculoPrecioRequest(
            recurso_id=recurso_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cantidad=cantidad,
            cliente_id=cliente_id
        )
        return PrecioService.calcular_precio(db, calculo_request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando precio del recurso: {str(e)}"
        )

# ============================================================================
# RUTAS PARA ESTADÍSTICAS Y REPORTES
# ============================================================================

@router.get("/estadisticas/general", response_model=EstadisticasPreciosResponse)
def obtener_estadisticas_precios(db: Session = Depends(get_db)):
    """Obtener estadísticas generales de precios"""
    try:
        return PrecioService.obtener_estadisticas(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.get("/estadisticas/servicio/{servicio_id}")
def obtener_estadisticas_servicio(servicio_id: int, db: Session = Depends(get_db)):
    """Obtener estadísticas de precios de un servicio específico"""
    try:
        precios = PrecioService.get_precios_by_servicio(db, servicio_id)
        
        if not precios:
            return {
                "servicio_id": servicio_id,
                "total_precios": 0,
                "precio_promedio": 0.0,
                "precio_minimo": 0.0,
                "precio_maximo": 0.0
            }
        
        precios_base = [p.precio_base for p in precios]
        
        return {
            "servicio_id": servicio_id,
            "total_precios": len(precios),
            "precio_promedio": sum(precios_base) / len(precios_base),
            "precio_minimo": min(precios_base),
            "precio_maximo": max(precios_base),
            "tipos_precio": list(set(p.tipo_precio.value for p in precios))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas del servicio: {str(e)}"
        )

@router.get("/estadisticas/recurso/{recurso_id}")
def obtener_estadisticas_recurso(recurso_id: int, db: Session = Depends(get_db)):
    """Obtener estadísticas de precios de un recurso específico"""
    try:
        precios = PrecioService.get_precios_by_recurso(db, recurso_id)
        
        if not precios:
            return {
                "recurso_id": recurso_id,
                "total_precios": 0,
                "precio_promedio": 0.0,
                "precio_minimo": 0.0,
                "precio_maximo": 0.0
            }
        
        precios_base = [p.precio_base for p in precios]
        
        return {
            "recurso_id": recurso_id,
            "total_precios": len(precios),
            "precio_promedio": sum(precios_base) / len(precios_base),
            "precio_minimo": min(precios_base),
            "precio_maximo": max(precios_base),
            "tipos_precio": list(set(p.tipo_precio.value for p in precios))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas del recurso: {str(e)}"
        )

# ============================================================================
# RUTAS PARA GESTIÓN AVANZADA
# ============================================================================

@router.post("/{precio_id}/activar")
def activar_precio(precio_id: int, db: Session = Depends(get_db)):
    """Activar un precio inactivo"""
    try:
        precio = PrecioService.get_precio(db, precio_id)
        precio.activo = True
        precio.updated_at = datetime.now()
        db.commit()
        db.refresh(precio)
        return {"mensaje": "Precio activado exitosamente", "precio_id": precio_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error activando precio: {str(e)}"
        )

@router.post("/{precio_id}/desactivar")
def desactivar_precio(precio_id: int, db: Session = Depends(get_db)):
    """Desactivar un precio activo"""
    try:
        precio = PrecioService.get_precio(db, precio_id)
        precio.activo = False
        precio.updated_at = datetime.now()
        db.commit()
        db.refresh(precio)
        return {"mensaje": "Precio desactivado exitosamente", "precio_id": precio_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error desactivando precio: {str(e)}"
        )

@router.post("/{precio_id}/duplicar", response_model=PrecioResponse)
def duplicar_precio(precio_id: int, db: Session = Depends(get_db)):
    """Duplicar un precio existente"""
    try:
        precio_original = PrecioService.get_precio(db, precio_id)
        
        # Crear nuevo precio duplicado
        nuevo_precio_data = PrecioCreate(
            servicio_id=precio_original.servicio_id,
            recurso_id=precio_original.recurso_id,
            tipo_precio=precio_original.tipo_precio,
            nombre=f"{precio_original.nombre} (Copia)",
            descripcion=precio_original.descripcion,
            precio_base=precio_original.precio_base,
            moneda=precio_original.moneda,
            activo=False,  # El duplicado inicia inactivo
            prioridad=precio_original.prioridad,
            fecha_inicio=precio_original.fecha_inicio,
            fecha_fin=precio_original.fecha_fin,
            cantidad_minima=precio_original.cantidad_minima,
            cantidad_maxima=precio_original.cantidad_maxima,
            dias_semana=precio_original.dias_semana,
            hora_inicio=precio_original.hora_inicio,
            hora_fin=precio_original.hora_fin,
            metadatos=precio_original.metadatos
        )
        
        return PrecioService.create_precio(db, nuevo_precio_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error duplicando precio: {str(e)}"
        )
