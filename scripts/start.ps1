$confirm = Read-Host "Are you sure you want to start production services? (y/n)"
if ($confirm -match '^[Yy]$') {
    Write-Host "Starting production services..."
    docker compose -f docker-compose.prod.yml up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services started successfully."
    } else {
        Write-Host "Failed to start services."
    }
} else {
    Write-Host "Aborted."
}
