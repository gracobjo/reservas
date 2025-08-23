from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base
import enum

class TipoIntegracion(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    GOOGLE_CALENDAR = "google_calendar"
    STRIPE = "stripe"
    PAYPAL = "paypal"

class EstadoIntegracion(enum.Enum):
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    ERROR = "error"
    CONFIGURANDO = "configurando"

class TipoNotificacion(enum.Enum):
    CONFIRMACION_RESERVA = "confirmacion_reserva"
    RECORDATORIO = "recordatorio"
    CANCELACION = "cancelacion"
    PAGO_EXITOSO = "pago_exitoso"
    PAGO_FALLIDO = "pago_fallido"
    FACTURA_GENERADA = "factura_generada"

class Integracion(Base):
    __tablename__ = "integraciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuración básica
    nombre = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoIntegracion), nullable=False)
    estado = Column(Enum(EstadoIntegracion), default=EstadoIntegracion.CONFIGURANDO)
    
    # Configuración específica (JSON)
    configuracion = Column(JSON, nullable=True)
    
    # Credenciales y tokens
    api_key = Column(String(500), nullable=True)
    api_secret = Column(String(500), nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    
    # Metadatos
    descripcion = Column(Text, nullable=True)
    webhook_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    ultima_sincronizacion = Column(DateTime, nullable=True)
    
    # Relaciones
    notificaciones = relationship("Notificacion", back_populates="integracion")

class Notificacion(Base):
    __tablename__ = "notificaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    integracion_id = Column(Integer, ForeignKey("integraciones.id"), nullable=False)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    
    # Información de la notificación
    tipo = Column(Enum(TipoNotificacion), nullable=False)
    destinatario = Column(String(255), nullable=False)  # Email, teléfono, etc.
    asunto = Column(String(255), nullable=True)
    contenido = Column(Text, nullable=False)
    
    # Estado y tracking
    enviada = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, nullable=True)
    fecha_lectura = Column(DateTime, nullable=True)
    
    # Respuesta del servicio externo
    respuesta_servicio = Column(Text, nullable=True)
    codigo_respuesta = Column(String(50), nullable=True)
    error_mensaje = Column(Text, nullable=True)
    
    # Reintentos
    intentos = Column(Integer, default=0)
    max_intentos = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    integracion = relationship("Integracion", back_populates="notificaciones")
    reserva = relationship("Reserva", back_populates="notificaciones")
    cliente = relationship("Cliente", back_populates="notificaciones")

class SincronizacionGoogleCalendar(Base):
    __tablename__ = "sincronizaciones_google_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    
    # Información de Google Calendar
    evento_google_id = Column(String(255), nullable=True)
    calendario_id = Column(String(255), nullable=True)
    
    # Estado de sincronización
    sincronizada = Column(Boolean, default=False)
    fecha_sincronizacion = Column(DateTime, nullable=True)
    
    # Metadatos
    link_evento = Column(String(500), nullable=True)
    error_sincronizacion = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    reserva = relationship("Reserva", back_populates="sincronizaciones_google")

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuración del webhook
    nombre = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    evento = Column(String(100), nullable=False)  # Tipo de evento que dispara el webhook
    
    # Configuración
    activo = Column(Boolean, default=True)
    metodo_http = Column(String(10), default="POST")
    headers = Column(JSON, nullable=True)
    
    # Seguridad
    secret_key = Column(String(255), nullable=True)
    verificar_ssl = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    ultimo_disparo = Column(DateTime, nullable=True)
    
    # Relaciones
    logs = relationship("WebhookLog", back_populates="webhook")

class WebhookLog(Base):
    __tablename__ = "webhooks_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    
    # Información de la ejecución
    evento_disparado = Column(String(100), nullable=False)
    payload_enviado = Column(JSON, nullable=True)
    
    # Respuesta del webhook
    codigo_respuesta = Column(Integer, nullable=True)
    respuesta_recibida = Column(Text, nullable=True)
    tiempo_respuesta = Column(Float, nullable=True)  # En segundos
    
    # Estado
    exitoso = Column(Boolean, default=False)
    error_mensaje = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relaciones
    webhook = relationship("Webhook", back_populates="logs")
