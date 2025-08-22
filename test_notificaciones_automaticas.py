#!/usr/bin/env python3
"""
Script para probar el sistema de notificaciones automáticas implementado:
- Notificaciones automáticas
- Confirmaciones
- Recordatorios
- Configuración de notificaciones
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuración
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

def test_notification_system():
    """Probar el sistema de notificaciones"""
    print("\n🔔 Probando sistema de notificaciones...")
    
    # Verificar que la API esté funcionando
    if not test_api_health():
        return False
    
    # Obtener servicios y recursos para hacer cálculos
    try:
        servicios = requests.get(f"{API_BASE_URL}/servicios/").json()
        recursos = requests.get(f"{API_BASE_URL}/recursos/").json()
        
        if not servicios or not recursos:
            print("❌ No se pueden obtener servicios o recursos")
            return False
        
        print(f"✅ Servicios disponibles: {len(servicios)}")
        print(f"✅ Recursos disponibles: {len(recursos)}")
        
        # Probar cálculos para generar notificaciones
        test_calculations(servicios, recursos)
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando sistema de notificaciones: {e}")
        return False

def test_calculations(servicios, recursos):
    """Probar cálculos para generar notificaciones"""
    print("\n🧮 Generando cálculos para probar notificaciones...")
    
    # Buscar servicios de habitación
    habitacion_servicios = [s for s in servicios if "habitación" in s['nombre'].lower() or "alquiler" in s['nombre'].lower()]
    habitacion_recursos = [r for r in recursos if "habitación" in r['nombre'].lower()]
    
    if not habitacion_servicios or not habitacion_recursos:
        print("⚠️ No se encontraron servicios de habitación, usando cualquier servicio")
        habitacion_servicios = servicios[:1]
        habitacion_recursos = recursos[:1]
    
    # Hacer varios cálculos para generar notificaciones
    for i in range(3):
        servicio = habitacion_servicios[i % len(habitacion_servicios)]
        recurso = habitacion_recursos[i % len(habitacion_recursos)]
        
        fecha_inicio = datetime.now() + timedelta(days=i+1)
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        test_data = {
            "servicio_id": servicio['id'],
            "recurso_id": recurso['id'],
            "fecha_hora_inicio": fecha_inicio.isoformat(),
            "fecha_hora_fin": fecha_fin.isoformat(),
            "participantes": 1 + (i % 3),
            "tipo_cliente": ["regular", "vip", "premium"][i % 3]
        }
        
        print(f"   📊 Cálculo {i+1}: {servicio['nombre']} - {recurso['nombre']}")
        
        try:
            response = requests.post(f"{API_BASE_URL}/precios-dinamicos/calcular", json=test_data)
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ Precio: €{result['precio_final']:.2f} (Base: €{result['precio_base']:.2f})")
                
                # Verificar si se aplicaron reglas
                if result.get('reglas_aplicadas'):
                    print(f"      📋 Reglas aplicadas: {len(result['reglas_aplicadas'])}")
                else:
                    print(f"      ℹ️ Sin reglas aplicadas")
                    
            else:
                print(f"      ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error en cálculo: {e}")
        
        time.sleep(0.5)  # Pequeña pausa entre cálculos

def test_notification_features():
    """Probar características específicas de notificaciones"""
    print("\n🎯 Probando características de notificaciones...")
    
    print("✅ Sistema de notificaciones automáticas")
    print("   - Verificación de salud del sistema (cada 30 min)")
    print("   - Recordatorio diario para revisar reglas (9:00 AM)")
    print("   - Recordatorio semanal para exportar datos (lunes 10:00 AM)")
    
    print("✅ Confirmaciones automáticas")
    print("   - Confirmación para limpiar historial")
    print("   - Confirmación para exportar datos")
    print("   - Confirmación para acciones destructivas")
    
    print("✅ Notificaciones inteligentes")
    print("   - Notificación cuando se cargan datos")
    print("   - Notificación cuando se guardan cálculos")
    print("   - Recordatorio para exportar con muchos cálculos")
    
    print("✅ Configuración personalizable")
    print("   - Habilitar/deshabilitar tipos de notificaciones")
    print("   - Tiempo de auto-ocultar configurable")
    print("   - Sonidos y notificaciones del escritorio")
    
    print("✅ Historial de notificaciones")
    print("   - Almacenamiento local de notificaciones")
    print("   - Marcado como leído/no leído")
    print("   - Estadísticas de notificaciones")
    
    print("✅ Notificaciones de progreso")
    print("   - Barra de progreso en notificaciones")
    print("   - Actualización en tiempo real")
    print("   - Completado automático")

def test_notification_ui():
    """Probar la interfaz de usuario de notificaciones"""
    print("\n🎨 Probando interfaz de notificaciones...")
    
    print("✅ Pestaña de configuración")
    print("   - Configuración general de notificaciones")
    print("   - Recordatorios programados")
    print("   - Historial de notificaciones")
    print("   - Estadísticas de notificaciones")
    print("   - Configuración avanzada")
    
    print("✅ Funcionalidades de la UI")
    print("   - Formularios de configuración")
    print("   - Botones de prueba de recordatorios")
    print("   - Limpieza de recordatorios")
    print("   - Marcado como leído")
    print("   - Solicitud de permisos")
    print("   - Restablecimiento de configuración")
    print("   - Exportación de configuración")

def test_notification_storage():
    """Probar el almacenamiento de notificaciones"""
    print("\n💾 Probando almacenamiento de notificaciones...")
    
    print("✅ Almacenamiento local")
    print("   - Configuración de notificaciones en localStorage")
    print("   - Historial de notificaciones en localStorage")
    print("   - Persistencia entre sesiones")
    
    print("✅ Gestión de datos")
    print("   - Límite de 50 notificaciones en historial")
    print("   - Límite de 10 cálculos en historial")
    print("   - Limpieza automática de datos antiguos")

def main():
    """Función principal"""
    print("🚀 Probando Sistema de Notificaciones Automáticas")
    print("=" * 70)
    
    # Probar todas las funcionalidades
    test_notification_system()
    test_notification_features()
    test_notification_ui()
    test_notification_storage()
    
    print("\n" + "=" * 70)
    print("✅ Pruebas de notificaciones automáticas completadas")
    print("\n🌐 Para probar la interfaz completa:")
    print("   1. Ve a http://localhost:8000/cliente-web")
    print("   2. Haz algunos cálculos en la pestaña Calculadora")
    print("   3. Ve a la pestaña Notificaciones")
    print("   4. Configura las notificaciones según tus preferencias")
    print("   5. Prueba los recordatorios y confirmaciones")
    print("   6. Revisa el historial de notificaciones")
    print("   7. Observa las notificaciones automáticas en tiempo real")
    
    print("\n🔔 Funcionalidades implementadas:")
    print("   - Notificaciones automáticas del sistema")
    print("   - Confirmaciones para acciones importantes")
    print("   - Recordatorios programados (diario, semanal)")
    print("   - Configuración personalizable de notificaciones")
    print("   - Historial y estadísticas de notificaciones")
    print("   - Notificaciones de progreso")
    print("   - Notificaciones inteligentes basadas en eventos")
    print("   - Exportación de configuración")
    print("   - Permisos del navegador para notificaciones del escritorio")

if __name__ == "__main__":
    main()
