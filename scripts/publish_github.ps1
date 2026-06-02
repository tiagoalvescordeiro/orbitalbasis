# Publica OrbitalBasis no GitHub (execute apos: gh auth login)
param(
    [string]$RepoName = "orbitalbasis",
    [ValidateSet("public", "private")]
    [string]$Visibility = "public",
    [string]$Description = "OrbitalBasis - Global Solution FIAP 2026.1 | Economia Espacial + IA agro"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Write-Host "Instale GitHub CLI: winget install GitHub.cli"
    exit 1
}

gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Faca login primeiro:"
    Write-Host "  gh auth login"
    Write-Host "Escolha: GitHub.com -> HTTPS -> Login via browser"
    exit 1
}

$hasRemote = $false
git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { $hasRemote = $true }

if (-not $hasRemote) {
    Write-Host "Criando repositorio $RepoName ($Visibility)..."
    gh repo create $RepoName --$Visibility --source=. --remote=origin --description=$Description --push
} else {
    Write-Host "Remote ja existe. Enviando push..."
    git push -u origin main
}

if ($LASTEXITCODE -eq 0) {
    gh repo view --web 2>$null
    gh repo view --json url -q .url
}
