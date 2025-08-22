# 🗄️ Documentación de la Base de Datos

## 📋 Información General

- **Motor**: SQLite 3
- **ORM**: SQLAlchemy 2.0+
- **Ubicación**: `app/database.db`
- **Migraciones**: Alembic (configurado pero no implementado)
- **Backup**: Automático en `app/database_backup.db`

## 🏗️ Esquema de la Base de Datos

### **Diagrama ER (Entidad-Relación)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    servicios    │    │    recursos     │    │  reglas_precios │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ nombre          │    │ nombre          │    │ nombre          │
│ descripcion     │    │ tipo            │    │ descripcion     │
│ duracion_minutos│    │ disponible      │    │ tipo_regla      │
│ precio_base     │    │ created_at      │    │ condicion       │
│ created_at      │    │ updated_at      │    │ tipo_modificador│
│ updated_at      │    └─────────────────┘    │ valor_modificador│
└─────────────────┘                           │ prioridad       │
                                              │ activa          │
                                              │ fecha_inicio    │
                                              │ fecha_fin       │
                                              │ servicios_aplicables │
                                              │ recursos_aplicables  │
                                              │ created_at      │
                                              │ updated_at      │
                                              └─────────────────┘
```

## 📊 Tablas Principales

### 1. **Tabla: `servicios`**
Almacena información sobre los servicios ofrecidos.

**Estructura:**
```sql
CREATE TABLE servicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    descripcion TEXT,
    duracion_minutos INTEGER NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- **`id`**: Identificador único del servicio (clave primaria)
- **`nombre`**: Nombre del servicio (único)
- **`descripcion`**: Descripción detallada del servicio
- **`duracion_minutos`**: Duración estándar en minutos
- **`precio_base`**: Precio base del servicio en euros
- **`created_at`**: Fecha de creación del registro
- **`updated_at`**: Fecha de última actualización

**Ejemplos de datos:**
```sql
INSERT INTO servicios (nombre, descripcion, duracion_minutos, precio_base) VALUES
('Alquiler Habitación Individual', 'Habitación individual con baño privado', 1440, 80.00),
('Alquiler Habitación Doble', 'Habitación doble con baño privado', 1440, 120.00),
('Consulta Médica', 'Consulta médica general', 45, 50.00),
('Masaje Relajante', 'Masaje terapéutico de 60 minutos', 60, 75.00);
```

### 2. **Tabla: `recursos`**
Almacena información sobre los recursos físicos disponibles.

**Estructura:**
```sql
CREATE TABLE recursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    tipo VARCHAR(100) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- **`id`**: Identificador único del recurso (clave primaria)
- **`nombre`**: Nombre del recurso (único)
- **`tipo`**: Tipo de recurso (habitacion, sala, equipo, etc.)
- **`disponible`**: Estado de disponibilidad del recurso
- **`created_at`**: Fecha de creación del registro
- **`updated_at`**: Fecha de última actualización

**Tipos de recursos:**
- `habitacion`: Habitaciones de hotel
- `sala`: Salas de reuniones, eventos
- `equipo`: Equipos deportivos, médicos
- `vehiculo`: Vehículos de alquiler
- `espacio`: Espacios al aire libre

**Ejemplos de datos:**
```sql
INSERT INTO recursos (nombre, tipo, disponible) VALUES
('Habitación 101 - Individual', 'habitacion', TRUE),
('Habitación 201 - Doble', 'habitacion', TRUE),
('Sala de Yoga', 'sala', TRUE),
('Gimnasio', 'espacio', TRUE);
```

### 3. **Tabla: `reglas_precios`**
Almacena las reglas de precios dinámicos del sistema.

**Estructura:**
```sql
CREATE TABLE reglas_precios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo_regla VARCHAR(100) NOT NULL,
    condicion TEXT NOT NULL,
    tipo_modificador VARCHAR(50) NOT NULL,
    valor_modificador DECIMAL(10,2) NOT NULL,
    prioridad INTEGER DEFAULT 0,
    activa BOOLEAN DEFAULT TRUE,
    fecha_inicio DATE,
    fecha_fin DATE,
    servicios_aplicables TEXT,
    recursos_aplicables TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Campos:**
- **`id`**: Identificador único de la regla (clave primaria)
- **`nombre`**: Nombre descriptivo de la regla
- **`descripcion`**: Descripción detallada de la regla
- **`tipo_regla`**: Tipo de regla (dia_semana, hora, temporada, etc.)
- **`condicion`**: Condición JSON que activa la regla
- **`tipo_modificador`**: Tipo de modificación (porcentaje, monto_fijo, precio_fijo)
- **`valor_modificador`**: Valor del modificador
- **`prioridad`**: Prioridad de aplicación (mayor número = mayor prioridad)
- **`activa`**: Estado de activación de la regla
- **`fecha_inicio`**: Fecha de inicio de validez (opcional)
- **`fecha_fin`**: Fecha de fin de validez (opcional)
- **`servicios_aplicables`**: Lista JSON de servicios donde aplica (opcional)
- **`recursos_aplicables`**: Lista JSON de recursos donde aplica (opcional)

**Tipos de reglas:**
- `dia_semana`: Reglas por día de la semana
- `hora`: Reglas por hora del día
- `temporada`: Reglas por temporada del año
- `anticipacion`: Reglas por anticipación en la reserva
- `duracion`: Reglas por duración de la reserva
- `participantes`: Reglas por número de participantes
- `tipo_cliente`: Reglas por tipo de cliente

**Tipos de modificadores:**
- `porcentaje`: Modificación porcentual (+30%, -15%)
- `monto_fijo`: Modificación de monto fijo (+€20, -€10)
- `precio_fijo`: Establece un precio fijo específico

**Ejemplos de datos:**
```sql
INSERT INTO reglas_precios (nombre, descripcion, tipo_regla, condicion, tipo_modificador, valor_modificador, prioridad) VALUES
('Recargo Fin de Semana', 'Recargo del 30% los sábados y domingos', 'dia_semana', '{"dias": [5, 6]}', 'porcentaje', 30.0, 10),
('Descuento Anticipación', 'Descuento del 15% por reservar con 7 días de anticipación', 'anticipacion', '{"dias_min": 7}', 'porcentaje', -15.0, 20),
('Recargo Hora Pico', 'Recargo del 25% en horario de 18:00 a 22:00', 'hora', '{"hora_inicio": "18:00", "hora_fin": "22:00"}', 'porcentaje', 25.0, 15);
```

## 🔗 Relaciones y Restricciones

### **Relaciones Principales**
- **`servicios` ↔ `recursos`**: Relación muchos a muchos (a través de reservas)
- **`reglas_precios` → `servicios`**: Reglas pueden aplicarse a servicios específicos
- **`reglas_precios` → `recursos`**: Reglas pueden aplicarse a recursos específicos

### **Restricciones de Integridad**
```sql
-- Restricción de unicidad en nombres
ALTER TABLE servicios ADD CONSTRAINT uk_servicios_nombre UNIQUE (nombre);
ALTER TABLE recursos ADD CONSTRAINT uk_recursos_nombre UNIQUE (nombre);

-- Restricción de valores válidos
ALTER TABLE reglas_precios ADD CONSTRAINT ck_tipo_modificador 
    CHECK (tipo_modificador IN ('porcentaje', 'monto_fijo', 'precio_fijo'));

-- Restricción de prioridad positiva
ALTER TABLE reglas_precios ADD CONSTRAINT ck_prioridad 
    CHECK (prioridad >= 0);

-- Restricción de fechas válidas
ALTER TABLE reglas_precios ADD CONSTRAINT ck_fechas 
    CHECK (fecha_inicio IS NULL OR fecha_fin IS NULL OR fecha_inicio <= fecha_fin);
```

## 📈 Tablas de Auditoría y Historial

### **Tabla: `historial_precios`** (Pendiente de implementar)
Registra el historial de cálculos de precios para análisis y auditoría.

**Estructura propuesta:**
```sql
CREATE TABLE historial_precios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servicio_id INTEGER,
    recurso_id INTEGER,
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    participantes INTEGER NOT NULL,
    tipo_cliente VARCHAR(50) NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    precio_final DECIMAL(10,2) NOT NULL,
    reglas_aplicadas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id),
    FOREIGN KEY (recurso_id) REFERENCES recursos(id)
);
```

### **Tabla: `usuarios`** (Pendiente de implementar)
Almacena información de usuarios del sistema.

**Estructura propuesta:**
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    apellidos VARCHAR(255),
    rol VARCHAR(50) DEFAULT 'cliente',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Tabla: `reservas`** (Pendiente de implementar)
Almacena las reservas realizadas por los usuarios.

**Estructura propuesta:**
```sql
CREATE TABLE reservas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    servicio_id INTEGER NOT NULL,
    recurso_id INTEGER NOT NULL,
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    participantes INTEGER NOT NULL,
    precio_final DECIMAL(10,2) NOT NULL,
    estado VARCHAR(50) DEFAULT 'confirmada',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (servicio_id) REFERENCES servicios(id),
    FOREIGN KEY (recurso_id) REFERENCES recursos(id)
);
```

## 🔧 Operaciones de Mantenimiento

### **Limpieza de Duplicados**
El sistema incluye un script automático para limpiar datos duplicados:

```python
# Script: limpiar_duplicados.py
def clean_duplicate_services():
    """Elimina servicios duplicados manteniendo el más antiguo"""
    # Implementación en el script

def clean_duplicate_resources():
    """Elimina recursos duplicados manteniendo el más antiguo"""
    # Implementación en el script
```

### **Backup Automático**
```python
# En app/db_sqlite_clean.py
def create_backup():
    """Crea una copia de seguridad de la base de datos"""
    import shutil
    shutil.copy2('app/database.db', 'app/database_backup.db')
```

### **Verificación de Integridad**
```sql
-- Verificar integridad referencial
PRAGMA foreign_key_check;

-- Verificar índices
PRAGMA index_list(servicios);
PRAGMA index_list(recursos);
PRAGMA index_list(reglas_precios);

-- Análisis de la base de datos
ANALYZE;
```

## 📊 Consultas de Análisis

### **Estadísticas de Servicios**
```sql
SELECT 
    COUNT(*) as total_servicios,
    AVG(precio_base) as precio_promedio,
    MIN(precio_base) as precio_minimo,
    MAX(precio_base) as precio_maximo
FROM servicios;
```

### **Reglas Activas por Tipo**
```sql
SELECT 
    tipo_regla,
    COUNT(*) as cantidad,
    AVG(valor_modificador) as modificador_promedio
FROM reglas_precios 
WHERE activa = 1 
GROUP BY tipo_regla;
```

### **Recursos por Tipo**
```sql
SELECT 
    tipo,
    COUNT(*) as cantidad,
    SUM(CASE WHEN disponible = 1 THEN 1 ELSE 0 END) as disponibles
FROM recursos 
GROUP BY tipo;
```

## 🚀 Optimizaciones de Rendimiento

### **Índices Recomendados**
```sql
-- Índices para búsquedas frecuentes
CREATE INDEX idx_servicios_nombre ON servicios(nombre);
CREATE INDEX idx_recursos_tipo ON recursos(tipo);
CREATE INDEX idx_reglas_activa ON reglas_precios(activa);
CREATE INDEX idx_reglas_prioridad ON reglas_precios(prioridad);
CREATE INDEX idx_reglas_tipo ON reglas_precios(tipo_regla);

-- Índices compuestos para consultas complejas
CREATE INDEX idx_reglas_activa_prioridad ON reglas_precios(activa, prioridad);
CREATE INDEX idx_reglas_tipo_activa ON reglas_precios(tipo_regla, activa);
```

### **Configuraciones SQLite**
```sql
-- Optimizaciones de rendimiento
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;
```

## 🔒 Seguridad y Privacidad

### **Acceso a Datos**
- **Lectura**: Todos los endpoints públicos permiten lectura
- **Escritura**: Solo endpoints administrativos (pendiente de implementar autenticación)
- **Eliminación**: Solo con confirmación y validación

### **Datos Sensibles**
- **Contraseñas**: Hash bcrypt (cuando se implemente)
- **Información personal**: Encriptación opcional para datos críticos
- **Logs**: Sin información personal identificable

## 📚 Referencias

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite Performance](https://www.sqlite.org/optoverview.html)
