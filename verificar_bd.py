#!/usr/bin/env python3
"""
Script de verificación automática de la base de datos
Verifica la estructura y datos después de la implementación del campo precio_base
"""

import sqlite3
import os
from datetime import datetime

def verificar_base_datos():
    """Verificar estructura y datos de la base de datos"""
    
    print("🔍 VERIFICACIÓN AUTOMÁTICA DE BASE DE DATOS")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db_path = "data/reservas.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en {db_path}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ Base de datos conectada exitosamente")
        print()
        
        # 1. Verificar tablas
        print("📋 VERIFICANDO TABLAS...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"   Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table}")
        print()
        
        # 2. Verificar estructura de recursos
        if 'recursos' in tables:
            print("🏢 VERIFICANDO TABLA 'RECURSOS'...")
            cursor.execute("PRAGMA table_info(recursos)")
            columns = cursor.fetchall()
            
            print(f"   Total columnas: {len(columns)}")
            print("   Estructura de columnas:")
            
            # Verificar campos nuevos
            campos_nuevos = ['precio_base', 'capacidad', 'descripcion']
            campos_encontrados = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                col_default = col[4]
                col_notnull = "NOT NULL" if col[3] else "NULL"
                
                print(f"   - {col_name}: {col_type} (Default: {col_default}) [{col_notnull}]")
                
                if col_name in campos_nuevos:
                    campos_encontrados.append(col_name)
            
            print()
            print("✅ CAMPOS NUEVOS VERIFICADOS:")
            for campo in campos_nuevos:
                if campo in campos_encontrados:
                    print(f"   ✅ {campo} - IMPLEMENTADO")
                else:
                    print(f"   ❌ {campo} - NO ENCONTRADO")
            
            print()
            
            # 3. Verificar datos
            print("📊 VERIFICANDO DATOS...")
            cursor.execute("SELECT COUNT(*) FROM recursos")
            total_recursos = cursor.fetchone()[0]
            print(f"   Total de recursos en la BD: {total_recursos}")
            
            if total_recursos > 0:
                # Verificar que los nuevos campos tienen datos
                cursor.execute("SELECT COUNT(*) FROM recursos WHERE precio_base IS NOT NULL")
                recursos_con_precio = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM recursos WHERE capacidad IS NOT NULL")
                recursos_con_capacidad = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM recursos WHERE descripcion IS NOT NULL")
                recursos_con_descripcion = cursor.fetchone()[0]
                
                print(f"   Recursos con precio_base: {recursos_con_precio}/{total_recursos}")
                print(f"   Recursos con capacidad: {recursos_con_capacidad}/{total_recursos}")
                print(f"   Recursos con descripcion: {recursos_con_descripcion}/{total_recursos}")
                
                # Mostrar algunos ejemplos
                print()
                print("📋 EJEMPLOS DE RECURSOS:")
                cursor.execute("SELECT id, nombre, tipo, precio_base, capacidad, disponible FROM recursos LIMIT 5")
                recursos = cursor.fetchall()
                
                for recurso in recursos:
                    id, nombre, tipo, precio, capacidad, disponible = recurso
                    estado = "✅ Disponible" if disponible else "❌ No Disponible"
                    print(f"   - ID {id}: {nombre} ({tipo}) - Precio: €{precio} - Capacidad: {capacidad} - {estado}")
                
                # Estadísticas de precios
                print()
                print("💰 ESTADÍSTICAS DE PRECIOS:")
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        AVG(precio_base) as promedio,
                        MIN(precio_base) as minimo,
                        MAX(precio_base) as maximo,
                        SUM(precio_base) as valor_total
                    FROM recursos
                """)
                stats = cursor.fetchone()
                
                if stats[1] is not None:  # Si hay precios
                    print(f"   Precio promedio: €{stats[1]:.2f}")
                    print(f"   Precio mínimo: €{stats[2]:.2f}")
                    print(f"   Precio máximo: €{stats[3]:.2f}")
                    print(f"   Valor total: €{stats[4]:.2f}")
                else:
                    print("   No hay precios configurados")
                
            else:
                print("   ⚠️  No hay recursos en la base de datos")
        
        else:
            print("❌ Tabla 'recursos' no encontrada")
        
        conn.close()
        
        print()
        print("🎯 RESUMEN DE VERIFICACIÓN:")
        if 'recursos' in tables and len(campos_encontrados) == len(campos_nuevos):
            print("   ✅ TODOS LOS CAMPOS NUEVOS IMPLEMENTADOS CORRECTAMENTE")
            print("   ✅ La migración fue exitosa")
            print("   ✅ El campo precio_base está funcionando")
        else:
            print("   ❌ ALGUNOS CAMPOS NO ESTÁN IMPLEMENTADOS")
            print("   ❌ Revisa la migración de la base de datos")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verificar_campo_especifico(campo):
    """Verificar un campo específico en la tabla recursos"""
    
    db_path = "data/reservas.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si el campo existe
        cursor.execute("PRAGMA table_info(recursos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if campo in columns:
            print(f"✅ Campo '{campo}' encontrado en la tabla recursos")
            
            # Verificar datos del campo
            cursor.execute(f"SELECT COUNT(*) FROM recursos WHERE {campo} IS NOT NULL")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM recursos")
            total = cursor.fetchone()[0]
            
            print(f"   Recursos con {campo}: {count}/{total}")
            
            # Mostrar algunos valores
            cursor.execute(f"SELECT nombre, {campo} FROM recursos WHERE {campo} IS NOT NULL LIMIT 3")
            valores = cursor.fetchall()
            
            if valores:
                print(f"   Ejemplos de valores:")
                for valor in valores:
                    print(f"   - {valor[0]}: {valor[1]}")
            
            conn.close()
            return True
        else:
            print(f"❌ Campo '{campo}' NO encontrado en la tabla recursos")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error verificando campo '{campo}': {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN DE BASE DE DATOS")
    print()
    
    # Verificación completa
    success = verificar_base_datos()
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        
        # Verificaciones específicas
        print()
        print("🔍 VERIFICACIONES ESPECÍFICAS:")
        verificar_campo_especifico('precio_base')
        verificar_campo_especifico('capacidad')
        verificar_campo_especifico('descripcion')
        
    else:
        print("💥 ERROR EN LA VERIFICACIÓN")
        print("💡 Revisa los mensajes de error arriba")
    
    print()
    print("📚 Para más información, consulta:")
    print("   - GUIA_BASE_DATOS.md")
    print("   - IMPLEMENTACION_PRECIO_BASE.md")
