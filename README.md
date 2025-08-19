# 🏥 Microservicio de Gestión de Reservas

Un microservicio robusto y escalable para gestionar reservas en diferentes tipos de aplicaciones como **ecommerce**, **citas médicas**, **alquileres**, **restaurantes**, **spas**, etc. Construido con FastAPI y PostgreSQL, incluye validación de solapamientos, autenticación JWT y verificación de disponibilidad en tiempo real.

## 🚀 Características Principales

- **🔐 Autenticación JWT** para proteger endpoints administrativos
- **⚡ API REST completa** con validación automática de datos
- **🕒 Validación de solapamientos** para evitar reservas conflictivas
- **📅 Verificación de disponibilidad** en tiempo real
- **🗄️ Base de datos PostgreSQL** con SQLAlchemy ORM
- **🔄 Migraciones automáticas** con Alembic
- **📚 Documentación automática** con Swagger/OpenAPI
- **🐳 Contenedores Docker** para fácil despliegue
- **⚙️ Configuración por variables de entorno**
- **🌐 CORS habilitado** para integración frontend

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph "Frontend/Cliente"
        WebApp[Aplicación Web]
        MobileApp[Aplicación Móvil]
        ThirdParty[API Externa]
    end
    
    subgraph "Microservicio de Reservas"
        FastAPI[FastAPI Server]
        Auth[JWT Auth]
        Services[Servicios de Negocio]
        Models[Modelos SQLAlchemy]
    end
    
    subgraph "Base de Datos"
        PostgreSQL[(PostgreSQL)]
        Migrations[Alembic Migrations]
    end
    
    subgraph "Integraciones"
        Webhooks[Webhooks]
        Notifications[Notificaciones]
        Calendar[Calendario]
    end
    
    WebApp -->|HTTP/REST| FastAPI
    MobileApp -->|HTTP/REST| FastAPI
    ThirdParty -->|HTTP/REST| FastAPI
    
    FastAPI --> Auth
    FastAPI --> Services
    Services --> Models
    Models --> PostgreSQL
    PostgreSQL --> Migrations
    
    FastAPI --> Webhooks
    FastAPI --> Notifications
    FastAPI --> Calendar
    
    style FastAPI fill:#009688
    style PostgreSQL fill:#336791
    style Auth fill:#FF6B6B
```

## 📋 Requisitos Previos

### **Obligatorios:**
- **Docker** 20.10+ y **Docker Compose** 2.0+
- **Python** 3.11+ (para desarrollo local)

### **Opcionales:**
- **PostgreSQL** 15+ (para desarrollo local sin Docker)
- **Git** para clonar el repositorio

## 🛠️ Instalación y Configuración

### **1. Clonar el Repositorio**

```bash
git clone <repository-url>
cd reservas
```

### **2. Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tus configuraciones
nano .env  # o usar tu editor preferido
```

**Variables importantes en `.env`:**
```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/reservas_db

# JWT
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la app
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🚀 Ejecución

### **Opción A: Docker (Recomendado para producción)**

#### **Inicialización Automática (Recomendado)**
```bash
# Linux/macOS
chmod +x scripts/docker_init.sh
./scripts/docker_init.sh

# Windows PowerShell
.\scripts\docker_init.ps1
```

#### **Inicialización Manual**
```bash
# Construir y levantar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### **Opción B: Desarrollo Local**

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar PostgreSQL local (opcional)
# Asegúrate de tener PostgreSQL corriendo y crear la base de datos

# 5. Ejecutar migraciones
alembic upgrade head

# 6. Ejecutar script de inicialización
python scripts/init_data.py

# 7. Ejecutar aplicación
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 Inicialización de Datos de Prueba

El microservicio incluye scripts de inicialización automática que crean:

### **📊 Datos Creados Automáticamente:**
- **👥 1 Cliente**: María González López
- **🛠️ 1 Servicio**: Consulta Médica General (30 min, €50)
- **🏢 1 Recurso**: Consultorio Principal
- **👑 1 Usuario Admin**: admin/admin123
- **👤 1 Usuario Normal**: usuario/user123
- **💰 1 Regla de Precio**: Fin de semana (€65)
- **📅 1 Reserva de Ejemplo**: Para mañana a las 10:00 AM

### **🔑 Credenciales de Acceso:**
```
👑 Administrador:
   Username: admin
   Password: admin123
   Email: admin@reservas.com

👤 Usuario Normal:
   Username: usuario
   Password: user123
   Email: usuario@reservas.com
```

### **📝 Scripts Disponibles:**
- **`scripts/init_data.py`**: Script Python para inicialización manual
- **`scripts/docker_init.sh`**: Script bash para Linux/macOS
- **`scripts/docker_init.ps1`**: Script PowerShell para Windows
- **`init.sql`**: Script SQL para inicialización directa en PostgreSQL

## 🌐 Acceso a la Aplicación

Una vez ejecutada, accede a:

- **🏠 Página principal**: http://localhost:8000
- **📚 Documentación Swagger**: http://localhost:8000/docs
- **📖 Documentación ReDoc**: http://localhost:8000/redoc
- **💚 Health Check**: http://localhost:8000/health

## 📚 API Endpoints Disponibles

### **🔐 Autenticación**

#### **Registrar Usuario**
```http
POST /auth/register
Content-Type: application/json

{
  "username": "usuario_nuevo",
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

#### **Iniciar Sesión**
```http
POST /auth/login
Content-Type: application/json

{
  "username": "usuario_nuevo",
  "password": "contraseña_segura"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### **👥 Clientes**

#### **Crear Cliente**
```http
POST /clientes
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan.perez@email.com",
  "telefono": "+34 600 123 456"
}
```

#### **Obtener Cliente**
```http
GET /clientes/1
```

#### **Actualizar Cliente**
```http
PUT /clientes/1
Content-Type: application/json

{
  "telefono": "+34 600 123 789"
}
```

### **🛠️ Servicios**

#### **Crear Servicio**
```http
POST /servicios
Content-Type: application/json

{
  "nombre": "Consulta Dermatológica",
  "descripcion": "Consulta especializada en dermatología",
  "duracion_minutos": 45,
  "precio_base": 80.00
}
```

#### **Listar Servicios**
```http
GET /servicios?skip=0&limit=10
```

### **🏢 Recursos**

#### **Crear Recurso**
```http
POST /recursos
Content-Type: application/json

{
  "nombre": "Consultorio Dermatología 1",
  "tipo": "consultorio",
  "disponible": true
}
```

#### **Recursos Disponibles**
```http
GET /recursos/disponibles
```

### **📅 Reservas**

#### **Crear Reserva**
```http
POST /reservas
Content-Type: application/json

{
  "cliente_id": 1,
  "servicio_id": 1,
  "recurso_id": 1,
  "fecha_hora_inicio": "2024-01-15T10:00:00",
  "fecha_hora_fin": "2024-01-15T10:45:00"
}
```

#### **Verificar Disponibilidad**
```http
GET /reservas/disponibilidad?servicio_id=1&fecha=2024-01-15
```

**Respuesta:**
```json
{
  "fecha": "2024-01-15",
  "servicio_id": 1,
  "horarios_disponibles": [
    {
      "inicio": "09:00",
      "fin": "09:45",
      "disponible": true
    },
    {
      "inicio": "10:00",
      "fin": "10:45",
      "disponible": false
    }
  ]
}
```

#### **Cancelar Reserva**
```http
POST /reservas/1/cancelar
```

### **💰 Precios**

#### **Crear Regla de Precio**
```http
POST /precios
Content-Type: application/json

{
  "servicio_id": 1,
  "tipo_regla": "fin_de_semana",
  "valor": 95.00,
  "descripcion": "Precio especial para fines de semana"
}
```

## 🔐 Autenticación y Autorización

### **Uso de JWT**

Para endpoints protegidos, incluye el token en el header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### **Roles de Usuario**

- **Usuario normal**: Acceso a endpoints básicos
- **Admin**: Acceso completo a todos los endpoints

## 🗄️ Base de Datos

### **Estructura de Tablas**

- **`clientes`**: Información de clientes
- **`servicios`**: Servicios ofrecidos
- **`recursos`**: Recursos disponibles
- **`reservas`**: Reservas realizadas
- **`precios`**: Reglas de precios dinámicas
- **`usuarios`**: Sistema de autenticación

### **Migraciones con Alembic**

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Ver historial
alembic history
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-cov

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_reservas.py -v
```

## 🚀 Despliegue en Producción

### **Variables de Entorno de Producción**

```bash
DEBUG=False
SECRET_KEY=<clave-secreta-muy-segura>
DATABASE_URL=<url-produccion-postgresql>
HOST=0.0.0.0
PORT=8000
```

### **Docker en Producción**

```bash
# Construir imagen optimizada
docker build -t reservas-microservice:latest .

# Ejecutar con variables de producción
docker run -d \
  -p 8000:8000 \
  -e DEBUG=False \
  -e DATABASE_URL=<url-produccion> \
  -e SECRET_KEY=<clave-secreta> \
  reservas-microservice:latest
```

### **Docker Compose en Producción**

```bash
# Usar archivo de producción
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuración Avanzada

### **CORS**

Configurar en `app/main.py` según tus necesidades:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tudominio.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### **Rate Limiting**

Para implementar rate limiting, puedes usar `slowapi`:

```bash
pip install slowapi
```

### **Logging**

Configurar logging estructurado en `app/config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📊 Monitoreo y Métricas

### **Health Check**

```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "reservas-microservice",
  "timestamp": "2024-01-15T10:00:00Z",
  "version": "1.0.0"
}
```

### **Métricas Personalizadas**

Puedes agregar endpoints para métricas de negocio:

```http
GET /metrics/reservas/diarias
GET /metrics/recursos/ocupacion
GET /metrics/servicios/populares
```

## 🤝 Contribución

1. **Fork** el proyecto
2. Crear **rama feature** (`git checkout -b feature/NuevaFuncionalidad`)
3. **Commit** cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/NuevaFuncionalidad`)
5. Abrir **Pull Request**

### **Estándares de Código**

- Usar **Black** para formateo
- **Pylint** para linting
- **Type hints** en todas las funciones
- **Docstrings** en español para endpoints

## 🐛 Troubleshooting

### **Problemas Comunes**

#### **Error de Conexión a Base de Datos**
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Verificar variables de entorno
docker-compose exec app env | grep DATABASE
```

#### **Error de Migraciones**
```bash
# Recrear base de datos
docker-compose down -v
docker-compose up --build
```

#### **Error de Permisos JWT**
```bash
# Verificar SECRET_KEY en .env
# Regenerar token de autenticación
```

#### **Error en Scripts de Inicialización**
```bash
# Verificar permisos de ejecución
chmod +x scripts/*.sh

# Ejecutar manualmente
python scripts/init_data.py
```

## 📚 Recursos Adicionales

- [**FastAPI Documentation**](https://fastapi.tiangolo.com/)
- [**SQLAlchemy Documentation**](https://docs.sqlalchemy.org/)
- [**Alembic Documentation**](https://alembic.sqlalchemy.org/)
- [**PostgreSQL Documentation**](https://www.postgresql.org/docs/)

## 📄 Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte y preguntas:

- 📧 **Email**: soporte@reservas.com
- 🐛 **Issues**: Crear issue en GitHub
- 💬 **Discord**: [Servidor de la comunidad](https://discord.gg/reservas)

## 🔄 Roadmap

### **Versión 1.1 (Próxima)**
- [ ] Tests unitarios y de integración
- [ ] Cache con Redis
- [ ] Notificaciones por email/SMS
- [ ] API para reportes y estadísticas

### **Versión 1.2**
- [ ] Integración con sistemas de pagos
- [ ] Webhooks para eventos
- [ ] Métricas y monitoreo avanzado
- [ ] Rate limiting configurable

### **Versión 2.0**
- [ ] Microservicio de notificaciones
- [ ] Sistema de colas con Celery
- [ ] API GraphQL
- [ ] Dashboard administrativo

---

**⭐ Si este proyecto te es útil, ¡déjanos una estrella en GitHub!**
