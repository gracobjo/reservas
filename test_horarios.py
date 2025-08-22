#!/usr/bin/env python3
"""
Script de prueba para el sistema de horarios
"""

import requests
import json
from datetime import datetime, time, timedelta

# URL base de la API
BASE_URL = "http://localhost:8000"

def test_crear_recurso():
    """Crear un recurso de prueba"""
    print("🔧 Creando recurso de prueba...")
    
    recurso_data = {
        "nombre": "Consultorio Principal",
        "tipo": "consultorio",
        "disponible": True
    }
    
    response = requests.post(f"{BASE_URL}/recursos", json=recurso_data)
    if response.status_code == 200:
        recurso = response.json()
        print(f"✅ Recurso creado: {recurso['nombre']} (ID: {recurso['id']})")
        return recurso['id']
    else:
        print(f"❌ Error creando recurso: {response.text}")
        return None

def test_crear_servicio():
    """Crear un servicio de prueba"""
    print("🛠️ Creando servicio de prueba...")
    
    servicio_data = {
        "nombre": "Consulta Médica",
        "descripcion": "Consulta médica general",
        "duracion_minutos": 45,
        "precio_base": 50.0
    }
    
    response = requests.post(f"{BASE_URL}/servicios", json=servicio_data)
    if response.status_code == 200:
        servicio = response.json()
        print(f"✅ Servicio creado: {servicio['nombre']} (ID: {servicio['id']})")
        return servicio['id']
    else:
        print(f"❌ Error creando servicio: {response.text}")
        return None

def test_crear_horarios(recurso_id):
    """Crear horarios para el recurso"""
    print("🕒 Creando horarios...")
    
    # Horarios para la semana laboral (Lunes a Viernes)
    horarios_data = {
        "recurso_id": recurso_id,
        "horarios": [
            {
                "recurso_id": recurso_id,
                "dia_semana": 0,  # Lunes
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "duracion_slot_minutos": 45,
                "pausa_entre_slots": 15
            },
            {
                "recurso_id": recurso_id,
                "dia_semana": 1,  # Martes
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "duracion_slot_minutos": 45,
                "pausa_entre_slots": 15
            },
            {
                "recurso_id": recurso_id,
                "dia_semana": 2,  # Miércoles
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "duracion_slot_minutos": 45,
                "pausa_entre_slots": 15
            },
            {
                "recurso_id": recurso_id,
                "dia_semana": 3,  # Jueves
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "duracion_slot_minutos": 45,
                "pausa_entre_slots": 15
            },
            {
                "recurso_id": recurso_id,
                "dia_semana": 4,  # Viernes
                "hora_inicio": "09:00",
                "hora_fin": "17:00",
                "duracion_slot_minutos": 45,
                "pausa_entre_slots": 15
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/horarios/bulk", json=horarios_data)
    if response.status_code == 200:
        horarios = response.json()
        print(f"✅ {len(horarios)} horarios creados")
        return True
    else:
        print(f"❌ Error creando horarios: {response.text}")
        return False

def test_ver_horarios_semana(recurso_id):
    """Ver horarios de la semana"""
    print("📅 Verificando horarios de la semana...")
    
    response = requests.get(f"{BASE_URL}/horarios/semana/{recurso_id}")
    if response.status_code == 200:
        horarios_semana = response.json()
        print("✅ Horarios de la semana:")
        for dia, horarios in horarios_semana["horarios_semana"].items():
            if horarios:
                print(f"   {dia}: {len(horarios)} horario(s)")
                for h in horarios:
                    print(f"     - {h['hora_inicio']} a {h['hora_fin']} (slots de {h['duracion_slot_minutos']} min)")
        return True
    else:
        print(f"❌ Error obteniendo horarios: {response.text}")
        return False

def test_disponibilidad(recurso_id, servicio_id):
    """Probar el endpoint de disponibilidad"""
    print("🔍 Probando disponibilidad...")
    
    # Fecha de mañana
    tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    fecha = tomorrow.strftime("%Y-%m-%d")
    
    response = requests.get(f"{BASE_URL}/horarios/disponibilidad/{recurso_id}?fecha={fecha}&servicio_id={servicio_id}")
    if response.status_code == 200:
        disponibilidad = response.json()
        print(f"✅ Disponibilidad para {fecha}:")
        print(f"   Recurso: {disponibilidad['recurso_nombre']}")
        print(f"   Total slots: {disponibilidad['total_slots']}")
        print(f"   Slots disponibles: {disponibilidad['slots_disponibles_count']}")
        
        # Mostrar algunos slots
        for i, slot in enumerate(disponibilidad['slots_disponibles'][:5]):
            estado = "✅" if slot['disponible'] else "❌"
            print(f"   {estado} {slot['inicio']} - {slot['fin']}")
            if not slot['disponible']:
                print(f"      Motivo: {slot['motivo_no_disponible']}")
        
        return True
    else:
        print(f"❌ Error obteniendo disponibilidad: {response.text}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA DE HORARIOS")
    print("=" * 50)
    
    try:
        # Crear recurso
        recurso_id = test_crear_recurso()
        if not recurso_id:
            return
        
        # Crear servicio
        servicio_id = test_crear_servicio()
        if not servicio_id:
            return
        
        # Crear horarios
        if not test_crear_horarios(recurso_id):
            return
        
        # Ver horarios de la semana
        if not test_ver_horarios_semana(recurso_id):
            return
        
        # Probar disponibilidad
        if not test_disponibilidad(recurso_id, servicio_id):
            return
        
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("=" * 50)
        print("📚 Puedes ver la documentación completa en: http://localhost:8000/docs")
        print("🔍 Endpoints de horarios disponibles:")
        print("   - POST /horarios/ - Crear horario")
        print("   - POST /horarios/bulk - Crear múltiples horarios")
        print("   - GET /horarios/recurso/{id} - Ver horarios de un recurso")
        print("   - GET /horarios/semana/{id} - Ver horario semanal")
        print("   - GET /horarios/disponibilidad/{id} - Ver disponibilidad")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")

if __name__ == "__main__":
    main()
