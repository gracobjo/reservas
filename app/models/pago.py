from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base
import enum

class EstadoPago(enum.Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"
    REEMBOLSADO = "reembolsado"

class MetodoPago(enum.Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"

class Pago(Base):
    __tablename__ = "pagos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Información del pago
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), default="EUR")
    estado = Column(Enum(EstadoPago), default=EstadoPago.PENDIENTE)
    metodo_pago = Column(Enum(MetodoPago), nullable=False)
    
    # Información de la transacción externa
    transaccion_externa_id = Column(String(255), nullable=True)  # ID de Stripe/PayPal
    referencia_pago = Column(String(255), nullable=True)  # Referencia interna
    
    # Información de facturación
    factura_generada = Column(Boolean, default=False)
    numero_factura = Column(String(50), nullable=True)
    
    # Metadatos
    descripcion = Column(Text, nullable=True)
    metadatos_pago = Column(Text, nullable=True)  # JSON string para datos adicionales
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    fecha_pago = Column(DateTime, nullable=True)
    
    # Relaciones SQLAlchemy
    reserva = relationship("Reserva", back_populates="pagos")
    cliente = relationship("Cliente", back_populates="pagos")
    facturas = relationship("Factura", back_populates="pago")
    reembolsos = relationship("Reembolso", back_populates="pago")

class Factura(Base):
    __tablename__ = "facturas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Información de la factura
    numero_factura = Column(String(50), unique=True, nullable=False)
    fecha_emision = Column(DateTime, default=func.now())
    fecha_vencimiento = Column(DateTime, nullable=True)
    
    # Detalles fiscales
    subtotal = Column(Float, nullable=False)
    iva = Column(Float, default=21.0)  # 21% IVA por defecto
    total = Column(Float, nullable=False)
    
    # Estado
    pagada = Column(Boolean, default=False)
    cancelada = Column(Boolean, default=False)
    
    # Información del cliente
    nombre_cliente = Column(String(255), nullable=False)
    nif_cliente = Column(String(20), nullable=True)
    direccion_cliente = Column(Text, nullable=True)
    email_cliente = Column(String(255), nullable=False)
    
    # Archivos
    pdf_generado = Column(Boolean, default=False)
    ruta_pdf = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relaciones SQLAlchemy
    pago = relationship("Pago", back_populates="facturas")
    cliente = relationship("Cliente", back_populates="facturas")

class Reembolso(Base):
    __tablename__ = "reembolsos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    pago_id = Column(Integer, ForeignKey("pagos.id"), nullable=False)
    
    # Información del reembolso
    monto_reembolso = Column(Float, nullable=False)
    motivo = Column(Text, nullable=False)
    estado = Column(Enum(EstadoPago), default=EstadoPago.PENDIENTE)
    
    # Información de la transacción externa
    transaccion_reembolso_id = Column(String(255), nullable=True)
    
    # Aprobación
    aprobado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    
    # Timestamps
    fecha_solicitud = Column(DateTime, default=func.now())
    fecha_procesamiento = Column(DateTime, nullable=True)
    
    # Relaciones SQLAlchemy
    pago = relationship("Pago", back_populates="reembolsos")
    usuario_aprobador = relationship("Usuario", back_populates="reembolsos_aprobados")
