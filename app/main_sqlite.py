from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db_sqlite import engine, Base
from .routes import (
    cliente_router,
    servicio_router,
    recurso_router,
    reserva_router,
    precio_router,
    auth_router
)

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Microservicio de gestión de reservas con SQLite para ecommerce, citas médicas, alquileres, etc.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Agregar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(cliente_router)
app.include_router(servicio_router)
app.include_router(recurso_router)
app.include_router(reserva_router)
app.include_router(precio_router)

@app.get("/")
async def root():
    """Endpoint raíz del microservicio"""
    return {
        "message": "Bienvenido al Microservicio de Gestión de Reservas (SQLite)",
        "version": "1.0.0",
        "database": "SQLite",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {
        "status": "healthy", 
        "service": "reservas-microservice",
        "database": "SQLite",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_sqlite:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
