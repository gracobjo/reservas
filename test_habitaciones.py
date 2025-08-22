#!/usr/bin/env python3
"""
Script para probar el cálculo de precios con habitaciones
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_habitacion_individual():
    """Probar cálculo con habitación individual"""
    print("🏨 Probando Habitación Individual...")
    
    # Buscar servicio de habitación individual
    response = requests.get(f"{API_BASE_URL}/servicios/")
    servicios = response.json()
    
    habitacion_individual = None
    for servicio in servicios:
        if "individual" in servicio['nombre'].lower():
            habitacion_individual = servicio
            break
    
    if not habitacion_individual:
        print("❌ No se encontró servicio de habitación individual")
        return
    
    # Buscar recurso de habitación individual
    response = requests.get(f"{API_BASE_URL}/recursos/")
    recursos = response.json()
    
    habitacion_recurso = None
    for recurso in recursos:
        if "individual" in recurso['nombre'].lower():
            habitacion_recurso = recurso
            break
    
    if not habitacion_recurso:
        print("❌ No se encontró recurso de habitación individual")
        return
    
    print(f"✅ Servicio: {habitacion_individual['nombre']} (ID: {habitacion_individual['id']})")
    print(f"✅ Recurso: {habitacion_recurso['nombre']} (ID: {habitacion_recurso['id']})")
    
    # Probar diferentes duraciones
    duraciones = [1, 2, 3, 7]  # 1, 2, 3, 7 noches
    
    for noches in duraciones:
        print(f"\n🌙 Probando {noches} noche{'s' if noches > 1 else ''}...")
        
        # Crear fechas
        fecha_inicio = datetime.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(days=noches)
        
        test_data = {
            "servicio_id": habitacion_individual['id'],
            "recurso_id": habitacion_recurso['id'],
            "fecha_hora_inicio": fecha_inicio.isoformat(),
            "fecha_hora_fin": fecha_fin.isoformat(),
            "participantes": 1,
            "tipo_cliente": "regular"
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                precio_base = result['precio_base']
                precio_final = result['precio_final']
                reglas_aplicadas = len(result['reglas_aplicadas'])
                
                print(f"   💰 Precio base: €{precio_base:.2f}")
                print(f"   💸 Precio final: €{precio_final:.2f}")
                print(f"   📋 Reglas aplicadas: {reglas_aplicadas}")
                
                if reglas_aplicadas > 0:
                    for regla in result['reglas_aplicadas']:
                        print(f"      📌 {regla['nombre']}")
                
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_habitacion_doble():
    """Probar cálculo con habitación doble"""
    print("\n🏨 Probando Habitación Doble...")
    
    # Buscar servicio de habitación doble
    response = requests.get(f"{API_BASE_URL}/servicios/")
    servicios = response.json()
    
    habitacion_doble = None
    for servicio in servicios:
        if "doble" in servicio['nombre'].lower():
            habitacion_doble = servicio
            break
    
    if not habitacion_doble:
        print("❌ No se encontró servicio de habitación doble")
        return
    
    # Buscar recurso de habitación doble
    response = requests.get(f"{API_BASE_URL}/recursos/")
    recursos = response.json()
    
    habitacion_recurso = None
    for recurso in recursos:
        if "doble" in recurso['nombre'].lower():
            habitacion_recurso = recurso
            break
    
    if not habitacion_recurso:
        print("❌ No se encontró recurso de habitación doble")
        return
    
    print(f"✅ Servicio: {habitacion_doble['nombre']} (ID: {habitacion_doble['id']})")
    print(f"✅ Recurso: {habitacion_recurso['nombre']} (ID: {habitacion_recurso['id']})")
    
    # Probar fin de semana (sábado)
    print(f"\n🌙 Probando fin de semana (sábado)...")
    
    # Calcular próximo sábado
    hoy = datetime.now()
    dias_hasta_sabado = (5 - hoy.weekday()) % 7  # 5 = sábado
    if dias_hasta_sabado == 0:
        dias_hasta_sabado = 7  # Si hoy es sábado, ir al próximo
    
    fecha_sabado = hoy + timedelta(days=dias_hasta_sabado)
    fecha_inicio = fecha_sabado.replace(hour=14, minute=0, second=0, microsecond=0)  # Check-in 14:00
    fecha_fin = fecha_inicio + timedelta(days=2)  # 2 noches (sábado y domingo)
    
    test_data = {
        "servicio_id": habitacion_doble['id'],
        "recurso_id": habitacion_recurso['id'],
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": 2,
        "tipo_cliente": "regular"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            precio_base = result['precio_base']
            precio_final = result['precio_final']
            reglas_aplicadas = len(result['reglas_aplicadas'])
            
            print(f"   📅 Fecha: {fecha_inicio.strftime('%A %d/%m/%Y')}")
            print(f"   💰 Precio base: €{precio_base:.2f}")
            print(f"   💸 Precio final: €{precio_final:.2f}")
            print(f"   📋 Reglas aplicadas: {reglas_aplicadas}")
            
            if reglas_aplicadas > 0:
                for regla in result['reglas_aplicadas']:
                    print(f"      📌 {regla['nombre']}")
            
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Probando Cálculo de Precios para Habitaciones")
    print("=" * 60)
    
    # Verificar que la API esté funcionando
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API no está disponible")
            return
        print("✅ API conectada correctamente")
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")
        return
    
    # Probar habitaciones
    test_habitacion_individual()
    test_habitacion_doble()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
