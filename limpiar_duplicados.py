#!/usr/bin/env python3
"""
Script para limpiar servicios y recursos duplicados de la base de datos
"""

import requests
import json
from datetime import datetime

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
            return resources
        else:
            print(f"❌ Error obteniendo recursos: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def delete_service(service_id):
    """Eliminar un servicio por ID"""
    try:
        response = requests.delete(f"{API_BASE_URL}/servicios/{service_id}")
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error eliminando servicio {service_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def delete_resource(resource_id):
    """Eliminar un recurso por ID"""
    try:
        response = requests.delete(f"{API_BASE_URL}/recursos/{resource_id}")
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error eliminando recurso {resource_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def clean_duplicate_services():
    """Limpiar servicios duplicados"""
    print("\n🧹 Limpiando servicios duplicados...")
    
    services = get_services()
    if not services:
        print("❌ No se pueden obtener servicios")
        return False
    
    # Agrupar por nombre
    services_by_name = {}
    for service in services:
        name = service['nombre']
        if name not in services_by_name:
            services_by_name[name] = []
        services_by_name[name].append(service)
    
    # Identificar duplicados
    duplicates_to_remove = []
    for name, service_list in services_by_name.items():
        if len(service_list) > 1:
            print(f"🔍 Servicio duplicado encontrado: '{name}' ({len(service_list)} instancias)")
            
            # Mantener el primero (más antiguo) y eliminar los demás
            for i, service in enumerate(service_list[1:], 1):
                print(f"   • Eliminando instancia {i+1}: ID {service['id']}")
                duplicates_to_remove.append(service['id'])
    
    if not duplicates_to_remove:
        print("✅ No hay servicios duplicados para eliminar")
        return True
    
    # Eliminar duplicados
    print(f"\n🗑️ Eliminando {len(duplicates_to_remove)} servicios duplicados...")
    deleted_count = 0
    
    for service_id in duplicates_to_remove:
        if delete_service(service_id):
            deleted_count += 1
            print(f"   ✅ Servicio {service_id} eliminado")
        else:
            print(f"   ❌ Error eliminando servicio {service_id}")
    
    print(f"✅ {deleted_count} servicios duplicados eliminados")
    return True

def clean_duplicate_resources():
    """Limpiar recursos duplicados"""
    print("\n🧹 Limpiando recursos duplicados...")
    
    resources = get_resources()
    if not resources:
        print("❌ No se pueden obtener recursos")
        return False
    
    # Agrupar por nombre
    resources_by_name = {}
    for resource in resources:
        name = resource['nombre']
        if name not in resources_by_name:
            resources_by_name[name] = []
        resources_by_name[name].append(resource)
    
    # Identificar duplicados
    duplicates_to_remove = []
    for name, resource_list in resources_by_name.items():
        if len(resource_list) > 1:
            print(f"🔍 Recurso duplicado encontrado: '{name}' ({len(resource_list)} instancias)")
            
            # Mantener el primero (más antiguo) y eliminar los demás
            for i, resource in enumerate(resource_list[1:], 1):
                print(f"   • Eliminando instancia {i+1}: ID {resource['id']}")
                duplicates_to_remove.append(resource['id'])
    
    if not duplicates_to_remove:
        print("✅ No hay recursos duplicados para eliminar")
        return True
    
    # Eliminar duplicados
    print(f"\n🗑️ Eliminando {len(duplicates_to_remove)} recursos duplicados...")
    deleted_count = 0
    
    for resource_id in duplicates_to_remove:
        if delete_resource(resource_id):
            deleted_count += 1
            print(f"   ✅ Recurso {resource_id} eliminado")
        else:
            print(f"   ❌ Error eliminando recurso {resource_id}")
    
    print(f"✅ {deleted_count} recursos duplicados eliminados")
    return True

def verify_cleanup():
    """Verificar que la limpieza fue exitosa"""
    print("\n🔍 Verificando limpieza...")
    
    services = get_services()
    resources = get_resources()
    
    if not services or not resources:
        print("❌ No se pueden obtener datos para verificación")
        return False
    
    # Verificar servicios
    service_names = [s['nombre'] for s in services]
    service_duplicates = [name for name in set(service_names) if service_names.count(name) > 1]
    
    if service_duplicates:
        print(f"❌ Aún hay servicios duplicados: {service_duplicates}")
        return False
    else:
        print("✅ No hay servicios duplicados")
    
    # Verificar recursos
    resource_names = [r['nombre'] for r in resources]
    resource_duplicates = [name for name in set(resource_names) if resource_names.count(name) > 1]
    
    if resource_duplicates:
        print(f"❌ Aún hay recursos duplicados: {resource_duplicates}")
        return False
    else:
        print("✅ No hay recursos duplicados")
    
    print(f"📊 Resumen final:")
    print(f"   • Servicios únicos: {len(services)}")
    print(f"   • Recursos únicos: {len(resources)}")
    
    return True

def main():
    """Función principal"""
    print("🚀 Limpiando Duplicados de la Base de Datos")
    print("=" * 70)
    
    # Verificar que la API esté funcionando
    if not test_health():
        print("\n❌ No se puede continuar sin conexión a la API")
        return
    
    # Obtener estado inicial
    print("\n📊 Estado inicial:")
    initial_services = get_services()
    initial_resources = get_resources()
    
    if initial_services:
        print(f"   • Servicios: {len(initial_services)}")
    if initial_resources:
        print(f"   • Recursos: {len(initial_resources)}")
    
    # Limpiar duplicados
    services_cleaned = clean_duplicate_services()
    resources_cleaned = clean_duplicate_resources()
    
    # Verificar limpieza
    if services_cleaned and resources_cleaned:
        cleanup_successful = verify_cleanup()
        
        if cleanup_successful:
            print("\n🎉 Limpieza completada exitosamente!")
            print("   Los selectores del frontend ya no deberían mostrar duplicados")
        else:
            print("\n⚠️ La limpieza no fue completamente exitosa")
            print("   Revisa los errores anteriores")
    else:
        print("\n❌ Error durante la limpieza")
        print("   Revisa los errores anteriores")

if __name__ == "__main__":
    main()
