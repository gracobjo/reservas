# =====================================================
# SCRIPT DE INICIALIZACIÓN PARA DOCKER (WINDOWS)
# MICROSERVICIO DE GESTIÓN DE RESERVAS
# =====================================================

param(
    [switch]$SkipEnvCheck
)

# Configurar colores para output
$Host.UI.RawUI.ForegroundColor = "White"

Write-Host "🏥 MICROSERVICIO DE GESTIÓN DE RESERVAS" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Función para imprimir con colores
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar que Docker esté corriendo
Write-Status "Verificando que Docker esté corriendo..."
try {
    docker info | Out-Null
    Write-Success "Docker está corriendo"
} catch {
    Write-Error "Docker no está corriendo. Por favor, inicia Docker Desktop y vuelve a intentar."
    exit 1
}

# Verificar que docker-compose esté disponible
Write-Status "Verificando docker-compose..."
try {
    docker-compose --version | Out-Null
    Write-Success "docker-compose está disponible"
} catch {
    Write-Error "docker-compose no está instalado. Por favor, instálalo y vuelve a intentar."
    exit 1
}

# Verificar que el archivo .env exista
Write-Status "Verificando archivo .env..."
if (-not (Test-Path ".env")) {
    Write-Warning "Archivo .env no encontrado. Creando desde env.example..."
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Success "Archivo .env creado desde env.example"
        Write-Warning "Por favor, edita el archivo .env con tus configuraciones antes de continuar"
        Write-Host ""
        Write-Host "Variables importantes a configurar:" -ForegroundColor Yellow
        Write-Host "  - SECRET_KEY: Clave secreta para JWT" -ForegroundColor Yellow
        Write-Host "  - DATABASE_URL: URL de conexión a PostgreSQL" -ForegroundColor Yellow
        Write-Host ""
        
        if (-not $SkipEnvCheck) {
            $response = Read-Host "¿Deseas continuar después de editar .env? (y/n)"
            if ($response -ne "y" -and $response -ne "Y") {
                Write-Status "Por favor, edita .env y ejecuta el script nuevamente"
                exit 0
            }
        }
    } else {
        Write-Error "Archivo env.example no encontrado. Por favor, crea un archivo .env manualmente"
        exit 1
    }
} else {
    Write-Success "Archivo .env encontrado"
}

# Construir y levantar servicios
Write-Status "Construyendo y levantando servicios con Docker Compose..."
docker-compose up --build -d

# Esperar a que PostgreSQL esté listo
Write-Status "Esperando a que PostgreSQL esté listo..."
Start-Sleep -Seconds 10

# Verificar que los servicios estén corriendo
Write-Status "Verificando estado de los servicios..."
$services = docker-compose ps
if ($services -match "Up") {
    Write-Success "Servicios levantados correctamente"
} else {
    Write-Error "Error al levantar servicios"
    docker-compose logs
    exit 1
}

# Ejecutar migraciones si es necesario
Write-Status "Verificando migraciones de base de datos..."
docker-compose exec app alembic upgrade head

# Ejecutar script de inicialización de datos
Write-Status "Ejecutando script de inicialización de datos..."
docker-compose exec app python scripts/init_data.py

Write-Host ""
Write-Host "🎉 ¡INICIALIZACIÓN COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ACCESO A LA APLICACIÓN:" -ForegroundColor Cyan
Write-Host "   🏠 Página principal: http://localhost:8000" -ForegroundColor White
Write-Host "   📚 Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   📖 ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host "   💚 Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🔑 CREDENCIALES DE ACCESO:" -ForegroundColor Cyan
Write-Host "   👑 Administrador:" -ForegroundColor Yellow
Write-Host "      Username: admin" -ForegroundColor White
Write-Host "      Password: admin123" -ForegroundColor White
Write-Host "      Email: admin@reservas.com" -ForegroundColor White
Write-Host ""
Write-Host "   👤 Usuario Normal:" -ForegroundColor Yellow
Write-Host "      Username: usuario" -ForegroundColor White
Write-Host "      Password: user123" -ForegroundColor White
Write-Host "      Email: usuario@reservas.com" -ForegroundColor White
Write-Host ""
Write-Host "📊 COMANDOS ÚTILES:" -ForegroundColor Cyan
Write-Host "   Ver logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Detener servicios: docker-compose down" -ForegroundColor White
Write-Host "   Reiniciar servicios: docker-compose restart" -ForegroundColor White
Write-Host "   Ver estado: docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "✨ ¡El microservicio está listo para usar!" -ForegroundColor Green

# Abrir Swagger UI en el navegador
Write-Host ""
$openBrowser = Read-Host "¿Deseas abrir Swagger UI en el navegador? (y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:8000/docs"
}
