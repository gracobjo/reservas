from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base

class Recurso(Base):
    __tablename__ = "recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # sala, persona, vehiculo, etc.
    capacidad = Column(Integer, default=1)  # Capacidad del recurso
    descripcion = Column(String, nullable=True)  # Descripción opcional
    disponible = Column(Boolean, default=True)
    precio_base = Column(Float, default=0.0)  # Precio base por hora
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    reservas = relationship("Reserva", back_populates="recurso")
    horarios = relationship("HorarioRecurso", back_populates="recurso")
    precios = relationship("Precio", back_populates="recurso")
