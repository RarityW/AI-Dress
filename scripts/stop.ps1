$confirm = Read-Host "Are you sure you want to stop production services? (y/n)"
if ($confirm -match '^[Yy]$') {
    Write-Host "Stopping production services..."
    docker compose -f docker-compose.prod.yml down
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Services stopped successfully."
    } else {
        Write-Host "Failed to stop services."
    }
} else {
    Write-Host "Aborted."
}
