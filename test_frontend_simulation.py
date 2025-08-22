#!/usr/bin/env python3
"""
Script para simular exactamente lo que hace el frontend y identificar el problema
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

def simular_frontend_calculo():
    """Simular exactamente lo que hace el frontend"""
    print("🖥️ Simulando Cálculo del Frontend")
    print("=" * 50)
    
    # Obtener servicios y recursos
    try:
        servicios = requests.get(f"{API_BASE_URL}/servicios/").json()
        recursos = requests.get(f"{API_BASE_URL}/recursos/").json()
        
        # Buscar servicio de habitación
        habitacion_servicio = None
        for servicio in servicios:
            if "habitación" in servicio['nombre'].lower() or "alquiler" in servicio['nombre'].lower():
                habitacion_servicio = servicio
                break
        
        if not habitacion_servicio:
            print("❌ No se encontró servicio de habitación")
            return
        
        # Buscar recurso de habitación
        habitacion_recurso = None
        for recurso in recursos:
            if "habitación" in recurso['nombre'].lower():
                habitacion_recurso = recurso
                break
        
        if not habitacion_recurso:
            print("❌ No se encontró recurso de habitación")
            return
        
        print(f"✅ Servicio: {habitacion_servicio['nombre']} (ID: {habitacion_servicio['id']})")
        print(f"✅ Recurso: {habitacion_recurso['nombre']} (ID: {habitacion_recurso['id']})")
        
        # Simular datos del frontend (como si fuera un sábado)
        fecha_base = datetime.now() + timedelta(days=1)
        while fecha_base.weekday() != 5:  # 5 = Sábado
            fecha_base += timedelta(days=1)
        
        fecha_inicio = fecha_base.replace(hour=14, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)  # 1 noche = 24 horas
        
        # Simular exactamente los datos que envía el frontend
        formData = {
            "servicio_id": int(habitacion_servicio['id']),
            "recurso_id": int(habitacion_recurso['id']),
            "fecha_hora_inicio": fecha_inicio.isoformat(),
            "fecha_hora_fin": fecha_fin.isoformat(),
            "participantes": 2,
            "tipo_cliente": "vip"
        }
        
        print(f"\n📅 Simulando reserva para: {fecha_inicio.strftime('%A %d/%m/%Y')} (Sábado)")
        print(f"   ⏰ Hora: {fecha_inicio.strftime('%H:%M')}")
        print(f"   🌙 Duración: 1 noche (24 horas)")
        print(f"   👥 Participantes: 2")
        print(f"   👤 Tipo Cliente: VIP")
        
        print(f"\n📤 Datos enviados al backend:")
        for key, value in formData.items():
            print(f"   • {key}: {value} (tipo: {type(value).__name__})")
        
        # Hacer la llamada a la API
        print(f"\n🔄 Llamando a la API...")
        try:
            response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=formData)
            print(f"   📡 Status Code: {response.status_code}")
            print(f"   📡 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Respuesta exitosa del backend:")
                print(f"   • Precio base: €{result['precio_base']:.2f}")
                print(f"   • Precio final: €{result['precio_final']:.2f}")
                print(f"   • Diferencia: €{result['precio_final'] - result['precio_base']:.2f}")
                
                reglas_aplicadas = result.get('reglas_aplicadas', [])
                print(f"   • Reglas aplicadas: {len(reglas_aplicadas)}")
                
                if reglas_aplicadas:
                    print(f"\n📋 Detalle de reglas aplicadas:")
                    for i, regla in enumerate(reglas_aplicadas, 1):
                        print(f"   {i}. {regla['nombre']}")
                        print(f"      - Tipo: {regla['tipo_regla']}")
                        print(f"      - Modificador: {regla['tipo_modificador']}")
                        print(f"      - Valor: {regla['valor_modificador']}")
                        print(f"      - Descuento: {regla['descuento']}")
                        print(f"      - Recargo: {regla['recargo']}")
                        print(f"      - Precio resultado: {regla['precio_resultado']}")
                else:
                    print(f"\nℹ️ Sin reglas aplicadas")
                
                # Verificar si se aplicó la regla de fin de semana
                if result['precio_final'] > result['precio_base']:
                    print(f"\n✅ Se aplicó al menos una regla (precio aumentó)")
                else:
                    print(f"\n❌ No se aplicó ninguna regla (precio no cambió)")
                
            else:
                print(f"\n❌ Error en la respuesta:")
                print(f"   • Status: {response.status_code}")
                print(f"   • Contenido: {response.text}")
                
        except Exception as e:
            print(f"\n❌ Error en la llamada a la API: {e}")
        
    except Exception as e:
        print(f"❌ Error obteniendo servicios/recursos: {e}")

def verificar_reglas_activas():
    """Verificar que las reglas estén activas y configuradas correctamente"""
    print("\n🔍 Verificando Reglas Activas")
    print("=" * 50)
    
    try:
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas?activas_solo=true")
        if response.status_code == 200:
            reglas = response.json()
            print(f"✅ Reglas activas encontradas: {len(reglas)}")
            
            for regla in reglas:
                print(f"\n   📌 {regla['nombre']}")
                print(f"      - ID: {regla['id']}")
                print(f"      - Tipo: {regla['tipo_regla']}")
                print(f"      - Modificador: {regla['tipo_modificador']} {regla['valor_modificador']}")
                print(f"      - Prioridad: {regla['prioridad']}")
                print(f"      - Activa: {regla['activa']}")
                
                # Mostrar condición
                try:
                    condicion = json.loads(regla['condicion'])
                    if regla['tipo_regla'] == 'dia_semana':
                        dias = condicion.get('dias', [])
                        dias_nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
                        dias_texto = [dias_nombres[d] for d in dias if 0 <= d < 7]
                        print(f"      - Aplica: {', '.join(dias_texto)}")
                    elif regla['tipo_regla'] == 'hora':
                        print(f"      - Horario: {condicion.get('hora_inicio', 'N/A')} - {condicion.get('hora_fin', 'N/A')}")
                    elif regla['tipo_regla'] == 'anticipacion':
                        print(f"      - Días mínimos: {condicion.get('dias_minimos', 'N/A')}")
                except Exception as e:
                    print(f"      - Condición: {regla['condicion']} (Error: {e})")
                    
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Simulando Frontend para Identificar Problemas")
    print("=" * 70)
    
    verificar_reglas_activas()
    simular_frontend_calculo()
    
    print("\n" + "=" * 70)
    print("✅ Simulación completada")
    print("\n🔍 Si las reglas se aplican en este script pero no en el frontend:")
    print("   1. Verifica la consola del navegador para errores JavaScript")
    print("   2. Verifica que el elemento 'calculationResult' exista en el HTML")
    print("   3. Verifica que la función displayCalculationResult se ejecute")
    print("   4. Verifica que las reglas se muestren en el HTML generado")

if __name__ == "__main__":
    main()
