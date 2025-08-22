from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..db_sqlite_clean import Base

class TipoRegla(str, Enum):
    """Tipos de reglas de precios"""
    DIA_SEMANA = "dia_semana"           # Lunes, Martes, etc.
    HORA = "hora"                       # Horario específico
    TEMPORADA = "temporada"             # Alta/Baja temporada
    FESTIVO = "festivo"                 # Días festivos
    ANTICIPACION = "anticipacion"       # Reserva con X días de anticipación
    DURACION = "duracion"               # Duración del servicio
    RECURSO = "recurso"                 # Recurso específico
    PARTICIPANTES = "participantes"     # Número de participantes
    CLIENTE_TIPO = "cliente_tipo"       # Tipo de cliente (VIP, regular, etc.)

class TipoModificador(str, Enum):
    """Tipos de modificadores de precio"""
    PORCENTAJE = "porcentaje"           # +20%, -15%
    MONTO_FIJO = "monto_fijo"          # +$10, -$5
    PRECIO_FIJO = "precio_fijo"        # Precio absoluto $50

class ReglaPrecio(Base):
    """Reglas de precios dinámicos"""
    __tablename__ = "reglas_precios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    
    # Configuración de la regla
    tipo_regla = Column(SQLEnum(TipoRegla), nullable=False)
    condicion = Column(Text, nullable=False)  # JSON con las condiciones
    
    # Modificador de precio
    tipo_modificador = Column(SQLEnum(TipoModificador), nullable=False)
    valor_modificador = Column(Float, nullable=False)
    
    # Configuración adicional
    prioridad = Column(Integer, default=0)  # Mayor número = mayor prioridad
    activa = Column(Boolean, default=True)
    
    # Fechas de vigencia (opcional)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    
    # Restricciones (opcional)
    servicios_aplicables = Column(Text)  # JSON array con IDs de servicios
    recursos_aplicables = Column(Text)   # JSON array con IDs de recursos
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<ReglaPrecio(nombre={self.nombre}, tipo={self.tipo_regla}, modificador={self.valor_modificador})>"

class HistorialPrecio(Base):
    """Historial de cálculos de precios para auditoría"""
    __tablename__ = "historial_precios"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Referencia a la reserva
    reserva_id = Column(Integer, ForeignKey("reservas.id"))
    servicio_id = Column(Integer, ForeignKey("servicios.id"))
    recurso_id = Column(Integer, ForeignKey("recursos.id"))
    
    # Información del cálculo
    precio_base = Column(Float, nullable=False)
    precio_final = Column(Float, nullable=False)
    descuento_total = Column(Float, default=0.0)
    recargo_total = Column(Float, default=0.0)
    
    # Reglas aplicadas
    reglas_aplicadas = Column(Text)  # JSON con detalles de reglas aplicadas
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=func.now())
    
    # Relationships
    reserva = relationship("Reserva", back_populates="historial_precios")
    servicio = relationship("Servicio")
    recurso = relationship("Recurso")
    
    def __repr__(self):
        return f"<HistorialPrecio(reserva_id={self.reserva_id}, precio_base={self.precio_base}, precio_final={self.precio_final})>"

class ConfiguracionPrecio(Base):
    """Configuración global de precios"""
    __tablename__ = "configuracion_precios"
    
    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String, unique=True, nullable=False)
    valor = Column(String, nullable=False)
    descripcion = Column(Text)
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<ConfiguracionPrecio(clave={self.clave}, valor={self.valor})>"
