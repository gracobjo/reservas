import sqlite3
import os

def migrate_pagos_metadata():
    """Migrar la columna 'metadata' a 'metadatos_pago' en la tabla pagos"""
    
    db_path = 'data/reservas.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración de columna 'metadata' a 'metadatos_pago'...")
        
        # Verificar si la columna metadata existe
        cursor.execute("PRAGMA table_info(pagos)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'metadata' not in column_names:
            print("ℹ️ La columna 'metadata' no existe, no es necesaria la migración")
            conn.close()
            return True
        
        if 'metadatos_pago' in column_names:
            print("ℹ️ La columna 'metadatos_pago' ya existe")
            conn.close()
            return True
        
        print("📝 Creando nueva columna 'metadatos_pago'...")
        
        # Crear nueva columna
        cursor.execute("ALTER TABLE pagos ADD COLUMN metadatos_pago TEXT")
        
        print("📋 Copiando datos de 'metadata' a 'metadatos_pago'...")
        
        # Copiar datos
        cursor.execute("UPDATE pagos SET metadatos_pago = metadata")
        
        print("🗑️ Eliminando columna 'metadata'...")
        
        # Crear nueva tabla sin la columna metadata
        cursor.execute("""
            CREATE TABLE pagos_new (
                id INTEGER PRIMARY KEY,
                reserva_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                moneda TEXT DEFAULT 'EUR',
                estado TEXT DEFAULT 'pendiente',
                metodo_pago TEXT NOT NULL,
                transaccion_externa_id TEXT,
                referencia_pago TEXT,
                factura_generada BOOLEAN DEFAULT 0,
                numero_factura TEXT,
                descripcion TEXT,
                metadatos_pago TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_pago TIMESTAMP
            )
        """)
        
        # Copiar datos a la nueva tabla
        cursor.execute("""
            INSERT INTO pagos_new 
            SELECT id, reserva_id, cliente_id, monto, moneda, estado, metodo_pago,
                   transaccion_externa_id, referencia_pago, factura_generada, numero_factura,
                   descripcion, metadatos_pago, fecha_creacion, fecha_actualizacion, fecha_pago
            FROM pagos
        """)
        
        # Eliminar tabla antigua y renombrar la nueva
        cursor.execute("DROP TABLE pagos")
        cursor.execute("ALTER TABLE pagos_new RENAME TO pagos")
        
        # Crear índices si existen
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pagos_reserva_id ON pagos(reserva_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pagos_cliente_id ON pagos(cliente_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pagos_estado ON pagos(estado)")
        
        conn.commit()
        conn.close()
        
        print("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = migrate_pagos_metadata()
    if success:
        print("\n🎉 La migración se completó correctamente")
        print("🔄 Ahora puedes reiniciar el servidor")
    else:
        print("\n💥 La migración falló")
        print("🔍 Revisa los errores y vuelve a intentar")
