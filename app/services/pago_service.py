from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import uuid

from ..models.pago import Pago, Factura, Reembolso, EstadoPago, MetodoPago
from ..models.reserva import Reserva
from ..models.cliente import Cliente
from ..schemas.pago import PagoCreate, PagoUpdate, FacturaCreate, ReembolsoCreate

class PagoService:
    """Servicio para gestión de pagos"""
    
    @staticmethod
    def crear_pago(db: Session, pago_data: PagoCreate) -> Pago:
        """Crear un nuevo pago"""
        # Generar referencia única
        referencia = f"PAY-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        db_pago = Pago(
            **pago_data.dict(),
            referencia_pago=referencia,
            estado=EstadoPago.PENDIENTE
        )
        
        db.add(db_pago)
        db.commit()
        db.refresh(db_pago)
        return db_pago
    
    @staticmethod
    def obtener_pago(db: Session, pago_id: int) -> Optional[Pago]:
        """Obtener un pago por ID"""
        return db.query(Pago).filter(Pago.id == pago_id).first()
    
    @staticmethod
    def obtener_pagos_por_reserva(db: Session, reserva_id: int) -> List[Pago]:
        """Obtener todos los pagos de una reserva"""
        return db.query(Pago).filter(Pago.reserva_id == reserva_id).all()
    
    @staticmethod
    def obtener_pagos_por_cliente(db: Session, cliente_id: int) -> List[Pago]:
        """Obtener todos los pagos de un cliente"""
        return db.query(Pago).filter(Pago.cliente_id == cliente_id).all()
    
    @staticmethod
    def listar_pagos(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        estado: Optional[str] = None,
        metodo_pago: Optional[str] = None
    ) -> List[Pago]:
        """Listar todos los pagos con filtros opcionales"""
        query = db.query(Pago)
        
        # Aplicar filtros si se especifican
        if estado:
            query = query.filter(Pago.estado == estado)
        if metodo_pago:
            query = query.filter(Pago.metodo_pago == metodo_pago)
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(Pago.fecha_creacion.desc())
        
        # Aplicar paginación
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_pago(db: Session, pago_id: int, pago_data: PagoUpdate) -> Optional[Pago]:
        """Actualizar un pago existente"""
        db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not db_pago:
            return None
        
        # Si el pago se completa, actualizar fecha_pago
        if pago_data.estado == EstadoPago.COMPLETADO and not db_pago.fecha_pago:
            pago_data.fecha_pago = datetime.now()
        
        for field, value in pago_data.dict(exclude_unset=True).items():
            setattr(db_pago, field, value)
        
        db.commit()
        db.refresh(db_pago)
        return db_pago
    
    @staticmethod
    def procesar_pago_stripe(db: Session, pago_id: int, stripe_payment_intent_id: str) -> Optional[Pago]:
        """Procesar pago con Stripe"""
        db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not db_pago:
            return None
        
        # Simular procesamiento de Stripe
        db_pago.estado = EstadoPago.PROCESANDO
        db_pago.transaccion_externa_id = stripe_payment_intent_id
        
        # En un entorno real, aquí se haría la llamada a Stripe
        # stripe.PaymentIntent.retrieve(stripe_payment_intent_id)
        
        # Simular pago exitoso
        db_pago.estado = EstadoPago.COMPLETADO
        db_pago.fecha_pago = datetime.now()
        
        db.commit()
        db.refresh(db_pago)
        return db_pago
    
    @staticmethod
    def procesar_pago_paypal(db: Session, pago_id: int, paypal_order_id: str) -> Optional[Pago]:
        """Procesar pago con PayPal"""
        db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not db_pago:
            return None
        
        # Simular procesamiento de PayPal
        db_pago.estado = EstadoPago.PROCESANDO
        db_pago.transaccion_externa_id = paypal_order_id
        
        # En un entorno real, aquí se haría la llamada a PayPal
        # paypal.orders.get(paypal_order_id)
        
        # Simular pago exitoso
        db_pago.estado = EstadoPago.COMPLETADO
        db_pago.fecha_pago = datetime.now()
        
        db.commit()
        db.refresh(db_pago)
        return db_pago
    
    @staticmethod
    def cancelar_pago(db: Session, pago_id: int, motivo: str) -> Optional[Pago]:
        """Cancelar un pago"""
        db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not db_pago:
            return None
        
        if db_pago.estado not in [EstadoPago.PENDIENTE, EstadoPago.PROCESANDO]:
            raise ValueError("Solo se pueden cancelar pagos pendientes o en procesamiento")
        
        db_pago.estado = EstadoPago.CANCELADO
        db_pago.metadatos_pago = json.dumps({"motivo_cancelacion": motivo, "fecha_cancelacion": datetime.now().isoformat()})
        
        db.commit()
        db.refresh(db_pago)
        return db_pago

class FacturaService:
    """Servicio para gestión de facturas"""
    
    @staticmethod
    def generar_factura(db: Session, pago_id: int) -> Optional[Factura]:
        """Generar factura para un pago"""
        db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
        if not db_pago or db_pago.estado != EstadoPago.COMPLETADO:
            return None
        
        # Verificar si ya existe factura
        if db_pago.factura_generada:
            return db.query(Factura).filter(Factura.pago_id == pago_id).first()
        
        # Generar número de factura
        numero_factura = f"FAC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcular total con IVA
        subtotal = db_pago.monto
        iva_porcentaje = 21.0  # 21% IVA
        iva_monto = subtotal * (iva_porcentaje / 100)
        total = subtotal + iva_monto
        
        # Obtener información del cliente
        cliente = db.query(Cliente).filter(Cliente.id == db_pago.cliente_id).first()
        
        # Crear factura
        db_factura = Factura(
            pago_id=pago_id,
            cliente_id=db_pago.cliente_id,
            numero_factura=numero_factura,
            subtotal=subtotal,
            iva=iva_porcentaje,
            total=total,
            nombre_cliente=cliente.nombre if cliente else "Cliente",
            email_cliente=cliente.email if cliente else "",
            nif_cliente=cliente.nif if cliente else None,
            direccion_cliente=cliente.direccion if cliente else None,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        db.add(db_factura)
        
        # Marcar pago como facturado
        db_pago.factura_generada = True
        db_pago.numero_factura = numero_factura
        
        db.commit()
        db.refresh(db_factura)
        return db_factura
    
    @staticmethod
    def obtener_factura(db: Session, factura_id: int) -> Optional[Factura]:
        """Obtener una factura por ID"""
        return db.query(Factura).filter(Factura.id == factura_id).first()
    
    @staticmethod
    def obtener_facturas_por_cliente(db: Session, cliente_id: int) -> List[Factura]:
        """Obtener todas las facturas de un cliente"""
        return db.query(Factura).filter(Factura.cliente_id == cliente_id).all()
    
    @staticmethod
    def marcar_factura_pagada(db: Session, factura_id: int) -> Optional[Factura]:
        """Marcar una factura como pagada"""
        db_factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not db_factura:
            return None
        
        db_factura.pagada = True
        db.commit()
        db.refresh(db_factura)
        return db_factura

class ReembolsoService:
    """Servicio para gestión de reembolsos"""
    
    @staticmethod
    def solicitar_reembolso(db: Session, reembolso_data: ReembolsoCreate) -> Optional[Reembolso]:
        """Solicitar un reembolso"""
        # Verificar que el pago existe y está completado
        db_pago = db.query(Pago).filter(Pago.id == reembolso_data.pago_id).first()
        if not db_pago or db_pago.estado != EstadoPago.COMPLETADO:
            raise ValueError("Solo se pueden reembolsar pagos completados")
        
        # Verificar que el monto del reembolso no exceda el pago
        if reembolso_data.monto_reembolso > db_pago.monto:
            raise ValueError("El monto del reembolso no puede exceder el monto del pago")
        
        # Crear reembolso
        db_reembolso = Reembolso(**reembolso_data.dict())
        db.add(db_reembolso)
        db.commit()
        db.refresh(db_reembolso)
        return db_reembolso
    
    @staticmethod
    def aprobar_reembolso(db: Session, reembolso_id: int, usuario_id: int) -> Optional[Reembolso]:
        """Aprobar un reembolso"""
        db_reembolso = db.query(Reembolso).filter(Reembolso.id == reembolso_id).first()
        if not db_reembolso:
            return None
        
        if db_reembolso.estado != EstadoPago.PENDIENTE:
            raise ValueError("Solo se pueden aprobar reembolsos pendientes")
        
        db_reembolso.estado = EstadoPago.PROCESANDO
        db_reembolso.aprobado_por = usuario_id
        db_reembolso.fecha_aprobacion = datetime.now()
        
        db.commit()
        db.refresh(db_reembolso)
        return db_reembolso
    
    @staticmethod
    def procesar_reembolso(db: Session, reembolso_id: int, transaccion_id: str) -> Optional[Reembolso]:
        """Procesar un reembolso aprobado"""
        db_reembolso = db.query(Reembolso).filter(Reembolso.id == reembolso_id).first()
        if not db_reembolso:
            return None
        
        if db_reembolso.estado != EstadoPago.PROCESANDO:
            raise ValueError("Solo se pueden procesar reembolsos aprobados")
        
        # Simular procesamiento del reembolso
        db_reembolso.estado = EstadoPago.COMPLETADO
        db_reembolso.transaccion_reembolso_id = transaccion_id
        db_reembolso.fecha_procesamiento = datetime.now()
        
        # Actualizar estado del pago original
        db_pago = db.query(Pago).filter(Pago.id == db_reembolso.pago_id).first()
        if db_pago:
            db_pago.estado = EstadoPago.REEMBOLSADO
        
        db.commit()
        db.refresh(db_reembolso)
        return db_reembolso

class ResumenPagosService:
    """Servicio para resúmenes y estadísticas de pagos"""
    
    @staticmethod
    def obtener_resumen_pagos(db: Session) -> Dict[str, Any]:
        """Obtener resumen general de pagos"""
        total_pagos = db.query(func.count(Pago.id)).scalar()
        total_facturado = db.query(func.sum(Pago.monto)).filter(Pago.estado == EstadoPago.COMPLETADO).scalar() or 0
        
        pagos_pendientes = db.query(func.count(Pago.id)).filter(Pago.estado == EstadoPago.PENDIENTE).scalar()
        pagos_completados = db.query(func.count(Pago.id)).filter(Pago.estado == EstadoPago.COMPLETADO).scalar()
        pagos_fallidos = db.query(func.count(Pago.id)).filter(Pago.estado == EstadoPago.FALLIDO).scalar()
        
        # Últimos 5 pagos
        ultimos_pagos = db.query(Pago).order_by(Pago.fecha_creacion.desc()).limit(5).all()
        
        return {
            "total_pagos": total_pagos,
            "total_facturado": float(total_facturado),
            "pagos_pendientes": pagos_pendientes,
            "pagos_completados": pagos_completados,
            "pagos_fallidos": pagos_fallidos,
            "ultimos_pagos": ultimos_pagos
        }
    
    @staticmethod
    def obtener_estadisticas_mensuales(db: Session, año: int, mes: int) -> Dict[str, Any]:
        """Obtener estadísticas de pagos por mes"""
        inicio_mes = datetime(año, mes, 1)
        if mes == 12:
            fin_mes = datetime(año + 1, 1, 1)
        else:
            fin_mes = datetime(año, mes + 1, 1)
        
        pagos_mes = db.query(Pago).filter(
            and_(
                Pago.fecha_creacion >= inicio_mes,
                Pago.fecha_creacion < fin_mes
            )
        ).all()
        
        total_mes = sum(pago.monto for pago in pagos_mes if pago.estado == EstadoPago.COMPLETADO)
        pagos_exitosos = len([p for p in pagos_mes if p.estado == EstadoPago.COMPLETADO])
        pagos_fallidos = len([p for p in pagos_mes if p.estado == EstadoPago.FALLIDO])
        
        return {
            "año": año,
            "mes": mes,
            "total_pagos": len(pagos_mes),
            "total_facturado": total_mes,
            "pagos_exitosos": pagos_exitosos,
            "pagos_fallidos": pagos_fallidos,
            "tasa_exito": (pagos_exitosos / len(pagos_mes) * 100) if pagos_mes else 0
        }
