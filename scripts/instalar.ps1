# Instalacion automatica en Windows (PowerShell). Ejecutar desde la raiz del proyecto:
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path venv)) { python -m venv venv }
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    $key = & .\venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
    (Get-Content .env) -replace 'FLASK_SECRET_KEY=.*', "FLASK_SECRET_KEY=$key" | Set-Content .env
    Write-Host "Se creo .env. Abrelo y escribe tu DB_PASSWORD de MySQL, luego ejecuta este script de nuevo."
    exit 0
}

& .\venv\Scripts\python.exe database\init_db.py
Write-Host "Instalacion completa. Para iniciar: .\venv\Scripts\python.exe app.py"
