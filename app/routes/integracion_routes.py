from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..db_sqlite_clean import get_db
from ..services.integracion_service import (
    IntegracionService, NotificacionService, GoogleCalendarService, 
    WebhookService, ResumenIntegracionesService
)
from ..models.integracion import Integracion, Notificacion, SincronizacionGoogleCalendar, Webhook
from ..schemas.integracion import (
    IntegracionCreate, IntegracionUpdate, IntegracionResponse,
    NotificacionCreate, NotificacionUpdate, NotificacionResponse,
    SincronizacionGoogleCalendarCreate, SincronizacionGoogleCalendarResponse,
    WebhookCreate, WebhookUpdate, WebhookResponse,
    EstadoIntegracionesResponse, ResumenNotificacionesResponse,
    TestIntegracionRequest, TestIntegracionResponse
)

router = APIRouter(prefix="/api/integraciones", tags=["integraciones"])

# ============================================================================
# RUTAS PARA INTEGRACIONES
# ============================================================================

@router.post("/", response_model=IntegracionResponse, status_code=status.HTTP_201_CREATED)
def crear_integracion(integracion_data: IntegracionCreate, db: Session = Depends(get_db)):
    """Crear una nueva integración"""
    try:
        integracion = IntegracionService.crear_integracion(db, integracion_data)
        return integracion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear integración: {str(e)}"
        )

@router.get("/", response_model=List[IntegracionResponse])
def obtener_integraciones(db: Session = Depends(get_db)):
    """Obtener todas las integraciones"""
    integraciones = db.query(Integracion).all()
    return integraciones

@router.get("/{integracion_id}", response_model=IntegracionResponse)
def obtener_integracion(integracion_id: int, db: Session = Depends(get_db)):
    """Obtener una integración por ID"""
    integracion = IntegracionService.obtener_integracion(db, integracion_id)
    if not integracion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integración no encontrada"
        )
    return integracion

@router.get("/tipo/{tipo}", response_model=List[IntegracionResponse])
def obtener_integraciones_por_tipo(tipo: str, db: Session = Depends(get_db)):
    """Obtener integraciones por tipo"""
    try:
        from ..models.integracion import TipoIntegracion
        tipo_enum = TipoIntegracion(tipo)
        integraciones = IntegracionService.obtener_integraciones_por_tipo(db, tipo_enum)
        return integraciones
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de integración '{tipo}' no válido"
        )

@router.put("/{integracion_id}", response_model=IntegracionResponse)
def actualizar_integracion(integracion_id: int, integracion_data: IntegracionUpdate, db: Session = Depends(get_db)):
    """Actualizar una integración existente"""
    integracion = IntegracionService.actualizar_integracion(db, integracion_id, integracion_data)
    if not integracion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integración no encontrada"
        )
    return integracion

@router.delete("/{integracion_id}")
def eliminar_integracion(integracion_id: int, db: Session = Depends(get_db)):
    """Eliminar una integración"""
    integracion = db.query(Integracion).filter(Integracion.id == integracion_id).first()
    if not integracion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integración no encontrada"
        )
    
    db.delete(integracion)
    db.commit()
    return {"mensaje": "Integración eliminada exitosamente"}

@router.post("/{integracion_id}/probar", response_model=TestIntegracionResponse)
def probar_integracion(
    integracion_id: int, 
    test_data: TestIntegracionRequest, 
    db: Session = Depends(get_db)
):
    """Probar una integración enviando un mensaje de prueba"""
    resultado = IntegracionService.probar_integracion(
        db, integracion_id, test_data.destinatario, test_data.mensaje
    )
    return TestIntegracionResponse(**resultado)

# ============================================================================
# RUTAS PARA NOTIFICACIONES
# ============================================================================

@router.post("/notificaciones", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
def crear_notificacion(notificacion_data: NotificacionCreate, db: Session = Depends(get_db)):
    """Crear una nueva notificación"""
    try:
        notificacion = NotificacionService.crear_notificacion(db, notificacion_data)
        return notificacion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear notificación: {str(e)}"
        )

@router.get("/notificaciones", response_model=List[NotificacionResponse])
def obtener_notificaciones(db: Session = Depends(get_db)):
    """Obtener todas las notificaciones"""
    notificaciones = db.query(Notificacion).order_by(Notificacion.created_at.desc()).all()
    return notificaciones

@router.get("/notificaciones/{notificacion_id}", response_model=NotificacionResponse)
def obtener_notificacion(notificacion_id: int, db: Session = Depends(get_db)):
    """Obtener una notificación por ID"""
    notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    return notificacion

@router.put("/notificaciones/{notificacion_id}", response_model=NotificacionResponse)
def actualizar_notificacion(notificacion_id: int, notificacion_data: NotificacionUpdate, db: Session = Depends(get_db)):
    """Actualizar una notificación existente"""
    notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    for field, value in notificacion_data.dict(exclude_unset=True).items():
        setattr(notificacion, field, value)
    
    db.commit()
    db.refresh(notificacion)
    return notificacion

@router.post("/notificaciones/{notificacion_id}/enviar")
def enviar_notificacion(notificacion_id: int, db: Session = Depends(get_db)):
    """Enviar una notificación específica"""
    notificacion = NotificacionService.enviar_notificacion(db, notificacion_id)
    if not notificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )
    
    if notificacion.enviada:
        return {"mensaje": "Notificación enviada exitosamente", "notificacion_id": notificacion_id}
    else:
        return {"mensaje": "Error al enviar notificación", "error": notificacion.error_mensaje}

@router.post("/notificaciones/procesar-pendientes")
def procesar_notificaciones_pendientes(db: Session = Depends(get_db)):
    """Procesar todas las notificaciones pendientes"""
    enviadas = NotificacionService.procesar_notificaciones_pendientes(db)
    return {"mensaje": f"Procesadas {enviadas} notificaciones pendientes"}

# ============================================================================
# RUTAS PARA GOOGLE CALENDAR
# ============================================================================

@router.post("/google-calendar/sincronizar", response_model=SincronizacionGoogleCalendarResponse, status_code=status.HTTP_201_CREATED)
def sincronizar_reserva_google_calendar(
    sincronizacion_data: SincronizacionGoogleCalendarCreate, 
    db: Session = Depends(get_db)
):
    """Sincronizar una reserva con Google Calendar"""
    try:
        sincronizacion = GoogleCalendarService.sincronizar_reserva(
            db, sincronizacion_data.reserva_id, sincronizacion_data.calendario_id
        )
        if not sincronizacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo sincronizar la reserva con Google Calendar"
            )
        return sincronizacion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al sincronizar con Google Calendar: {str(e)}"
        )

@router.get("/google-calendar/sincronizaciones", response_model=List[SincronizacionGoogleCalendarResponse])
def obtener_sincronizaciones_google_calendar(db: Session = Depends(get_db)):
    """Obtener todas las sincronizaciones con Google Calendar"""
    from ..models.integracion import SincronizacionGoogleCalendar
    sincronizaciones = db.query(SincronizacionGoogleCalendar).all()
    return sincronizaciones

# ============================================================================
# RUTAS PARA WEBHOOKS
# ============================================================================

@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
def crear_webhook(webhook_data: WebhookCreate, db: Session = Depends(get_db)):
    """Crear un nuevo webhook"""
    try:
        webhook = WebhookService.crear_webhook(db, webhook_data)
        return webhook
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear webhook: {str(e)}"
        )

@router.get("/webhooks", response_model=List[WebhookResponse])
def obtener_webhooks(db: Session = Depends(get_db)):
    """Obtener todos los webhooks"""
    from ..models.integracion import Webhook
    webhooks = db.query(Webhook).all()
    return webhooks

@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
def obtener_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """Obtener un webhook por ID"""
    from ..models.integracion import Webhook
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook no encontrado"
        )
    return webhook

@router.put("/webhooks/{webhook_id}", response_model=WebhookResponse)
def actualizar_webhook(webhook_id: int, webhook_data: WebhookUpdate, db: Session = Depends(get_db)):
    """Actualizar un webhook existente"""
    from ..models.integracion import Webhook
    webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook no encontrado"
        )
    
    for field, value in webhook_data.dict(exclude_unset=True).items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    return webhook

@router.post("/webhooks/{webhook_id}/disparar")
def disparar_webhook(webhook_id: int, evento: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Disparar un webhook específico"""
    log = WebhookService.disparar_webhook(db, webhook_id, evento, payload)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook no encontrado o inactivo"
        )
    
    if log.exitoso:
        return {"mensaje": "Webhook disparado exitosamente", "log_id": log.id}
    else:
        return {"mensaje": "Error al disparar webhook", "error": log.error_mensaje}

@router.post("/webhooks/disparar/{evento}")
def disparar_webhooks_por_evento(evento: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Disparar todos los webhooks configurados para un evento específico"""
    logs = WebhookService.disparar_webhooks_por_evento(db, evento, payload)
    return {"mensaje": f"Disparados {len(logs)} webhooks para el evento '{evento}'", "logs": logs}

# ============================================================================
# RUTAS PARA ESTADÍSTICAS Y RESUMENES
# ============================================================================

@router.get("/estado/general", response_model=EstadoIntegracionesResponse)
def obtener_estado_integraciones(db: Session = Depends(get_db)):
    """Obtener estado general de todas las integraciones"""
    estado = ResumenIntegracionesService.obtener_estado_integraciones(db)
    return estado

@router.get("/notificaciones/resumen", response_model=ResumenNotificacionesResponse)
def obtener_resumen_notificaciones(db: Session = Depends(get_db)):
    """Obtener resumen de notificaciones"""
    resumen = ResumenIntegracionesService.obtener_resumen_notificaciones(db)
    return resumen

# ============================================================================
# RUTAS PARA WEBHOOKS EXTERNOS
# ============================================================================

@router.post("/webhook/externo")
async def webhook_externo(request: Request, db: Session = Depends(get_db)):
    """Endpoint para recibir webhooks externos"""
    try:
        # Obtener el cuerpo del webhook
        body = await request.json()
        headers = dict(request.headers)
        
        # Log del webhook recibido
        print(f"🔔 Webhook externo recibido:")
        print(f"   Headers: {headers}")
        print(f"   Body: {body}")
        
        # Aquí podrías procesar el webhook según el tipo
        # Por ejemplo, verificar la autenticidad, procesar el evento, etc.
        
        return {"mensaje": "Webhook externo recibido exitosamente", "status": "success"}
        
    except Exception as e:
        print(f"❌ Error procesando webhook externo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error procesando webhook: {str(e)}"
        )

# ============================================================================
# RUTAS PARA PRUEBAS Y DIAGNÓSTICO
# ============================================================================

@router.get("/health")
def health_check():
    """Verificar el estado de las integraciones"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Servicio de integraciones funcionando correctamente"
    }

@router.get("/tipos-disponibles")
def obtener_tipos_integracion_disponibles():
    """Obtener lista de tipos de integración disponibles"""
    from ..models.integracion import TipoIntegracion
    return {
        "tipos_disponibles": [tipo.value for tipo in TipoIntegracion],
        "descripcion": "Tipos de integración soportados por el sistema"
    }
