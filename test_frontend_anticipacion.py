#!/usr/bin/env python3
"""
Script para simular exactamente el comportamiento del frontend
y verificar por qué no se aplica el descuento por anticipación
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_health():
    """Verificar que la API esté funcionando"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API funcionando correctamente")
            return True
        else:
            print(f"❌ API respondiendo con status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar a la API: {e}")
        return False

def get_services():
    """Obtener lista de servicios"""
    try:
        response = requests.get(f"{API_BASE_URL}/servicios/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener servicios: {e}")
        return []

def get_resources():
    """Obtener lista de recursos"""
    try:
        response = requests.get(f"{API_BASE_URL}/recursos/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener recursos: {e}")
        return []

def simulate_frontend_calculation(service_id, resource_id, fecha, hora, duracion_noches, participantes, tipo_cliente="regular"):
    """
    Simula exactamente lo que hace el frontend:
    1. Crea fecha_hora_inicio = fecha + hora
    2. Crea fecha_hora_fin = fecha_hora_inicio + (duracion_noches * 24 horas)
    """
    # Simular el comportamiento del frontend
    fecha_hora_inicio = datetime.strptime(f"{fecha}T{hora}", "%Y-%m-%dT%H:%M")
    
    # Convertir noches a horas (como hace el frontend)
    duracion_horas = duracion_noches * 24
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)
    
    # Calcular días de anticipación (desde hoy hasta la fecha de inicio)
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dias_anticipacion = (fecha_hora_inicio.date() - hoy.date()).days
    
    print(f"\n🔍 Simulando cálculo del frontend:")
    print(f"   Fecha seleccionada: {fecha}")
    print(f"   Hora seleccionada: {hora}")
    print(f"   Duración en noches: {duracion_noches}")
    print(f"   Duración convertida a horas: {duracion_horas}")
    print(f"   Fecha/hora inicio: {fecha_hora_inicio}")
    print(f"   Fecha/hora fin: {fecha_hora_fin}")
    print(f"   Días de anticipación: {dias_anticipacion}")
    
    # Enviar a la API
    url = f"{API_BASE_URL}/precios-dinamicos/calcular"
    payload = {
        "servicio_id": service_id,
        "recurso_id": resource_id,
        "fecha_hora_inicio": fecha_hora_inicio.isoformat(),
        "fecha_hora_fin": fecha_hora_fin.isoformat(),
        "participantes": participantes,
        "tipo_cliente": tipo_cliente
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Cálculo exitoso:")
        print(f"   💰 Precio base: {result.get('precio_base')}€")
        print(f"   💰 Precio final: {result.get('precio_final')}€")
        print(f"   💰 Descuento total: {result.get('descuento_total')}€")
        print(f"   📋 Reglas aplicadas: {len(result.get('reglas_aplicadas', []))}")
        
        for regla in result.get('reglas_aplicadas', []):
            print(f"      - {regla.get('nombre')}: {regla.get('tipo_modificador')} {regla.get('valor_modificador')}")
        
        # Verificar si se aplicó el descuento por anticipación
        if dias_anticipacion >= 7:
            if result.get('descuento_total', 0) > 0:
                print(f"   ✅ Descuento por anticipación aplicado correctamente")
            else:
                print(f"   ❌ Descuento por anticipación NO se aplicó (esperado: sí)")
        else:
            if result.get('descuento_total', 0) == 0:
                print(f"   ✅ Sin descuento por anticipación (esperado: no)")
            else:
                print(f"   ⚠️ Descuento aplicado inesperadamente")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    print("🔍 Simulando Comportamiento del Frontend")
    print("=" * 60)

    if not test_health():
        return

    services = get_services()
    resources = get_resources()

    if not services or not resources:
        print("No se pudieron cargar servicios o recursos")
        return

    # Usar el primer servicio y recurso disponibles
    service_id = services[0]['id']
    resource_id = resources[0]['id']
    
    print(f"\n🧪 Probando con servicio: {services[0]['nombre']} (ID: {service_id})")
    print(f"   Recurso: {resources[0]['nombre']} (ID: {resource_id})")

    # Obtener fecha de hoy
    hoy = datetime.now()
    
    # Casos de prueba que simulan el frontend
    test_cases = [
        {
            "nombre": "Reserva inmediata (hoy)",
            "fecha": hoy.strftime("%Y-%m-%d"),
            "hora": "10:00",
            "duracion_noches": 1,
            "participantes": 1
        },
        {
            "nombre": "Reserva con 3 días de anticipación",
            "fecha": (hoy + timedelta(days=3)).strftime("%Y-%m-%d"),
            "hora": "10:00",
            "duracion_noches": 1,
            "participantes": 1
        },
        {
            "nombre": "Reserva con 7 días de anticipación",
            "fecha": (hoy + timedelta(days=7)).strftime("%Y-%m-%d"),
            "hora": "10:00",
            "duracion_noches": 1,
            "participantes": 1
        },
        {
            "nombre": "Reserva con 14 días de anticipación",
            "fecha": (hoy + timedelta(days=14)).strftime("%Y-%m-%d"),
            "hora": "10:00",
            "duracion_noches": 1,
            "participantes": 1
        },
        {
            "nombre": "Reserva con 30 días de anticipación",
            "fecha": (hoy + timedelta(days=30)).strftime("%Y-%m-%d"),
            "hora": "10:00",
            "duracion_noches": 1,
            "participantes": 1
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"🧪 {test_case['nombre']}")
        print(f"{'='*60}")
        
        simulate_frontend_calculation(
            service_id=service_id,
            resource_id=resource_id,
            fecha=test_case['fecha'],
            hora=test_case['hora'],
            duracion_noches=test_case['duracion_noches'],
            participantes=test_case['participantes']
        )

if __name__ == "__main__":
    main()
