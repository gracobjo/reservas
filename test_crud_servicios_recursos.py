#!/usr/bin/env python3
"""
Script para testear el CRUD de servicios y recursos
"""

import requests
import json
from datetime import datetime

def test_crud_servicios():
    print("🔍 Test CRUD de Servicios")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Crear servicio
    print("\n📝 Test 1: Crear Servicio")
    print("-" * 30)
    
    new_service = {
        "nombre": "Servicio de Test",
        "descripcion": "Servicio creado para testing",
        "precio_base": 50.00,
        "categoria": "actividades"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/servicios/", json=new_service)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            created_service = response.json()
            print(f"✅ Servicio creado: ID {created_service['id']}")
            service_id = created_service['id']
        else:
            print(f"❌ Error creando servicio: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Obtener servicio por ID
    print("\n📖 Test 2: Obtener Servicio por ID")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/servicios/{service_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            service = response.json()
            print(f"✅ Servicio obtenido: {service['nombre']} - €{service['precio_base']}")
        else:
            print(f"❌ Error obteniendo servicio: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Actualizar servicio
    print("\n✏️ Test 3: Actualizar Servicio")
    print("-" * 30)
    
    updated_service = {
        "nombre": "Servicio de Test Actualizado",
        "descripcion": "Servicio actualizado para testing",
        "precio_base": 75.00,
        "categoria": "actividades"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/servicios/{service_id}", json=updated_service)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ Servicio actualizado: {updated['nombre']} - €{updated['precio_base']}")
        else:
            print(f"❌ Error actualizando servicio: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Obtener todos los servicios
    print("\n📋 Test 4: Obtener Todos los Servicios")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/servicios/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Total servicios: {len(services)}")
            for service in services[:3]:  # Mostrar solo los primeros 3
                print(f"   • {service['nombre']} - €{service['precio_base']}")
        else:
            print(f"❌ Error obteniendo servicios: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Eliminar servicio
    print("\n🗑️ Test 5: Eliminar Servicio")
    print("-" * 30)
    
    try:
        response = requests.delete(f"{BASE_URL}/servicios/{service_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Servicio eliminado correctamente")
        else:
            print(f"❌ Error eliminando servicio: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_crud_recursos():
    print("\n\n🔍 Test CRUD de Recursos")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # Test 1: Crear recurso
    print("\n📝 Test 1: Crear Recurso")
    print("-" * 30)
    
    new_resource = {
        "nombre": "Recurso de Test",
        "tipo": "equipamiento",
        "capacidad": 5,
        "descripcion": "Recurso creado para testing",
        "disponible": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/recursos/", json=new_resource)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            created_resource = response.json()
            print(f"✅ Recurso creado: ID {created_resource['id']}")
            resource_id = created_resource['id']
        else:
            print(f"❌ Error creando recurso: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: Obtener recurso por ID
    print("\n📖 Test 2: Obtener Recurso por ID")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/recursos/{resource_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            resource = response.json()
            print(f"✅ Recurso obtenido: {resource['nombre']} - {resource['tipo']}")
        else:
            print(f"❌ Error obteniendo recurso: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Actualizar recurso
    print("\n✏️ Test 3: Actualizar Recurso")
    print("-" * 30)
    
    updated_resource = {
        "nombre": "Recurso de Test Actualizado",
        "tipo": "sala",
        "capacidad": 10,
        "descripcion": "Recurso actualizado para testing",
        "disponible": True
    }
    
    try:
        response = requests.put(f"{BASE_URL}/recursos/{resource_id}", json=updated_resource)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            updated = response.json()
            print(f"✅ Recurso actualizado: {updated['nombre']} - {updated['tipo']}")
        else:
            print(f"❌ Error actualizando recurso: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Cambiar disponibilidad
    print("\n🔄 Test 4: Cambiar Disponibilidad")
    print("-" * 30)
    
    try:
        response = requests.put(f"{BASE_URL}/recursos/{resource_id}/toggle-disponibilidad")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            toggled = response.json()
            print(f"✅ Disponibilidad cambiada: {toggled['disponible']}")
        else:
            print(f"❌ Error cambiando disponibilidad: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Obtener todos los recursos
    print("\n📋 Test 5: Obtener Todos los Recursos")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/recursos/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            resources = response.json()
            print(f"✅ Total recursos: {len(resources)}")
            for resource in resources[:3]:  # Mostrar solo los primeros 3
                print(f"   • {resource['nombre']} - {resource['tipo']} - {'✅' if resource['disponible'] else '❌'}")
        else:
            print(f"❌ Error obteniendo recursos: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Eliminar recurso
    print("\n🗑️ Test 6: Eliminar Recurso")
    print("-" * 30)
    
    try:
        response = requests.delete(f"{BASE_URL}/recursos/{resource_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Recurso eliminado correctamente")
        else:
            print(f"❌ Error eliminando recurso: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Test CRUD de Servicios y Recursos")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # Test servicios
        test_crud_servicios()
        
        # Test recursos
        test_crud_recursos()
        
        print("\n" + "=" * 60)
        print("🏁 Test CRUD Completado")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en el test: {e}")
