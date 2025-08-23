# 🎯 Sistema de Reservas con Precios Dinámicos e Integraciones

## 📋 **Descripción del Proyecto**

Sistema completo de gestión de reservas que incluye un **Sistema de Precios Dinámicos** avanzado y un **Sistema de Integraciones** robusto para conectar con servicios externos. Desarrollado con FastAPI, SQLAlchemy y una interfaz moderna con Bootstrap 5.

## 🚀 **Características Principales**

### ✨ **Sistema de Precios Dinámicos**
- **Gestión completa de precios** con operaciones CRUD
- **Tipos de precios múltiples**: Base, Descuento, Recargo, Por Hora, Por Día, Temporada, Grupo
- **Sistema de prioridades** para aplicar precios en orden correcto
- **Filtros avanzados** por tipo, moneda, estado y rango de precio
- **Calculadora de precios** con aplicación automática de reglas
- **Modal de edición dinámico** con UX mejorado

### 🔗 **Sistema de Integraciones**
- **Gestión de integraciones externas**: Email SMTP, WhatsApp Business, Google Calendar
- **Estados de integración**: ACTIVA, INACTIVA, ERROR, CONFIGURANDO
- **Sistema de notificaciones** con reintentos automáticos
- **Webhooks configurables** para eventos del sistema
- **Sincronización con Google Calendar**

### 🎨 **Interfaz de Usuario Moderna**
- **Sistema de pestañas funcional** con navegación independiente
- **Modales responsivos** con z-index optimizado
- **Filtros y búsquedas** en tiempo real
- **Dashboard con estadísticas** visuales
- **Navegación intuitiva** entre módulos

## 🛠️ **Tecnologías Utilizadas**

### **Backend**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **SQLite** - Base de datos ligera
- **Pydantic** - Validación de datos y serialización
- **Uvicorn** - Servidor ASGI

### **Frontend**
- **HTML5** - Estructura semántica
- **CSS3** - Estilos modernos y responsivos
- **JavaScript ES6+** - Lógica de la aplicación
- **Bootstrap 5.3.0** - Framework CSS
- **Font Awesome 6.4.0** - Iconografía

### **Herramientas de Desarrollo**
- **Python 3.8+** - Lenguaje principal
- **Git** - Control de versiones
- **SQLite Browser** - Gestión de base de datos

## 📁 **Estructura del Proyecto**

```
reservas/
├── app/                          # Código de la aplicación
│   ├── models/                  # Modelos de base de datos
│   │   ├── precio.py           # Modelo de precios
│   │   ├── integracion.py      # Modelo de integraciones
│   │   └── pago.py             # Modelo de pagos
│   ├── schemas/                 # Esquemas Pydantic
│   │   ├── precio.py           # Esquemas para precios
│   │   ├── integracion.py      # Esquemas para integraciones
│   │   └── pago.py             # Esquemas para pagos
│   ├── services/                # Lógica de negocio
│   │   ├── precio_service.py   # Servicios de precios
│   │   ├── integracion_service.py # Servicios de integraciones
│   │   └── pago_service.py     # Servicios de pagos
│   └── routes/                  # Endpoints de la API
│       ├── precio_routes.py    # Rutas para precios
│       ├── integracion_routes.py # Rutas para integraciones
│       └── pago_routes.py      # Rutas para pagos
├── static/                      # Archivos estáticos
│   ├── app.js                  # Lógica principal
│   ├── precios.js              # Lógica de precios
│   └── styles.css              # Estilos personalizados
├── data/                       # Base de datos
│   └── reservas.db             # Base de datos SQLite
├── cliente_web.html            # Interfaz principal
├── requirements.txt            # Dependencias de Python
├── README.md                   # Este archivo
└── DOCUMENTACION_SISTEMA_PRECIOS_INTEGRACIONES.md # Documentación completa
```

## 🚀 **Instalación y Configuración**

### **Requisitos del Sistema**
- Python 3.8 o superior
- SQLite3
- Git

### **Pasos de Instalación**

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd reservas
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   ```bash
   # La base de datos se creará automáticamente al ejecutar la aplicación
   ```

5. **Iniciar servidor**
   ```bash
   uvicorn app.main_sqlite:app --reload --host 0.0.0.0 --port 8000
   ```

### **Acceso a la Aplicación**
- **Frontend**: http://localhost:8000/cliente-web
- **API Documentation**: http://localhost:8000/docs
- **Base de datos**: data/reservas.db

## 📚 **Documentación**

### **Documentación Completa**
- **[DOCUMENTACION_SISTEMA_PRECIOS_INTEGRACIONES.md](DOCUMENTACION_SISTEMA_PRECIOS_INTEGRACIONES.md)** - Documentación técnica completa del sistema

### **APIs Disponibles**

#### **Precios**
- `GET /api/precios/` - Listar todos los precios
- `POST /api/precios/` - Crear nuevo precio
- `PUT /api/precios/{id}` - Actualizar precio existente
- `DELETE /api/precios/{id}` - Eliminar precio
- `GET /api/precios/calcular` - Calcular precio con reglas

#### **Integraciones**
- `GET /api/integraciones/` - Listar integraciones
- `POST /api/integraciones/` - Crear nueva integración
- `PUT /api/integraciones/{id}` - Actualizar integración
- `DELETE /api/integraciones/{id}` - Eliminar integración

## 🎯 **Funcionalidades Destacadas**

### **Sistema de Precios**
- ✅ **Gestión completa** de precios con CRUD
- ✅ **Tipos múltiples** de precios (Base, Descuento, Recargo, etc.)
- ✅ **Sistema de prioridades** para reglas complejas
- ✅ **Filtros avanzados** y búsquedas
- ✅ **Calculadora automática** de precios finales

### **Sistema de Integraciones**
- ✅ **Múltiples proveedores** (Email, WhatsApp, Google Calendar)
- ✅ **Estados de integración** con monitoreo
- ✅ **Sistema de notificaciones** robusto
- ✅ **Webhooks configurables** para eventos

### **Interfaz de Usuario**
- ✅ **Sistema de pestañas** funcional y navegable
- ✅ **Modales responsivos** con UX optimizada
- ✅ **Dashboard con estadísticas** visuales
- ✅ **Navegación intuitiva** entre módulos

## 🔧 **Desarrollo y Contribución**

### **Estructura de Desarrollo**
- **Sprint 5**: Sistema de Precios e Integraciones ✅ Completado
- **Sprint 6**: Sistema de Auditoría y Notificaciones (Planificado)
- **Sprint 7**: Optimizaciones de Performance (Planificado)

### **Estándares de Código**
- **Python**: PEP 8
- **JavaScript**: ES6+ con funciones modernas
- **HTML**: Semántico y accesible
- **CSS**: BEM methodology

### **Testing**
- **APIs**: Tests unitarios con pytest
- **Frontend**: Tests de integración
- **Base de datos**: Tests de migración

## 📊 **Estado del Proyecto**

### **✅ Completado (Sprint 5)**
- Sistema de Precios Dinámicos
- Sistema de Integraciones
- Interfaz de Usuario Moderna
- APIs RESTful Completas
- Base de Datos Optimizada

### **🔄 En Desarrollo**
- Sistema de Auditoría
- Notificaciones Avanzadas
- Tests Automatizados

### **📋 Planificado**
- Sistema de Pagos
- Exportación de Datos
- CI/CD Pipeline
- Docker Deployment

## 🤝 **Contribución**

### **Cómo Contribuir**
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### **Reportar Bugs**
- Usa el sistema de Issues de GitHub
- Incluye pasos para reproducir el bug
- Adjunta logs y capturas de pantalla si es necesario

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 **Equipo de Desarrollo**

- **Desarrollador Principal**: [Tu Nombre]
- **Arquitecto de Software**: [Tu Nombre]
- **Diseñador UX/UI**: [Tu Nombre]

## 📞 **Contacto**

- **Email**: [tu-email@ejemplo.com]
- **GitHub**: [tu-usuario-github]
- **LinkedIn**: [tu-perfil-linkedin]

## 🙏 **Agradecimientos**

- **FastAPI** por el framework web excepcional
- **Bootstrap** por el sistema de componentes CSS
- **SQLAlchemy** por el ORM robusto
- **Comunidad open source** por las herramientas y librerías

---

**Última actualización**: 24 de Agosto, 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Sistema Completamente Funcional
