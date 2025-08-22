#!/usr/bin/env python3
"""
Script para debuggear exactamente qué está enviando el frontend
y qué está recibiendo, para identificar por qué no se aplica el descuento
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

def debug_frontend_request():
    """
    Simula exactamente lo que hace el frontend cuando el usuario:
    1. Selecciona una fecha futura (7+ días)
    2. Selecciona una hora
    3. Selecciona duración en noches
    4. Hace clic en calcular
    """
    print("🔍 Debuggeando Request del Frontend")
    print("=" * 50)
    
    # Simular selección del usuario en el frontend
    fecha_seleccionada = "2025-08-27"  # 7 días en el futuro
    hora_seleccionada = "10:00"
    duracion_noches = 1
    participantes = 1
    tipo_cliente = "regular"
    
    print(f"📅 Fecha seleccionada por el usuario: {fecha_seleccionada}")
    print(f"🕐 Hora seleccionada por el usuario: {hora_seleccionada}")
    print(f"🌙 Duración seleccionada: {duracion_noches} noche(s)")
    print(f"👥 Participantes: {participantes}")
    print(f"👤 Tipo cliente: {tipo_cliente}")
    
    # Simular el cálculo del frontend (línea 425-430 de app.js)
    fecha_hora_inicio = datetime.strptime(f"{fecha_seleccionada}T{hora_seleccionada}", "%Y-%m-%dT%H:%M")
    duracion_horas = duracion_noches * 24  # Línea 430 de app.js
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=duracion_horas)
    
    print(f"\n🔧 Cálculo del frontend:")
    print(f"   fecha_hora_inicio = new Date('{fecha_seleccionada}T{hora_seleccionada}')")
    print(f"   duracion_horas = {duracion_noches} * 24 = {duracion_horas}")
    print(f"   fecha_hora_fin = fecha_hora_inicio + ({duracion_horas} * 60 * 60 * 1000)")
    print(f"   Resultado: {fecha_hora_inicio} -> {fecha_hora_fin}")
    
    # Calcular días de anticipación
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dias_anticipacion = (fecha_hora_inicio.date() - hoy.date()).days
    
    print(f"\n📊 Análisis de anticipación:")
    print(f"   Fecha de hoy: {hoy.date()}")
    print(f"   Fecha de reserva: {fecha_hora_inicio.date()}")
    print(f"   Días de anticipación: {dias_anticipacion}")
    print(f"   ¿Debería aplicar descuento? {'SÍ' if dias_anticipacion >= 7 else 'NO'}")
    
    # Simular el payload que envía el frontend (línea 432-438 de app.js)
    payload = {
        "servicio_id": 1,  # Consulta Médica
        "recurso_id": 1,   # Consultorio 1
        "fecha_hora_inicio": fecha_hora_inicio.isoformat(),
        "fecha_hora_fin": fecha_hora_fin.isoformat(),
        "participantes": participantes,
        "tipo_cliente": tipo_cliente
    }
    
    print(f"\n📤 Payload que envía el frontend:")
    print(json.dumps(payload, indent=2))
    
    # Enviar a la API
    print(f"\n🚀 Enviando a la API...")
    url = f"{API_BASE_URL}/precios-dinamicos/calcular"
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Respuesta de la API:")
        print(f"   Status: {response.status_code}")
        print(f"   Precio base: {result.get('precio_base')}€")
        print(f"   Precio final: {result.get('precio_final')}€")
        print(f"   Descuento total: {result.get('descuento_total')}€")
        print(f"   Reglas aplicadas: {len(result.get('reglas_aplicadas', []))}")
        
        for regla in result.get('reglas_aplicadas', []):
            print(f"      - {regla.get('nombre')}: {regla.get('tipo_modificador')} {regla.get('valor_modificador')}")
        
        # Verificar si se aplicó el descuento por anticipación
        if dias_anticipacion >= 7:
            if result.get('descuento_total', 0) > 0:
                print(f"\n✅ RESULTADO: Descuento por anticipación SÍ se aplicó")
                print(f"   El backend está funcionando correctamente")
                print(f"   El problema debe estar en el frontend")
            else:
                print(f"\n❌ RESULTADO: Descuento por anticipación NO se aplicó")
                print(f"   El problema está en el backend")
        else:
            print(f"\nℹ️ RESULTADO: Sin descuento por anticipación (esperado)")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e.response.status_code}")
        print(f"   Respuesta: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    print("🚀 Debug Frontend - Descuento por Anticipación")
    print("=" * 60)
    
    if not test_health():
        return
    
    debug_frontend_request()

if __name__ == "__main__":
    main()
