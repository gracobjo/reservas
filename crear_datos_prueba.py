#!/usr/bin/env python3
"""
Script para crear datos de prueba en el sistema de reservas
Crea servicios, recursos y reglas básicas para probar el cliente web
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"

def crear_servicio(nombre, descripcion, duracion_minutos, precio_base):
    """Crear un servicio en el sistema"""
    url = f"{API_BASE_URL}/servicios/"
    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "duracion_minutos": duracion_minutos,
        "precio_base": precio_base
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            servicio = response.json()
            print(f"✅ Servicio creado: {servicio['nombre']} - €{servicio['precio_base']}")
            return servicio
        else:
            print(f"❌ Error creando servicio {nombre}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def crear_recurso(nombre, tipo, disponible=True):
    """Crear un recurso en el sistema"""
    url = f"{API_BASE_URL}/recursos/"
    data = {
        "nombre": nombre,
        "tipo": tipo,
        "disponible": disponible
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            recurso = response.json()
            print(f"✅ Recurso creado: {recurso['nombre']} ({recurso['tipo']})")
            return recurso
        else:
            print(f"❌ Error creando recurso {nombre}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def crear_regla_hora_pico(nombre, hora_inicio, hora_fin, porcentaje_recargo, dias_semana):
    """Crear una regla de recargo por hora pico"""
    url = f"{API_BASE_URL}/precios-dinamicos/reglas-rapidas/hora-pico"
    data = {
        "tipo": "hora_pico",
        "nombre": nombre,
        "configuracion": {
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "porcentaje_recargo": porcentaje_recargo,
            "dias_semana": dias_semana
        }
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            regla = response.json()
            print(f"✅ Regla creada: {regla['nombre']} (+{porcentaje_recargo}%)")
            return regla
        else:
            print(f"❌ Error creando regla {nombre}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def crear_regla_descuento_anticipacion(nombre, dias_minimos, porcentaje_descuento):
    """Crear una regla de descuento por anticipación"""
    url = f"{API_BASE_URL}/precios-dinamicos/reglas-rapidas/descuento-anticipacion"
    data = {
        "tipo": "descuento_anticipacion",
        "nombre": nombre,
        "configuracion": {
            "dias_minimos": dias_minimos,
            "porcentaje_descuento": porcentaje_descuento
        }
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            regla = response.json()
            print(f"✅ Regla creada: {regla['nombre']} (-{porcentaje_descuento}%)")
            return regla
        else:
            print(f"❌ Error creando regla {nombre}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def crear_regla_fin_de_semana(nombre, porcentaje_recargo):
    """Crear una regla de recargo por fin de semana"""
    url = f"{API_BASE_URL}/precios-dinamicos/reglas-rapidas/fin-de-semana"
    data = {
        "tipo": "fin_de_semana",
        "nombre": nombre,
        "configuracion": {
            "porcentaje_recargo": porcentaje_recargo,
            "prioridad": 15
        }
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            regla = response.json()
            print(f"✅ Regla creada: {regla['nombre']} (+{porcentaje_recargo}%)")
            return regla
        else:
            print(f"❌ Error creando regla {nombre}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    """Función principal para crear todos los datos de prueba"""
    print("🚀 Creando datos de prueba para el sistema de reservas...")
    print("=" * 60)
    
    # Verificar conexión
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ La API no está respondiendo. Asegúrate de que esté ejecutándose en http://localhost:8000")
            return
        print("✅ API conectada correctamente")
    except Exception as e:
        print(f"❌ No se puede conectar a la API: {e}")
        return
    
    print("\n📋 Creando servicios...")
    servicios = []
    
    # Crear servicios
    servicios.append(crear_servicio("Consulta Médica", "Consulta médica general", 45, 50.0))
    servicios.append(crear_servicio("Terapia Física", "Sesión de fisioterapia", 60, 80.0))
    servicios.append(crear_servicio("Masaje Relajante", "Masaje de 30 minutos", 30, 40.0))
    servicios.append(crear_servicio("Clase de Yoga", "Clase grupal de yoga", 90, 25.0))
    servicios.append(crear_servicio("Entrenamiento Personal", "Sesión individual de entrenamiento", 60, 60.0))
    
    # Nuevo servicio de alquiler de habitación
    servicios.append(crear_servicio("Alquiler Habitación Individual", "Habitación individual por noche", 1440, 80.0))  # 24 horas = 1440 minutos
    servicios.append(crear_servicio("Alquiler Habitación Doble", "Habitación doble por noche", 1440, 120.0))  # 24 horas = 1440 minutos
    
    print("\n🏢 Creando recursos...")
    recursos = []
    
    # Crear recursos
    recursos.append(crear_recurso("Consultorio 1", "consultorio"))
    recursos.append(crear_recurso("Consultorio 2", "consultorio"))
    recursos.append(crear_recurso("Sala de Terapia", "sala"))
    recursos.append(crear_recurso("Spa", "spa"))
    recursos.append(crear_recurso("Gimnasio", "gimnasio"))
    recursos.append(crear_recurso("Sala de Yoga", "sala"))
    
    # Nuevos recursos de habitaciones
    recursos.append(crear_recurso("Habitación 101 - Individual", "habitacion_individual"))
    recursos.append(crear_recurso("Habitación 102 - Individual", "habitacion_individual"))
    recursos.append(crear_recurso("Habitación 201 - Doble", "habitacion_doble"))
    recursos.append(crear_recurso("Habitación 202 - Doble", "habitacion_doble"))
    recursos.append(crear_recurso("Suite 301 - Doble Premium", "habitacion_doble"))
    
    print("\n⚡ Creando reglas de precio...")
    
    # Regla de hora pico (mañana)
    crear_regla_hora_pico(
        "Hora Pico Mañana",
        "08:00",
        "12:00",
        20.0,
        [0, 1, 2, 3, 4]  # Lunes a Viernes
    )
    
    # Regla de hora pico (tarde)
    crear_regla_hora_pico(
        "Hora Pico Tarde",
        "17:00",
        "20:00",
        25.0,
        [0, 1, 2, 3, 4]  # Lunes a Viernes
    )
    
    # Regla de descuento por anticipación
    crear_regla_descuento_anticipacion(
        "Descuento Reserva Anticipada",
        7,  # 7 días mínimo
        15.0  # 15% de descuento
    )
    
    # Regla de descuento por anticipación (larga)
    crear_regla_descuento_anticipacion(
        "Descuento Reserva Muy Anticipada",
        30,  # 30 días mínimo
        25.0  # 25% de descuento
    )
    
    # Regla de recargo por fin de semana (para habitaciones)
    crear_regla_fin_de_semana(
        "Recargo Fin de Semana",
        30.0  # 30% de recargo
    )
    
    print("\n" + "=" * 60)
    print("🎉 Datos de prueba creados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • Servicios creados: {len([s for s in servicios if s])}")
    print(f"   • Recursos creados: {len([r for r in recursos if r])}")
    print(f"   • Reglas de precio: 5")
    
    print("\n🌐 Ahora puedes:")
    print("   1. Ir a http://localhost:8000/cliente-web")
    print("   2. Usar la calculadora con los servicios y recursos creados")
    print("   3. Ver las reglas de precio en el dashboard")
    print("   4. Probar la simulación semanal")
    
    print("\n💡 Ejemplo de uso:")
    print("   • Servicio: Alquiler Habitación Individual")
    print("   • Recurso: Habitación 101 - Individual")
    print("   • Fecha: Sábado (aplicará recargo fin de semana +30%)")
    print("   • Duración: 2 noches (48 horas)")
    print("   • Precio base: €80/noche")
    print("   • Precio final: €208 (con recargo fin de semana)")

if __name__ == "__main__":
    main()
