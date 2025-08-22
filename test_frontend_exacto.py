#!/usr/bin/env python3
"""
Script para simular exactamente lo que está haciendo el frontend
y ver por qué no aparece el descuento de anticipación
"""

import requests
import json
from datetime import datetime, timedelta

def test_frontend_exacto():
    print("🔍 Test Simulación Frontend - Misma lógica")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # Simular exactamente lo que hace el frontend
    # Según el resultado del usuario: 264 horas, precio base 80€, precio final 96€
    
    # Fecha actual + 30 días (como hace el frontend)
    fecha_inicio = datetime.now() + timedelta(days=30)
    fecha_fin = fecha_inicio + timedelta(hours=264)
    
    # Formato ISO como lo hace el frontend
    fecha_hora_inicio = fecha_inicio.isoformat()
    fecha_hora_fin = fecha_fin.isoformat()
    
    print(f"📅 Fecha inicio: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"📅 Fecha fin: {fecha_fin.strftime('%d/%m/%Y %H:%M')}")
    print(f"⏱️ Duración: 264 horas ({264/24:.1f} días)")
    
    # Buscar el servicio que tenga precio base 80€
    print(f"\n🔍 Buscando servicio con precio base 80€...")
    try:
        servicios_response = requests.get(f"{BASE_URL}/servicios/")
        if servicios_response.status_code == 200:
            servicios = servicios_response.json()
            servicio_80 = None
            for servicio in servicios:
                if servicio.get('precio_base') == 80.0:
                    servicio_80 = servicio
                    break
            
            if servicio_80:
                print(f"✅ Servicio encontrado: {servicio_80['nombre']} - €{servicio_80['precio_base']}")
                servicio_id = servicio_80['id']
            else:
                print(f"❌ No se encontró servicio con precio base 80€")
                print(f"   Servicios disponibles:")
                for servicio in servicios:
                    print(f"     - {servicio['nombre']}: €{servicio['precio_base']}")
                return
        else:
            print(f"❌ Error obteniendo servicios: {servicios_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Buscar un recurso disponible
    print(f"\n🔍 Buscando recurso disponible...")
    try:
        recursos_response = requests.get(f"{BASE_URL}/recursos/")
        if recursos_response.status_code == 200:
            recursos = recursos_response.json()
            recurso_disponible = None
            for recurso in recursos:
                if recurso.get('disponible'):
                    recurso_disponible = recurso
                    break
            
            if recurso_disponible:
                print(f"✅ Recurso encontrado: {recurso_disponible['nombre']} - {recurso_disponible['tipo']}")
                recurso_id = recurso_disponible['id']
            else:
                print(f"❌ No se encontró recurso disponible")
                return
        else:
            print(f"❌ Error obteniendo recursos: {recursos_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Datos para la petición (exactamente como el frontend)
    payload = {
        "servicio_id": servicio_id,
        "recurso_id": recurso_id,
        "fecha_hora_inicio": fecha_hora_inicio,
        "fecha_hora_fin": fecha_hora_fin,
        "participantes": 1,
        "tipo_cliente": "regular"
    }
    
    print(f"\n📤 Payload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        # Llamada a la API
        print(f"\n🚀 Llamando a la API...")
        response = requests.post(
            f"{BASE_URL}/precios-dinamicos/calcular",
            json=payload
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            resultado = response.json()
            print(f"✅ Respuesta exitosa!")
            
            # Mostrar resultado completo
            print(f"\n📋 Resultado completo:")
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
            
            # Verificar si coincide con lo que ve el usuario
            precio_base = resultado.get('precio_base', 0)
            precio_final = resultado.get('precio_final', 0)
            reglas_aplicadas = resultado.get('reglas_aplicadas', [])
            
            print(f"\n🔍 Análisis del resultado:")
            print(f"   Precio base: €{precio_base}")
            print(f"   Precio final: €{precio_final}")
            print(f"   Reglas aplicadas: {len(reglas_aplicadas)}")
            
            if precio_base == 80.0 and precio_final == 96.0:
                print(f"   ✅ ¡Coincide exactamente con lo que ve el usuario!")
            else:
                print(f"   ❌ No coincide con lo que ve el usuario")
                print(f"      Usuario ve: €80.00 -> €96.00")
                print(f"      API devuelve: €{precio_base} -> €{precio_final}")
            
            # Verificar reglas de anticipación
            reglas_anticipacion = [r for r in reglas_aplicadas if r.get('tipo_regla') == 'anticipacion']
            if reglas_anticipacion:
                print(f"\n🎉 ¡DESCUENTO DE ANTICIPACIÓN ENCONTRADO!")
                for regla in reglas_anticipacion:
                    print(f"   - {regla.get('nombre')}: {regla.get('descuento')}€")
            else:
                print(f"\n❌ No se aplicó descuento de anticipación")
                
                # Verificar qué reglas se aplicaron
                print(f"\n🔍 Reglas que SÍ se aplicaron:")
                for regla in reglas_aplicadas:
                    print(f"   - {regla.get('nombre')} ({regla.get('tipo_regla')}): {regla.get('valor_modificador')}")
            
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    print("🚀 Test Simulación Frontend")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        test_frontend_exacto()
        
        print("\n" + "=" * 60)
        print("🏁 Test Completado")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en el test: {e}")
