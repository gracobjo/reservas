#!/usr/bin/env python3
"""
Script para reproducir exactamente lo que ve el usuario:
- Duración: 264 horas
- Precio base: 80.00 €
- Precio final: 96.00 €
- Reglas aplicadas: Hora Pico Mañana: +20%
"""

import requests
import json
from datetime import datetime, timedelta

def test_usuario_264_horas():
    print("🔍 Test Usuario - 264 horas, 80€ -> 96€")
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
                for recurso in recursos_disponibles[:3]:
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
    
    # Probar diferentes horarios para encontrar el que dé precio final 96€
    # El usuario ve que se aplica "Hora Pico Mañana" (+20%)
    horarios = [
        ("08:00", "Mañana temprano"),
        ("09:00", "Mañana"),
        ("10:00", "Mañana"),
        ("11:00", "Mañana"),
        ("12:00", "Mediodía"),
        ("13:00", "Tarde"),
        ("14:00", "Tarde"),
        ("15:00", "Tarde"),
        ("16:00", "Tarde"),
        ("17:00", "Tarde tarde"),
        ("18:00", "Tarde tarde"),
        ("19:00", "Tarde tarde"),
        ("20:00", "Noche"),
        ("21:00", "Noche")
    ]
    
    print(f"\n🔍 Probando diferentes horarios para encontrar precio final 96€...")
    print(f"   Duración fija: 264 horas")
    
    for hora, descripcion in horarios:
        # Fecha actual + 30 días (como hace el frontend)
        fecha_inicio = datetime.now() + timedelta(days=30)
        # Establecer la hora específica
        fecha_inicio = fecha_inicio.replace(hour=int(hora.split(':')[0]), minute=int(hora.split(':')[1]), second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(hours=264)
        
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
                
                print(f"   {hora:5s} ({descripcion:12s}): €{precio_base:5.2f} -> €{precio_final:5.2f} ({len(reglas_aplicadas)} reglas)")
                
                # Si encontramos el resultado que busca el usuario
                if precio_base == 80.0 and precio_final == 96.0:
                    print(f"\n🎉 ¡ENCONTRADO! Hora: {hora} ({descripcion})")
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
                        print(f"   Esto explica por qué el usuario no lo ve")
                    
                    return
                    
        except Exception as e:
            print(f"   {hora:5s} ({descripcion:12s}): Error - {e}")
            continue
    
    print(f"\n❌ No se encontró ningún horario que dé precio final 96€")
    print(f"   Esto sugiere que el usuario está viendo datos diferentes")

if __name__ == "__main__":
    print("🚀 Test Usuario - 264 horas")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        test_usuario_264_horas()
        
        print("\n" + "=" * 60)
        print("🏁 Test Completado")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en el test: {e}")
