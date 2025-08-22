#!/usr/bin/env python3
"""
Prueba simple de SQLite
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Crear engine SQLite
engine = create_engine(
    "sqlite:///./data/test.db",
    connect_args={"check_same_thread": False},
    echo=True
)

# Crear base
Base = declarative_base()

# Modelo simple
class TestModel(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    activo = Column(Boolean, default=True)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Crear registro de prueba
test_item = TestModel(nombre="Prueba", activo=True)
db.add(test_item)
db.commit()

# Consultar
result = db.query(TestModel).first()
print(f"✅ Registro creado: {result.nombre}")

db.close()
print("✅ Prueba SQLite completada exitosamente")
