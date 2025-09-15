Write-Host "=== SOLUCIÓN ERROR DOCKER COMPOSE ===" -ForegroundColor Green

# 1. Verificar directorio actual
Write-Host "1. Directorio actual:" -ForegroundColor Yellow
$currentDir = Get-Location
Write-Host $currentDir.Path

# 2. Verificar archivos
Write-Host "`n2. Archivos en el directorio:" -ForegroundColor Yellow
Get-ChildItem -File | Format-Table Name, Length

# 3. Buscar archivos YAML
Write-Host "`n3. Buscando archivos docker-compose:" -ForegroundColor Yellow
$composeFiles = Get-ChildItem -Name *compose*
if ($composeFiles) {
    Write-Host "Encontrados: $composeFiles" -ForegroundColor Green
} else {
    Write-Host "No se encontraron archivos docker-compose" -ForegroundColor Red
}

# 4. Buscar archivos YML
$ymlFiles = Get-ChildItem -Name *.yml
if ($ymlFiles) {
    Write-Host "Archivos YML encontrados: $ymlFiles" -ForegroundColor Green
} else {
    Write-Host "No se encontraron archivos YML" -ForegroundColor Red
}

# 5. Crear docker-compose.yml si no existe
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "`n4. Creando docker-compose.yml..." -ForegroundColor Yellow
    @"
version: '3.8'

services:
  cinemagic-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - MYSQL_HOST=cinemagic-db
      - MYSQL_USER=root
      - MYSQL_PASSWORD=123456
      - MYSQL_DATABASE=cine
    depends_on:
      - cinemagic-db
    volumes:
      - .:/app
    restart: unless-stopped

  cinemagic-db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=123456
      - MYSQL_DATABASE=cine
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  mysql_data:
"@ | Out-File -FilePath docker-compose.yml -Encoding UTF8
    Write-Host "docker-compose.yml creado exitosamente!" -ForegroundColor Green
}

# 6. Verificar contenido
Write-Host "`n5. Contenido de docker-compose.yml:" -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Get-Content docker-compose.yml | Select-Object -First 10
    Write-Host "..."
}

# 7. Intentar ejecutar
Write-Host "`n6. Intentando ejecutar Docker Compose..." -ForegroundColor Yellow
try {
    docker-compose -f docker-compose.yml up -d
    Write-Host "¡Éxito! Docker Compose se ejecutó correctamente." -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host "`n=== PROCESO COMPLETADO ===" -ForegroundColor Green