from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    reservas = relationship("Reserva", back_populates="cliente")
    pagos = relationship("Pago", back_populates="cliente")
    facturas = relationship("Factura", back_populates="cliente")
    notificaciones = relationship("Notificacion", back_populates="cliente")
