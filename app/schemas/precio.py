from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TipoPrecioEnum(str, Enum):
    """Tipos de precios disponibles"""
    BASE = "base"
    HORA = "hora"
    DIA = "dia"
    SEMANA = "semana"
    MES = "mes"
    TEMPORADA = "temporada"
    GRUPO = "grupo"
    DESCUENTO = "descuento"
    RECARGO = "recargo"

class MonedaEnum(str, Enum):
    """Monedas soportadas"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class PrecioBase(BaseModel):
    """Esquema base para precios"""
    servicio_id: Optional[int] = Field(None, description="ID del servicio (opcional si es recurso)")
    recurso_id: Optional[int] = Field(None, description="ID del recurso (opcional si es servicio)")
    tipo_precio: TipoPrecioEnum = Field(..., description="Tipo de precio")
    nombre: str = Field(..., max_length=100, description="Nombre del precio")
    descripcion: Optional[str] = Field(None, description="Descripción del precio")
    precio_base: float = Field(..., gt=0, description="Precio base")
    precio_final: Optional[float] = Field(None, gt=0, description="Precio final calculado")
    moneda: MonedaEnum = Field(MonedaEnum.EUR, description="Moneda del precio")
    activo: bool = Field(True, description="Si el precio está activo")
    prioridad: int = Field(0, ge=0, description="Prioridad del precio")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio de validez")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin de validez")
    cantidad_minima: Optional[int] = Field(None, ge=1, description="Cantidad mínima para aplicar")
    cantidad_maxima: Optional[int] = Field(None, ge=1, description="Cantidad máxima para aplicar")
    dias_semana: Optional[str] = Field(None, max_length=50, description="Días de la semana (1,2,3,4,5,6,7)")
    hora_inicio: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Hora de inicio (HH:MM)")
    hora_fin: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Hora de fin (HH:MM)")
    metadatos: Optional[str] = Field(None, description="Metadatos adicionales en formato JSON")

    @validator('servicio_id', 'recurso_id')
    def validate_service_or_resource(cls, v, values):
        """Valida que se especifique al menos uno: servicio_id o recurso_id"""
        if 'servicio_id' in values and 'recurso_id' in values:
            if values['servicio_id'] is not None and values['recurso_id'] is not None:
                raise ValueError("No se puede especificar servicio_id y recurso_id al mismo tiempo")
        return v

    @validator('fecha_fin')
    def validate_fecha_fin(cls, v, values):
        """Valida que fecha_fin sea posterior a fecha_inicio"""
        if v and 'fecha_inicio' in values and values['fecha_inicio']:
            if v <= values['fecha_inicio']:
                raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return v

    @validator('hora_fin')
    def validate_hora_fin(cls, v, values):
        """Valida que hora_fin sea posterior a hora_inicio"""
        if v and 'hora_inicio' in values and values['hora_inicio']:
            if v <= values['hora_inicio']:
                raise ValueError("hora_fin debe ser posterior a hora_inicio")
        return v

class PrecioCreate(PrecioBase):
    """Esquema para crear un nuevo precio"""
    pass

class PrecioUpdate(BaseModel):
    """Esquema para actualizar un precio existente"""
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(None, gt=0)
    precio_final: Optional[float] = Field(None, gt=0)
    moneda: Optional[MonedaEnum] = None
    activo: Optional[bool] = None
    prioridad: Optional[int] = Field(None, ge=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    cantidad_minima: Optional[int] = Field(None, ge=1)
    cantidad_maxima: Optional[int] = Field(None, ge=1)
    dias_semana: Optional[str] = Field(None, max_length=50)
    hora_inicio: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    hora_fin: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    metadatos: Optional[str] = None

class PrecioResponse(BaseModel):
    """Esquema de respuesta para precios"""
    id: int
    servicio_id: Optional[int] = None
    recurso_id: Optional[int] = None
    tipo_precio: str  # Usar str en lugar del enum para respuestas
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    precio_final: Optional[float] = None
    moneda: str  # Usar str en lugar del enum para respuestas
    activo: bool
    prioridad: int
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    cantidad_minima: Optional[int] = None
    cantidad_maxima: Optional[int] = None
    dias_semana: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    metadatos: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PrecioCompletoResponse(PrecioResponse):
    """Esquema de respuesta completo con información del servicio/recurso"""
    servicio: Optional[dict] = None
    recurso: Optional[dict] = None

# Esquemas para cálculos de precios
class CalculoPrecioRequest(BaseModel):
    """Esquema para solicitar cálculo de precio"""
    servicio_id: Optional[int] = Field(None, description="ID del servicio")
    recurso_id: Optional[int] = Field(None, description="ID del recurso")
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_fin: datetime = Field(..., description="Fecha y hora de fin")
    cantidad: int = Field(1, ge=1, description="Cantidad de unidades")
    cliente_id: Optional[int] = Field(None, description="ID del cliente para descuentos")

class CalculoPrecioResponse(BaseModel):
    """Esquema de respuesta para cálculo de precio"""
    precio_base: float = Field(..., description="Precio base")
    precio_final: float = Field(..., description="Precio final calculado")
    descuentos: List[dict] = Field(default_factory=list, description="Descuentos aplicados")
    recargos: List[dict] = Field(default_factory=list, description="Recargos aplicados")
    reglas_aplicadas: List[dict] = Field(default_factory=list, description="Reglas de precio aplicadas")
    desglose: dict = Field(..., description="Desglose detallado del precio")

# Esquemas para estadísticas
class EstadisticasPreciosResponse(BaseModel):
    """Esquema de respuesta para estadísticas de precios"""
    total_precios: int
    precios_activos: int
    precios_inactivos: int
    precio_promedio: float
    precio_minimo: float
    precio_maximo: float
    monedas_utilizadas: List[str]
    tipos_precio: List[str]

# Esquemas para búsqueda y filtros
class FiltroPrecios(BaseModel):
    """Esquema para filtrar precios"""
    servicio_id: Optional[int] = None
    recurso_id: Optional[int] = None
    tipo_precio: Optional[TipoPrecioEnum] = None
    moneda: Optional[MonedaEnum] = None
    activo: Optional[bool] = None
    precio_minimo: Optional[float] = None
    precio_maximo: Optional[float] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
