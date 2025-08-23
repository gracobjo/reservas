import sqlite3

try:
    conn = sqlite3.connect('data/reservas.db')
    cursor = conn.cursor()
    
    # Verificar tablas existentes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tablas en la base de datos:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Verificar si existe la tabla pagos
    if ('pagos',) in tables:
        print("\nEstructura de la tabla 'pagos':")
        cursor.execute("PRAGMA table_info(pagos)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) FROM pagos")
        count = cursor.fetchone()[0]
        print(f"\nNúmero de registros en 'pagos': {count}")
        
        if count > 0:
            print("\nPrimer registro:")
            cursor.execute("SELECT * FROM pagos LIMIT 1")
            row = cursor.fetchone()
            print(f"  {row}")
    else:
        print("\nLa tabla 'pagos' NO existe")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
