from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base

class Reserva(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=False)
    fecha_hora_inicio = Column(DateTime, nullable=False)
    fecha_hora_fin = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False, default="pendiente")  # pendiente, confirmada, cancelada
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Check constraint for estado values
    __table_args__ = (
        CheckConstraint(estado.in_(['pendiente', 'confirmada', 'cancelada']), name='check_estado'),
    )
    
    # Relationships
    cliente = relationship("Cliente", back_populates="reservas")
    servicio = relationship("Servicio", back_populates="reservas")
    recurso = relationship("Recurso", back_populates="reservas")
    historial_precios = relationship("HistorialPrecio", back_populates="reserva")
