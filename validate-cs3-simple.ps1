Write-Host "=== Validacao de Arquivos .cs3 ===" -ForegroundColor Green
Write-Host ""

$buildsPath = "builds"
$cs3Files = Get-ChildItem -Path $buildsPath -Filter "*.cs3"

if ($cs3Files.Count -eq 0) {
    Write-Host "Nenhum arquivo .cs3 encontrado" -ForegroundColor Red
    exit 1
}

$allValid = $true

foreach ($file in $cs3Files) {
    Write-Host "Validando: $($file.Name)" -ForegroundColor Cyan
    
    if ($file.Length -eq 0) {
        Write-Host "  Arquivo vazio" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $header = [System.Text.Encoding]::ASCII.GetString($bytes[0..1])
        
        if ($header -eq "PK") {
            Write-Host "  Assinatura ZIP valida" -ForegroundColor Green
        } else {
            Write-Host "  Assinatura ZIP invalida: $header" -ForegroundColor Red
            $allValid = $false
            continue
        }
    } catch {
        Write-Host "  Erro ao ler arquivo: $_" -ForegroundColor Red
        $allValid = $false
        continue
    }
    
    $sizeKB = [math]::Round($file.Length / 1024, 2)
    Write-Host "  Tamanho: $sizeKB KB" -ForegroundColor Yellow
    Write-Host "  Modificado: $($file.LastWriteTime)" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Validando plugins.json..." -ForegroundColor Cyan
$pluginsJsonPath = Join-Path $buildsPath "plugins.json"

if (Test-Path $pluginsJsonPath) {
    try {
        $pluginsContent = Get-Content $pluginsJsonPath -Raw | ConvertFrom-Json
        Write-Host "  plugins.json e um JSON valido" -ForegroundColor Green
        Write-Host "  Contem $($pluginsContent.Count) plugins" -ForegroundColor Yellow
    } catch {
        Write-Host "  Erro ao validar plugins.json: $_" -ForegroundColor Red
        $allValid = $false
    }
} else {
    Write-Host "  plugins.json nao encontrado" -ForegroundColor Red
    $allValid = $false
}

Write-Host ""
Write-Host "Validando repo.json..." -ForegroundColor Cyan
$repoJsonPath = Join-Path $buildsPath "repo.json"

if (Test-Path $repoJsonPath) {
    try {
        $repoContent = Get-Content $repoJsonPath -Raw | ConvertFrom-Json
        Write-Host "  repo.json e um JSON valido" -ForegroundColor Green
    } catch {
        Write-Host "  Erro ao validar repo.json: $_" -ForegroundColor Red
        $allValid = $false
    }
} else {
    Write-Host "  repo.json nao encontrado" -ForegroundColor Red
    $allValid = $false
}

Write-Host ""
Write-Host "=== Resultado Final ===" -ForegroundColor Green

if ($allValid) {
    Write-Host "Todos os arquivos estao validos e prontos para o Cloudstream!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Alguns arquivos tem problemas que precisam ser corrigidos." -ForegroundColor Red
    exit 1
}