#!/usr/bin/env python3
"""
Aplicación FastAPI simplificada para el microservicio de reservas con SQLite
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os

# Configuración de la base de datos SQLite
DATABASE_URL = "sqlite:///./data/reservas.db"
SECRET_KEY = "tu-clave-secreta-muy-larga-y-segura-para-sqlite"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Modelos de base de datos
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    created_at = Column(DateTime, default=func.now())

class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(Text)
    duracion_minutos = Column(Integer)
    precio_base = Column(Float)
    created_at = Column(DateTime, default=func.now())

class Recurso(Base):
    __tablename__ = "recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    tipo = Column(String)
    disponible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Precio(Base):
    __tablename__ = "precios"
    
    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"))
    tipo_regla = Column(String)
    valor = Column(Float)
    descripcion = Column(Text)
    created_at = Column(DateTime, default=func.now())

class Reserva(Base):
    __tablename__ = "reservas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servicio_id = Column(Integer, ForeignKey("servicios.id"))
    recurso_id = Column(Integer, ForeignKey("recursos.id"))
    fecha_hora_inicio = Column(DateTime)
    fecha_hora_fin = Column(DateTime)
    estado = Column(String, default="confirmada")
    created_at = Column(DateTime, default=func.now())

# Crear tablas
Base.metadata.create_all(bind=engine)

# Pydantic models
class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    
    class Config:
        from_attributes = True

class ClienteCreate(BaseModel):
    nombre: str
    email: str
    telefono: str

class ClienteResponse(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: str
    
    class Config:
        from_attributes = True

class ServicioCreate(BaseModel):
    nombre: str
    descripcion: str
    duracion_minutos: int
    precio_base: float

class ServicioResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    duracion_minutos: int
    precio_base: float
    
    class Config:
        from_attributes = True

class RecursoCreate(BaseModel):
    nombre: str
    tipo: str
    disponible: bool = True

class RecursoResponse(BaseModel):
    id: int
    nombre: str
    tipo: str
    disponible: bool
    
    class Config:
        from_attributes = True

class ReservaCreate(BaseModel):
    cliente_id: int
    servicio_id: int
    recurso_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime

class ReservaResponse(BaseModel):
    id: int
    cliente_id: int
    servicio_id: int
    recurso_id: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    
    class Config:
        from_attributes = True

# Dependency para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear aplicación FastAPI
app = FastAPI(
    title="Microservicio de Reservas (SQLite)",
    description="API para gestión de reservas con SQLite",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints básicos
@app.get("/")
async def root():
    return {
        "message": "Bienvenido al Microservicio de Gestión de Reservas (SQLite)",
        "version": "1.0.0",
        "database": "SQLite",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "reservas-microservice",
        "database": "SQLite",
        "version": "1.0.0"
    }

# Endpoints de clientes
@app.post("/clientes", response_model=ClienteResponse)
async def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente.dict())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@app.get("/clientes", response_model=List[ClienteResponse])
async def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# Endpoints de servicios
@app.post("/servicios", response_model=ServicioResponse)
async def crear_servicio(servicio: ServicioCreate, db: Session = Depends(get_db)):
    db_servicio = Servicio(**servicio.dict())
    db.add(db_servicio)
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

@app.get("/servicios", response_model=List[ServicioResponse])
async def listar_servicios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).offset(skip).limit(limit).all()
    return servicios

# Endpoints de recursos
@app.post("/recursos", response_model=RecursoResponse)
async def crear_recurso(recurso: RecursoCreate, db: Session = Depends(get_db)):
    db_recurso = Recurso(**recurso.dict())
    db.add(db_recurso)
    db.commit()
    db.refresh(db_recurso)
    return db_recurso

@app.get("/recursos", response_model=List[RecursoResponse])
async def listar_recursos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recursos = db.query(Recurso).offset(skip).limit(limit).all()
    return recursos

# Endpoints de reservas
@app.post("/reservas", response_model=ReservaResponse)
async def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    db_reserva = Reserva(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

@app.get("/reservas", response_model=List[ReservaResponse])
async def listar_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reservas = db.query(Reserva).offset(skip).limit(limit).all()
    return reservas

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Microservicio de Reservas (SQLite)...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("🏠 Página principal: http://localhost:8000")
    print("💚 Health check: http://localhost:8000/health")
    print("")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 50)
    
    uvicorn.run(
        "simple_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
