#!/usr/bin/env python3
"""
Script de prueba para validar la lógica de habitaciones individuales vs dobles
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
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Servicios encontrados: {len(services)}")
            return services
        else:
            print(f"❌ Error obteniendo servicios: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_resources():
    """Obtener lista de recursos"""
    try:
        response = requests.get(f"{API_BASE_URL}/recursos/")
        if response.status_code == 200:
            resources = response.json()
            print(f"✅ Recursos encontrados: {len(resources)}")
            return resources
        else:
            print(f"❌ Error obteniendo recursos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_individual_room_validation():
    """Probar validación de habitación individual con 2 personas"""
    print("\n🧪 Probando validación de habitación individual con 2 personas")
    
    # Buscar habitación individual
    services = get_services()
    resources = get_resources()
    
    individual_service = None
    individual_resource = None
    
    for service in services:
        if 'individual' in service['nombre'].lower():
            individual_service = service
            break
    
    for resource in resources:
        if 'individual' in resource['nombre'].lower():
            individual_resource = resource
            break
    
    if not individual_service or not individual_resource:
        print("❌ No se encontraron habitaciones individuales para probar")
        return False
    
    print(f"✅ Habitación individual encontrada:")
    print(f"   Servicio: {individual_service['nombre']}")
    print(f"   Recurso: {individual_resource['nombre']}")
    
    # Probar cálculo con 2 personas (debería fallar)
    tomorrow = datetime.now() + timedelta(days=1)
    fecha_hora_inicio = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=24)
    
    test_data = {
        "servicio_id": individual_service['id'],
        "recurso_id": individual_resource['id'],
        "fecha_hora_inicio": fecha_hora_inicio.isoformat(),
        "fecha_hora_fin": fecha_hora_fin.isoformat(),
        "participantes": 2,  # ❌ Esto debería fallar
        "tipo_cliente": "regular"
    }
    
    print(f"\n📤 Enviando datos de prueba (2 personas en habitación individual):")
    print(f"   • Servicio ID: {test_data['servicio_id']}")
    print(f"   • Recurso ID: {test_data['recurso_id']}")
    print(f"   • Participantes: {test_data['participantes']}")
    print(f"   • Fecha: {fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/precios-dinamicos/calcular",
            json=test_data
        )
        
        if response.status_code == 422:
            print("✅ Validación funcionando: API rechazó la solicitud (422)")
            print("   Esto significa que el backend está validando correctamente")
            return True
        elif response.status_code == 200:
            print("❌ Validación fallando: API aceptó la solicitud (200)")
            print("   El backend debería rechazar habitaciones individuales con 2 personas")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def test_double_room_validation():
    """Probar validación de habitación doble con 2 personas (debería funcionar)"""
    print("\n🧪 Probando validación de habitación doble con 2 personas")
    
    services = get_services()
    resources = get_resources()
    
    double_service = None
    double_resource = None
    
    for service in services:
        if 'doble' in service['nombre'].lower():
            double_service = service
            break
    
    for resource in resources:
        if 'doble' in resource['nombre'].lower():
            double_resource = resource
            break
    
    if not double_service or not double_resource:
        print("❌ No se encontraron habitaciones dobles para probar")
        return False
    
    print(f"✅ Habitación doble encontrada:")
    print(f"   Servicio: {double_service['nombre']}")
    print(f"   Recurso: {double_resource['nombre']}")
    
    # Probar cálculo con 2 personas (debería funcionar)
    tomorrow = datetime.now() + timedelta(days=1)
    fecha_hora_inicio = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    fecha_hora_fin = fecha_hora_inicio + timedelta(hours=24)
    
    test_data = {
        "servicio_id": double_service['id'],
        "recurso_id": double_resource['id'],
        "fecha_hora_inicio": fecha_hora_inicio.isoformat(),
        "fecha_hora_fin": fecha_hora_fin.isoformat(),
        "participantes": 2,  # ✅ Esto debería funcionar
        "tipo_cliente": "regular"
    }
    
    print(f"\n📤 Enviando datos de prueba (2 personas en habitación doble):")
    print(f"   • Servicio ID: {test_data['servicio_id']}")
    print(f"   • Recurso ID: {test_data['recurso_id']}")
    print(f"   • Participantes: {test_data['participantes']}")
    print(f"   • Fecha: {fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/precios-dinamicos/calcular",
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Validación funcionando: API aceptó la solicitud (200)")
            print(f"   • Precio base: €{result.get('precio_base', 0):.2f}")
            print(f"   • Precio final: €{result.get('precio_final', 0):.2f}")
            print(f"   • Reglas aplicadas: {len(result.get('reglas_aplicadas', []))}")
            return True
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando Validación de Habitaciones Individuales vs Dobles")
    print("=" * 70)
    
    # Verificar que la API esté funcionando
    if not test_health():
        print("\n❌ No se puede continuar sin conexión a la API")
        return
    
    # Obtener datos necesarios
    services = get_services()
    resources = get_resources()
    
    if not services or not resources:
        print("\n❌ No se pueden obtener los datos necesarios")
        return
    
    # Probar validaciones
    test1_passed = test_individual_room_validation()
    test2_passed = test_double_room_validation()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    if test1_passed:
        print("✅ Test 1: Validación habitación individual con 2 personas - PASÓ")
    else:
        print("❌ Test 1: Validación habitación individual con 2 personas - FALLÓ")
    
    if test2_passed:
        print("✅ Test 2: Validación habitación doble con 2 personas - PASÓ")
    else:
        print("❌ Test 2: Validación habitación doble con 2 personas - FALLÓ")
    
    if test1_passed and test2_passed:
        print("\n🎉 Todas las pruebas pasaron correctamente!")
        print("   El sistema está validando correctamente las habitaciones")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("   Revisa la implementación de las validaciones")
    
    print("\n💡 Nota: Estas pruebas verifican el backend.")
    print("   Para probar el frontend, ve a la calculadora web y:")
    print("   1. Selecciona 'Alquiler Habitación Individual'")
    print("   2. Intenta seleccionar 2 participantes")
    print("   3. Deberías ver un mensaje de error")

if __name__ == "__main__":
    main()
