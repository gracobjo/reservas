#!/usr/bin/env python3
"""
Verificar en detalle las reglas de anticipación para entender por qué no se aplican
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def verificar_reglas_anticipacion_detalle():
    """Verificar en detalle las reglas de anticipación"""
    
    print("🔍 Verificando reglas de anticipación en detalle")
    print("=" * 60)
    
    try:
        # Obtener todas las reglas
        response = requests.get(f"{API_BASE_URL}/precios-dinamicos/reglas")
        
        if response.status_code == 200:
            reglas = response.json()
            
            # Filtrar reglas de anticipación
            reglas_anticipacion = [r for r in reglas if r.get('tipo_regla') == 'anticipacion']
            
            if reglas_anticipacion:
                print(f"✅ Se encontraron {len(reglas_anticipacion)} reglas de anticipación:")
                print()
                
                for i, regla in enumerate(reglas_anticipacion, 1):
                    print(f"📋 Regla {i}: {regla.get('nombre')}")
                    print(f"   - ID: {regla.get('id')}")
                    print(f"   - Activa: {regla.get('activa')}")
                    print(f"   - Tipo: {regla.get('tipo_regla')}")
                    print(f"   - Modificador: {regla.get('tipo_modificador')}")
                    print(f"   - Valor: {regla.get('valor_modificador')}")
                    print(f"   - Prioridad: {regla.get('prioridad')}")
                    
                    # Analizar la condición
                    condicion = regla.get('condicion')
                    if condicion:
                        try:
                            condicion_parsed = json.loads(condicion)
                            print(f"   - Condición (JSON): {condicion_parsed}")
                            
                            # Verificar campos específicos
                            if 'dias_minimos' in condicion_parsed:
                                print(f"   - Días mínimos: {condicion_parsed['dias_minimos']}")
                            else:
                                print(f"   - ⚠️ NO tiene campo 'dias_minimos'")
                                
                        except json.JSONDecodeError:
                            print(f"   - ❌ Condición no es JSON válido: {condicion}")
                    else:
                        print(f"   - ❌ NO tiene condición")
                    
                    print()
            else:
                print("❌ No se encontraron reglas de anticipación")
                
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando reglas: {e}")

def test_calculo_con_fechas_especificas():
    """Test con fechas específicas para entender el cálculo de anticipación"""
    
    print("\n🔍 Test con fechas específicas para anticipación")
    print("=" * 60)
    
    # Fecha actual
    ahora = datetime.now()
    print(f"📅 Fecha actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calcular diferentes escenarios
    escenarios = [
        ("Mañana (1 día)", 1),
        ("En 3 días", 3),
        ("En 7 días", 7),
        ("En 8 días", 8),
        ("En 14 días", 14),
        ("En 30 días", 30)
    ]
    
    for descripcion, dias in escenarios:
        fecha_inicio = ahora + timedelta(days=dias)
        fecha_fin = fecha_inicio + timedelta(hours=192)  # 8 días
        
        dias_anticipacion = (fecha_inicio.date() - ahora.date()).days
        
        print(f"\n📋 {descripcion}:")
        print(f"   - Fecha inicio: {fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Fecha fin: {fecha_fin.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Días de anticipación: {dias_anticipacion}")
        print(f"   - Duración: 192 horas (8 días)")
        
        # Verificar si se cumplirían las reglas de anticipación
        if dias_anticipacion >= 7:
            print(f"   - ✅ Cumple regla de 7+ días")
        else:
            print(f"   - ❌ NO cumple regla de 7+ días")
            
        if dias_anticipacion >= 14:
            print(f"   - ✅ Cumple regla de 14+ días")
        else:
            print(f"   - ❌ NO cumple regla de 14+ días")

def test_api_con_fecha_especifica():
    """Test de la API con una fecha específica que debería aplicar anticipación"""
    
    print("\n🔍 Test de API con fecha específica (30 días de anticipación)")
    print("=" * 60)
    
    # Fecha de inicio: 30 días desde ahora
    fecha_inicio = datetime.now() + timedelta(days=30)
    fecha_fin = fecha_inicio + timedelta(hours=192)  # 8 días
    
    print(f"📅 Fecha inicio: {fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Fecha fin: {fecha_fin.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Días de anticipación: {(fecha_inicio.date() - datetime.now().date()).days}")
    
    payload = {
        "servicio_id": 12,  # Alquiler Habitación Individual
        "recurso_id": 15,   # Habitación Individual 1
        "fecha_hora_inicio": fecha_inicio.isoformat(),
        "fecha_hora_fin": fecha_fin.isoformat(),
        "participantes": 1,
        "tipo_cliente": "regular"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/precios-dinamicos/calcular",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Respuesta de la API:")
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
            else:
                print("❌ No se aplicaron reglas")
                
        else:
            print(f"❌ Error en la API: {response.status_code}")
            print(f"   - Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en el test: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando verificación detallada de reglas de anticipación")
    print()
    
    # Verificar reglas en detalle
    verificar_reglas_anticipacion_detalle()
    
    # Test con fechas específicas
    test_calculo_con_fechas_especificas()
    
    # Test de API con fecha específica
    test_api_con_fecha_especifica()
    
    print("\n✅ Verificación completada")
