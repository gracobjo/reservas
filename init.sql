-- =====================================================
-- SCRIPT DE INICIALIZACIÓN - MICROSERVICIO DE RESERVAS
-- =====================================================

-- Crear cliente de prueba
INSERT INTO clientes (nombre, email, telefono) 
VALUES ('María González López', 'maria.gonzalez@email.com', '+34 600 123 456')
ON CONFLICT (id) DO NOTHING;

-- Crear servicio de prueba
INSERT INTO servicios (nombre, descripcion, duracion_minutos, precio_base) 
VALUES ('Consulta Médica General', 'Consulta médica general de 30 minutos con revisión completa', 30, 50.00)
ON CONFLICT (id) DO NOTHING;

-- Crear recurso de prueba
INSERT INTO recursos (nombre, tipo, disponible) 
VALUES ('Consultorio Principal', 'consultorio', true)
ON CONFLICT (id) DO NOTHING;

-- Crear usuario administrador (password: admin123)
INSERT INTO usuarios (username, email, hashed_password, is_admin, is_active) 
VALUES ('admin', 'admin@reservas.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.s6.m', true, true)
ON CONFLICT (id) DO NOTHING;

-- Crear usuario de prueba (password: user123)
INSERT INTO usuarios (username, email, hashed_password, is_admin, is_active) 
VALUES ('usuario', 'usuario@reservas.com', '$2b$12$EixZaYVK1fsbOD1sJdO1uO29Mi9aFqCqDoFsxVJMnqjAxfSJQSmgy', false, true)
ON CONFLICT (id) DO NOTHING;

-- Crear regla de precio de ejemplo
INSERT INTO precios (servicio_id, tipo_regla, valor, descripcion) 
VALUES (1, 'fin_de_semana', 65.00, 'Precio especial para fines de semana')
ON CONFLICT (id) DO NOTHING;

-- Crear reserva de ejemplo (si el cliente, servicio y recurso existen)
INSERT INTO reservas (cliente_id, servicio_id, recurso_id, fecha_hora_inicio, fecha_hora_fin, estado) 
VALUES (
    1, 
    1, 
    1, 
    CURRENT_DATE + INTERVAL '1 day' + INTERVAL '10:00:00', 
    CURRENT_DATE + INTERVAL '1 day' + INTERVAL '10:30:00', 
    'confirmada'
)
ON CONFLICT (id) DO NOTHING;

-- Mostrar datos creados
SELECT '=== CLIENTES ===' as info;
SELECT id, nombre, email, telefono FROM clientes;

SELECT '=== SERVICIOS ===' as info;
SELECT id, nombre, descripcion, duracion_minutos, precio_base FROM servicios;

SELECT '=== RECURSOS ===' as info;
SELECT id, nombre, tipo, disponible FROM recursos;

SELECT '=== USUARIOS ===' as info;
SELECT id, username, email, is_admin, is_active FROM usuarios;

SELECT '=== PRECIOS ===' as info;
SELECT id, servicio_id, tipo_regla, valor, descripcion FROM precios;

SELECT '=== RESERVAS ===' as info;
SELECT id, cliente_id, servicio_id, recurso_id, fecha_hora_inicio, fecha_hora_fin, estado FROM reservas;
