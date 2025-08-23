from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..models.integracion import (
    Integracion, Notificacion, SincronizacionGoogleCalendar, 
    Webhook, WebhookLog, TipoIntegracion, EstadoIntegracion, 
    TipoNotificacion
)
from ..schemas.integracion import (
    IntegracionCreate, IntegracionUpdate, NotificacionCreate,
    SincronizacionGoogleCalendarCreate, WebhookCreate
)

class IntegracionService:
    """Servicio para gestión de integraciones externas"""
    
    @staticmethod
    def crear_integracion(db: Session, integracion_data: IntegracionCreate) -> Integracion:
        """Crear una nueva integración"""
        db_integracion = Integracion(**integracion_data.dict())
        db.add(db_integracion)
        db.commit()
        db.refresh(db_integracion)
        return db_integracion
    
    @staticmethod
    def obtener_integracion(db: Session, integracion_id: int) -> Optional[Integracion]:
        """Obtener una integración por ID"""
        return db.query(Integracion).filter(Integracion.id == integracion_id).first()
    
    @staticmethod
    def obtener_integraciones_por_tipo(db: Session, tipo: TipoIntegracion) -> List[Integracion]:
        """Obtener integraciones por tipo"""
        return db.query(Integracion).filter(Integracion.tipo == tipo).all()
    
    @staticmethod
    def actualizar_integracion(db: Session, integracion_id: int, integracion_data: IntegracionUpdate) -> Optional[Integracion]:
        """Actualizar una integración existente"""
        db_integracion = db.query(Integracion).filter(Integracion.id == integracion_id).first()
        if not db_integracion:
            return None
        
        for field, value in integracion_data.dict(exclude_unset=True).items():
            setattr(db_integracion, field, value)
        
        db.commit()
        db.refresh(db_integracion)
        return db_integracion
    
    @staticmethod
    def probar_integracion(db: Session, integracion_id: int, destinatario: str, mensaje: str) -> Dict[str, Any]:
        """Probar una integración enviando un mensaje de prueba"""
        db_integracion = db.query(Integracion).filter(Integracion.id == integracion_id).first()
        if not db_integracion:
            return {"exitoso": False, "mensaje": "Integración no encontrada"}
        
        try:
            if db_integracion.tipo == TipoIntegracion.EMAIL:
                resultado = IntegracionService._enviar_email_prueba(db_integracion, destinatario, mensaje)
            elif db_integracion.tipo == TipoIntegracion.SMS:
                resultado = IntegracionService._enviar_sms_prueba(db_integracion, destinatario, mensaje)
            elif db_integracion.tipo == TipoIntegracion.WHATSAPP:
                resultado = IntegracionService._enviar_whatsapp_prueba(db_integracion, destinatario, mensaje)
            else:
                resultado = {"exitoso": False, "mensaje": f"Tipo de integración {db_integracion.tipo} no soportado para pruebas"}
            
            # Actualizar estado de la integración
            if resultado["exitoso"]:
                db_integracion.estado = EstadoIntegracion.ACTIVA
                db_integracion.ultima_sincronizacion = datetime.now()
            else:
                db_integracion.estado = EstadoIntegracion.ERROR
            
            db.commit()
            return resultado
            
        except Exception as e:
            db_integracion.estado = EstadoIntegracion.ERROR
            db.commit()
            return {"exitoso": False, "mensaje": f"Error al probar integración: {str(e)}"}
    
    @staticmethod
    def _enviar_email_prueba(integracion: Integracion, destinatario: str, mensaje: str) -> Dict[str, Any]:
        """Enviar email de prueba usando la configuración de la integración"""
        try:
            # En un entorno real, aquí se usaría la configuración de la integración
            # Por ahora, simulamos el envío
            print(f"📧 Enviando email de prueba a {destinatario}: {mensaje}")
            
            # Simular envío exitoso
            return {
                "exitoso": True,
                "mensaje": "Email de prueba enviado correctamente",
                "detalles": {
                    "destinatario": destinatario,
                    "timestamp": datetime.now().isoformat(),
                    "servicio": "SMTP Simulado"
                }
            }
        except Exception as e:
            return {
                "exitoso": False,
                "mensaje": f"Error al enviar email: {str(e)}",
                "detalles": {"error": str(e)}
            }
    
    @staticmethod
    def _enviar_sms_prueba(integracion: Integracion, destinatario: str, mensaje: str) -> Dict[str, Any]:
        """Enviar SMS de prueba"""
        try:
            # Simular envío de SMS
            print(f"📱 Enviando SMS de prueba a {destinatario}: {mensaje}")
            
            return {
                "exitoso": True,
                "mensaje": "SMS de prueba enviado correctamente",
                "detalles": {
                    "destinatario": destinatario,
                    "timestamp": datetime.now().isoformat(),
                    "servicio": "SMS Simulado"
                }
            }
        except Exception as e:
            return {
                "exitoso": False,
                "mensaje": f"Error al enviar SMS: {str(e)}",
                "detalles": {"error": str(e)}
            }
    
    @staticmethod
    def _enviar_whatsapp_prueba(integracion: Integracion, destinatario: str, mensaje: str) -> Dict[str, Any]:
        """Enviar mensaje de WhatsApp de prueba"""
        try:
            # Simular envío de WhatsApp
            print(f"💬 Enviando WhatsApp de prueba a {destinatario}: {mensaje}")
            
            return {
                "exitoso": True,
                "mensaje": "WhatsApp de prueba enviado correctamente",
                "detalles": {
                    "destinatario": destinatario,
                    "timestamp": datetime.now().isoformat(),
                    "servicio": "WhatsApp Business API Simulado"
                }
            }
        except Exception as e:
            return {
                "exitoso": False,
                "mensaje": f"Error al enviar WhatsApp: {str(e)}",
                "detalles": {"error": str(e)}
            }

class NotificacionService:
    """Servicio para gestión de notificaciones"""
    
    @staticmethod
    def crear_notificacion(db: Session, notificacion_data: NotificacionCreate) -> Notificacion:
        """Crear una nueva notificación"""
        db_notificacion = Notificacion(**notificacion_data.dict())
        db.add(db_notificacion)
        db.commit()
        db.refresh(db_notificacion)
        return db_notificacion
    
    @staticmethod
    def enviar_notificacion(db: Session, notificacion_id: int) -> Optional[Notificacion]:
        """Enviar una notificación"""
        db_notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        if not db_notificacion:
            return None
        
        try:
            # Obtener la integración
            integracion = db.query(Integracion).filter(Integracion.id == db_notificacion.integracion_id).first()
            if not integracion or integracion.estado != EstadoIntegracion.ACTIVA:
                raise Exception("Integración no disponible")
            
            # Enviar según el tipo de integración
            if integracion.tipo == TipoIntegracion.EMAIL:
                resultado = NotificacionService._enviar_email(integracion, db_notificacion)
            elif integracion.tipo == TipoIntegracion.SMS:
                resultado = NotificacionService._enviar_sms(integracion, db_notificacion)
            elif integracion.tipo == TipoIntegracion.WHATSAPP:
                resultado = NotificacionService._enviar_whatsapp(integracion, db_notificacion)
            else:
                raise Exception(f"Tipo de integración {integracion.tipo} no soportado")
            
            # Actualizar estado de la notificación
            if resultado["exitoso"]:
                db_notificacion.enviada = True
                db_notificacion.fecha_envio = datetime.now()
                db_notificacion.respuesta_servicio = resultado.get("respuesta", "")
                db_notificacion.codigo_respuesta = "200"
            else:
                db_notificacion.error_mensaje = resultado.get("error", "Error desconocido")
                db_notificacion.intentos += 1
            
            db.commit()
            return db_notificacion
            
        except Exception as e:
            db_notificacion.error_mensaje = str(e)
            db_notificacion.intentos += 1
            db.commit()
            return db_notificacion
    
    @staticmethod
    def _enviar_email(integracion: Integracion, notificacion: Notificacion) -> Dict[str, Any]:
        """Enviar email usando la integración"""
        try:
            # Simular envío de email
            print(f"📧 Enviando email a {notificacion.destinatario}: {notificacion.asunto}")
            
            return {
                "exitoso": True,
                "respuesta": "Email enviado correctamente"
            }
        except Exception as e:
            return {
                "exitoso": False,
                "error": str(e)
            }
    
    @staticmethod
    def _enviar_sms(integracion: Integracion, notificacion: Notificacion) -> Dict[str, Any]:
        """Enviar SMS usando la integración"""
        try:
            # Simular envío de SMS
            print(f"📱 Enviando SMS a {notificacion.destinatario}: {notificacion.contenido}")
            
            return {
                "exitoso": True,
                "respuesta": "SMS enviado correctamente"
            }
        except Exception as e:
            return {
                "exitoso": False,
                "error": str(e)
            }
    
    @staticmethod
    def _enviar_whatsapp(integracion: Integracion, notificacion: Notificacion) -> Dict[str, Any]:
        """Enviar mensaje de WhatsApp usando la integración"""
        try:
            # Simular envío de WhatsApp
            print(f"💬 Enviando WhatsApp a {notificacion.destinatario}: {notificacion.contenido}")
            
            return {
                "exitoso": True,
                "respuesta": "WhatsApp enviado correctamente"
            }
        except Exception as e:
            return {
                "exitoso": False,
                "error": str(e)
            }
    
    @staticmethod
    def procesar_notificaciones_pendientes(db: Session) -> int:
        """Procesar todas las notificaciones pendientes"""
        notificaciones_pendientes = db.query(Notificacion).filter(
            and_(
                Notificacion.enviada == False,
                Notificacion.intentos < Notificacion.max_intentos
            )
        ).all()
        
        enviadas = 0
        for notificacion in notificaciones_pendientes:
            try:
                NotificacionService.enviar_notificacion(db, notificacion.id)
                if notificacion.enviada:
                    enviadas += 1
            except Exception as e:
                print(f"Error procesando notificación {notificacion.id}: {e}")
        
        return enviadas

class GoogleCalendarService:
    """Servicio para integración con Google Calendar"""
    
    @staticmethod
    def sincronizar_reserva(db: Session, reserva_id: int, calendario_id: str = None) -> Optional[SincronizacionGoogleCalendar]:
        """Sincronizar una reserva con Google Calendar"""
        try:
            # Verificar si ya existe sincronización
            sincronizacion_existente = db.query(SincronizacionGoogleCalendar).filter(
                SincronizacionGoogleCalendar.reserva_id == reserva_id
            ).first()
            
            if sincronizacion_existente:
                return sincronizacion_existente
            
            # Crear nueva sincronización
            db_sincronizacion = SincronizacionGoogleCalendar(
                reserva_id=reserva_id,
                calendario_id=calendario_id or "primary"
            )
            
            # En un entorno real, aquí se haría la llamada a Google Calendar API
            # Por ahora, simulamos la sincronización
            db_sincronizacion.sincronizada = True
            db_sincronizacion.fecha_sincronizacion = datetime.now()
            db_sincronizacion.evento_google_id = f"event_{reserva_id}_{int(datetime.now().timestamp())}"
            db_sincronizacion.link_evento = f"https://calendar.google.com/event?eid={db_sincronizacion.evento_google_id}"
            
            db.add(db_sincronizacion)
            db.commit()
            db.refresh(db_sincronizacion)
            
            return db_sincronizacion
            
        except Exception as e:
            print(f"Error sincronizando reserva {reserva_id} con Google Calendar: {e}")
            return None

class WebhookService:
    """Servicio para gestión de webhooks"""
    
    @staticmethod
    def crear_webhook(db: Session, webhook_data: WebhookCreate) -> Webhook:
        """Crear un nuevo webhook"""
        db_webhook = Webhook(**webhook_data.dict())
        db.add(db_webhook)
        db.commit()
        db.refresh(db_webhook)
        return db_webhook
    
    @staticmethod
    def disparar_webhook(db: Session, webhook_id: int, evento: str, payload: Dict[str, Any]) -> Optional[WebhookLog]:
        """Disparar un webhook"""
        db_webhook = db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not db_webhook or not db_webhook.activo:
            return None
        
        # Crear log del webhook
        db_log = WebhookLog(
            webhook_id=webhook_id,
            evento_disparado=evento,
            payload_enviado=payload
        )
        db.add(db_log)
        
        try:
            # Enviar webhook
            inicio = datetime.now()
            response = requests.post(
                db_webhook.url,
                json=payload,
                headers=db_webhook.headers or {},
                timeout=30,
                verify=db_webhook.verificar_ssl
            )
            fin = datetime.now()
            
            # Actualizar log
            db_log.codigo_respuesta = response.status_code
            db_log.respuesta_recibida = response.text
            db_log.tiempo_respuesta = (fin - inicio).total_seconds()
            db_log.exitoso = 200 <= response.status_code < 300
            
            # Actualizar webhook
            db_webhook.ultimo_disparo = datetime.now()
            
        except Exception as e:
            db_log.error_mensaje = str(e)
            db_log.exitoso = False
        
        db.commit()
        db.refresh(db_log)
        return db_log
    
    @staticmethod
    def disparar_webhooks_por_evento(db: Session, evento: str, payload: Dict[str, Any]) -> List[WebhookLog]:
        """Disparar todos los webhooks configurados para un evento específico"""
        webhooks = db.query(Webhook).filter(
            and_(
                Webhook.evento == evento,
                Webhook.activo == True
            )
        ).all()
        
        logs = []
        for webhook in webhooks:
            log = WebhookService.disparar_webhook(db, webhook.id, evento, payload)
            if log:
                logs.append(log)
        
        return logs

class ResumenIntegracionesService:
    """Servicio para resúmenes de integraciones"""
    
    @staticmethod
    def obtener_estado_integraciones(db: Session) -> Dict[str, Any]:
        """Obtener estado general de todas las integraciones"""
        total_integraciones = db.query(func.count(Integracion.id)).scalar()
        integraciones_activas = db.query(func.count(Integracion.id)).filter(
            Integracion.estado == EstadoIntegracion.ACTIVA
        ).scalar()
        integraciones_error = db.query(func.count(Integracion.id)).filter(
            Integracion.estado == EstadoIntegracion.ERROR
        ).scalar()
        
        # Última sincronización
        ultima_sincronizacion = db.query(func.max(Integracion.ultima_sincronizacion)).scalar()
        
        # Lista de integraciones
        integraciones = db.query(Integracion).all()
        
        return {
            "total_integraciones": total_integraciones,
            "integraciones_activas": integraciones_activas,
            "integraciones_error": integraciones_error,
            "ultima_sincronizacion": ultima_sincronizacion,
            "integraciones": integraciones
        }
    
    @staticmethod
    def obtener_resumen_notificaciones(db: Session) -> Dict[str, Any]:
        """Obtener resumen de notificaciones"""
        total_notificaciones = db.query(func.count(Notificacion.id)).scalar()
        notificaciones_enviadas = db.query(func.count(Notificacion.id)).filter(
            Notificacion.enviada == True
        ).scalar()
        notificaciones_pendientes = db.query(func.count(Notificacion.id)).filter(
            Notificacion.enviada == False
        ).scalar()
        notificaciones_fallidas = db.query(func.count(Notificacion.id)).filter(
            Notificacion.error_mensaje.isnot(None)
        ).scalar()
        
        # Últimas 10 notificaciones
        ultimas_notificaciones = db.query(Notificacion).order_by(
            Notificacion.created_at.desc()
        ).limit(10).all()
        
        return {
            "total_notificaciones": total_notificaciones,
            "notificaciones_enviadas": notificaciones_enviadas,
            "notificaciones_pendientes": notificaciones_pendientes,
            "notificaciones_fallidas": notificaciones_fallidas,
            "ultimas_notificaciones": ultimas_notificaciones
        }
