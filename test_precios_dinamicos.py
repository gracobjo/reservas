#!/usr/bin/env python3
"""
Script completo de prueba para el sistema de precios dinámicos
"""

import requests
import json
from datetime import datetime, timedelta

# URL base de la API
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprimir título de sección"""
    print(f"\n{'='*60}")
    print(f"🔥 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Imprimir mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprimir mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprimir información"""
    print(f"ℹ️  {message}")

def test_crear_recurso_servicio():
    """Crear recurso y servicio para las pruebas"""
    print_section("CONFIGURACIÓN INICIAL")
    
    # Crear recurso
    recurso_data = {
        "nombre": "Sala de Yoga Premium",
        "tipo": "sala",
        "disponible": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/recursos", json=recurso_data)
        if response.status_code == 200:
            recurso = response.json()
            print_success(f"Recurso creado: {recurso['nombre']} (ID: {recurso['id']})")
            recurso_id = recurso['id']
        else:
            print_error(f"Error creando recurso: {response.text}")
            return None, None
    except Exception as e:
        print_error(f"Error: {e}")
        return None, None
    
    # Crear servicio
    servicio_data = {
        "nombre": "Clase de Yoga Personalizada",
        "descripcion": "Clase de yoga uno a uno con instructor certificado",
        "duracion_minutos": 60,
        "precio_base": 50.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/servicios", json=servicio_data)
        if response.status_code == 200:
            servicio = response.json()
            print_success(f"Servicio creado: {servicio['nombre']} (ID: {servicio['id']}) - Precio base: ${servicio['precio_base']}")
            return recurso_id, servicio['id']
        else:
            print_error(f"Error creando servicio: {response.text}")
            return None, None
    except Exception as e:
        print_error(f"Error: {e}")
        return None, None

def test_crear_regla_hora_pico(recurso_id, servicio_id):
    """Crear regla de hora pico"""
    print_section("CREANDO REGLA DE HORA PICO")
    
    url = f"{BASE_URL}/precios-dinamicos/reglas-rapidas/hora-pico"
    params = {
        "nombre": "Hora Pico Tarde",
        "hora_inicio": "17:00",
        "hora_fin": "20:00",
        "porcentaje_recargo": 25.0,
        "dias_lunes": True,
        "dias_martes": True,
        "dias_miercoles": True,
        "dias_jueves": True,
        "dias_viernes": True
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            regla = response.json()
            print_success(f"Regla de hora pico creada: {regla['nombre']}")
            print_info(f"   Recargo: +{regla['valor_modificador']}%")
            print_info(f"   Horario: 17:00-20:00 (Lunes a Viernes)")
            return regla['id']
        else:
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_crear_regla_descuento_anticipacion():
    """Crear regla de descuento por anticipación"""
    print_section("CREANDO REGLA DE DESCUENTO POR ANTICIPACIÓN")
    
    url = f"{BASE_URL}/precios-dinamicos/reglas-rapidas/descuento-anticipacion"
    params = {
        "nombre": "Descuento Reserva Anticipada",
        "dias_minimos": 7,
        "porcentaje_descuento": 15.0
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            regla = response.json()
            print_success(f"Regla de descuento creada: {regla['nombre']}")
            print_info(f"   Descuento: {abs(regla['valor_modificador'])}%")
            print_info(f"   Mínimo: 7 días de anticipación")
            return regla['id']
        else:
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_crear_regla_temporada_alta():
    """Crear regla de temporada alta"""
    print_section("CREANDO REGLA DE TEMPORADA ALTA")
    
    # Temporada alta: próximas 2 semanas
    fecha_inicio = datetime.now().date().strftime("%Y-%m-%d")
    fecha_fin = (datetime.now().date() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/precios-dinamicos/reglas-rapidas/temporada-alta"
    params = {
        "nombre": "Temporada Alta Verano",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "porcentaje_recargo": 30.0
    }
    
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            regla = response.json()
            print_success(f"Regla de temporada alta creada: {regla['nombre']}")
            print_info(f"   Recargo: +{regla['valor_modificador']}%")
            print_info(f"   Período: {fecha_inicio} a {fecha_fin}")
            return regla['id']
        else:
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_calcular_precio_escenarios(recurso_id, servicio_id):
    """Probar diferentes escenarios de cálculo de precio"""
    print_section("PROBANDO CÁLCULO DE PRECIOS EN DIFERENTES ESCENARIOS")
    
    # Escenario 1: Horario normal, sin reglas especiales
    print("\n🧪 Escenario 1: Horario normal (10:00 AM)")
    fecha_normal = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    test_calcular_precio_individual(
        servicio_id, recurso_id, fecha_normal, 
        "Horario normal", "Sin reglas especiales aplicables"
    )
    
    # Escenario 2: Hora pico + anticipación
    print("\n🧪 Escenario 2: Hora pico con anticipación (18:00 PM en 8 días)")
    fecha_pico_anticipacion = (datetime.now() + timedelta(days=8)).replace(hour=18, minute=0, second=0, microsecond=0)
    test_calcular_precio_individual(
        servicio_id, recurso_id, fecha_pico_anticipacion,
        "Hora pico + Anticipación", "Recargo de hora pico + descuento por anticipación"
    )
    
    # Escenario 3: Solo hora pico (sin anticipación)
    print("\n🧪 Escenario 3: Solo hora pico (18:00 PM mañana)")
    fecha_pico = (datetime.now() + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
    test_calcular_precio_individual(
        servicio_id, recurso_id, fecha_pico,
        "Solo hora pico", "Solo recargo de hora pico"
    )
    
    # Escenario 4: Fin de semana (sin reglas)
    print("\n🧪 Escenario 4: Fin de semana (Sábado 14:00)")
    # Encontrar el próximo sábado
    fecha_base = datetime.now() + timedelta(days=1)
    while fecha_base.weekday() != 5:  # 5 = Sábado
        fecha_base += timedelta(days=1)
    fecha_weekend = fecha_base.replace(hour=14, minute=0, second=0, microsecond=0)
    test_calcular_precio_individual(
        servicio_id, recurso_id, fecha_weekend,
        "Fin de semana", "Sábado - reglas de días laborales no aplican"
    )

def test_calcular_precio_individual(servicio_id, recurso_id, fecha_inicio, nombre_escenario, descripcion):
    """Calcular precio para un escenario específico"""
    fecha_fin = fecha_inicio + timedelta(hours=1)
    
    request_data = {
        "servicio_id": servicio_id,
        "recurso_id": recurso_id,
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": 1,
        "tipo_cliente": "regular"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/precios-dinamicos/calcular", json=request_data)
        if response.status_code == 200:
            calculo = response.json()
            
            print_info(f"Fecha/Hora: {fecha_inicio.strftime('%Y-%m-%d %H:%M')}")
            print_info(f"Descripción: {descripcion}")
            print(f"   💰 Precio base: ${calculo['precio_base']:.2f}")
            print(f"   💸 Precio final: ${calculo['precio_final']:.2f}")
            
            if calculo['descuento_total'] > 0:
                print(f"   🎯 Descuento total: -${calculo['descuento_total']:.2f}")
            
            if calculo['recargo_total'] > 0:
                print(f"   📈 Recargo total: +${calculo['recargo_total']:.2f}")
                
            if calculo['ahorro_total'] > 0:
                print(f"   💡 Ahorro total: ${calculo['ahorro_total']:.2f}")
            
            print(f"   📋 Reglas aplicadas: {len(calculo['reglas_aplicadas'])}")
            
            for regla in calculo['reglas_aplicadas']:
                simbolo = "🎯" if regla['descuento'] > 0 else "📈"
                valor = f"-${regla['descuento']:.2f}" if regla['descuento'] > 0 else f"+${regla['recargo']:.2f}"
                print(f"      {simbolo} {regla['nombre']}: {valor}")
            
            return calculo
        else:
            print_error(f"Error calculando precio: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_simulacion_semanal(servicio_id, recurso_id):
    """Probar simulación de precios para una semana"""
    print_section("SIMULACIÓN DE PRECIOS SEMANAL")
    
    fecha_inicio = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = f"{BASE_URL}/precios-dinamicos/simular/{servicio_id}"
    params = {
        "recurso_id": recurso_id,
        "fecha_inicio": fecha_inicio,
        "hora_servicio": "18:00",  # Hora pico
        "duracion_horas": 1,
        "participantes": 1
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            simulacion = response.json()
            print_success("Simulación semanal completada")
            print_info(f"Semana del: {fecha_inicio}")
            print_info("Hora del servicio: 18:00 (hora pico)")
            
            print("\n📊 Resultados por día:")
            for dia, resultado in simulacion['simulacion_semanal'].items():
                if 'error' not in resultado:
                    precio_base = resultado['precio_base']
                    precio_final = resultado['precio_final']
                    diferencia = precio_final - precio_base
                    simbolo = "📈" if diferencia > 0 else "🎯" if diferencia < 0 else "💰"
                    
                    print(f"   {simbolo} {dia:9} ({resultado['fecha']}): ${precio_base:.2f} → ${precio_final:.2f}")
                    if diferencia != 0:
                        print(f"             Diferencia: {'+' if diferencia > 0 else ''}${diferencia:.2f} ({len(resultado.get('reglas_aplicadas', 0))} reglas)")
            
            return simulacion
        else:
            print_error(f"Error en simulación: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_estadisticas_reglas():
    """Obtener estadísticas de las reglas"""
    print_section("ESTADÍSTICAS DE REGLAS")
    
    try:
        response = requests.get(f"{BASE_URL}/precios-dinamicos/estadisticas/reglas")
        if response.status_code == 200:
            stats = response.json()
            print_success("Estadísticas obtenidas")
            print(f"   📊 Total de reglas: {stats['total_reglas']}")
            print(f"   ✅ Reglas activas: {stats['reglas_activas']}")
            print(f"   ❌ Reglas inactivas: {stats['reglas_inactivas']}")
            
            print("\n📈 Por tipo de regla:")
            for tipo, cantidad in stats['por_tipo'].items():
                print(f"   {tipo}: {cantidad}")
            
            print("\n💰 Por tipo de modificador:")
            for modificador, cantidad in stats['por_modificador'].items():
                print(f"   {modificador}: {cantidad}")
            
            return stats
        else:
            print_error(f"Error obteniendo estadísticas: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_listar_reglas():
    """Listar todas las reglas creadas"""
    print_section("LISTADO DE REGLAS CREADAS")
    
    try:
        response = requests.get(f"{BASE_URL}/precios-dinamicos/reglas")
        if response.status_code == 200:
            reglas = response.json()
            print_success(f"Se encontraron {len(reglas)} reglas")
            
            for regla in reglas:
                estado = "🟢 ACTIVA" if regla['activa'] else "🔴 INACTIVA"
                print(f"\n   📋 {regla['nombre']} (ID: {regla['id']}) - {estado}")
                print(f"      Tipo: {regla['tipo_regla']}")
                print(f"      Modificador: {regla['tipo_modificador']} ({regla['valor_modificador']})")
                print(f"      Prioridad: {regla['prioridad']}")
                if regla['descripcion']:
                    print(f"      Descripción: {regla['descripcion']}")
            
            return reglas
        else:
            print_error(f"Error listando reglas: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA DE PRECIOS DINÁMICOS")
    print("=" * 80)
    
    try:
        # 1. Configuración inicial
        recurso_id, servicio_id = test_crear_recurso_servicio()
        if not recurso_id or not servicio_id:
            print_error("No se pudo completar la configuración inicial")
            return
        
        # 2. Crear reglas de precio
        regla_hora_pico = test_crear_regla_hora_pico(recurso_id, servicio_id)
        regla_anticipacion = test_crear_regla_descuento_anticipacion()
        regla_temporada = test_crear_regla_temporada_alta()
        
        # 3. Probar cálculos de precio
        test_calcular_precio_escenarios(recurso_id, servicio_id)
        
        # 4. Simulación semanal
        test_simulacion_semanal(servicio_id, recurso_id)
        
        # 5. Listar reglas creadas
        test_listar_reglas()
        
        # 6. Estadísticas
        test_estadisticas_reglas()
        
        print_section("RESUMEN FINAL")
        print_success("✨ ¡Todas las pruebas del sistema de precios dinámicos completadas!")
        print_info("📚 Revisa la documentación completa en: http://localhost:8000/docs")
        print_info("🔍 Endpoints principales de precios dinámicos:")
        print("   - POST /precios-dinamicos/reglas - Crear regla personalizada")
        print("   - POST /precios-dinamicos/calcular - Calcular precio dinámico")
        print("   - GET  /precios-dinamicos/simular/{servicio_id} - Simular precios")
        print("   - POST /precios-dinamicos/reglas-rapidas/* - Crear reglas predefinidas")
        
    except KeyboardInterrupt:
        print_error("\nPruebas interrumpidas por el usuario")
    except Exception as e:
        print_error(f"Error durante las pruebas: {e}")

if __name__ == "__main__":
    main()
