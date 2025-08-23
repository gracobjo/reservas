from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EstadoPagoEnum(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    FALLIDO = "fallido"
    CANCELADO = "cancelado"
    REEMBOLSADO = "reembolsado"

class MetodoPagoEnum(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"

# Esquemas para Pagos
class PagoBase(BaseModel):
    reserva_id: int = Field(..., description="ID de la reserva")
    cliente_id: int = Field(..., description="ID del cliente")
    monto: float = Field(..., gt=0, description="Monto del pago")
    moneda: str = Field("EUR", max_length=3, description="Moneda del pago")
    metodo_pago: MetodoPagoEnum = Field(..., description="Método de pago")
    descripcion: Optional[str] = Field(None, description="Descripción del pago")

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    estado: Optional[EstadoPagoEnum] = None
    transaccion_externa_id: Optional[str] = Field(None, max_length=255)
    referencia_pago: Optional[str] = Field(None, max_length=255)
    factura_generada: Optional[bool] = None
    numero_factura: Optional[str] = Field(None, max_length=50)
    fecha_pago: Optional[datetime] = None
    metadatos_pago: Optional[str] = None

class PagoResponse(PagoBase):
    id: int
    estado: EstadoPagoEnum
    transaccion_externa_id: Optional[str]
    referencia_pago: Optional[str]
    factura_generada: bool
    numero_factura: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    fecha_pago: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Facturas
class FacturaBase(BaseModel):
    pago_id: int = Field(..., description="ID del pago")
    cliente_id: int = Field(..., description="ID del cliente")
    subtotal: float = Field(..., gt=0, description="Subtotal sin IVA")
    iva: float = Field(21.0, ge=0, le=100, description="Porcentaje de IVA")
    nombre_cliente: str = Field(..., max_length=255, description="Nombre del cliente")
    email_cliente: str = Field(..., description="Email del cliente")
    nif_cliente: Optional[str] = Field(None, max_length=20, description="NIF del cliente")
    direccion_cliente: Optional[str] = Field(None, description="Dirección del cliente")

class FacturaCreate(FacturaBase):
    pass

class FacturaUpdate(BaseModel):
    pagada: Optional[bool] = None
    cancelada: Optional[bool] = None
    pdf_generado: Optional[bool] = None
    ruta_pdf: Optional[str] = Field(None, max_length=500)

class FacturaResponse(FacturaBase):
    id: int
    numero_factura: str
    total: float
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime]
    pagada: bool
    cancelada: bool
    pdf_generado: bool
    ruta_pdf: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Reembolsos
class ReembolsoBase(BaseModel):
    pago_id: int = Field(..., description="ID del pago a reembolsar")
    monto_reembolso: float = Field(..., gt=0, description="Monto a reembolsar")
    motivo: str = Field(..., description="Motivo del reembolso")

class ReembolsoCreate(ReembolsoBase):
    pass

class ReembolsoUpdate(BaseModel):
    estado: Optional[EstadoPagoEnum] = None
    transaccion_reembolso_id: Optional[str] = Field(None, max_length=255)
    aprobado_por: Optional[int] = None
    fecha_aprobacion: Optional[datetime] = None
    fecha_procesamiento: Optional[datetime] = None

class ReembolsoResponse(ReembolsoBase):
    id: int
    estado: EstadoPagoEnum
    transaccion_reembolso_id: Optional[str]
    aprobado_por: Optional[int]
    fecha_aprobacion: Optional[datetime]
    fecha_solicitud: datetime
    fecha_procesamiento: Optional[datetime]
    
    class Config:
        from_attributes = True

# Esquemas para Respuestas de API
class PagoCompletoResponse(PagoResponse):
    factura: Optional[FacturaResponse] = None
    reembolsos: List[ReembolsoResponse] = []

class ResumenPagosResponse(BaseModel):
    total_pagos: int
    total_facturado: float
    pagos_pendientes: int
    pagos_completados: int
    pagos_fallidos: int
    ultimos_pagos: List[PagoResponse]
