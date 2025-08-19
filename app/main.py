from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import engine, Base
from .routes import (
    cliente_router,
    servicio_router,
    recurso_router,
    reserva_router,
    precio_router,
    auth_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Microservicio de gestión de reservas para ecommerce, citas médicas, alquileres, etc.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure according to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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
        "message": "Bienvenido al Microservicio de Gestión de Reservas",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del servicio"""
    return {"status": "healthy", "service": "reservas-microservice"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
