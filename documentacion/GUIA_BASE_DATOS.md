# 🗄️ Guía de Acceso y Verificación de Base de Datos

## 📋 Índice

1. [Acceso a la Base de Datos](#acceso-a-la-base-de-datos)
2. [Verificación de Estructura](#verificación-de-estructura)
3. [Consulta de Datos](#consulta-de-datos)
4. [Verificación de Campos Nuevos](#verificación-de-campos-nuevos)
5. [Herramientas de Verificación](#herramientas-de-verificación)
6. [Troubleshooting](#troubleshooting)
7. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 🔑 Acceso a la Base de Datos

### **Ubicación de la Base de Datos**
```
📁 Ruta: data/reservas.db
📁 Tipo: SQLite
🔧 Motor: SQLAlchemy + SQLite
```

### **Métodos de Acceso**

#### **1. Acceso Directo con Python**
```bash
# Desde la raíz del proyecto
python -c "import sqlite3; conn = sqlite3.connect('data/reservas.db'); print('✅ Base de datos conectada')"
```

#### **2. Acceso con SQLite CLI**
```bash
# Instalar SQLite CLI (si no está instalado)
# Windows: Descargar desde https://www.sqlite.org/download.html
# Linux/Mac: sudo apt-get install sqlite3

# Conectar a la base de datos
sqlite3 data/reservas.db
```

#### **3. Acceso desde el Código**
```python
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('data/reservas.db')
cursor = conn.cursor()

# Ejecutar consultas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tablas disponibles:", tables)

# Cerrar conexión
conn.close()
```

---

## 🔍 Verificación de Estructura

### **Verificar Tablas Existentes**
```sql
-- Listar todas las tablas
SELECT name FROM sqlite_master WHERE type='table';

-- Ver estructura de una tabla específica
PRAGMA table_info(recursos);
```

### **Verificar Campos de la Tabla Recursos**
```sql
-- Ver estructura completa de la tabla recursos
PRAGMA table_info(recursos);

-- Resultado esperado después de la migración:
-- id | INTEGER | 0 | 1 | 1
-- nombre | VARCHAR | 0 | 0 | 0
-- tipo | VARCHAR | 0 | 0 | 0
-- disponible | BOOLEAN | 0 | 0 | 0
-- created_at | DATETIME | 0 | 0 | 0
-- updated_at | DATETIME | 0 | 0 | 0
-- capacidad | INTEGER | 0 | 1 | 0
-- descripcion | TEXT | 0 | 0 | 0
-- precio_base | REAL | 0 | 0.0 | 0
```

---

## 📊 Consulta de Datos

### **Consultas Básicas**

#### **Ver Todos los Recursos**
```sql
SELECT * FROM recursos;
```

#### **Ver Recursos con Precio Base**
```sql
SELECT id, nombre, tipo, precio_base, capacidad, disponible 
FROM recursos 
ORDER BY precio_base DESC;
```

#### **Contar Recursos por Tipo**
```sql
SELECT tipo, COUNT(*) as cantidad, AVG(precio_base) as precio_promedio
FROM recursos 
GROUP BY tipo;
```

#### **Recursos con Precio Base > 0**
```sql
SELECT nombre, tipo, precio_base, capacidad
FROM recursos 
WHERE precio_base > 0
ORDER BY precio_base DESC;
```

### **Consultas Avanzadas**

#### **Recursos Disponibles con Precio**
```sql
SELECT 
    r.nombre,
    r.tipo,
    r.precio_base,
    r.capacidad,
    r.descripcion,
    CASE 
        WHEN r.disponible = 1 THEN 'Disponible'
        ELSE 'No Disponible'
    END as estado
FROM recursos r
WHERE r.disponible = 1
ORDER BY r.precio_base DESC;
```

#### **Estadísticas de Precios**
```sql
SELECT 
    COUNT(*) as total_recursos,
    AVG(precio_base) as precio_promedio,
    MIN(precio_base) as precio_minimo,
    MAX(precio_base) as precio_maximo,
    SUM(precio_base) as valor_total
FROM recursos;
```

---

## ✅ Verificación de Campos Nuevos

### **Verificar que los Nuevos Campos Existen**

#### **1. Verificar Columna `precio_base`**
```sql
-- Verificar que la columna precio_base existe
SELECT precio_base FROM recursos LIMIT 1;

-- Si no existe, agregarla manualmente
ALTER TABLE recursos ADD COLUMN precio_base REAL DEFAULT 0.0;
```

#### **2. Verificar Columna `capacidad`**
```sql
-- Verificar que la columna capacidad existe
SELECT capacidad FROM recursos LIMIT 1;

-- Si no existe, agregarla manualmente
ALTER TABLE recursos ADD COLUMN capacidad INTEGER DEFAULT 1;
```

#### **3. Verificar Columna `descripcion`**
```sql
-- Verificar que la columna descripcion existe
SELECT descripcion FROM recursos LIMIT 1;

-- Si no existe, agregarla manualmente
ALTER TABLE recursos ADD COLUMN descripcion TEXT;
```

### **Actualizar Registros Existentes**
```sql
-- Actualizar registros existentes con valores por defecto
UPDATE recursos SET capacidad = 1 WHERE capacidad IS NULL;
UPDATE recursos SET precio_base = 0.0 WHERE precio_base IS NULL;
UPDATE recursos SET descripcion = '' WHERE descripcion IS NULL;
```

---

## 🛠️ Herramientas de Verificación

### **Script de Verificación Automática**
```python
#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos
"""

import sqlite3
import os

def verificar_base_datos():
    """Verificar estructura y datos de la base de datos"""
    
    db_path = "data/reservas.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estructura de la base de datos...")
        
        # 1. Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 Tablas encontradas: {tables}")
        
        # 2. Verificar estructura de recursos
        if 'recursos' in tables:
            print("\n🏢 Verificando tabla 'recursos'...")
            cursor.execute("PRAGMA table_info(recursos)")
            columns = cursor.fetchall()
            
            print("📊 Columnas de la tabla recursos:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) - Default: {col[4]}")
            
            # 3. Verificar campos nuevos
            column_names = [col[1] for col in columns]
            
            if 'precio_base' in column_names:
                print("✅ Campo 'precio_base' encontrado")
            else:
                print("❌ Campo 'precio_base' NO encontrado")
            
            if 'capacidad' in column_names:
                print("✅ Campo 'capacidad' encontrado")
            else:
                print("❌ Campo 'capacidad' NO encontrado")
            
            if 'descripcion' in column_names:
                print("✅ Campo 'descripcion' encontrado")
            else:
                print("❌ Campo 'descripcion' NO encontrado")
            
            # 4. Verificar datos
            cursor.execute("SELECT COUNT(*) FROM recursos")
            total_recursos = cursor.fetchone()[0]
            print(f"\n📊 Total de recursos en la BD: {total_recursos}")
            
            if total_recursos > 0:
                cursor.execute("SELECT nombre, tipo, precio_base, capacidad FROM recursos LIMIT 5")
                recursos = cursor.fetchall()
                
                print("\n📋 Primeros 5 recursos:")
                for recurso in recursos:
                    print(f"  - {recurso[0]} ({recurso[1]}) - Precio: €{recurso[2]} - Capacidad: {recurso[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    verificar_base_datos()
```

### **Ejecutar Verificación**
```bash
# Crear y ejecutar el script de verificación
python -c "
import sqlite3
conn = sqlite3.connect('data/reservas.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(recursos)')
columns = cursor.fetchall()
print('Columnas de recursos:')
for col in columns:
    print(f'  - {col[1]} ({col[2]})')
conn.close()
"
```

---

## 🔧 Troubleshooting

### **Problemas Comunes**

#### **1. Base de Datos No Encontrada**
```bash
# Verificar que el archivo existe
dir data\reservas.db

# Si no existe, verificar la ruta
dir data\
```

#### **2. Campos No Existen**
```sql
-- Verificar estructura actual
PRAGMA table_info(recursos);

-- Agregar campos manualmente si es necesario
ALTER TABLE recursos ADD COLUMN precio_base REAL DEFAULT 0.0;
ALTER TABLE recursos ADD COLUMN capacidad INTEGER DEFAULT 1;
ALTER TABLE recursos ADD COLUMN descripcion TEXT;
```

#### **3. Errores de Permisos**
```bash
# En Windows, ejecutar como administrador
# En Linux/Mac, verificar permisos
ls -la data/reservas.db
```

### **Soluciones Rápidas**

#### **Recrear Base de Datos (ÚLTIMO RECURSO)**
```bash
# 1. Hacer backup de datos existentes
cp data/reservas.db data/reservas_backup.db

# 2. Eliminar base de datos actual
rm data/reservas.db

# 3. Reiniciar servidor (recreará la BD)
python run_sqlite.py
```

---

## 📝 Ejemplos Prácticos

### **Ejemplo 1: Verificar un Recurso Específico**
```sql
-- Buscar recurso por nombre
SELECT * FROM recursos WHERE nombre LIKE '%Sala%';

-- Ver recurso por ID
SELECT * FROM recursos WHERE id = 1;
```

### **Ejemplo 2: Actualizar Precio de un Recurso**
```sql
-- Actualizar precio base
UPDATE recursos SET precio_base = 50.00 WHERE id = 1;

-- Verificar cambio
SELECT id, nombre, precio_base FROM recursos WHERE id = 1;
```

### **Ejemplo 3: Crear Recurso de Prueba**
```sql
-- Insertar recurso de prueba
INSERT INTO recursos (nombre, tipo, capacidad, descripcion, disponible, precio_base)
VALUES ('Sala de Prueba', 'sala', 10, 'Sala para testing', 1, 25.50);

-- Verificar inserción
SELECT * FROM recursos WHERE nombre = 'Sala de Prueba';
```

### **Ejemplo 4: Exportar Datos**
```sql
-- Exportar recursos a CSV (desde SQLite CLI)
.mode csv
.headers on
.output recursos_export.csv
SELECT id, nombre, tipo, capacidad, precio_base, disponible FROM recursos;
.output stdout
```

---

## 🚀 Comandos Rápidos de Verificación

### **Verificar Estructura Completa**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/reservas.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(recursos)')
cols = cursor.fetchall()
print('Estructura de tabla recursos:')
for c in cols:
    print(f'  {c[1]}: {c[2]} (Default: {c[4]})')
conn.close()
"
```

### **Verificar Datos de Recursos**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/reservas.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM recursos')
total = cursor.fetchone()[0]
cursor.execute('SELECT nombre, precio_base FROM recursos LIMIT 3')
recursos = cursor.fetchall()
print(f'Total recursos: {total}')
print('Primeros 3 recursos:')
for r in recursos:
    print(f'  {r[0]}: €{r[1]}')
conn.close()
"
```

### **Verificar Campos Nuevos**
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/reservas.db')
cursor = conn.cursor()
cursor.execute('SELECT precio_base, capacidad, descripcion FROM recursos LIMIT 1')
data = cursor.fetchone()
print('Campos nuevos verificados:')
print(f'  precio_base: {data[0]} (tipo: {type(data[0])})')
print(f'  capacidad: {data[1]} (tipo: {type(data[1])})')
print(f'  descripcion: {data[2]} (tipo: {type(data[2])})')
conn.close()
"
```

---

## 📚 Referencias

### **Documentación Relacionada**
- [Implementación del Campo precio_base](./IMPLEMENTACION_PRECIO_BASE.md)
- [Base de Datos](./BASE_DATOS.md)
- [API Endpoints](./API_ENDPOINTS.md)

### **Recursos Externos**
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite CLI](https://www.sqlite.org/cli.html)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0  
**Autor**: Sistema de Gestión de Reservas
