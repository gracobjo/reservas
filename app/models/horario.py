from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db_sqlite_clean import Base

class HorarioRecurso(Base):
    __tablename__ = "horarios_recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=False)
    
    # Día de la semana (0=Lunes, 1=Martes, 2=Miércoles, 3=Jueves, 4=Viernes, 5=Sábado, 6=Domingo)
    dia_semana = Column(Integer, nullable=False)
    
    # Horarios de inicio y fin (usar String para compatibilidad con SQLite)
    hora_inicio = Column(String, nullable=False)  # Formato: "HH:MM"
    hora_fin = Column(String, nullable=False)     # Formato: "HH:MM"
    
    # Estado del horario
    disponible = Column(Boolean, default=True)
    
    # Configuración adicional
    duracion_slot_minutos = Column(Integer, default=30)  # Duración de cada slot de reserva
    pausa_entre_slots = Column(Integer, default=0)  # Pausa entre slots en minutos
    
    # Metadatos
    created_at = Column(String, default=lambda: func.now().strftime("%H:%M:%S"))
    updated_at = Column(String, onupdate=lambda: func.now().strftime("%H:%M:%S"))
    
    # Check constraints
    __table_args__ = (
        CheckConstraint(dia_semana >= 0, name='check_dia_semana_min'),
        CheckConstraint(dia_semana <= 6, name='check_dia_semana_max'),
        CheckConstraint(duracion_slot_minutos > 0, name='check_duracion_slot'),
        CheckConstraint(pausa_entre_slots >= 0, name='check_pausa_slots'),
    )
    
    # Relationships
    recurso = relationship("Recurso", back_populates="horarios")
    
    def __repr__(self):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return f"<HorarioRecurso(recurso_id={self.recurso_id}, dia={dias[self.dia_semana]}, {self.hora_inicio}-{self.hora_fin})>"
