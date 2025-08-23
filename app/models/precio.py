from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base
import enum

class TipoPrecio(str, enum.Enum):
    """Tipos de precios disponibles"""
    BASE = "base"                    # Precio base del servicio/recurso
    HORA = "hora"                    # Precio por hora
    DIA = "dia"                      # Precio por día
    SEMANA = "semana"                # Precio por semana
    MES = "mes"                      # Precio por mes
    TEMPORADA = "temporada"          # Precio por temporada
    GRUPO = "grupo"                  # Precio para grupos
    DESCUENTO = "descuento"          # Descuentos especiales
    RECARGO = "recargo"              # Recargos especiales

class Moneda(str, enum.Enum):
    """Monedas soportadas"""
    EUR = "EUR"                      # Euro
    USD = "USD"                      # Dólar estadounidense
    GBP = "GBP"                      # Libra esterlina

class Precio(Base):
    __tablename__ = "precios"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones con servicios y recursos
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=True)
    
    # Información del precio
    tipo_precio = Column(String, nullable=False, default='base')
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Valores del precio
    precio_base = Column(Float, nullable=False, default=0.0)
    precio_final = Column(Float, nullable=True)
    moneda = Column(String, nullable=False, default='EUR')
    
    # Configuración del precio
    activo = Column(Boolean, default=True)
    prioridad = Column(Integer, default=0)  # Prioridad para aplicar precios
    
    # Fechas de validez
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    
    # Condiciones especiales
    cantidad_minima = Column(Integer, nullable=True)  # Cantidad mínima para aplicar
    cantidad_maxima = Column(Integer, nullable=True)  # Cantidad máxima para aplicar
    dias_semana = Column(String(50), nullable=True)   # Días de la semana (1,2,3,4,5,6,7)
    hora_inicio = Column(String(5), nullable=True)    # Hora de inicio (HH:MM)
    hora_fin = Column(String(5), nullable=True)       # Hora de fin (HH:MM)
    
    # Metadatos
    metadatos = Column(Text, nullable=True)  # JSON string para datos adicionales
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    servicio = relationship("Servicio", back_populates="precios")
    recurso = relationship("Recurso", back_populates="precios")
    
    def __repr__(self):
        return f"<Precio(id={self.id}, tipo={self.tipo_precio}, precio={self.precio_base} {self.moneda})>"
    
    def es_valido_en_fecha(self, fecha):
        """Verifica si el precio es válido en una fecha específica"""
        if self.fecha_inicio and fecha < self.fecha_inicio:
            return False
        if self.fecha_fin and fecha > self.fecha_fin:
            return False
        return True
    
    def es_valido_en_hora(self, hora):
        """Verifica si el precio es válido en una hora específica"""
        if not self.hora_inicio or not self.hora_fin:
            return True
        
        try:
            hora_actual = hora.strftime("%H:%M")
            return self.hora_inicio <= hora_actual <= self.hora_fin
        except:
            return True
    
    def es_valido_para_cantidad(self, cantidad):
        """Verifica si el precio es válido para una cantidad específica"""
        if self.cantidad_minima and cantidad < self.cantidad_minima:
            return False
        if self.cantidad_maxima and cantidad > self.cantidad_maxima:
            return False
        return True
