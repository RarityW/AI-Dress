param([string]$Version)

if (-not $Version) {
    Write-Host "Usage: .\rollback.ps1 <version>"
    exit 1
}

$confirm = Read-Host "Are you sure you want to rollback to $Version? (y/n)"
if ($confirm -match '^[Yy]$') {
    Write-Host "Rolling back to $Version..."
    $env:IMAGE_TAG = $Version
    docker compose -f docker-compose.prod.yml down
    docker compose -f docker-compose.prod.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Rollback successful."
    } else {
        Write-Host "Rollback failed."
    }
} else {
    Write-Host "Aborted."
}
