#!/usr/bin/env python3
"""
Script para probar la calculadora del frontend y verificar que las reglas se muestren
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

def test_calculadora_frontend():
    """Probar la calculadora del frontend"""
    print("🧮 Probando Calculadora del Frontend")
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
        
        print(f"✅ Servicio: {habitacion_servicio['nombre']}")
        print(f"✅ Recurso: {habitacion_recurso['nombre']}")
        
        # Probar cálculo para fin de semana (sábado)
        fecha_base = datetime.now() + timedelta(days=1)
        while fecha_base.weekday() != 5:  # 5 = Sábado
            fecha_base += timedelta(days=1)
        
        fecha_inicio = fecha_base.replace(hour=14, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)  # 1 noche
        
        test_data = {
            "servicio_id": habitacion_servicio['id'],
            "recurso_id": habitacion_recurso['id'],
            "fecha_hora_inicio": fecha_inicio.isoformat(),
            "fecha_hora_fin": fecha_fin.isoformat(),
            "participantes": 2,
            "tipo_cliente": "vip"
        }
        
        print(f"\n📅 Probando para: {fecha_inicio.strftime('%A %d/%m/%Y')} (Sábado)")
        print(f"   ⏰ Hora: {fecha_inicio.strftime('%H:%M')}")
        print(f"   🌙 Duración: 1 noche")
        print(f"   👥 Participantes: 2")
        print(f"   👤 Tipo Cliente: VIP")
        
        try:
            response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
            if response.status_code == 200:
                result = response.json()
                precio_base = result['precio_base']
                precio_final = result['precio_final']
                reglas_aplicadas = result['reglas_aplicadas']
                
                print(f"\n💰 Resultado del cálculo:")
                print(f"   • Precio base: €{precio_base:.2f}")
                print(f"   • Precio final: €{precio_final:.2f}")
                print(f"   • Diferencia: €{precio_final - precio_base:.2f}")
                
                if reglas_aplicadas:
                    print(f"\n📋 Reglas aplicadas ({len(reglas_aplicadas)}):")
                    for regla in reglas_aplicadas:
                        print(f"   • {regla['nombre']}")
                        print(f"     - Tipo: {regla['tipo_regla']}")
                        print(f"     - Modificador: {regla['tipo_modificador']} {regla['valor_modificador']}")
                        if regla['tipo_modificador'] == 'porcentaje':
                            print(f"     - Efecto: {regla['valor_modificador']:+.1f}%")
                        else:
                            print(f"     - Efecto: {regla['valor_modificador']:+.2f}€")
                else:
                    print(f"\nℹ️ Sin reglas aplicadas")
                
                # Verificar que se aplicó la regla de fin de semana
                if precio_final > precio_base:
                    print(f"\n✅ Se aplicó al menos una regla (precio aumentó)")
                else:
                    print(f"\n❌ No se aplicó ninguna regla (precio no cambió)")
                
            else:
                print(f"❌ Error en cálculo: {response.status_code}")
                print(f"   📝 Datos enviados: {test_data}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error obteniendo servicios/recursos: {e}")

def test_reglas_disponibles():
    """Verificar qué reglas están disponibles"""
    print("\n📋 Verificando reglas disponibles...")
    try:
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas")
        if response.status_code == 200:
            reglas = response.json()
            print(f"✅ Total de reglas: {len(reglas)}")
            
            for regla in reglas:
                print(f"\n   📌 {regla['nombre']}")
                print(f"      - Tipo: {regla['tipo_regla']}")
                print(f"      - Modificador: {regla['tipo_modificador']} {regla['valor_modificador']}")
                print(f"      - Prioridad: {regla['prioridad']}")
                print(f"      - Activa: {'✅' if regla['activa'] else '❌'}")
                
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
                except:
                    print(f"      - Condición: {regla['condicion']}")
                    
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Probando Calculadora del Frontend")
    print("=" * 60)
    
    test_reglas_disponibles()
    test_calculadora_frontend()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("\n🌐 Para probar manualmente:")
    print("   1. Ve a http://localhost:8000/cliente-web")
    print("   2. En la calculadora, selecciona:")
    print("      • Servicio: Alquiler Habitación Individual")
    print("      • Recurso: Habitación 101 - Individual")
    print("      • Fecha: Sábado o domingo")
    print("      • Hora: 14:00")
    print("      • Duración: 1 noche")
    print("      • Participantes: 2")
    print("      • Tipo Cliente: VIP")
    print("   3. Haz clic en 'Calcular Precio'")
    print("   4. Verifica que se muestren las reglas aplicadas")

if __name__ == "__main__":
    main()
