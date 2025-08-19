from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Configuración para SQLite
if settings.database_url.startswith("sqlite"):
    # Para SQLite, usar check_same_thread=False para compatibilidad con FastAPI
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        echo=settings.debug  # Mostrar SQL en modo debug
    )
else:
    # Para PostgreSQL (mantener compatibilidad)
    engine = create_engine(
        settings.database_url,
        echo=settings.debug
    )

# Crear sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependency para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
