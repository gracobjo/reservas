# 📚 Índice de Documentación del Sistema

## 🎯 Documentación Principal

### **📖 [README.md](README.md)**
Documentación completa del sistema con estado actual, funcionalidades implementadas y pendientes.

**Contenido:**
- Descripción general del proyecto
- Estado actual (70% completado)
- Funcionalidades implementadas vs pendientes
- Arquitectura del sistema
- Instrucciones de uso
- Problemas técnicos resueltos
- Métricas del sistema

---

## 🔌 Documentación Técnica

### **🔌 [API_ENDPOINTS.md](API_ENDPOINTS.md)**
Documentación completa de todos los endpoints de la API REST.

**Contenido:**
- Información general de la API
- Endpoints de salud, servicios, recursos
- Endpoints de precios dinámicos
- Endpoints de reglas rápidas
- Endpoints de estadísticas
- Endpoints pendientes (autenticación, horarios, reservas)
- Códigos de estado HTTP
- Ejemplos de uso con curl

### **🗄️ [BASE_DATOS.md](BASE_DATOS.md)**
Documentación completa de la base de datos y modelos de datos.

**Contenido:**
- Esquema de la base de datos (SQLite)
- Diagrama ER (Entidad-Relación)
- Estructura de tablas principales
- Relaciones y restricciones
- Tablas de auditoría (pendientes)
- Operaciones de mantenimiento
- Consultas de análisis
- Optimizaciones de rendimiento

---

## 🎨 Documentación del Frontend

### **🎨 [FRONTEND_GUIA.md](FRONTEND_GUIA.md)**
Guía completa del cliente web y componentes de la interfaz.

**Contenido:**
- Estructura de la aplicación
- Pestañas principales (Dashboard, Calculadora, Historial, Notificaciones)
- Funcionalidades del sistema
- Componentes de UI
- Flujo de uso típico
- Solución de problemas
- Responsividad y adaptaciones móviles
- Seguridad y privacidad

### **📅 [CALENDARIO_RESERVAS.md](CALENDARIO_RESERVAS.md)**
Documentación completa del sistema de calendario y gestión de reservas.

**Contenido:**
- Funcionalidades del calendario (mensual/semanal)
- Modal de reservas desde calendario
- Cálculo automático de duración
- Opciones de reserva múltiple
- Gestión de reservas
- Correcciones de zona horaria
- Integración con API
- Historial de versiones y evolución

### **🏢 [GESTION_RECURSOS_PRECIOS.md](GESTION_RECURSOS_PRECIOS.md)**
Documentación completa del sistema de gestión de recursos y precios dinámicos.

**Contenido:**
- CRUD completo de recursos (Crear, Leer, Editar, Eliminar)
- Sistema de precios base por recurso
- Reglas de precios dinámicos (por hora, día, temporada)
- Modales centrados con navegación por tabs
- Integración con sistema de reservas
- API endpoints y estructura de datos
- Flujos de trabajo y troubleshooting
- Roadmap de mejoras futuras

### **💰 [IMPLEMENTACION_PRECIO_BASE.md](IMPLEMENTACION_PRECIO_BASE.md)**
Documentación completa de la implementación del campo precio_base.

**Contenido:**
- Problema identificado y solución implementada
- Cambios en modelos, esquemas y base de datos
- Migración automática de la estructura
- Pruebas de funcionalidad completas
- Estado final de la implementación

### **🚀 [SPRINT5_INTEGRACIONES_PAGOS.md](SPRINT5_INTEGRACIONES_PAGOS.md)**
Documentación completa del Sprint 5: Integraciones y Pagos.

**Contenido:**
- Sistema completo de pagos (Stripe, PayPal, Transferencia, Efectivo)
- Sistema de facturación automática con IVA
- Gestión de reembolsos
- Integraciones externas (Email, SMS, WhatsApp, Google Calendar)
- Sistema de notificaciones automáticas
- Webhooks para eventos del sistema
- APIs REST completas con validación
- Arquitectura del sistema y modelos de datos

### **🎨 [FRONTEND_SPRINT5.md](FRONTEND_SPRINT5.md)**
Documentación completa del frontend del Sprint 5: Interfaces de usuario.

**Contenido:**
- Interfaces completas para gestión de pagos
- Sistema de modales para CRUD operations
- Tabs anidadas para integraciones
- Filtros avanzados y búsquedas
- Diseño responsive y moderno
- Funcionalidades JavaScript completas
- Estilos CSS personalizados
- Flujos de usuario y UX

### **🗄️ [GUIA_BASE_DATOS.md](GUIA_BASE_DATOS.md)**
Guía completa para acceder y verificar la base de datos.

**Contenido:**
- Métodos de acceso a la base de datos SQLite
- Verificación de estructura y campos
- Consultas SQL para verificar datos
- Herramientas de verificación automática
- Troubleshooting y soluciones rápidas

---

## 🗺️ Planificación y Desarrollo

### **🗺️ [ROADMAP.md](ROADMAP.md)**
Roadmap detallado con plan de desarrollo por sprints.

**Contenido:**
- Objetivos del proyecto
- Plan de desarrollo por sprints (7 sprints)
- Criterios de aceptación
- Métricas de progreso
- Riesgos y mitigaciones
- Cronograma estimado
- Proceso de desarrollo
- Recursos y referencias

---

## 📋 Resumen de Funcionalidades

### ✅ **IMPLEMENTADAS (85%)**

#### **Backend (95%)**
- ✅ API REST completa con FastAPI
- ✅ Base de datos SQLite con SQLAlchemy
- ✅ Sistema de precios dinámicos
- ✅ Reglas de precios configurables
- ✅ Cálculo automático de precios
- ✅ Endpoints de servicios y recursos
- ✅ Sistema de reglas rápidas

#### **Frontend (95%)**
- ✅ Cliente web moderno con Bootstrap 5
- ✅ Calculadora de precios en tiempo real
- ✅ Sistema de notificaciones
- ✅ Historial de cálculos
- ✅ Validaciones de negocio
- ✅ Formato de moneda español
- ✅ Exportación de datos
- ✅ Calendario visual (mensual/semanal)
- ✅ Modal de reservas integrado
- ✅ Gestión completa de reservas
- ✅ **Sistema de gestión de recursos con CRUD completo**
- ✅ **Modal de gestión de precios con tabs**
- ✅ **Reglas de precios dinámicos (hora, día, temporada)**

#### **Validaciones (100%)**
- ✅ Habitaciones individuales: máximo 1 persona
- ✅ Habitaciones dobles: máximo 2 personas
- ✅ Duración por noches (números enteros)
- ✅ Compatibilidad servicio-recurso

### ✅ **SISTEMA DE RESERVAS (100%)**

#### **Calendario y Reservas**
- ✅ Creación de reservas desde calendario
- ✅ Gestión de disponibilidad visual
- ✅ Calendario mensual y semanal
- ✅ Confirmaciones y estados de reserva
- ✅ Cálculo automático de duración
- ✅ Reservas múltiples y recurrentes
- ✅ Integración completa con API

### ✅ **GESTIÓN DE RECURSOS Y PRECIOS (100%)**

#### **CRUD de Recursos**
- ✅ Creación de recursos con formulario modal
- ✅ Visualización en tarjetas interactivas
- ✅ Edición completa de recursos
- ✅ Eliminación con confirmación
- ✅ Modal de información detallada

#### **Sistema de Precios**
- ✅ Precio base configurable por recurso
- ✅ Reglas de precio por hora (franjas horarias)
- ✅ Reglas de precio por día (días de la semana)
- ✅ Reglas de precio por temporada (fechas específicas)
- ✅ Modal de gestión con navegación por tabs
- ✅ Formularios específicos para cada tipo de regla

### 📋 **PLANIFICADAS (0%)**

#### **Sprint 1: Reservas Básicas** ✅ COMPLETADO
- ✅ Modelo de datos para reservas
- ✅ API de reservas
- ✅ Validaciones de disponibilidad
- ✅ Frontend de reservas

#### **Sprint 2: Gestión de Horarios**
- 📋 Modelo de horarios
- 📋 API de horarios
- 📋 Sistema de disponibilidad
- 📋 Frontend de horarios

#### **Sprint 3: Autenticación**
- 📋 Modelo de usuarios
- 📋 Sistema de autenticación JWT
- 📋 Gestión de perfiles
- 📋 Frontend de autenticación

#### **Sprint 4: Calendario Visual** ✅ COMPLETADO
- ✅ Calendario visual de disponibilidad
- ✅ Mejoras de UX
- ✅ Notificaciones avanzadas

#### **Sprint 5: Integraciones y Pagos** ✅ COMPLETADO
- ✅ Sistema de pagos (Stripe, PayPal, Transferencia, Efectivo)
- ✅ Sistema de facturación automática con IVA
- ✅ Gestión de reembolsos
- ✅ Integraciones externas (Email, SMS, WhatsApp, Google Calendar)
- ✅ Sistema de notificaciones automáticas
- ✅ Webhooks para eventos del sistema
- ✅ APIs REST completas con validación

#### **Sprint 6: Analytics**
- 📋 Dashboard ejecutivo
- 📋 Reportes avanzados
- 📋 Analytics en tiempo real

#### **Sprint 7: Funcionalidades Avanzadas**
- 📋 Sistema de descuentos
- 📋 Programa de fidelidad
- 📋 Optimizaciones técnicas

---

## 🚀 Cómo Usar Esta Documentación

### **Para Desarrolladores:**
1. **Comenzar con [README.md](README.md)** para entender el estado general
2. **Revisar [API_ENDPOINTS.md](API_ENDPOINTS.md)** para entender la API
3. **Consultar [BASE_DATOS.md](BASE_DATOS.md)** para el esquema de datos
4. **Revisar [ROADMAP.md](ROADMAP.md)** para el plan de desarrollo

### **Para Usuarios Finales:**
1. **Comenzar con [README.md](README.md)** para funcionalidades disponibles
2. **Revisar [FRONTEND_GUIA.md](FRONTEND_GUIA.md)** para uso del cliente web
3. **Consultar [API_ENDPOINTS.md](API_ENDPOINTS.md)** si necesitan integrar con la API

### **Para Gestores de Proyecto:**
1. **Revisar [ROADMAP.md](ROADMAP.md)** para planificación
2. **Consultar [README.md](README.md)** para estado actual
3. **Revisar métricas de progreso** en cada documento

---

## 📝 Mantenimiento de la Documentación

### **Cuándo Actualizar:**
- ✅ **Después de cada sprint** completado
- ✅ **Al implementar nuevas funcionalidades**
- ✅ **Al resolver problemas técnicos**
- ✅ **Al cambiar la arquitectura del sistema**
- ✅ **Al actualizar el roadmap**

### **Qué Mantener Actualizado:**
- **README.md**: Estado general y funcionalidades
- **API_ENDPOINTS.md**: Nuevos endpoints implementados
- **BASE_DATOS.md**: Cambios en esquema de base de datos
- **FRONTEND_GUIA.md**: Nuevas funcionalidades del frontend
- **ROADMAP.md**: Progreso de sprints y fechas

### **Formato de Actualización:**
- **Fecha de actualización** en cada documento
- **Versión del sistema** actualizada
- **Progreso porcentual** actualizado
- **Checklist** de funcionalidades actualizado
- **Log de cambios** en README.md

---

## 🔗 Enlaces Útiles

### **Documentación Externa:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### **Herramientas del Proyecto:**
- **API Docs**: `http://localhost:8000/docs`
- **Cliente Web**: `http://localhost:8000/cliente-web`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

---

**Última actualización del índice**: Diciembre 2024  
**Versión del sistema**: 3.0.0  
**Estado de la documentación**: 100% actualizada
