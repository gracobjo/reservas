#!/usr/bin/env python3
"""
Script para testear específicamente el descuento de anticipación
que no aparece en el frontend para 264 horas (11 días)
"""

import requests
import json
from datetime import datetime, timedelta

def test_descuento_anticipacion_264_horas():
    print("🔍 Test Descuento de Anticipación - 264 horas (11 días)")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # Calcular fechas para 264 horas (11 días)
    fecha_inicio = datetime.now() + timedelta(days=30)  # 30 días en el futuro
    fecha_fin = fecha_inicio + timedelta(hours=264)
    
    # Formato ISO para la API
    fecha_hora_inicio = fecha_inicio.isoformat()
    fecha_hora_fin = fecha_fin.isoformat()
    
    print(f"📅 Fecha inicio: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
    print(f"📅 Fecha fin: {fecha_fin.strftime('%d/%m/%Y %H:%M')}")
    print(f"⏱️ Duración: 264 horas ({264/24:.1f} días)")
    print(f"🔗 URLs: {fecha_hora_inicio} -> {fecha_hora_fin}")
    
    # Datos para la petición
    payload = {
        "servicio_id": 12,  # Alquiler Habitación Individual
        "recurso_id": 15,   # Habitación Individual 1
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
            
            # Verificar si se aplicó el descuento de anticipación
            reglas_aplicadas = resultado.get('reglas_aplicadas', [])
            descuento_anticipacion = None
            
            print(f"\n🔍 Analizando reglas aplicadas ({len(reglas_aplicadas)} reglas):")
            
            for i, regla in enumerate(reglas_aplicadas):
                print(f"\n  Regla {i+1}:")
                print(f"    Nombre: {regla.get('nombre', 'N/A')}")
                print(f"    Tipo: {regla.get('tipo_regla', 'N/A')}")
                print(f"    Modificador: {regla.get('tipo_modificador', 'N/A')}")
                print(f"    Valor: {regla.get('valor_modificador', 'N/A')}")
                print(f"    Descuento: {regla.get('descuento', 'N/A')}")
                print(f"    Recargo: {regla.get('recargo', 'N/A')}")
                
                if regla.get('tipo_regla') == 'anticipacion':
                    descuento_anticipacion = regla
                    print(f"    ⭐ ¡DESCUENTO DE ANTICIPACIÓN ENCONTRADO!")
            
            if descuento_anticipacion:
                print(f"\n🎉 CONCLUSIÓN: SÍ se aplicó el descuento de anticipación")
                print(f"   Descuento: {descuento_anticipacion.get('descuento', 'N/A')}")
            else:
                print(f"\n❌ CONCLUSIÓN: NO se aplicó el descuento de anticipación")
                print(f"   Esto explica por qué no aparece en el frontend")
                
                # Verificar qué reglas de anticipación existen en la base de datos
                print(f"\n🔍 Verificando reglas de anticipación en la base de datos...")
                try:
                    reglas_response = requests.get(f"{BASE_URL}/precios-dinamicos/reglas")
                    if reglas_response.status_code == 200:
                        reglas = reglas_response.json()
                        reglas_anticipacion = [r for r in reglas if r.get('tipo_regla') == 'anticipacion']
                        print(f"   Total reglas: {len(reglas)}")
                        print(f"   Reglas de anticipación: {len(reglas_anticipacion)}")
                        
                        for regla in reglas_anticipacion:
                            print(f"     - {regla.get('nombre')}: {regla.get('descripcion', 'Sin descripción')}")
                    else:
                        print(f"   ❌ Error obteniendo reglas: {reglas_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error verificando reglas: {e}")
            
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    print("🚀 Test Descuento de Anticipación")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        test_descuento_anticipacion_264_horas()
        
        print("\n" + "=" * 60)
        print("🏁 Test Completado")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en el test: {e}")
