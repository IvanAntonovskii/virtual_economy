Write-Host "Создание структуры проекта..." -ForegroundColor Green

# Создаем директории
$folders = @(
    "app",
    "app/core",
    "app/models",
    "app/schemas",
    "app/services",
    "app/repositories",
    "app/api",
    "app/api/endpoints",
    "scripts"
)

foreach ($folder in $folders) {
    New-Item -ItemType Directory -Force -Path $folder
    Write-Host "Создана: $folder"
}

# Создаем __init__.py файлы
foreach ($folder in $folders) {
    $initFile = "$folder/__init__.py"
    if (!(Test-Path $initFile)) {
        New-Item -ItemType File -Path $initFile -Force
        Write-Host "Создан: $initFile"
    }
}

Write-Host "✅ Структура проекта создана!" -ForegroundColor Green
