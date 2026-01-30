# Guia Rapido: Configurar ADB e Ver Logs do CloudStream

Write-Host "Verificando ADB..." -ForegroundColor Cyan

# Verificar se ADB esta no PATH
$adbPath = Get-Command adb -ErrorAction SilentlyContinue

if (-not $adbPath) {
    Write-Host "ERRO: ADB nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solucoes:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPCAO 1: Instalar Android Platform Tools" -ForegroundColor Cyan
    Write-Host "  1. Baixar: https://developer.android.com/tools/releases/platform-tools" -ForegroundColor White
    Write-Host "  2. Extrair em: C:\platform-tools" -ForegroundColor White
    Write-Host "  3. Adicionar ao PATH:" -ForegroundColor White
    Write-Host '     $env:Path += ";C:\platform-tools"' -ForegroundColor Gray
    Write-Host ""
    Write-Host "OPCAO 2: Instalar via Scoop" -ForegroundColor Cyan
    Write-Host "  scoop install adb" -ForegroundColor White
    Write-Host ""
    Write-Host "OPCAO 3: Usar Android Studio SDK" -ForegroundColor Cyan
    Write-Host '  Adicionar ao PATH: C:\Users\KYTHOURS\AppData\Local\Android\Sdk\platform-tools' -ForegroundColor White
    Write-Host ""
    
    # Tentar encontrar ADB em locais comuns
    $commonPaths = @(
        "C:\platform-tools\adb.exe",
        "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk\platform-tools\adb.exe",
        "C:\Android\platform-tools\adb.exe"
    )
    
    $foundPath = $null
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $foundPath = $path
            break
        }
    }
    
    if ($foundPath) {
        Write-Host "ENCONTRADO: ADB em $foundPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para usar, execute:" -ForegroundColor Yellow
        Write-Host "  & '$foundPath' devices" -ForegroundColor White
        Write-Host ""
        Write-Host "Ou adicione ao PATH:" -ForegroundColor Yellow
        $adbDir = Split-Path $foundPath
        Write-Host "  `$env:Path += ';$adbDir'" -ForegroundColor White
    }
    
    exit 1
}

Write-Host "OK ADB encontrado: $($adbPath.Source)" -ForegroundColor Green
Write-Host ""

# Verificar dispositivos conectados
Write-Host "Verificando dispositivos conectados..." -ForegroundColor Cyan
$devices = adb devices

if ($devices -match "device$") {
    Write-Host "OK Dispositivo(s) conectado(s)!" -ForegroundColor Green
    Write-Host ""
    
    # Mostrar opcoes de logs
    Write-Host "Opcoes de monitoramento:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Ver todos os logs do CloudStream:" -ForegroundColor Cyan
    Write-Host '   adb logcat | Select-String "cloudstream"' -ForegroundColor White
    Write-Host ""
    Write-Host "2. Ver apenas logs do MegaEmbed V8:" -ForegroundColor Cyan
    Write-Host '   adb logcat | Select-String "MegaEmbedV8"' -ForegroundColor White
    Write-Host ""
    Write-Host "3. Ver logs do MaxSeries:" -ForegroundColor Cyan
    Write-Host '   adb logcat | Select-String "MaxSeries"' -ForegroundColor White
    Write-Host ""
    Write-Host "4. Salvar logs em arquivo:" -ForegroundColor Cyan
    Write-Host '   adb logcat > logs_cloudstream.txt' -ForegroundColor White
    Write-Host ""
    Write-Host "Qual deseja executar? (1-4): " -NoNewline -ForegroundColor Yellow
    $choice = Read-Host
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "Iniciando logs do CloudStream (Ctrl+C para parar)..." -ForegroundColor Green
            adb logcat | Select-String "cloudstream" -CaseSensitive:$false
        }
        "2" {
            Write-Host ""
            Write-Host "Iniciando logs do MegaEmbed V8 (Ctrl+C para parar)..." -ForegroundColor Green
            adb logcat | Select-String "MegaEmbed"
        }
        "3" {
            Write-Host ""
            Write-Host "Iniciando logs do MaxSeries (Ctrl+C para parar)..." -ForegroundColor Green
            adb logcat | Select-String "MaxSeries"
        }
        "4" {
            $filename = "logs_cloudstream_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
            Write-Host ""
            Write-Host "Salvando logs em: $filename" -ForegroundColor Green
            Write-Host "Pressione Ctrl+C para parar..." -ForegroundColor Yellow
            adb logcat > $filename
        }
        default {
            Write-Host "Opcao invalida. Mostrando logs gerais..." -ForegroundColor Yellow
            adb logcat | Select-String "MegaEmbed"
        }
    }
    
} else {
    Write-Host "ERRO: Nenhum dispositivo conectado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Passos para conectar:" -ForegroundColor Yellow
    Write-Host "  1. Ativar 'Depuracao USB' no Android:" -ForegroundColor White
    Write-Host "     Settings -> Developer Options -> USB Debugging" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Conectar via cabo USB" -ForegroundColor White
    Write-Host ""
    Write-Host "  3. OU conectar via WiFi:" -ForegroundColor White
    Write-Host "     adb connect SEU_IP:5555" -ForegroundColor Gray
    Write-Host ""
}
