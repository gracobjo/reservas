#!/usr/bin/env python3
"""
Script para verificar qué reglas existen en la base de datos
y específicamente buscar reglas de "Hora Pico Mañana"
"""

import requests
import json
from datetime import datetime

def verificar_reglas():
    print("🔍 Verificando Reglas en la Base de Datos")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    try:
        # Obtener todas las reglas
        print("📋 Obteniendo reglas de la base de datos...")
        response = requests.get(f"{BASE_URL}/precios-dinamicos/reglas")
        
        if response.status_code == 200:
            reglas = response.json()
            print(f"✅ Total de reglas encontradas: {len(reglas)}")
            
            # Mostrar todas las reglas
            print(f"\n📋 Lista completa de reglas:")
            for i, regla in enumerate(reglas):
                print(f"\n  Regla {i+1}:")
                print(f"    ID: {regla.get('id', 'N/A')}")
                print(f"    Nombre: {regla.get('nombre', 'N/A')}")
                print(f"    Tipo: {regla.get('tipo_regla', 'N/A')}")
                print(f"    Tipo Modificador: {regla.get('tipo_modificador', 'N/A')}")
                print(f"    Valor: {regla.get('valor_modificador', 'N/A')}")
                print(f"    Activa: {regla.get('activa', 'N/A')}")
                print(f"    Prioridad: {regla.get('prioridad', 'N/A')}")
                if regla.get('condicion'):
                    print(f"    Condición: {regla.get('condicion', 'N/A')}")
            
            # Buscar específicamente reglas de "Hora Pico Mañana"
            print(f"\n🔍 Buscando reglas de 'Hora Pico Mañana'...")
            reglas_hora_pico = [r for r in reglas if 'mañana' in r.get('nombre', '').lower() or 'hora pico' in r.get('nombre', '').lower()]
            
            if reglas_hora_pico:
                print(f"✅ Reglas de 'Hora Pico Mañana' encontradas:")
                for regla in reglas_hora_pico:
                    print(f"   - {regla['nombre']}: {regla['tipo_regla']} - {regla['valor_modificador']}")
            else:
                print(f"❌ No se encontraron reglas de 'Hora Pico Mañana'")
            
            # Buscar reglas de tipo 'hora'
            print(f"\n🔍 Buscando reglas de tipo 'hora'...")
            reglas_hora = [r for r in reglas if r.get('tipo_regla') == 'hora']
            
            if reglas_hora:
                print(f"✅ Reglas de tipo 'hora' encontradas:")
                for regla in reglas_hora:
                    print(f"   - {regla['nombre']}: {regla['valor_modificador']}")
            else:
                print(f"❌ No se encontraron reglas de tipo 'hora'")
            
            # Buscar reglas de anticipación
            print(f"\n🔍 Buscando reglas de anticipación...")
            reglas_anticipacion = [r for r in reglas if r.get('tipo_regla') == 'anticipacion']
            
            if reglas_anticipacion:
                print(f"✅ Reglas de anticipación encontradas:")
                for regla in reglas_anticipacion:
                    print(f"   - {regla['nombre']}: {regla['valor_modificador']}")
            else:
                print(f"❌ No se encontraron reglas de anticipación")
                
        else:
            print(f"❌ Error obteniendo reglas: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    print("🚀 Verificación de Reglas")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        verificar_reglas()
        
        print("\n" + "=" * 60)
        print("🏁 Verificación Completada")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error general en la verificación: {e}")
