$confirm = Read-Host "Are you sure you want to deploy? (y/n)"
if ($confirm -match '^[Yy]$') {
    Write-Host "Deploying..."
    git pull origin main
    docker compose -f docker-compose.prod.yml pull
    docker compose -f docker-compose.prod.yml up -d --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Deploy successful."
    } else {
        Write-Host "Deploy failed."
    }
} else {
    Write-Host "Aborted."
}
