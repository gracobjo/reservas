from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TipoIntegracionEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    GOOGLE_CALENDAR = "google_calendar"
    STRIPE = "stripe"
    PAYPAL = "paypal"

class EstadoIntegracionEnum(str, Enum):
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    ERROR = "error"
    CONFIGURANDO = "configurando"

class TipoNotificacionEnum(str, Enum):
    CONFIRMACION_RESERVA = "confirmacion_reserva"
    RECORDATORIO = "recordatorio"
    CANCELACION = "cancelacion"
    PAGO_EXITOSO = "pago_exitoso"
    PAGO_FALLIDO = "pago_fallido"
    FACTURA_GENERADA = "factura_generada"

# Esquemas para Integraciones
class IntegracionBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre de la integración")
    tipo: TipoIntegracionEnum = Field(..., description="Tipo de integración")
    descripcion: Optional[str] = Field(None, description="Descripción de la integración")
    webhook_url: Optional[str] = Field(None, max_length=500, description="URL del webhook")

class IntegracionCreate(IntegracionBase):
    configuracion: Optional[Dict[str, Any]] = Field(None, description="Configuración específica")
    api_key: Optional[str] = Field(None, max_length=500, description="API Key")
    api_secret: Optional[str] = Field(None, max_length=500, description="API Secret")

class IntegracionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    estado: Optional[EstadoIntegracionEnum] = None
    configuracion: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = Field(None, max_length=500)
    api_key: Optional[str] = Field(None, max_length=500)
    api_secret: Optional[str] = Field(None, max_length=500)

class IntegracionResponse(IntegracionBase):
    id: int
    estado: EstadoIntegracionEnum
    configuracion: Optional[Dict[str, Any]]
    ultima_sincronizacion: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Notificaciones
class NotificacionBase(BaseModel):
    integracion_id: int = Field(..., description="ID de la integración")
    reserva_id: Optional[int] = Field(None, description="ID de la reserva")
    cliente_id: Optional[int] = Field(None, description="ID del cliente")
    tipo: TipoNotificacionEnum = Field(..., description="Tipo de notificación")
    destinatario: str = Field(..., max_length=255, description="Destinatario")
    asunto: Optional[str] = Field(None, max_length=255, description="Asunto")
    contenido: str = Field(..., description="Contenido de la notificación")

class NotificacionCreate(NotificacionBase):
    pass

class NotificacionUpdate(BaseModel):
    enviada: Optional[bool] = None
    fecha_envio: Optional[datetime] = None
    fecha_lectura: Optional[datetime] = None
    respuesta_servicio: Optional[str] = None
    codigo_respuesta: Optional[str] = Field(None, max_length=50)
    error_mensaje: Optional[str] = None
    intentos: Optional[int] = Field(None, ge=0)

class NotificacionResponse(NotificacionBase):
    id: int
    enviada: bool
    fecha_envio: Optional[datetime]
    fecha_lectura: Optional[datetime]
    respuesta_servicio: Optional[str]
    codigo_respuesta: Optional[str]
    error_mensaje: Optional[str]
    intentos: int
    max_intentos: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Google Calendar
class SincronizacionGoogleCalendarBase(BaseModel):
    reserva_id: int = Field(..., description="ID de la reserva")
    calendario_id: Optional[str] = Field(None, max_length=255, description="ID del calendario de Google")

class SincronizacionGoogleCalendarCreate(SincronizacionGoogleCalendarBase):
    pass

class SincronizacionGoogleCalendarUpdate(BaseModel):
    evento_google_id: Optional[str] = Field(None, max_length=255)
    sincronizada: Optional[bool] = None
    fecha_sincronizacion: Optional[datetime] = None
    link_evento: Optional[str] = Field(None, max_length=500)
    error_sincronizacion: Optional[str] = None

class SincronizacionGoogleCalendarResponse(SincronizacionGoogleCalendarBase):
    id: int
    evento_google_id: Optional[str]
    sincronizada: bool
    fecha_sincronizacion: Optional[datetime]
    link_evento: Optional[str]
    error_sincronizacion: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Webhooks
class WebhookBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre del webhook")
    url: str = Field(..., max_length=500, description="URL del webhook")
    evento: str = Field(..., max_length=100, description="Tipo de evento")
    metodo_http: str = Field("POST", max_length=10, description="Método HTTP")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers personalizados")
    secret_key: Optional[str] = Field(None, max_length=255, description="Clave secreta para verificación")
    verificar_ssl: bool = Field(True, description="Verificar certificado SSL")

class WebhookCreate(WebhookBase):
    pass

class WebhookUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    url: Optional[str] = Field(None, max_length=500)
    evento: Optional[str] = Field(None, max_length=100)
    activo: Optional[bool] = None
    metodo_http: Optional[str] = Field(None, max_length=10)
    headers: Optional[Dict[str, str]] = None
    secret_key: Optional[str] = Field(None, max_length=255)
    verificar_ssl: Optional[bool] = None

class WebhookResponse(WebhookBase):
    id: int
    activo: bool
    ultimo_disparo: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Logs de Webhooks
class WebhookLogBase(BaseModel):
    webhook_id: int = Field(..., description="ID del webhook")
    evento_disparado: str = Field(..., max_length=100, description="Evento que disparó el webhook")
    payload_enviado: Optional[Dict[str, Any]] = Field(None, description="Payload enviado")

class WebhookLogCreate(WebhookLogBase):
    pass

class WebhookLogResponse(WebhookLogBase):
    id: int
    codigo_respuesta: Optional[int]
    respuesta_recibida: Optional[str]
    tiempo_respuesta: Optional[float]
    exitoso: bool
    error_mensaje: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para Respuestas de API
class EstadoIntegracionesResponse(BaseModel):
    total_integraciones: int
    integraciones_activas: int
    integraciones_error: int
    ultima_sincronizacion: Optional[datetime]
    integraciones: List[IntegracionResponse]

class ResumenNotificacionesResponse(BaseModel):
    total_notificaciones: int
    notificaciones_enviadas: int
    notificaciones_pendientes: int
    notificaciones_fallidas: int
    ultimas_notificaciones: List[NotificacionResponse]

class TestIntegracionRequest(BaseModel):
    destinatario: str = Field(..., description="Destinatario de prueba")
    mensaje: str = Field(..., description="Mensaje de prueba")

class TestIntegracionResponse(BaseModel):
    exitoso: bool
    mensaje: str
    detalles: Optional[Dict[str, Any]] = None
