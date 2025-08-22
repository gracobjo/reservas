from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base

class Recurso(Base):
    __tablename__ = "recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # sala, persona, vehiculo, etc.
    disponible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    reservas = relationship("Reserva", back_populates="recurso")
    horarios = relationship("HorarioRecurso", back_populates="recurso")
