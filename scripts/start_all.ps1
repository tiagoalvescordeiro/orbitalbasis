# OrbitalBasis — sobe stack completa
param(
    [switch]$Docker,
    [switch]$Local
)

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($Docker) {
    Write-Host "Subindo Docker Compose (API + Dashboard)..."
    docker compose up --build
    exit
}

if (-not $Local) {
    Write-Host "Uso:"
    Write-Host "  .\scripts\start_all.ps1 -Docker   # recomendado"
    Write-Host "  .\scripts\start_all.ps1 -Local    # API + instrucoes Streamlit"
    exit
}

pip install -q -r requirements.txt
python scripts/index_rag.py

Write-Host "Iniciando API http://127.0.0.1:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; uvicorn src.applications.api.main:app --reload --port 8000"

Start-Sleep -Seconds 2
Write-Host "Execute em outro terminal:"
Write-Host "  streamlit run src/applications/dashboard/app.py"
