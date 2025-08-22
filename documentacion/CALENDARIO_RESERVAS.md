# 📅 Funcionalidades del Calendario y Reservas

## Índice
1. [Resumen General](#resumen-general)
2. [Funcionalidades del Calendario](#funcionalidades-del-calendario)
3. [Modal de Reservas desde Calendario](#modal-de-reservas-desde-calendario)
4. [Gestión de Reservas](#gestión-de-reservas)
5. [Correcciones de Zona Horaria](#correcciones-de-zona-horaria)
6. [Flujo Completo de Reserva](#flujo-completo-de-reserva)
7. [Integración con API](#integración-con-api)

---

## Resumen General

El sistema de calendario y reservas permite a los gestores crear, visualizar y administrar reservas de forma intuitiva directamente desde una interfaz de calendario. Incluye funcionalidades avanzadas como reservas múltiples, cálculo automático de duración y sincronización en tiempo real.

---

## Funcionalidades del Calendario

### 🗓️ Vista Mensual
- **Visualización**: Grid de 7x6 celdas representando días del mes
- **Navegación**: Botones para mes anterior/siguiente y "Ir a Hoy"
- **Estados de celda**:
  - Días del mes actual
  - Días de otros meses (sombreados)
  - Día actual (resaltado)
  - Días con reservas (muestra reservas)
  - Días disponibles (botón "Hacer Reserva")

### 📋 Vista Semanal
- **Visualización**: Grid por horas (08:00-20:00) x días de la semana
- **Granularidad**: Slots de 1 hora
- **Estados de celda**:
  - Horas con reservas (muestra detalles)
  - Horas disponibles (botón "Hacer Reserva")
  - Cabecera con días de la semana

### 🔄 Navegación del Calendario
```javascript
// Funciones de navegación
navegarCalendario(direccion)  // anterior/siguiente
irHoy()                      // ir a fecha actual
cambiarVistaCalendario(vista) // mensual/semanal/diaria
```

### 📊 Visualización de Reservas
- **Colores por estado**:
  - 🟢 Confirmada: Verde
  - 🟡 Pendiente: Amarillo
  - 🔴 Cancelada: Rojo
  - 🔵 Completada: Azul
- **Información mostrada**:
  - Nombre del cliente
  - Nombre del servicio
  - Hora (en vista semanal)

### 🔍 Filtros del Calendario
- **Por servicio**: Filtrar reservas de un servicio específico
- **Por recurso**: Filtrar reservas de un recurso específico
- **Aplicación en tiempo real**: Los filtros se aplican inmediatamente

---

## Modal de Reservas desde Calendario

### 🎯 Apertura del Modal
- **Desde calendario mensual**: Click en celda disponible → Modal con fecha seleccionada
- **Desde calendario semanal**: Click en celda disponible → Modal con fecha y hora específica

### 📝 Formulario de Reserva
#### Campos Obligatorios:
- **Cliente**: Selector poblado automáticamente desde API
- **Servicio**: Selector con servicios disponibles (incluye precio y duración)
- **Recurso**: Selector con recursos disponibles
- **Fecha y Hora de Inicio**: Pre-rellenada según selección del calendario
- **Fecha y Hora de Fin**: Calculada automáticamente según duración del servicio
- **Estado**: Confirmada, Pendiente, Cancelada, Completada

#### ⚡ Cálculo Automático de Duración
```javascript
// Al seleccionar un servicio, se recalcula automáticamente la fecha de fin
calcularFechaFinDesdeServicio() {
    const duracionMinutos = parseInt(selectedOption.getAttribute('data-duracion'));
    const fechaFin = new Date(fechaInicio);
    fechaFin.setMinutes(fechaInicio.getMinutes() + duracionMinutos);
}
```

### 🔄 Opciones de Reserva Múltiple
#### Reserva de Múltiples Días:
- **Configuración**: Días adicionales (1-30)
- **Funcionamiento**: Crea reservas consecutivas con la misma hora
- **Ejemplo**: Reserva del 1-5 agosto a las 09:00

#### Reserva Recurrente:
- **Tipos**: Diaria, Semanal, Mensual
- **Configuración**: Tipo de recurrencia seleccionable
- **Funcionamiento**: Crea múltiples reservas según patrón

#### Bloquear Período Completo:
- **Uso**: Para mantenimiento o eventos especiales
- **Funcionamiento**: Marca período como no disponible

### 🧮 Botón Manual de Recálculo
- **Ubicación**: Junto al campo "Fecha y Hora de Fin"
- **Función**: Recalcula fecha de fin basándose en servicio seleccionado
- **Uso**: Backup en caso de que el cálculo automático falle

---

## Gestión de Reservas

### 📋 Lista de Reservas
- **Endpoint**: `/reservas/listar`
- **Funcionalidades**:
  - Visualización en tabla
  - Edición de reservas existentes
  - Eliminación de reservas
  - Filtros por cliente, servicio, recurso

### 🔄 Sincronización Automática
- **Después de crear reserva**: El calendario se actualiza automáticamente
- **Después de editar/eliminar**: Sincronización en tiempo real
- **Función**: `actualizarCalendario()` - Recarga reservas y re-renderiza

### 📊 Estados de Reserva
```javascript
const estadosReserva = {
    'confirmada': 'success',  // Verde
    'pendiente': 'warning',   // Amarillo  
    'cancelada': 'danger',    // Rojo
    'completada': 'info'      // Azul
};
```

---

## Correcciones de Zona Horaria

### 🔧 Problema Identificado
- **Issue**: JavaScript `toISOString()` convierte fechas a UTC
- **Síntoma**: Reservas aparecen en día incorrecto (±1 día)
- **Afectaba**: Calendario, modal de reservas, cálculo de duración

### ✅ Solución Implementada
#### Formato Local Sin Conversión UTC:
```javascript
// ANTES (Problemático):
fecha.toISOString().split('T')[0]  // Conversión UTC

// AHORA (Correcto):
const fechaStr = fecha.getFullYear() + '-' + 
                String(fecha.getMonth() + 1).padStart(2, '0') + '-' + 
                String(fecha.getDate()).padStart(2, '0');
```

#### Funciones Corregidas:
- `abrirModalReservaDesdeCalendario()` - Fechas del modal
- `calcularFechaFinDesdeServicio()` - Cálculo de duración
- `getReservasDelDia()` - Filtrado de reservas por día
- `getReservasEnHora()` - Filtrado de reservas por hora
- `renderizarVistaMensual()` - Generación de fechas en calendario
- `renderizarVistaSemanal()` - Generación de fechas en calendario

---

## Flujo Completo de Reserva

### 1. 🎯 Selección desde Calendario
```
Usuario hace click en celda disponible
   ↓
Modal se abre con fecha/hora pre-rellenada
   ↓
Selectores se pueblan automáticamente
```

### 2. 📝 Completar Formulario
```
Seleccionar cliente → Campo obligatorio
   ↓
Seleccionar servicio → Cálculo automático de fecha fin
   ↓
Seleccionar recurso → Validación de disponibilidad
   ↓
Revisar fechas → Ajustar si necesario
   ↓
Configurar opciones múltiples → Si aplica
```

### 3. ✅ Validaciones
```javascript
// Validaciones antes de crear reserva:
- Todos los campos obligatorios completos
- Fecha fin posterior a fecha inicio  
- Duración coincide con servicio seleccionado
- Recurso disponible en horario seleccionado
```

### 4. 🚀 Creación y Sincronización
```
Envío a API /reservas/ (POST)
   ↓
Validación del backend
   ↓
Creación exitosa
   ↓
Modal se cierra automáticamente
   ↓
Calendario se actualiza
   ↓
Reserva aparece en calendario
   ↓
Disponible en Gestión de Reservas
```

---

## Integración con API

### 📡 Endpoints Utilizados

#### Reservas:
- `GET /reservas/listar` - Listar todas las reservas
- `POST /reservas/` - Crear nueva reserva
- `PUT /reservas/{id}` - Actualizar reserva
- `DELETE /reservas/{id}` - Eliminar reserva

#### Datos Maestros:
- `GET /clientes/` - Listar clientes
- `GET /servicios/` - Listar servicios (con duración)
- `GET /recursos/` - Listar recursos

### 🔄 Manejo de Errores
```javascript
try {
    const newReserva = await this.apiCall('/reservas/', 'POST', formData);
    // Éxito: actualizar calendario
} catch (error) {
    // Error: mostrar mensaje al usuario
    this.showCalendarioReservaMessage('Error al crear la reserva', 'danger');
}
```

### ⚡ Optimización
- **Carga inicial**: Todas las reservas se cargan una vez
- **Filtrado local**: Los filtros se aplican en cliente (no requieren API)
- **Caché de datos**: Servicios, recursos y clientes se cargan una vez

---

## Versiones y Evolución

### 🚀 Historial de Versiones

#### v2.9 - Calendario UTC Corregido
- ✅ Corregidas fechas en `getReservasDelDia()` y `getReservasEnHora()`
- ✅ Reservas aparecen en día correcto del calendario

#### v2.8 - Modal UTC Corregido  
- ✅ Corregida conversión UTC en `calcularFechaFinDesdeServicio()`
- ✅ Fechas de fin calculadas correctamente

#### v2.7 - Botón Manual de Recálculo
- ✅ Agregado botón 🧮 para recalcular fecha de fin manualmente
- ✅ Event listeners mejorados con limpieza automática

#### v2.6 - Cálculo Mejorado
- ✅ Logs de diagnóstico detallados
- ✅ Validaciones adicionales en cálculo de duración

#### v2.5 - Variable Corregida
- ✅ Corregido error `fechaFinStr is not defined`

#### v2.4 - Duración Automática
- ✅ Implementado cálculo automático de duración basado en servicio
- ✅ Event listener para recálculo al cambiar servicio

#### v2.3 - UTC Corregido (Primera iteración)
- ✅ Corregidas fechas en calendario mensual y semanal

#### v2.2 - Fechas Corregidas
- ✅ Implementado manejo de fechas sin problemas de zona horaria

#### v2.1 - Variables Corregidas
- ✅ Corregidos errores de inicialización de variables

#### v2.0 - Logs Adicionales
- ✅ Sistema de logs para debugging
- ✅ Creación del objeto `formData`

---

## 🎯 Características Destacadas

### ✨ Usabilidad
- **Interfaz intuitiva**: Click directo en calendario para crear reservas
- **Cálculo automático**: Duración basada en servicio seleccionado
- **Feedback visual**: Estados de reserva claramente diferenciados
- **Navegación fluida**: Entre vistas y períodos de tiempo

### 🔧 Robustez Técnica
- **Manejo de zona horaria**: Sin problemas de conversión UTC
- **Validaciones múltiples**: En frontend y backend
- **Manejo de errores**: Con mensajes claros al usuario
- **Logs de diagnóstico**: Para debugging y monitoreo

### ⚡ Performance
- **Carga optimizada**: Datos maestros cargados una vez
- **Filtrado local**: Sin llamadas adicionales a API
- **Actualización selectiva**: Solo se re-renderiza cuando es necesario

### 🔄 Escalabilidad
- **Arquitectura modular**: Funciones bien separadas
- **Extensible**: Fácil agregar nuevos tipos de reserva
- **Mantenible**: Código documentado y estructurado

---

*Documentación generada el 22 de agosto de 2025 - Versión 2.9*
