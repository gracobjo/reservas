#!/usr/bin/env python3
"""
Script para verificar si hay duplicados en los selectores del frontend
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

def check_for_duplicates():
    """Verificar si hay duplicados en los datos"""
    print("\n🔍 Verificando duplicados en los datos...")
    
    services = get_services()
    resources = get_resources()
    
    if not services or not resources:
        print("❌ No se pueden obtener los datos necesarios")
        return False
    
    # Verificar duplicados en servicios
    service_names = [s['nombre'] for s in services]
    service_duplicates = [name for name in set(service_names) if service_names.count(name) > 1]
    
    if service_duplicates:
        print(f"❌ Servicios duplicados encontrados: {service_duplicates}")
        return False
    else:
        print("✅ No hay servicios duplicados")
    
    # Verificar duplicados en recursos
    resource_names = [r['nombre'] for r in resources]
    resource_duplicates = [name for name in set(resource_names) if resource_names.count(name) > 1]
    
    if resource_duplicates:
        print(f"❌ Recursos duplicados encontrados: {resource_duplicates}")
        return False
    else:
        print("✅ No hay recursos duplicados")
    
    # Verificar IDs duplicados
    service_ids = [s['id'] for s in services]
    resource_ids = [r['id'] for r in resources]
    
    if len(service_ids) != len(set(service_ids)):
        print("❌ IDs de servicios duplicados encontrados")
        return False
    else:
        print("✅ No hay IDs de servicios duplicados")
    
    if len(resource_ids) != len(set(resource_ids)):
        print("❌ IDs de recursos duplicados encontrados")
        return False
    else:
        print("✅ No hay IDs de recursos duplicados")
    
    return True

def test_frontend_data():
    """Probar si el frontend recibe datos correctos"""
    print("\n🧪 Probando datos del frontend...")
    
    services = get_services()
    resources = get_resources()
    
    if not services or not resources:
        print("❌ No se pueden obtener los datos necesarios")
        return False
    
    # Simular lo que hace el frontend
    print(f"📊 Datos que recibiría el frontend:")
    print(f"   • Servicios: {len(services)}")
    print(f"   • Recursos: {len(resources)}")
    
    # Mostrar algunos ejemplos
    print(f"\n📋 Ejemplos de servicios:")
    for i, service in enumerate(services[:3]):
        print(f"   {i+1}. {service['nombre']} - €{service['precio_base']:.2f}")
    
    print(f"\n📋 Ejemplos de recursos:")
    for i, resource in enumerate(resources[:3]):
        print(f"   {i+1}. {resource['nombre']} ({resource['tipo']})")
    
    return True

def main():
    """Función principal"""
    print("🚀 Verificando Duplicados en Selectores del Frontend")
    print("=" * 70)
    
    # Verificar que la API esté funcionando
    if not test_health():
        print("\n❌ No se puede continuar sin conexión a la API")
        return
    
    # Verificar duplicados
    duplicates_ok = check_for_duplicates()
    
    # Probar datos del frontend
    frontend_ok = test_frontend_data()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    
    if duplicates_ok:
        print("✅ Verificación de duplicados: PASÓ")
    else:
        print("❌ Verificación de duplicados: FALLÓ")
    
    if frontend_ok:
        print("✅ Datos del frontend: PASÓ")
    else:
        print("❌ Datos del frontend: FALLÓ")
    
    if duplicates_ok and frontend_ok:
        print("\n🎉 Todas las verificaciones pasaron correctamente!")
        print("   Los datos están limpios y no hay duplicados")
        print("\n💡 Si sigues viendo duplicados en el frontend:")
        print("   1. Abre la consola del navegador (F12)")
        print("   2. Recarga la página")
        print("   3. Busca los logs que empiecen con 🔍")
        print("   4. Verifica si populateSelectors se ejecuta múltiples veces")
    else:
        print("\n⚠️ Algunas verificaciones fallaron")
        print("   Revisa los datos en la base de datos")

if __name__ == "__main__":
    main()
