# 🌐 Cliente Web para Sistema de Precios Dinámicos

Este cliente web proporciona una interfaz visual e interactiva para probar y gestionar el sistema de precios dinámicos de la API de reservas.

## 🚀 Características

### 📊 Dashboard
- **Estadísticas en tiempo real**: Total de reglas, reglas activas, servicios y recursos
- **Gráficos interactivos**: Distribución de reglas por tipo y modificador
- **Lista de reglas recientes**: Las 5 reglas más recientes con estado visual

### ⚙️ Gestión de Reglas
- **Tabla completa**: Todas las reglas con acciones de edición y eliminación
- **Modal de creación**: Formulario completo para reglas personalizadas
- **Validación en tiempo real**: Verificación de campos y formato JSON

### 🧮 Calculadora de Precios
- **Cálculo instantáneo**: Precio dinámico en tiempo real
- **Desglose detallado**: Muestra todas las reglas aplicadas
- **Visualización clara**: Diferenciación entre precios base y final

### 📈 Simulación Semanal
- **Vista de 7 días**: Precios simulados para toda la semana
- **Comparación horaria**: Precios por hora del día
- **Análisis de tendencias**: Identificación de patrones de precios

### ⚡ Reglas Rápidas
- **Hora Pico**: Recargos por horarios específicos
- **Descuento por Anticipación**: Reducciones por reservas adelantadas
- **Temporada Alta**: Recargos por períodos específicos

## 🛠️ Tecnologías Utilizadas

- **HTML5**: Estructura semántica y accesible
- **CSS3**: Estilos modernos con variables CSS y animaciones
- **JavaScript ES6+**: Lógica de aplicación con clases y async/await
- **Bootstrap 5**: Framework CSS para diseño responsive
- **Chart.js**: Gráficos interactivos y responsivos
- **Font Awesome**: Iconografía moderna y consistente

## 📁 Estructura de Archivos

```
static/
├── index.html          # Página principal con toda la interfaz
├── styles.css          # Estilos personalizados y animaciones
├── app.js             # Lógica principal de la aplicación
└── README.md          # Este archivo de documentación
```

## 🚀 Cómo Usar

### 1. Preparación
- Asegúrate de que la API esté ejecutándose en `http://localhost:8000`
- La API debe tener servicios y recursos creados para funcionar correctamente

### 2. Acceso
- Abre `index.html` en tu navegador web
- La aplicación se conectará automáticamente a la API

### 3. Navegación
- **Dashboard**: Vista general del sistema
- **Reglas de Precio**: Gestión completa de reglas
- **Calculadora**: Cálculo de precios dinámicos
- **Simulación**: Análisis semanal de precios
- **Reglas Rápidas**: Creación rápida de reglas comunes

## 🔧 Funcionalidades Principales

### Crear Reglas de Precio
1. Ve a la pestaña "Reglas de Precio"
2. Haz clic en "Nueva Regla"
3. Completa el formulario con:
   - Nombre y descripción
   - Tipo de regla (día, hora, temporada, etc.)
   - Modificador (porcentaje, monto fijo, precio fijo)
   - Condiciones específicas en formato JSON
4. Haz clic en "Guardar Regla"

### Calcular Precios
1. Ve a la pestaña "Calculadora"
2. Selecciona servicio y recurso
3. Configura fecha, hora y duración
4. Especifica participantes y tipo de cliente
5. Haz clic en "Calcular Precio"
6. Revisa el resultado y el desglose de reglas aplicadas

### Simular Semana
1. Ve a la pestaña "Simulación"
2. Configura los parámetros de simulación
3. Haz clic en "Simular Semana"
4. Revisa los precios simulados día por día

### Reglas Rápidas
1. Ve a la pestaña "Reglas Rápidas"
2. Completa el formulario correspondiente:
   - **Hora Pico**: Horarios y días de recargo
   - **Anticipación**: Días mínimos para descuento
   - **Temporada**: Fechas de temporada alta
3. Haz clic en el botón de creación

## 📱 Diseño Responsive

La aplicación está diseñada para funcionar en:
- **Desktop**: Pantallas grandes con layout completo
- **Tablet**: Adaptación automática para pantallas medianas
- **Mobile**: Navegación optimizada para dispositivos móviles

## 🎨 Personalización

### Colores
Los colores principales se pueden modificar en `styles.css`:
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
}
```

### Estilos
- **Cards**: Bordes redondeados y sombras
- **Botones**: Gradientes y efectos hover
- **Formularios**: Validación visual y estados de foco
- **Tablas**: Diseño limpio con hover effects

## 🔍 Debugging

### Consola del Navegador
- Abre las herramientas de desarrollador (F12)
- Revisa la consola para errores y logs
- La aplicación registra todas las operaciones importantes

### Errores Comunes
- **CORS**: Asegúrate de que la API permita requests desde el cliente
- **API no disponible**: Verifica que la API esté ejecutándose
- **Datos faltantes**: Crea servicios y recursos antes de usar la aplicación

## 🚀 Próximas Funcionalidades

- [ ] **Edición de reglas**: Modificar reglas existentes
- [ ] **Importar/Exportar**: Backup y restauración de reglas
- [ ] **Historial de cambios**: Auditoría de modificaciones
- [ ] **Templates**: Reglas predefinidas para casos comunes
- [ ] **Notificaciones**: Sistema de alertas en tiempo real

## 📞 Soporte

Para problemas o sugerencias:
1. Revisa la consola del navegador
2. Verifica la conectividad con la API
3. Consulta los logs de la API
4. Revisa la documentación de la API

## 🎯 Casos de Uso

### Gimnasio
- **Hora Pico**: +25% de 17:00 a 20:00 L-V
- **Descuento Anticipación**: -15% por reservas de 7+ días
- **Temporada Alta**: +30% en enero (año nuevo)

### Clínica Médica
- **Hora Pico**: +20% de 9:00 a 12:00 L-V
- **Fines de Semana**: +40% sábados y domingos
- **Tipo Cliente**: -10% para pacientes VIP

### Hotel
- **Temporada Baja**: -20% de noviembre a marzo
- **Temporada Alta**: +50% de junio a agosto
- **Anticipación**: -25% por reservas de 30+ días

---

**¡Disfruta probando el sistema de precios dinámicos! 🎉**
