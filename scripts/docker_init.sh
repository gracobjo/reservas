#!/bin/bash

# =====================================================
# SCRIPT DE INICIALIZACIÓN PARA DOCKER
# MICROSERVICIO DE GESTIÓN DE RESERVAS
# =====================================================

set -e

echo "🏥 MICROSERVICIO DE GESTIÓN DE RESERVAS"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que Docker esté corriendo
print_status "Verificando que Docker esté corriendo..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor, inicia Docker y vuelve a intentar."
    exit 1
fi
print_success "Docker está corriendo"

# Verificar que docker-compose esté disponible
print_status "Verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose no está instalado. Por favor, instálalo y vuelve a intentar."
    exit 1
fi
print_success "docker-compose está disponible"

# Verificar que el archivo .env exista
print_status "Verificando archivo .env..."
if [ ! -f .env ]; then
    print_warning "Archivo .env no encontrado. Creando desde env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        print_success "Archivo .env creado desde env.example"
        print_warning "Por favor, edita el archivo .env con tus configuraciones antes de continuar"
        echo ""
        echo "Variables importantes a configurar:"
        echo "  - SECRET_KEY: Clave secreta para JWT"
        echo "  - DATABASE_URL: URL de conexión a PostgreSQL"
        echo ""
        read -p "¿Deseas continuar después de editar .env? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Por favor, edita .env y ejecuta el script nuevamente"
            exit 0
        fi
    else
        print_error "Archivo env.example no encontrado. Por favor, crea un archivo .env manualmente"
        exit 1
    fi
else
    print_success "Archivo .env encontrado"
fi

# Construir y levantar servicios
print_status "Construyendo y levantando servicios con Docker Compose..."
docker-compose up --build -d

# Esperar a que PostgreSQL esté listo
print_status "Esperando a que PostgreSQL esté listo..."
sleep 10

# Verificar que los servicios estén corriendo
print_status "Verificando estado de los servicios..."
if docker-compose ps | grep -q "Up"; then
    print_success "Servicios levantados correctamente"
else
    print_error "Error al levantar servicios"
    docker-compose logs
    exit 1
fi

# Ejecutar migraciones si es necesario
print_status "Verificando migraciones de base de datos..."
docker-compose exec app alembic upgrade head

# Ejecutar script de inicialización de datos
print_status "Ejecutando script de inicialización de datos..."
docker-compose exec app python scripts/init_data.py

echo ""
echo "🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!"
echo "=================================================="
echo ""
echo "🌐 ACCESO A LA APLICACIÓN:"
echo "   🏠 Página principal: http://localhost:8000"
echo "   📚 Swagger UI: http://localhost:8000/docs"
echo "   📖 ReDoc: http://localhost:8000/redoc"
echo "   💚 Health Check: http://localhost:8000/health"
echo ""
echo "🔑 CREDENCIALES DE ACCESO:"
echo "   👑 Administrador:"
echo "      Username: admin"
echo "      Password: admin123"
echo "      Email: admin@reservas.com"
echo ""
echo "   👤 Usuario Normal:"
echo "      Username: usuario"
echo "      Password: user123"
echo "      Email: usuario@reservas.com"
echo ""
echo "📊 COMANDOS ÚTILES:"
echo "   Ver logs: docker-compose logs -f"
echo "   Detener servicios: docker-compose down"
echo "   Reiniciar servicios: docker-compose restart"
echo "   Ver estado: docker-compose ps"
echo ""
echo "✨ ¡El microservicio está listo para usar!"
