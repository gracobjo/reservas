from .cliente_routes import router as cliente_router
from .servicio_routes import router as servicio_router
from .recurso_routes import router as recurso_router
from .reserva_routes import router as reserva_router
from .precio_routes import router as precio_router
from .auth_routes import router as auth_router

__all__ = [
    "cliente_router",
    "servicio_router",
    "recurso_router",
    "reserva_router",
    "precio_router",
    "auth_router"
]
