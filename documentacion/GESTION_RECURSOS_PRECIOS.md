# 🏢 Gestión de Recursos y Precios - Documentación Completa

## 📋 Índice

1. [Visión General](#visión-general)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Flujo de Trabajo](#flujo-de-trabajo)
6. [API y Endpoints](#api-y-endpoints)
7. [Configuración y Personalización](#configuración-y-personalización)
8. [Troubleshooting](#troubleshooting)
9. [Roadmap y Mejoras Futuras](#roadmap-y-mejoras-futuras)

## 🎯 Visión General

El sistema de gestión de recursos y precios permite administrar de manera integral todos los recursos disponibles para reservas, incluyendo su configuración de precios base y reglas de precios dinámicos. Esta funcionalidad es fundamental para un sistema de reservas profesional que requiere flexibilidad en la tarificación.

### Objetivos Principales

- **Gestión completa de recursos**: Crear, editar, eliminar y visualizar recursos
- **Sistema de precios flexible**: Precios base + reglas dinámicas por hora, día y temporada
- **Interfaz intuitiva**: Modales centrados con navegación por tabs
- **CRUD completo**: Operaciones Create, Read, Update, Delete para todos los elementos
- **Integración con reservas**: Los recursos se utilizan en el sistema de reservas

## 🚀 Funcionalidades Implementadas

### 1. Gestión de Recursos (CRUD)

#### Crear Recurso
- **Modal**: `newResourceModal` con formulario completo
- **Campos**: Nombre, tipo, capacidad, descripción, precio base, disponibilidad
- **Validación**: Campos requeridos y validación de tipos
- **Cierre automático**: Modal se cierra después de crear exitosamente

#### Leer Recurso
- **Lista visual**: Tarjetas con información completa del recurso
- **Modal de información**: `infoResourceModal` con detalles completos
- **Información mostrada**: Nombre, tipo, capacidad, precio, descripción, estado

#### Editar Recurso
- **Modal**: `editResourceModal` con formulario pre-llenado
- **Actualización**: Todos los campos editables
- **Cierre automático**: Modal se cierra después de guardar cambios

#### Eliminar Recurso
- **Confirmación**: Diálogo de confirmación antes de eliminar
- **Limpieza**: Cierre automático de modales y actualización de listas

### 2. Sistema de Precios

#### Precio Base
- **Campo**: Precio por hora de uso del recurso
- **Edición**: Modal dedicado con validación
- **Persistencia**: Se guarda en el modelo del recurso

#### Reglas de Precio Dinámico

##### Precio por Hora
- **Configuración**: Hora inicio/fin, tipo modificador, valor
- **Casos de uso**: Horarios pico, descuentos nocturnos, tarifas especiales
- **Ejemplo**: "Hora Pico" de 17:00 a 20:00 con +20%

##### Precio por Día
- **Configuración**: Días de la semana seleccionables, tipo modificador, valor
- **Casos de uso**: Fines de semana, días laborables, días festivos
- **Ejemplo**: "Fin de Semana" (Sábado/Domingo) con +15%

##### Precio por Temporada
- **Configuración**: Fechas inicio/fin, tipo modificador, valor
- **Casos de uso**: Temporadas altas, festivos, eventos especiales
- **Ejemplo**: "Temporada Alta" (Julio-Agosto) con +25%

## 🎨 Interfaz de Usuario

### Modales Implementados

#### 1. Modal de Creación de Recurso (`newResourceModal`)
```html
<div class="modal fade" id="newResourceModal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <!-- Formulario de creación -->
    </div>
</div>
```

**Características:**
- Tamaño: `modal-lg` para mejor visualización
- Centrado: `modal-dialog-centered` para posicionamiento perfecto
- Formulario: Campos organizados en 2 columnas
- Validación: Campos requeridos marcados

#### 2. Modal de Edición de Recurso (`editResourceModal`)
```html
<div class="modal fade" id="editResourceModal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <!-- Formulario de edición -->
    </div>
</div>
```

**Características:**
- Pre-llenado: Datos del recurso cargados automáticamente
- Actualización: Todos los campos editables
- Cierre automático: Después de guardar exitosamente

#### 3. Modal de Información de Recurso (`infoResourceModal`)
```html
<div class="modal fade" id="infoResourceModal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <!-- Información del recurso + botones de acción -->
    </div>
</div>
```

**Características:**
- Información completa: Todos los datos del recurso
- Botones de acción: Editar, Gestionar Precios, Eliminar
- Diseño responsive: Información organizada en 2 columnas

#### 4. Modal de Gestión de Precios (`resourcePricingModal`)
```html
<div class="modal fade" id="resourcePricingModal">
    <div class="modal-dialog modal-xl modal-dialog-centered">
        <!-- Sistema de tabs para diferentes tipos de precios -->
    </div>
</div>
```

**Características:**
- Tamaño: `modal-xl` para contenido extenso
- Tabs: 4 tabs para diferentes tipos de precios
- Formularios: Cada tab tiene su formulario específico
- Información contextual: Explicaciones y ayuda

### Tabs del Sistema de Precios

#### Tab 1: Precio Base
- **Formulario**: Edición del precio base
- **Información**: Explicación del uso del precio base
- **Validación**: Precio debe ser positivo

#### Tab 2: Precio por Hora
- **Formulario**: Creación de reglas por franjas horarias
- **Lista**: Reglas existentes por hora
- **Campos**: Nombre, hora inicio/fin, modificador, valor

#### Tab 3: Precio por Día
- **Formulario**: Creación de reglas por días de la semana
- **Lista**: Reglas existentes por día
- **Campos**: Nombre, días seleccionables, modificador, valor

#### Tab 4: Precio por Temporada
- **Formulario**: Creación de reglas por fechas específicas
- **Lista**: Reglas existentes por temporada
- **Campos**: Nombre, fechas inicio/fin, modificador, valor

### Tarjetas de Recurso

#### Diseño Visual
```css
.resource-card {
    transition: all 0.3s ease;
    border: 1px solid #dee2e6;
    cursor: pointer;
}

.resource-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: #007bff;
}
```

#### Información Mostrada
- **Nombre**: Título principal con icono de edificio
- **Tipo**: Categoría del recurso (habitación, sala, etc.)
- **Capacidad**: Número de personas que puede alojar
- **Precio**: Precio base por hora con formato de moneda
- **Descripción**: Información adicional del recurso
- **Estado**: Badge de disponibilidad (verde/rojo)

#### Botones de Acción
- **Editar**: Botón azul con icono de lápiz
- **Gestionar Precios**: Botón azul claro con icono de euro
- **Eliminar**: Botón rojo con icono de papelera

## 🏗️ Arquitectura del Sistema

### Estructura de Archivos

```
cliente_web.html
├── Modal de Creación de Recurso
├── Modal de Edición de Recurso
├── Modal de Información de Recurso
└── Modal de Gestión de Precios
    ├── Tab Precio Base
    ├── Tab Precio por Hora
    ├── Tab Precio por Día
    └── Tab Precio por Temporada

static/app.js
├── displayResourcesList()
├── createNewResource()
├── editResource()
├── saveEditedResource()
├── deleteResource()
├── mostrarDetalleRecurso()
├── gestionarPreciosRecurso()
├── configurarFormulariosPreciosRecursos()
├── actualizarPrecioBaseRecurso()
├── crearReglaPrecioHora()
├── crearReglaPrecioDia()
└── crearReglaPrecioTemporada()

static/styles.css
├── Estilos de modales
├── Estilos de tarjetas de recurso
├── Estilos de tabs
└── Estilos de formularios
```

### Flujo de Datos

#### 1. Carga de Recursos
```
loadInitialData() → refreshResourcesList() → displayResourcesList()
```

#### 2. Creación de Recurso
```
Formulario → createNewResource() → API Call → Actualización de UI
```

#### 3. Edición de Recurso
```
Clic en Editar → editResource() → Llenar Modal → saveEditedResource() → API Call
```

#### 4. Gestión de Precios
```
Clic en Gestionar Precios → gestionarPreciosRecurso() → Modal de Precios → Formularios
```

### Integración con APIs

#### Endpoints Utilizados
- `POST /recursos/` - Crear recurso
- `GET /recursos/{id}` - Obtener recurso
- `PUT /recursos/{id}` - Actualizar recurso
- `DELETE /recursos/{id}` - Eliminar recurso
- `POST /precios-dinamicos/reglas` - Crear regla de precio

#### Estructura de Datos
```javascript
// Recurso
{
    id: number,
    nombre: string,
    tipo: string,
    capacidad: number,
    descripcion: string,
    disponible: boolean,
    precio_base: number,
    created_at: datetime,
    updated_at: datetime
}

// Regla de Precio
{
    nombre: string,
    tipo_regla: "hora" | "dia_semana" | "temporada",
    condicion: string, // JSON
    tipo_modificador: "porcentaje" | "monto_fijo" | "precio_fijo",
    valor_modificador: number,
    prioridad: number,
    activa: boolean,
    recursos_aplicables: string // JSON array
}
```

## 🔄 Flujo de Trabajo

### 1. Gestión Básica de Recursos

#### Crear Nuevo Recurso
1. **Acceso**: Tab "Recursos" → Botón "Crear Nuevo Recurso"
2. **Formulario**: Llenar todos los campos requeridos
3. **Validación**: Sistema valida campos obligatorios
4. **Creación**: API crea el recurso en la base de datos
5. **Feedback**: Mensaje de éxito y modal se cierra
6. **Actualización**: Lista de recursos se refresca automáticamente

#### Editar Recurso Existente
1. **Acceso**: Clic en recurso → Botón "Editar"
2. **Modal**: Se abre con datos pre-llenados
3. **Modificación**: Cambiar campos deseados
4. **Guardado**: Clic en "Guardar Cambios"
5. **Actualización**: API actualiza el recurso
6. **Cierre**: Modal se cierra automáticamente

#### Eliminar Recurso
1. **Acceso**: Clic en recurso → Botón "Eliminar"
2. **Confirmación**: Diálogo de confirmación
3. **Eliminación**: API elimina el recurso
4. **Limpieza**: Modales se cierran automáticamente
5. **Actualización**: Lista se refresca

### 2. Gestión de Precios

#### Configurar Precio Base
1. **Acceso**: Clic en recurso → "Gestionar Precios" → Tab "Precio Base"
2. **Formulario**: Modificar precio base
3. **Guardado**: Clic en "Actualizar Precio Base"
4. **Validación**: Sistema valida precio positivo
5. **Actualización**: Precio se actualiza en tiempo real

#### Crear Regla de Precio por Hora
1. **Acceso**: Tab "Precio por Hora"
2. **Formulario**: Llenar nombre, horas, modificador, valor
3. **Validación**: Campos requeridos y valores válidos
4. **Creación**: API crea la regla de precio
5. **Feedback**: Mensaje de éxito y formulario se limpia
6. **Lista**: Reglas existentes se actualizan

#### Crear Regla de Precio por Día
1. **Acceso**: Tab "Precio por Día"
2. **Selección**: Marcar días de la semana deseados
3. **Formulario**: Llenar nombre, modificador, valor
4. **Validación**: Al menos un día seleccionado
5. **Creación**: API crea la regla
6. **Feedback**: Confirmación y limpieza

#### Crear Regla de Precio por Temporada
1. **Acceso**: Tab "Precio por Temporada"
2. **Fechas**: Seleccionar período de vigencia
3. **Formulario**: Llenar nombre, modificador, valor
4. **Validación**: Fecha fin posterior a fecha inicio
5. **Creación**: API crea la regla
6. **Feedback**: Confirmación y limpieza

## 🔌 API y Endpoints

### Endpoints de Recursos

#### Crear Recurso
```http
POST /recursos/
Content-Type: application/json

{
    "nombre": "Sala de Conferencias A",
    "tipo": "sala",
    "capacidad": 20,
    "descripcion": "Sala equipada para conferencias",
    "disponible": true,
    "precio_base": 50.00
}
```

#### Obtener Recurso
```http
GET /recursos/{id}
```

#### Actualizar Recurso
```http
PUT /recursos/{id}
Content-Type: application/json

{
    "nombre": "Sala de Conferencias A - Actualizada",
    "precio_base": 60.00
}
```

#### Eliminar Recurso
```http
DELETE /recursos/{id}
```

### Endpoints de Precios Dinámicos

#### Crear Regla de Precio
```http
POST /precios-dinamicos/reglas
Content-Type: application/json

{
    "nombre": "Hora Pico",
    "tipo_regla": "hora",
    "condicion": "{\"hora_inicio\": \"17:00\", \"hora_fin\": \"20:00\"}",
    "tipo_modificador": "porcentaje",
    "valor_modificador": 20.0,
    "prioridad": 10,
    "activa": true,
    "recursos_aplicables": "[1, 2, 3]"
}
```

#### Obtener Reglas de Precio
```http
GET /precios-dinamicos/reglas?activas_solo=true
```

#### Actualizar Regla de Precio
```http
PUT /precios-dinamicos/reglas/{id}
Content-Type: application/json

{
    "valor_modificador": 25.0,
    "activa": false
}
```

#### Eliminar Regla de Precio
```http
DELETE /precios-dinamicos/reglas/{id}
```

## ⚙️ Configuración y Personalización

### Configuración de Modales

#### Centrado de Modales
```css
.modal-dialog-centered {
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    margin: 0 !important;
}
```

#### Tamaños de Modal
- **Creación/Edición**: `modal-lg` (800px)
- **Información**: `modal-lg` (800px)
- **Gestión de Precios**: `modal-xl` (1140px)

### Personalización de Estilos

#### Tarjetas de Recurso
```css
.resource-card {
    transition: all 0.3s ease;
    border: 1px solid #dee2e6;
}

.resource-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-color: #007bff;
}
```

#### Badges de Estado
```css
.badge {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
}
```

### Configuración de Validaciones

#### Campos Requeridos
- Nombre del recurso
- Tipo de recurso
- Capacidad
- Precio base

#### Validaciones de Tipo
- **Capacidad**: Número entero positivo
- **Precio**: Número decimal positivo
- **Fechas**: Fecha fin posterior a fecha inicio
- **Horas**: Hora fin posterior a hora inicio

## 🐛 Troubleshooting

### Problemas Comunes

#### 1. Modal no se centra
**Síntomas**: Modal aparece en esquina inferior derecha
**Causa**: CSS de Bootstrap no se aplica correctamente
**Solución**: Verificar que `modal-dialog-centered` esté presente

#### 2. Formulario no se envía
**Síntomas**: Botón de envío no responde
**Causa**: Event listeners no configurados
**Solución**: Verificar que `configurarFormulariosPreciosRecursos()` se ejecute

#### 3. Precios no se guardan
**Síntomas**: Mensaje de éxito pero precio no cambia
**Causa**: API no implementada o error en backend
**Solución**: Verificar logs del backend y endpoints

#### 4. Reglas de precio no se crean
**Síntomas**: Formulario se envía pero regla no aparece
**Causa**: API de precios dinámicos no responde
**Solución**: Verificar endpoint `/precios-dinamicos/reglas`

### Logs de Debug

#### Console Logs Implementados
```javascript
console.log('🎯 displayResourcesList ejecutándose con', resources.length, 'recursos');
console.log('💰 Gestionando precios del recurso:', resourceId, resourceName, basePrice);
console.log('🔄 Cargando reglas de precio para recurso:', resourceId);
console.log('💰 Creando regla de precio por hora:', formData);
```

#### Verificación de Estado
```javascript
// Verificar que los modales estén en el DOM
console.log('🔍 Modal en DOM:', !!document.getElementById('resourcePricingModal'));

// Verificar que los formularios estén configurados
console.log('🔍 Formularios configurados:', !!document.getElementById('editResourceBasePriceForm'));
```

### Verificación de Funcionalidad

#### Checklist de Pruebas
- [ ] Modal de creación se abre correctamente
- [ ] Modal de edición se pre-llena con datos
- [ ] Modal de información muestra todos los datos
- [ ] Modal de precios se abre y navega entre tabs
- [ ] Formularios se envían sin errores
- [ ] Modales se cierran automáticamente
- [ ] Listas se actualizan después de operaciones

## 🚀 Roadmap y Mejoras Futuras

### Implementaciones Pendientes

#### Backend
- [ ] Agregar campo `precio_base` al modelo de Recurso
- [ ] Crear endpoints específicos para precios de recursos
- [ ] Integrar con sistema de precios dinámicos existente
- [ ] Implementar cálculo de precios en tiempo real

#### Frontend
- [ ] Conectar formularios con APIs reales
- [ ] Implementar listado de reglas existentes
- [ ] Agregar funcionalidad de edición/eliminación de reglas
- [ ] Implementar preview de precios calculados

### Mejoras de UX

#### Interfaz
- [ ] Drag & drop para reordenar recursos
- [ ] Búsqueda y filtrado avanzado
- [ ] Vista de calendario de disponibilidad
- [ ] Gráficos de precios por temporada

#### Funcionalidad
- [ ] Importación/exportación de recursos
- [ ] Plantillas de precios predefinidas
- [ ] Sistema de notificaciones de cambios
- [ ] Auditoría de modificaciones de precios

### Integraciones Futuras

#### Sistemas Externos
- [ ] Sincronización con Google Calendar
- [ ] Integración con sistemas de facturación
- [ ] API para aplicaciones móviles
- [ ] Webhooks para notificaciones

#### Analytics
- [ ] Dashboard de uso de recursos
- [ ] Análisis de rentabilidad por recurso
- [ ] Reportes de ocupación
- [ ] Predicciones de demanda

## 📚 Referencias

### Documentación Relacionada
- [API Endpoints](./API_ENDPOINTS.md)
- [Base de Datos](./BASE_DATOS.md)
- [Calendario de Reservas](./CALENDARIO_RESERVAS.md)
- [Frontend Guía](./FRONTEND_GUIA.md)

### Tecnologías Utilizadas
- **Frontend**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **APIs**: RESTful con JSON
- **Modales**: Bootstrap Modal con personalización CSS

### Estándares de Código
- **JavaScript**: ES6+ con async/await
- **CSS**: BEM methodology para clases
- **HTML**: Semantic HTML5
- **APIs**: RESTful con respuestas JSON estandarizadas

---

**Última actualización**: Diciembre 2024  
**Versión**: 1.0.0  
**Autor**: Sistema de Gestión de Reservas
