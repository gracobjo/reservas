#!/usr/bin/env python3
"""
Test específico para el cálculo de 192 horas (8 días) 
que no está mostrando descuentos de anticipación en el frontend
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_calculo_192_horas():
    """Test específico para 192 horas (8 días)"""
    
    print("🔍 Test específico para 192 horas (8 días)")
    print("=" * 50)
    
    # Calcular fechas para 192 horas (8 días)
    fecha_inicio = datetime.now() + timedelta(days=1)
    fecha_fin = fecha_inicio + timedelta(hours=192)
    
    # Datos del test (simulando el frontend)
    payload = {
        "servicio_id": 12,  # Alquiler Habitación Individual
        "recurso_id": 15,   # Habitación Individual 1
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": 1,
        "tipo_cliente": "regular"
    }
    
    print(f"📤 Enviando payload:")
    print(f"   - Servicio ID: {payload['servicio_id']}")
    print(f"   - Recurso ID: {payload['recurso_id']}")
    print(f"   - Fecha inicio: {payload['fecha_hora_inicio']}")
    print(f"   - Fecha fin: {payload['fecha_hora_fin']}")
    print(f"   - Duración: 192 horas (8 días)")
    print(f"   - Participantes: {payload['participantes']}")
    print(f"   - Tipo cliente: {payload['tipo_cliente']}")
    print()
    
    try:
        # Llamar a la API
        response = requests.post(
            f"{API_BASE_URL}/precios-dinamicos/calcular",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Respuesta de la API:")
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   - Precio base: {result.get('precio_base', 'N/A')}€")
            print(f"   - Precio final: {result.get('precio_final', 'N/A')}€")
            print(f"   - Diferencia: {result.get('precio_final', 0) - result.get('precio_base', 0):.2f}€")
            
            # Analizar reglas aplicadas
            reglas_aplicadas = result.get('reglas_aplicadas', [])
            print(f"   - Total reglas aplicadas: {len(reglas_aplicadas)}")
            
            if reglas_aplicadas:
                print("\n🔍 Reglas aplicadas:")
                for i, regla in enumerate(reglas_aplicadas, 1):
                    print(f"   {i}. {regla.get('nombre', 'Sin nombre')}")
                    print(f"      - Tipo: {regla.get('tipo_regla', 'N/A')}")
                    print(f"      - Modificador: {regla.get('tipo_modificador', 'N/A')}")
                    print(f"      - Valor: {regla.get('valor_modificador', 'N/A')}")
                    print(f"      - Descuento: {regla.get('descuento', 0):.2f}€")
                    print(f"      - Recargo: {regla.get('recargo', 0):.2f}€")
                    print()
                
                # Verificar específicamente descuentos de anticipación
                reglas_anticipacion = [r for r in reglas_aplicadas if r.get('tipo_regla') == 'anticipacion']
                if reglas_anticipacion:
                    print("✅ ¡DESCUENTOS DE ANTICIPACIÓN ENCONTRADOS!")
                    for regla in reglas_anticipacion:
                        print(f"   - {regla.get('nombre')}: {regla.get('descuento', 0):.2f}€")
                else:
                    print("❌ NO se encontraron descuentos de anticipación")
                    
                # Verificar reglas de hora pico
                reglas_hora_pico = [r for r in reglas_aplicadas if r.get('tipo_regla') == 'hora']
                if reglas_hora_pico:
                    print("✅ ¡REGLAS DE HORA PICO ENCONTRADAS!")
                    for regla in reglas_hora_pico:
                        print(f"   - {regla.get('nombre')}: {regla.get('recargo', 0):.2f}€")
            else:
                print("❌ No se aplicaron reglas")
                
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en el test: {e}")

def verificar_reglas_anticipacion():
    """Verificar que las reglas de anticipación existen y están activas"""
    
    print("\n🔍 Verificando reglas de anticipación en la base de datos")
    print("=" * 50)
    
    try:
        # Obtener todas las reglas
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas")
        
        if response.status_code == 200:
            reglas = response.json()
            
            # Filtrar reglas de anticipación
            reglas_anticipacion = [r for r in reglas if r.get('tipo_regla') == 'anticipacion']
            
            if reglas_anticipacion:
                print(f"✅ Se encontraron {len(reglas_anticipacion)} reglas de anticipación:")
                for regla in reglas_anticipacion:
                    print(f"   - {regla.get('nombre')}")
                    print(f"     * Activa: {regla.get('activa', False)}")
                    print(f"     * Tipo: {regla.get('tipo_regla')}")
                    print(f"     * Modificador: {regla.get('tipo_modificador')}")
                    print(f"     * Valor: {regla.get('valor_modificador')}")
                    print(f"     * Prioridad: {regla.get('prioridad')}")
                    print()
            else:
                print("❌ No se encontraron reglas de anticipación")
                
            # Mostrar todas las reglas para debug
            print("📋 Todas las reglas disponibles:")
            for regla in reglas:
                print(f"   - {regla.get('nombre')} ({regla.get('tipo_regla')}) - Activa: {regla.get('activa')}")
                
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando reglas: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando test de descuento por anticipación para 192 horas")
    print()
    
    # Verificar reglas primero
    verificar_reglas_anticipacion()
    
    # Test específico
    test_calculo_192_horas()
    
    print("\n✅ Test completado")
