# Dashboard Streamlit consumindo FastAPI (modo distribuído)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$env:ORBITAL_USE_API = "true"
$env:ORBITAL_API_URL = "http://127.0.0.1:8000"

@"
ORBITAL_USE_API=true
ORBITAL_API_URL=http://127.0.0.1:8000
ORBITAL_RAG_MODE=hybrid
"@ | Set-Content -Path "$root\.env" -Encoding utf8

Write-Host "ORBITAL_USE_API=$env:ORBITAL_USE_API"
Write-Host "ORBITAL_API_URL=$env:ORBITAL_API_URL"
Write-Host ".env gravado em $root\.env"
Write-Host "Certifique-se de que a API esta em http://127.0.0.1:8000"
python -m streamlit run src/applications/dashboard/app.py --server.port 8501
