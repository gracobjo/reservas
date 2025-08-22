# 🔌 Documentación de la API

## 📋 Información General

- **Base URL**: `http://localhost:8000`
- **Framework**: FastAPI
- **Documentación automática**: `http://localhost:8000/docs`
- **Esquemas OpenAPI**: `http://localhost:8000/openapi.json`

## 🏥 Endpoints de Salud

### GET `/health`
Verifica el estado de la API.

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-20T01:46:00.000Z",
  "version": "1.0.0"
}
```

## 🎯 Endpoints de Servicios

### GET `/servicios/`
Obtiene la lista de todos los servicios disponibles.

**Parámetros de consulta:**
- `skip` (opcional): Número de registros a omitir (paginación)
- `limit` (opcional): Número máximo de registros a retornar

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Alquiler Habitación Individual",
    "descripcion": "Habitación individual con baño privado",
    "duracion_minutos": 1440,
    "precio_base": 80.0,
    "created_at": "2025-08-20T01:46:00.000Z",
    "updated_at": null
  }
]
```

### POST `/servicios`
Crea un nuevo servicio.

**Cuerpo de la petición:**
```json
{
  "nombre": "Nuevo Servicio",
  "descripcion": "Descripción del servicio",
  "duracion_minutos": 60,
  "precio_base": 50.0
}
```

### GET `/servicios/{servicio_id}`
Obtiene un servicio específico por ID.

### PUT `/servicios/{servicio_id}`
Actualiza un servicio existente.

### DELETE `/servicios/{servicio_id}`
Elimina un servicio.

## 🏠 Endpoints de Recursos

### GET `/recursos/`
Obtiene la lista de todos los recursos disponibles.

**Parámetros de consulta:**
- `skip` (opcional): Número de registros a omitir
- `limit` (opcional): Número máximo de registros

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Habitación 101 - Individual",
    "tipo": "habitacion",
    "disponible": true,
    "created_at": "2025-08-20T01:46:00.000Z",
    "updated_at": null
  }
]
```

### POST `/recursos`
Crea un nuevo recurso.

**Cuerpo de la petición:**
```json
{
  "nombre": "Nuevo Recurso",
  "tipo": "sala",
  "disponible": true
}
```

### GET `/recursos/{recurso_id}`
Obtiene un recurso específico por ID.

### PUT `/recursos/{recurso_id}`
Actualiza un recurso existente.

### DELETE `/recursos/{recurso_id}`
Elimina un recurso.

## 💰 Endpoints de Precios Dinámicos

### GET `/precios-dinamicos/reglas`
Obtiene todas las reglas de precios configuradas.

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Recargo Fin de Semana",
    "descripcion": "Recargo del 30% los sábados y domingos",
    "tipo_regla": "dia_semana",
    "condicion": "{\"dias\": [5, 6]}",
    "tipo_modificador": "porcentaje",
    "valor_modificador": 30.0,
    "prioridad": 10,
    "activa": true,
    "fecha_inicio": null,
    "fecha_fin": null,
    "servicios_aplicables": null,
    "recursos_aplicables": null,
    "created_at": "2025-08-20T01:46:00.000Z",
    "updated_at": null
  }
]
```

### POST `/precios-dinamicos/calcular`
Calcula el precio final aplicando todas las reglas activas.

**Cuerpo de la petición:**
```json
{
  "servicio_id": 1,
  "recurso_id": 1,
  "fecha_hora_inicio": "2025-08-24T08:00:00.000Z",
  "fecha_hora_fin": "2025-08-25T08:00:00.000Z",
  "participantes": 1,
  "tipo_cliente": "regular"
}
```

**Respuesta:**
```json
{
  "precio_base": 80.0,
  "precio_final": 104.0,
  "reglas_aplicadas": [
    {
      "id": 1,
      "nombre": "Recargo Fin de Semana",
      "tipo_modificador": "porcentaje",
      "valor_modificador": 30.0,
      "descripcion": "Recargo del 30% los sábados y domingos"
    }
  ],
  "desglose": {
    "precio_servicio": 80.0,
    "modificadores": 24.0,
    "total": 104.0
  }
}
```

### GET `/precios-dinamicos/estadisticas/reglas`
Obtiene estadísticas generales de las reglas de precios.

**Respuesta:**
```json
{
  "total_reglas": 5,
  "reglas_activas": 4,
  "reglas_inactivas": 1,
  "tipos_regla": {
    "dia_semana": 2,
    "hora": 1,
    "anticipacion": 1,
    "temporada": 1
  },
  "modificadores": {
    "porcentaje": 3,
    "monto_fijo": 1,
    "precio_fijo": 1
  }
}
```

## ⚡ Endpoints de Reglas Rápidas

### POST `/precios-dinamicos/reglas-rapidas/hora-pico`
Crea una regla de recargo por hora pico.

**Cuerpo de la petición:**
```json
{
  "tipo": "hora_pico",
  "configuracion": {
    "nombre": "Recargo Hora Pico",
    "hora_inicio": "18:00",
    "hora_fin": "22:00",
    "porcentaje_recargo": 25.0,
    "prioridad": 10,
    "dias_lunes": true,
    "dias_martes": true,
    "dias_miercoles": true,
    "dias_jueves": true,
    "dias_viernes": true,
    "dias_sabado": false,
    "dias_domingo": false
  }
}
```

### POST `/precios-dinamicos/reglas-rapidas/descuento-anticipacion`
Crea una regla de descuento por anticipación.

**Cuerpo de la petición:**
```json
{
  "tipo": "descuento_anticipacion",
  "configuracion": {
    "nombre": "Descuento 7 días",
    "dias_anticipacion_min": 7,
    "porcentaje_descuento": 15.0,
    "prioridad": 20
  }
}
```

### POST `/precios-dinamicos/reglas-rapidas/fin-de-semana`
Crea una regla de recargo por fin de semana.

**Cuerpo de la petición:**
```json
{
  "tipo": "fin_de_semana",
  "configuracion": {
    "nombre": "Recargo Fin de Semana",
    "porcentaje_recargo": 30.0,
    "prioridad": 15,
    "dias_sabado": true,
    "dias_domingo": true
  }
}
```

## 📊 Endpoints de Estadísticas

### GET `/precios-dinamicos/estadisticas/reglas`
Obtiene estadísticas detalladas de las reglas de precios.

### GET `/precios-dinamicos/estadisticas/calculo`
Obtiene estadísticas de los cálculos realizados.

## 🔐 Endpoints de Autenticación (Pendientes)

### POST `/auth/login`
Login de usuario (pendiente de implementar).

### POST `/auth/register`
Registro de usuario (pendiente de implementar).

### POST `/auth/refresh`
Renovación de token (pendiente de implementar).

## 📅 Endpoints de Horarios (Pendientes)

### GET `/horarios`
Obtiene horarios de operación (pendiente de implementar).

### POST `/horarios`
Crea horarios de operación (pendiente de implementar).

## 🏷️ Endpoints de Reservas (Pendientes)

### GET `/reservas`
Obtiene lista de reservas (pendiente de implementar).

### POST `/reservas`
Crea una nueva reserva (pendiente de implementar).

### PUT `/reservas/{reserva_id}`
Actualiza una reserva (pendiente de implementar).

### DELETE `/reservas/{reserva_id}`
Cancela una reserva (pendiente de implementar).

## 📝 Códigos de Estado HTTP

- **200 OK**: Petición exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos de petición inválidos
- **401 Unauthorized**: No autenticado
- **403 Forbidden**: No autorizado
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Error de validación
- **500 Internal Server Error**: Error interno del servidor

## 🔍 Ejemplos de Uso

### Ejemplo 1: Calcular precio para fin de semana
```bash
curl -X POST "http://localhost:8000/precios-dinamicos/calcular" \
  -H "Content-Type: application/json" \
  -d '{
    "servicio_id": 1,
    "recurso_id": 1,
    "fecha_hora_inicio": "2025-08-24T08:00:00.000Z",
    "fecha_hora_fin": "2025-08-25T08:00:00.000Z",
    "participantes": 1,
    "tipo_cliente": "regular"
  }'
```

### Ejemplo 2: Crear regla de hora pico
```bash
curl -X POST "http://localhost:8000/precios-dinamicos/reglas-rapidas/hora-pico" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "hora_pico",
    "configuracion": {
      "nombre": "Recargo Tarde",
      "hora_inicio": "16:00",
      "hora_fin": "20:00",
      "porcentaje_recargo": 20.0,
      "prioridad": 10,
      "dias_lunes": true,
      "dias_martes": true,
      "dias_miercoles": true,
      "dias_jueves": true,
      "dias_viernes": true,
      "dias_sabado": false,
      "dias_domingo": false
    }
  }'
```

## 📚 Referencias

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Especificación OpenAPI](https://swagger.io/specification/)
- [Códigos de estado HTTP](https://developer.mozilla.org/es/docs/Web/HTTP/Status)
