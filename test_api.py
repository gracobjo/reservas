#!/usr/bin/env python3
"""
Script para probar la API de cálculo de precios
Ayuda a identificar qué está causando el error 422
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_health():
    """Probar endpoint de salud"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Respuesta: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_servicios():
    """Probar endpoint de servicios"""
    try:
        response = requests.get(f"{API_BASE_URL}/servicios/")
        print(f"✅ Servicios: {response.status_code}")
        if response.status_code == 200:
            servicios = response.json()
            print(f"   Total servicios: {len(servicios)}")
            for servicio in servicios[:3]:  # Mostrar solo los primeros 3
                print(f"   - {servicio['nombre']} (ID: {servicio['id']})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error obteniendo servicios: {e}")
        return False

def test_recursos():
    """Probar endpoint de recursos"""
    try:
        response = requests.get(f"{API_BASE_URL}/recursos/")
        print(f"✅ Recursos: {response.status_code}")
        if response.status_code == 200:
            recursos = response.json()
            print(f"   Total recursos: {len(recursos)}")
            for recurso in recursos[:3]:  # Mostrar solo los primeros 3
                print(f"   - {recurso['nombre']} (ID: {recurso['id']})")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error obteniendo recursos: {e}")
        return False

def test_calculo_precio():
    """Probar endpoint de cálculo de precios"""
    from datetime import datetime, timedelta
    
    # Crear fechas de prueba
    fecha_inicio = datetime.now() + timedelta(days=1)  # Mañana
    fecha_fin = fecha_inicio + timedelta(hours=24)     # 24 horas después
    
    # Datos de prueba
    test_data = {
        "servicio_id": 1,
        "recurso_id": 1,
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": 1,
        "tipo_cliente": "regular"
    }
    
    print(f"🔍 Probando cálculo con datos: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
        print(f"✅ Cálculo de precio: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Respuesta exitosa: {json.dumps(result, indent=2)}")
        elif response.status_code == 422:
            print(f"   ❌ Error 422 - Datos inválidos")
            try:
                error_detail = response.json()
                print(f"   Detalles del error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Texto del error: {response.text}")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error en cálculo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando API de Sistema de Reservas")
    print("=" * 50)
    
    # Probar endpoints básicos
    if not test_health():
        print("❌ API no está disponible")
        return
    
    if not test_servicios():
        print("❌ No se pueden obtener servicios")
        return
        
    if not test_recursos():
        print("❌ No se pueden obtener recursos")
        return
    
    print("\n" + "=" * 50)
    print("🔍 Probando cálculo de precios...")
    
    # Probar cálculo
    test_calculo_precio()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
