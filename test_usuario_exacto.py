#!/usr/bin/env python3
"""
Script para reproducir exactamente lo que ve el usuario:
- Precio base: 80.00 €
- Precio final: 96.00 €
- Reglas aplicadas: Hora Pico Mañana: +20%
"""

import requests
import json
from datetime import datetime, timedelta

def test_usuario_exacto():
    print("🔍 Test Reproducción Usuario - Precio 80€ -> 96€")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # El usuario ve precio base 80€ y final 96€
    # Esto significa que se aplicó un recargo del 20% (96/80 = 1.2)
    # Busquemos qué servicio y recurso pueden dar este resultado
    
    print(f"🔍 Buscando servicios con precio base 80€...")
    try:
        servicios_response = requests.get(f"{BASE_URL}/servicios/")
        if servicios_response.status_code == 200:
            servicios = servicios_response.json()
            servicios_80 = [s for s in servicios if s.get('precio_base') == 80.0]
            
            if servicios_80:
                print(f"✅ Servicios con precio base 80€ encontrados:")
                for servicio in servicios_80:
                    print(f"   - {servicio['nombre']} (ID: {servicio['id']})")
                servicio_id = servicios_80[0]['id']
            else:
                print(f"❌ No se encontró servicio con precio base 80€")
                print(f"   Servicios disponibles:")
                for servicio in servicios[:5]:  # Mostrar solo los primeros 5
                    print(f"     - {servicio['nombre']}: €{servicio['precio_base']}")
                return
        else:
            print(f"❌ Error obteniendo servicios: {servicios_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Buscar recursos disponibles
    print(f"\n🔍 Buscando recursos disponibles...")
    try:
        recursos_response = requests.get(f"{BASE_URL}/recursos/")
        if recursos_response.status_code == 200:
            recursos = recursos_response.json()
            recursos_disponibles = [r for r in recursos if r.get('disponible')]
            
            if recursos_disponibles:
                print(f"✅ Recursos disponibles encontrados:")
                for recurso in recursos_disponibles[:3]:  # Mostrar solo los primeros 3
                    print(f"   - {recurso['nombre']} ({recurso['tipo']})")
                recurso_id = recursos_disponibles[0]['id']
            else:
                print(f"❌ No se encontró recurso disponible")
                return
        else:
            print(f"❌ Error obteniendo recursos: {recursos_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Probar diferentes duraciones para encontrar la que dé precio final 96€
    duraciones = [24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336]
    
    print(f"\n🔍 Probando diferentes duraciones para encontrar precio final 96€...")
    
    for duracion in duraciones:
        # Fecha actual + 30 días (como hace el frontend)
        fecha_inicio = datetime.now() + timedelta(days=30)
        fecha_fin = fecha_inicio + timedelta(hours=duracion)
        
        # Formato ISO como lo hace el frontend
        fecha_hora_inicio = fecha_inicio.isoformat()
        fecha_hora_fin = fecha_fin.isoformat()
        
        # Datos para la petición
        payload = {
            "servicio_id": servicio_id,
            "recurso_id": recurso_id,
            "fecha_hora_inicio": fecha_hora_inicio,
            "fecha_hora_fin": fecha_hora_fin,
            "participantes": 1,
            "tipo_cliente": "regular"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/precios-dinamicos/calcular",
                json=payload
            )
            
            if response.status_code == 200:
                resultado = response.json()
                precio_base = resultado.get('precio_base', 0)
                precio_final = resultado.get('precio_final', 0)
                reglas_aplicadas = resultado.get('reglas_aplicadas', [])
                
                print(f"   {duracion:3d} horas: €{precio_base:5.2f} -> €{precio_final:5.2f} ({len(reglas_aplicadas)} reglas)")
                
                # Si encontramos el resultado que busca el usuario
                if precio_base == 80.0 and precio_final == 96.0:
                    print(f"\n🎉 ¡ENCONTRADO! Duración: {duracion} horas")
                    print(f"   Precio base: €{precio_base}")
                    print(f"   Precio final: €{precio_final}")
                    print(f"   Reglas aplicadas: {len(reglas_aplicadas)}")
                    
                    # Mostrar las reglas aplicadas
                    for i, regla in enumerate(reglas_aplicadas):
                        print(f"\n  Regla {i+1}:")
                        print(f"    Nombre: {regla.get('nombre', 'N/A')}")
                        print(f"    Tipo: {regla.get('tipo_regla', 'N/A')}")
                        print(f"    Modificador: {regla.get('tipo_modificador', 'N/A')}")
                        print(f"    Valor: {regla.get('valor_modificador', 'N/A')}")
                        print(f"    Descuento: {regla.get('descuento', 'N/A')}")
                        print(f"    Recargo: {regla.get('recargo', 'N/A')}")
                    
                    # Verificar si hay reglas de anticipación
                    reglas_anticipacion = [r for r in reglas_aplicadas if r.get('tipo_regla') == 'anticipacion']
                    if reglas_anticipacion:
                        print(f"\n🎉 ¡DESCUENTO DE ANTICIPACIÓN ENCONTRADO!")
                        for regla in reglas_anticipacion:
                            print(f"   - {regla.get('nombre')}: {regla.get('descuento')}€")
                    else:
                        print(f"\n❌ No se aplicó descuento de anticipación")
                    
                    return
                    
        except Exception as e:
            print(f"   {duracion:3d} horas: Error - {e}")
            continue
    
    print(f"\n❌ No se encontró ninguna duración que dé precio final 96€")
    print(f"   Esto sugiere que el usuario está viendo datos diferentes")

if __name__ == "__main__":
    print("🚀 Test Reproducción Usuario")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        test_usuario_exacto()
        
        print("\n" + "=" * 60)
        print("🏁 Test Completado")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en el test: {e}")
