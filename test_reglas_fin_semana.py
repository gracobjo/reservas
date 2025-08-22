#!/usr/bin/env python3
"""
Script para probar que las reglas de fin de semana se apliquen correctamente
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

def test_api_health():
    """Probar la salud de la API"""
    print("🏥 Probando salud de la API...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API saludable: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ API no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a la API: {e}")
        return False

def test_reglas_existentes():
    """Verificar que las reglas existen"""
    print("\n📋 Verificando reglas existentes...")
    try:
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas")
        if response.status_code == 200:
            reglas = response.json()
            print(f"✅ Reglas encontradas: {len(reglas)}")
            for regla in reglas:
                print(f"   • {regla['nombre']} - Tipo: {regla['tipo_regla']} - Modificador: {regla['valor_modificador']}%")
            return reglas
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_calculo_fin_semana():
    """Probar cálculo para fin de semana"""
    print("\n🏠 Probando cálculo para fin de semana...")
    
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
        
        print(f"✅ Usando servicio: {habitacion_servicio['nombre']}")
        print(f"✅ Usando recurso: {habitacion_recurso['nombre']}")
        
        # Probar diferentes fechas
        fechas_prueba = [
            ("Lunes (día laboral)", datetime.now() + timedelta(days=1)),  # Próximo lunes
            ("Sábado (fin de semana)", datetime.now() + timedelta(days=5)),  # Próximo sábado
            ("Domingo (fin de semana)", datetime.now() + timedelta(days=6)),  # Próximo domingo
        ]
        
        for nombre_fecha, fecha_base in fechas_prueba:
            # Ajustar para que sea lunes, sábado o domingo
            while fecha_base.weekday() not in [0, 5, 6]:  # 0=Lunes, 5=Sábado, 6=Domingo
                fecha_base += timedelta(days=1)
            
            fecha_inicio = fecha_base.replace(hour=14, minute=0, second=0, microsecond=0)
            fecha_fin = fecha_inicio + timedelta(days=1)  # 1 noche
            
            test_data = {
                "servicio_id": habitacion_servicio['id'],
                "recurso_id": habitacion_recurso['id'],
                "fecha_hora_inicio": fecha_inicio.isoformat(),
                "fecha_hora_fin": fecha_fin.isoformat(),
                "participantes": 2,
                "tipo_cliente": "regular"
            }
            
            print(f"\n   📅 {nombre_fecha}: {fecha_inicio.strftime('%A %d/%m/%Y')}")
            
            try:
                response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
                if response.status_code == 200:
                    result = response.json()
                    precio_base = result['precio_base']
                    precio_final = result['precio_final']
                    reglas_aplicadas = result['reglas_aplicadas']
                    
                    print(f"      💰 Precio base: €{precio_base:.2f}")
                    print(f"      💰 Precio final: €{precio_final:.2f}")
                    
                    if reglas_aplicadas:
                        print(f"      📋 Reglas aplicadas: {len(reglas_aplicadas)}")
                        for regla in reglas_aplicadas:
                            print(f"         • {regla['nombre']}: {regla['tipo_modificador']} {regla['valor_modificador']}%")
                    else:
                        print(f"      ℹ️ Sin reglas aplicadas")
                    
                    # Verificar si se aplicó la regla de fin de semana
                    if fecha_base.weekday() in [5, 6]:  # Sábado o domingo
                        if precio_final > precio_base:
                            print(f"      ✅ Regla de fin de semana aplicada correctamente")
                        else:
                            print(f"      ❌ Regla de fin de semana NO se aplicó")
                    else:
                        if precio_final == precio_base:
                            print(f"      ✅ Sin recargo en día laboral (correcto)")
                        else:
                            print(f"      ⚠️ Se aplicó recargo en día laboral (incorrecto)")
                            
                else:
                    print(f"      ❌ Error en cálculo: {response.status_code}")
                    print(f"      📝 Datos enviados: {test_data}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error obteniendo servicios/recursos: {e}")

def main():
    """Función principal"""
    print("🚀 Probando Reglas de Fin de Semana")
    print("=" * 50)
    
    if not test_api_health():
        return
    
    reglas = test_reglas_existentes()
    if not reglas:
        print("❌ No hay reglas para probar")
        return
    
    test_calculo_fin_semana()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
    print("\n🌐 Para probar manualmente:")
    print("   1. Ve a http://localhost:8000/cliente-web")
    print("   2. En la calculadora, selecciona un servicio de habitación")
    print("   3. Selecciona un recurso de habitación")
    print("   4. Elige una fecha de sábado o domingo")
    print("   5. Verifica que se aplique el recargo de fin de semana")

if __name__ == "__main__":
    main()
