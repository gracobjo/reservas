from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TipoRegla(str, Enum):
    DIA_SEMANA = "dia_semana"
    HORA = "hora"
    TEMPORADA = "temporada"
    FESTIVO = "festivo"
    ANTICIPACION = "anticipacion"
    DURACION = "duracion"
    RECURSO = "recurso"
    PARTICIPANTES = "participantes"
    CLIENTE_TIPO = "cliente_tipo"

class TipoModificador(str, Enum):
    PORCENTAJE = "porcentaje"
    MONTO_FIJO = "monto_fijo"
    PRECIO_FIJO = "precio_fijo"

# Schemas para ReglaPrecio
class ReglaPrecioBase(BaseModel):
    nombre: str = Field(..., description="Nombre de la regla")
    descripcion: Optional[str] = Field(None, description="Descripción de la regla")
    tipo_regla: TipoRegla = Field(..., description="Tipo de regla a aplicar")
    condicion: str = Field(..., description="Condiciones en formato JSON")
    tipo_modificador: TipoModificador = Field(..., description="Tipo de modificador de precio")
    valor_modificador: float = Field(..., description="Valor del modificador")
    prioridad: int = Field(0, description="Prioridad de la regla (mayor = más prioritaria)")
    activa: bool = Field(True, description="Si la regla está activa")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio de vigencia")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin de vigencia")
    servicios_aplicables: Optional[str] = Field(None, description="IDs de servicios aplicables (JSON)")
    recursos_aplicables: Optional[str] = Field(None, description="IDs de recursos aplicables (JSON)")

class ReglaPrecioCreate(ReglaPrecioBase):
    pass

class ReglaPrecioUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    condicion: Optional[str] = None
    tipo_modificador: Optional[TipoModificador] = None
    valor_modificador: Optional[float] = None
    prioridad: Optional[int] = None
    activa: Optional[bool] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    servicios_aplicables: Optional[str] = None
    recursos_aplicables: Optional[str] = None

class ReglaPrecioResponse(ReglaPrecioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para cálculo de precios
class CalculoPrecioRequest(BaseModel):
    servicio_id: int = Field(..., description="ID del servicio")
    recurso_id: int = Field(..., description="ID del recurso")
    fecha_hora_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_hora_fin: datetime = Field(..., description="Fecha y hora de fin")
    participantes: int = Field(1, ge=1, description="Número de participantes")
    cliente_id: Optional[int] = Field(None, description="ID del cliente (opcional)")
    tipo_cliente: Optional[str] = Field("regular", description="Tipo de cliente")

class ReglaAplicada(BaseModel):
    regla_id: int
    nombre: str
    tipo_regla: str
    tipo_modificador: str
    valor_modificador: float
    descuento: float = 0.0
    recargo: float = 0.0
    precio_resultado: float

class CalculoPrecioResponse(BaseModel):
    precio_base: float
    precio_final: float
    descuento_total: float = 0.0
    recargo_total: float = 0.0
    ahorro_total: float = 0.0
    reglas_aplicadas: List[ReglaAplicada] = []
    detalles: Dict[str, Any] = {}

# Schemas para configuración
class ConfiguracionPrecioBase(BaseModel):
    clave: str = Field(..., description="Clave de configuración")
    valor: str = Field(..., description="Valor de configuración")
    descripcion: Optional[str] = Field(None, description="Descripción")

class ConfiguracionPrecioCreate(ConfiguracionPrecioBase):
    pass

class ConfiguracionPrecioUpdate(BaseModel):
    valor: Optional[str] = None
    descripcion: Optional[str] = None

class ConfiguracionPrecioResponse(ConfiguracionPrecioBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas para historial
class HistorialPrecioResponse(BaseModel):
    id: int
    reserva_id: int
    servicio_id: int
    recurso_id: int
    precio_base: float
    precio_final: float
    descuento_total: float
    recargo_total: float
    reglas_aplicadas: str
    fecha_calculo: datetime
    
    class Config:
        from_attributes = True

# Schemas para reglas específicas
class ReglaDescuentoPorcentaje(BaseModel):
    """Regla de descuento por porcentaje"""
    porcentaje: float = Field(..., ge=0, le=100, description="Porcentaje de descuento")
    descripcion: Optional[str] = None

class ReglaRecargoHoraPico(BaseModel):
    """Regla de recargo por hora pico"""
    hora_inicio: str = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: str = Field(..., description="Hora de fin (HH:MM)")
    porcentaje_recargo: float = Field(..., gt=0, description="Porcentaje de recargo")
    dias_semana: List[int] = Field(..., description="Días de la semana (0=Lunes, 6=Domingo)")

class ReglaDescuentoAnticipar(BaseModel):
    """Regla de descuento por reservar con anticipación"""
    dias_minimos: int = Field(..., gt=0, description="Días mínimos de anticipación")
    porcentaje_descuento: float = Field(..., gt=0, le=100, description="Porcentaje de descuento")

class ReglaTemporadaAlta(BaseModel):
    """Regla de temporada alta"""
    fecha_inicio: str = Field(..., description="Fecha de inicio (YYYY-MM-DD)")
    fecha_fin: str = Field(..., description="Fecha de fin (YYYY-MM-DD)")
    porcentaje_recargo: float = Field(..., gt=0, description="Porcentaje de recargo")
    nombre_temporada: str = Field(..., description="Nombre de la temporada")

# Schema para crear reglas predefinidas
class ReglaRapida(BaseModel):
    tipo: str = Field(..., description="Tipo de regla rápida")
    configuracion: Dict[str, Any] = Field(..., description="Configuración específica")
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: int = Field(0, description="Prioridad de la regla")
