from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base

class Precio(Base):
    __tablename__ = "precios"
    
    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    tipo_regla = Column(String, nullable=False)  # grupo, dia, franja_horaria
    valor = Column(Float, nullable=False)
    descripcion = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    servicio = relationship("Servicio", back_populates="precios")
