#!/usr/bin/env python3
"""
Script para verificar por qué no se aplica el descuento por anticipación
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

def get_rules():
    """Obtener todas las reglas de precios"""
    try:
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener reglas: {e}")
        return []

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

def calculate_price(service_id, resource_id, fecha_inicio, fecha_fin, participantes, tipo_cliente="regular"):
    """Realiza una solicitud de cálculo de precio a la API."""
    url = f"{API_BASE_URL}/precios-dinamicos/calcular"
    payload = {
        "servicio_id": service_id,
        "recurso_id": resource_id,
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": participantes,
        "tipo_cliente": tipo_cliente
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"\n➡️ Enviando solicitud de cálculo:")
    print(f"   Fecha inicio: {fecha_inicio}")
    print(f"   Fecha fin: {fecha_fin}")
    print(f"   Diferencia: {(fecha_fin - fecha_inicio).days} días")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        print(f"✅ Cálculo exitoso. Precio final: {result.get('precio_final')}€")
        print(f"   Reglas aplicadas: {len(result.get('reglas_aplicadas', []))}")
        for regla in result.get('reglas_aplicadas', []):
            print(f"   - {regla.get('nombre')}: {regla.get('tipo_modificador')} {regla.get('valor_modificador')}")
        return result
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP al calcular precio: {e.response.status_code} - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión al calcular precio: {e}")
        return None

def main():
    print("🔍 Investigando Descuento por Anticipación")
    print("=" * 60)

    if not test_health():
        return

    # Verificar reglas existentes
    print("\n📋 Verificando reglas de precios...")
    rules = get_rules()
    
    if not rules:
        print("❌ No hay reglas de precios configuradas")
        return
    
    print(f"📊 Total de reglas: {len(rules)}")
    
    # Buscar reglas de descuento por anticipación
    descuento_anticipacion_rules = []
    for rule in rules:
        print(f"\n🔍 Regla: {rule.get('nombre')}")
        print(f"   Tipo: {rule.get('tipo_regla')}")
        print(f"   Condición: {rule.get('condicion')}")
        print(f"   Modificador: {rule.get('tipo_modificador')} {rule.get('valor_modificador')}")
        
        if rule.get('tipo_regla') == 'anticipacion':
            descuento_anticipacion_rules.append(rule)
    
    if not descuento_anticipacion_rules:
        print("\n❌ No hay reglas de descuento por anticipación configuradas")
        print("   Esto explica por qué no se aplica el descuento")
        return
    
    print(f"\n✅ Se encontraron {len(descuento_anticipacion_rules)} regla(s) de descuento por anticipación")
    
    # Obtener servicios y recursos para probar
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
    
    # Probar con diferentes anticipaciones
    test_cases = [
        ("Reserva inmediata (hoy)", 0),
        ("Reserva con 3 días de anticipación", 3),
        ("Reserva con 7 días de anticipación", 7),
        ("Reserva con 14 días de anticipación", 14),
        ("Reserva con 30 días de anticipación", 30)
    ]
    
    for test_name, days_ahead in test_cases:
        print(f"\n{'='*50}")
        print(f"🧪 {test_name}")
        print(f"{'='*50}")
        
        fecha_inicio = datetime.now() + timedelta(days=days_ahead)
        fecha_fin = fecha_inicio + timedelta(hours=1)  # 1 hora de duración
        
        result = calculate_price(service_id, resource_id, fecha_inicio, fecha_fin, 1)
        
        if result:
            precio_base = result.get('precio_base', 0)
            precio_final = result.get('precio_final', 0)
            descuento = result.get('descuento_total', 0)
            reglas_aplicadas = result.get('reglas_aplicadas', [])
            
            print(f"   💰 Precio base: {precio_base}€")
            print(f"   💰 Precio final: {precio_final}€")
            print(f"   💰 Descuento total: {descuento}€")
            print(f"   📋 Reglas aplicadas: {len(reglas_aplicadas)}")
            
            if reglas_aplicadas:
                for regla in reglas_aplicadas:
                    print(f"      - {regla.get('nombre')}: {regla.get('tipo_modificador')} {regla.get('valor_modificador')}")
            else:
                print("      - Ninguna regla aplicada")
        else:
            print("   ❌ Error en el cálculo")

if __name__ == "__main__":
    main()
