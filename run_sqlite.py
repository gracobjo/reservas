#!/usr/bin/env python3
"""
Script simplificado para ejecutar el microservicio de reservas con SQLite
"""

import uvicorn
from app.main_sqlite import app

if __name__ == "__main__":
    print("🚀 Iniciando Microservicio de Reservas (SQLite)...")
    print("📚 Documentación disponible en: http://localhost:8000/docs")
    print("🏠 Página principal: http://localhost:8000")
    print("💚 Health check: http://localhost:8000/health")
    print("")
    print("🔑 Credenciales de prueba:")
    print("   👑 Admin: admin / admin123")
    print("   👤 Usuario: usuario / user123")
    print("")
    print("⏹️  Presiona Ctrl+C para detener")
    print("=" * 50)
    
    uvicorn.run(
        "app.main_sqlite:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
