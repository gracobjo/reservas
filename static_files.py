#!/usr/bin/env python3
"""
Script para servir archivos estáticos del cliente web
Útil para desarrollo y testing local
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

# Crear aplicación FastAPI
app = FastAPI(title="Cliente Web - Precios Dinámicos", version="1.0.0")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    """Servir la página principal del cliente web"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que el servidor esté funcionando"""
    return {"status": "healthy", "message": "Cliente web funcionando correctamente"}

if __name__ == "__main__":
    print("🌐 Iniciando servidor para cliente web...")
    print("📁 Archivos estáticos en: ./static/")
    print("🌍 Accede a: http://localhost:8080")
    print("📚 Documentación: http://localhost:8080/docs")
    print("\n💡 Para usar con la API principal:")
    print("   1. Ejecuta la API en http://localhost:8000")
    print("   2. Abre http://localhost:8080 en tu navegador")
    print("   3. El cliente se conectará automáticamente a la API")
    
    uvicorn.run(
        "static_files:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
