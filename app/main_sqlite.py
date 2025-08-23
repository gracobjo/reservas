from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .db_sqlite_clean import engine, Base
from .routes import (
    cliente_router,
    servicio_router,
    recurso_router,
    reserva_router,
    precio_router,
    auth_router,
    horario_router,
    precio_dinamico_router,
    pago_router,
    integracion_router
)

# Crear tablas de base de datos
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Microservicio de reservas con sistema de precios dinámicos y Sprint 5: Integraciones y Pagos",
    version="2.0.0",
    debug=settings.debug,
    openapi_tags=[
        {
            "name": "clientes",
            "description": "Operaciones CRUD para gestión de clientes"
        },
        {
            "name": "servicios", 
            "description": "Operaciones CRUD para gestión de servicios"
        },
        {
            "name": "recursos",
            "description": "Operaciones CRUD para gestión de recursos"
        },
        {
            "name": "reservas",
            "description": "Operaciones CRUD para gestión de reservas"
        },
        {
            "name": "precios",
            "description": "Operaciones CRUD para gestión de precios"
        },
        {
            "name": "horarios",
            "description": "Operaciones CRUD para gestión de horarios"
        },
        {
            "name": "precios-dinamicos",
            "description": "Sistema de precios dinámicos y reglas de precios"
        },
        {
            "name": "pagos",
            "description": "Sistema completo de pagos, facturas y reembolsos"
        },
        {
            "name": "integraciones",
            "description": "Sistema de integraciones externas, notificaciones y webhooks"
        }
    ]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth_router)
app.include_router(cliente_router)
app.include_router(servicio_router)
app.include_router(recurso_router)
app.include_router(reserva_router)
app.include_router(precio_router)
app.include_router(horario_router)
app.include_router(precio_dinamico_router)
app.include_router(pago_router)
app.include_router(integracion_router)

@app.get("/")
async def root():
    """Endpoint raíz del microservicio"""
    return {
        "message": "🎯 Sistema de Reservas con Precios Dinámicos",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "cliente_web": "/cliente-web"
    }

@app.get("/cliente-web")
async def cliente_web():
    """Servir la página principal del cliente web"""
    return FileResponse("cliente_web.html")

@app.get("/health")
async def health_check():
    """Endpoint de salud del microservicio"""
    return {
        "status": "healthy",
        "service": "reservas-microservice",
        "database": "sqlite",
        "timestamp": "2025-01-19T23:50:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_sqlite:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
