$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $projectRoot "docker-compose.yml"
$envFile = Join-Path $projectRoot ".env"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
	throw "No se encontró Docker. Instala Docker Desktop y vuelve a intentarlo."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
	throw "No se encontró uv. Instálalo y vuelve a intentarlo."
}

if (-not (Test-Path $envFile)) {
	throw "No se encontró el archivo .env esperado en: $envFile"
}

Push-Location $projectRoot
try {
	Write-Host "Iniciando PostgreSQL con Docker Compose..." -ForegroundColor Cyan
	& docker compose --env-file $envFile -f $composeFile up -d --wait --wait-timeout 90
	if ($LASTEXITCODE -ne 0) {
		throw "No se pudo iniciar PostgreSQL. Verifica que Docker Desktop esté iniciado y revisa sus logs con 'docker compose logs db'."
	}

	Write-Host "PostgreSQL está listo. Iniciando la API en http://127.0.0.1:8000 ..." -ForegroundColor Green
	$env:ENVIRONMENT = "development"
	& uv run --env-file $envFile fastapi dev main.py --host 127.0.0.1 --port 8000
	if ($LASTEXITCODE -ne 0) {
		throw "La API terminó con un error (código $LASTEXITCODE)."
	}
}
finally {
	Pop-Location
}
