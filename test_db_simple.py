#!/usr/bin/env python3
"""
Prueba simple de la base de datos
"""

import sqlite3
import os

# Ruta de la base de datos
DB_PATH = "./data/reservas.db"

# Verificar que existe
if not os.path.exists(DB_PATH):
    print(f"❌ Base de datos no encontrada: {DB_PATH}")
    exit(1)

print(f"✅ Base de datos encontrada: {DB_PATH}")

# Conectar a la base de datos
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Listar todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"📋 Tablas encontradas: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Verificar estructura de la tabla recursos
    if any('recursos' in table[0] for table in tables):
        print("\n🔍 Estructura de la tabla 'recursos':")
        cursor.execute("PRAGMA table_info(recursos);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - Nullable: {col[3]}")
    
    # Verificar estructura de la tabla horarios_recursos
    if any('horarios_recursos' in table[0] for table in tables):
        print("\n🔍 Estructura de la tabla 'horarios_recursos':")
        cursor.execute("PRAGMA table_info(horarios_recursos);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - Nullable: {col[3]}")
    
    conn.close()
    print("\n✅ Prueba de base de datos completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.close()
