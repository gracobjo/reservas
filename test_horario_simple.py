#!/usr/bin/env python3
"""
Prueba simple del modelo de horarios
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Crear engine SQLite
engine = create_engine(
    "sqlite:///./data/horarios_test.db",
    connect_args={"check_same_thread": False},
    echo=True
)

# Crear base
Base = declarative_base()

# Modelo de recurso simple
class RecursoSimple(Base):
    __tablename__ = "recursos_simple"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    disponible = Column(Boolean, default=True)

# Modelo de horario simple (sin Time por ahora)
class HorarioSimple(Base):
    __tablename__ = "horarios_simple"
    id = Column(Integer, primary_key=True)
    recurso_id = Column(Integer, ForeignKey("recursos_simple.id"), nullable=False)
    dia_semana = Column(Integer, nullable=False)
    hora_inicio_str = Column(String, nullable=False)  # Usar String en lugar de Time
    hora_fin_str = Column(String, nullable=False)
    duracion_slot_minutos = Column(Integer, default=30)
    disponible = Column(Boolean, default=True)
    
    # Relationship
    recurso = relationship("RecursoSimple", back_populates="horarios")

# Agregar relationship al recurso
RecursoSimple.horarios = relationship("HorarioSimple", back_populates="recurso")

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Crear recurso
recurso = RecursoSimple(nombre="Consultorio Test", tipo="consultorio")
db.add(recurso)
db.commit()

# Crear horario
horario = HorarioSimple(
    recurso_id=recurso.id,
    dia_semana=0,  # Lunes
    hora_inicio_str="09:00",
    hora_fin_str="17:00",
    duracion_slot_minutos=45
)
db.add(horario)
db.commit()

# Consultar
result = db.query(HorarioSimple).first()
print(f"✅ Horario creado: Día {result.dia_semana}, {result.hora_inicio_str}-{result.hora_fin_str}")

db.close()
print("✅ Prueba de horarios completada exitosamente")
