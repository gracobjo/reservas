# 🎨 Guía del Frontend

## 📋 Información General

- **URL de acceso**: `http://localhost:8000/cliente-web`
- **Framework**: HTML5 + CSS3 + JavaScript ES6+
- **UI Library**: Bootstrap 5
- **Iconos**: Font Awesome 6
- **Almacenamiento**: localStorage para persistencia local

## 🏗️ Estructura de la Aplicación

### **Archivos Principales**
- `static/index.html` - Estructura HTML principal
- `static/app.js` - Lógica de la aplicación JavaScript
- `static/styles.css` - Estilos y animaciones personalizadas

### **Clase Principal: `PreciosDinamicosApp`**
La aplicación está construida como una clase JavaScript que maneja toda la funcionalidad:

```javascript
class PreciosDinamicosApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentData = { services: [], resources: [], rules: [] };
        this.calculationHistory = [];
        this.notificationSettings = { /* ... */ };
        this.init();
    }
}
```

## 🎯 Pestañas Principales

### 1. **🏠 Dashboard**
Panel principal con estadísticas del sistema.

**Componentes:**
- **Tarjetas de estadísticas**: Total de reglas, reglas activas, servicios, recursos
- **Lista de reglas recientes**: Últimas 5 reglas creadas
- **Estado de la API**: Indicador de conexión

**Funcionalidades:**
- Actualización automática de estadísticas
- Exportación de datos a JSON
- Navegación rápida a otras secciones

### 2. **🧮 Calculadora**
Herramienta principal para calcular precios con reglas dinámicas.

**Formulario de entrada:**
- **Servicio**: Selector de servicios disponibles
- **Recurso**: Selector de recursos compatibles
- **Fecha y Hora**: Selector de fecha y hora de inicio
- **Duración**: Input numérico con selector de unidad (horas/días/noches)
- **Participantes**: Selector de número de personas
- **Tipo de Cliente**: Selector de tipo (regular, VIP, premium)

**Validaciones implementadas:**
- Habitaciones individuales: máximo 1 persona
- Habitaciones dobles: máximo 2 personas
- Duración por noches: solo números enteros
- Compatibilidad servicio-recurso

**Resultado del cálculo:**
- Precio base y precio final
- Diferencia y porcentaje de cambio
- Lista de reglas aplicadas
- Detalles de la reserva

### 3. **📋 Historial**
Registro de todos los cálculos realizados.

**Funcionalidades:**
- **Lista de cálculos**: Servicio, recurso, fecha, precio
- **Repetir cálculo**: Rellenar formulario con datos anteriores
- **Exportar a CSV**: Descarga de historial completo
- **Limpiar historial**: Eliminación de todos los registros

**Almacenamiento:**
- Persistencia en localStorage
- Máximo 10 elementos en historial
- Datos estructurados con timestamps

### 4. **⚙️ Notificaciones**
Sistema completo de gestión de notificaciones.

**Configuración general:**
- Confirmaciones automáticas
- Recordatorios programados
- Alertas del sistema
- Tiempo de auto-dismiss

**Configuración avanzada:**
- Sonidos de notificación
- Notificaciones del escritorio
- Notificaciones prioritarias
- Permisos del navegador

**Historial de notificaciones:**
- Lista de notificaciones importantes
- Estado leído/no leído
- Estadísticas de uso
- Exportación de configuración

## 🔧 Funcionalidades del Sistema

### **Sistema de Precios Dinámicos**
- **Cálculo en tiempo real** de precios
- **Aplicación automática** de reglas activas
- **Validación de compatibilidad** entre servicios y recursos
- **Formato de moneda español** (€ con comas decimales)

### **Validaciones de Negocio**
- **Habitaciones individuales**: Solo 1 persona
- **Habitaciones dobles**: Máximo 2 personas
- **Duración por noches**: Números enteros para habitaciones
- **Duración por horas**: Decimales permitidos para otros servicios

### **Sistema de Notificaciones**
- **Alertas visuales** con animaciones
- **Confirmaciones automáticas** para acciones críticas
- **Recordatorios programados** (diarios, semanales)
- **Notificaciones del navegador** (opcional)

### **Gestión de Datos**
- **Carga automática** de servicios y recursos
- **Limpieza de duplicados** en selectores
- **Persistencia local** del historial
- **Exportación de datos** (CSV, JSON)

## 🎨 Componentes de UI

### **Alertas y Notificaciones**
```javascript
// Mostrar alerta
this.showAlert('Mensaje de éxito', 'success');

// Mostrar notificación
this.showNotification('Regla aplicada', 'info', 4000);

// Mostrar confirmación
if (confirm('¿Estás seguro?')) {
    // Acción confirmada
}
```

### **Formateo de Datos**
```javascript
// Formato de moneda español
this.formatCurrency(1234.56); // "1.234,56 €"

// Formato numérico español
this.formatNumber(1234567); // "1.234.567"

// Formato de fecha
new Date().toLocaleString('es-ES');
```

### **Gestión del Historial**
```javascript
// Agregar al historial
this.addToHistory(formData, result);

// Repetir cálculo
this.repeatCalculation(historyId);

// Limpiar historial
this.clearHistory();

// Exportar a CSV
this.exportHistoryToCSV();
```

## 🚀 Flujo de Uso Típico

### **1. Configuración Inicial**
1. Acceder a `http://localhost:8000/cliente-web`
2. Verificar conexión a la API (indicador verde)
3. Configurar preferencias de notificaciones
4. Revisar estadísticas del dashboard

### **2. Cálculo de Precio**
1. Ir a la pestaña "Calculadora"
2. Seleccionar servicio (ej: "Alquiler Habitación Individual")
3. Seleccionar recurso (ej: "Habitación 101 - Individual")
4. Elegir fecha y hora de inicio
5. Establecer duración (ej: 2 noches)
6. Seleccionar número de participantes (1 para individual)
7. Elegir tipo de cliente
8. Hacer clic en "Calcular Precio"

### **3. Revisión de Resultados**
1. Ver precio base y precio final
2. Revisar reglas aplicadas (ej: recargo fin de semana)
3. Verificar detalles de la reserva
4. Guardar en historial (automático)

### **4. Gestión del Historial**
1. Ir a pestaña "Historial"
2. Revisar cálculos anteriores
3. Repetir cálculos si es necesario
4. Exportar datos a CSV

## 🔍 Solución de Problemas

### **Problemas Comunes**

#### **1. Selectores Vacíos**
- **Síntoma**: Los selectores de servicio/recurso están vacíos
- **Solución**: Verificar conexión a la API y recargar la página
- **Prevención**: Revisar logs de la consola del navegador

#### **2. Errores de Validación**
- **Síntoma**: Mensajes de error al calcular precios
- **Solución**: Verificar compatibilidad entre servicio y recurso
- **Prevención**: Seguir las reglas de validación implementadas

#### **3. Notificaciones No Funcionan**
- **Síntoma**: No se muestran notificaciones
- **Solución**: Verificar configuración en pestaña "Notificaciones"
- **Prevención**: Configurar preferencias al inicio

#### **4. Historial No Se Guarda**
- **Síntoma**: Los cálculos no aparecen en el historial
- **Solución**: Verificar localStorage del navegador
- **Prevención**: No usar modo incógnito

### **Logs de Depuración**
La aplicación incluye logs detallados para depuración:

```javascript
console.log('🔍 populateSelectors llamado');
console.log('🔍 Servicios disponibles:', this.currentData.services.length);
console.log('🔍 Datos que se envían a la API:', formData);
```

## 📱 Responsividad

### **Breakpoints de Bootstrap 5**
- **Extra small**: < 576px (móviles)
- **Small**: ≥ 576px (móviles grandes)
- **Medium**: ≥ 768px (tablets)
- **Large**: ≥ 992px (desktops)
- **Extra large**: ≥ 1200px (desktops grandes)

### **Adaptaciones Móviles**
- **Navegación**: Tabs colapsables en móviles
- **Formularios**: Campos apilados verticalmente
- **Resultados**: Diseño optimizado para pantallas pequeñas
- **Notificaciones**: Posicionamiento adaptativo

## 🔒 Seguridad y Privacidad

### **Datos Locales**
- **Historial**: Almacenado solo en el navegador del usuario
- **Configuración**: Preferencias guardadas localmente
- **No se envían** datos personales al servidor

### **Validaciones**
- **Frontend**: Validaciones en tiempo real para mejor UX
- **Backend**: Validaciones de seguridad en la API
- **Doble verificación** de datos críticos

## 🚀 Mejoras Futuras

### **Funcionalidades Pendientes**
- **Calendario visual** de disponibilidad
- **Sistema de pagos** integrado
- **Notificaciones por email** y SMS
- **Modo offline** con sincronización
- **Temas personalizables** (claro/oscuro)

### **Optimizaciones Técnicas**
- **Service Workers** para funcionalidad offline
- **WebSockets** para actualizaciones en tiempo real
- **PWA** (Progressive Web App) capabilities
- **Lazy loading** de componentes pesados

## 📚 Referencias

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [JavaScript ES6+ Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [localStorage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
