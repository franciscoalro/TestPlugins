# Setup Local CloudStream Library
# Remove dependencia do JitPack instavel

Write-Host "Configurando biblioteca local do CloudStream3..." -ForegroundColor Cyan
Write-Host "   Isso elimina a dependencia do JitPack instavel`n" -ForegroundColor Gray

# 1. Criar pasta libs
Write-Host "[1/6] Criando pasta libs..." -ForegroundColor Yellow
if (!(Test-Path "libs")) {
    New-Item -ItemType Directory -Force -Path "libs" | Out-Null
    Write-Host "   OK Pasta 'libs' criada" -ForegroundColor Green
} else {
    Write-Host "   INFO Pasta 'libs' ja existe" -ForegroundColor Cyan
}

# 2. Baixar biblioteca CloudStream3
Write-Host "`n[2/6] Baixando CloudStream3 library..." -ForegroundColor Yellow
$output = "libs\cloudstream-library.aar"

# URLs para tentar (em ordem de prioridade)
$urls = @(
    "https://github.com/recloudstream/cloudstream/releases/download/pre-release/library.aar",
    "https://github.com/LagradOst/CloudStream-3/releases/latest/download/library.aar"
)

$downloaded = $false
foreach ($url in $urls) {
    try {
        Write-Host "   Tentando: $url" -ForegroundColor Gray
        Invoke-WebRequest -Uri $url -OutFile $output -ErrorAction Stop
        $downloaded = $true
        Write-Host "   OK Download bem-sucedido!" -ForegroundColor Green
        break
    } catch {
        Write-Host "   AVISO Falhou, tentando proxima URL..." -ForegroundColor Yellow
    }
}

if (-not $downloaded) {
    Write-Host "`n   ERRO: Nao foi possivel baixar de nenhuma URL" -ForegroundColor Red
    Write-Host "   SOLUCAO: Baixe manualmente de:" -ForegroundColor Yellow
    Write-Host "      https://github.com/recloudstream/cloudstream/releases" -ForegroundColor Cyan
    Write-Host "      E salve em: libs\cloudstream-library.aar`n" -ForegroundColor Cyan
    exit 1
}

# 3. Verificar arquivo
Write-Host "`n[3/6] Verificando arquivo baixado..." -ForegroundColor Yellow
if (Test-Path $output) {
    $size = (Get-Item $output).Length / 1MB
    Write-Host "   OK Arquivo: $output" -ForegroundColor Green
    Write-Host "   OK Tamanho: " -NoNewline -ForegroundColor Green
    Write-Host "$([math]::Round($size, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "   ERRO: Arquivo nao encontrado!" -ForegroundColor Red
    exit 1
}

# 4. Backup do build.gradle.kts
Write-Host "`n[4/6] Criando backup..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "build.gradle.kts.backup_$timestamp"
Copy-Item "build.gradle.kts" $backupFile
Write-Host "   OK Backup: $backupFile" -ForegroundColor Green

# 5. Modificar build.gradle.kts
Write-Host "`n[5/6] Modificando build.gradle.kts..." -ForegroundColor Yellow

$content = Get-Content "build.gradle.kts" -Raw

# Verificar se ja foi modificado
if ($content -match 'flatDir') {
    Write-Host "   INFO build.gradle.kts ja esta configurado para usar biblioteca local" -ForegroundColor Cyan
} else {
    # Adicionar flatDir repository apos subprojects {
    $newRepos = @'

    repositories {
        flatDir {
            dirs("${'$'}rootDir/libs")
        }
    }
'@
    $content = $content -replace '(subprojects \{)', "`$1$newRepos"
}

# Substituir dependencia JitPack por local
$oldPattern = 'implementation\("com\.github\.recloudstream\.cloudstream:library:[^"]+"\)'
$newDependency = 'implementation(name: "cloudstream-library", ext: "aar") // Local library (sem JitPack)'

if ($content -match $oldPattern) {
    $content = $content -replace $oldPattern, $newDependency
    Write-Host "   OK Dependencia JitPack substituida por local" -ForegroundColor Green
} else {
    Write-Host "   INFO Dependencia ja esta configurada" -ForegroundColor Cyan
}

Set-Content "build.gradle.kts" $content -NoNewline

# 6. Testar build
Write-Host "`n[6/6] Testando build local..." -ForegroundColor Yellow
Write-Host "   Aguarde... (pode levar 1-2 minutos)`n" -ForegroundColor Gray

./gradlew.bat clean | Out-Null
$buildOutput = ./gradlew.bat MaxSeries:assembleRelease 2>&1 | Out-String

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "     SUCESSO TOTAL!              " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "OK Biblioteca local configurada" -ForegroundColor Green
    Write-Host "OK Build bem-sucedido" -ForegroundColor Green
    Write-Host "OK JitPack ELIMINADO do projeto" -ForegroundColor Green
    Write-Host "OK MaxSeries.cs3 compilado`n" -ForegroundColor Green
    
    # Verificar se .cs3 foi criado
    $cs3File = "MaxSeries\build\MaxSeries.cs3"
    if (Test-Path $cs3File) {
        $cs3Size = (Get-Item $cs3File).Length / 1KB
        Write-Host "Arquivo gerado:" -ForegroundColor Cyan
        Write-Host "   $cs3File" -ForegroundColor White
        Write-Host "   Tamanho: $([math]::Round($cs3Size, 2)) KB`n" -ForegroundColor White
    }
    
    Write-Host "Proximos passos:" -ForegroundColor Cyan
    Write-Host "   1. Fazer commit (git add . && git commit)" -ForegroundColor White
    Write-Host "   2. Fazer push (git push origin main)" -ForegroundColor White
    Write-Host "   3. Build no GitHub Actions funcionara PERFEITAMENTE`n" -ForegroundColor White
    
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "     BUILD FALHOU                " -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "ERRO durante o build" -ForegroundColor Red
    Write-Host "Restaurando backup...`n" -ForegroundColor Yellow
    
    Copy-Item $backupFile "build.gradle.kts" -Force
    Write-Host "OK build.gradle.kts restaurado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Logs do erro:" -ForegroundColor Yellow
    Write-Host $buildOutput -ForegroundColor Gray
}

Write-Host "`nDocumentacao completa em: SOLUCAO_SEM_JITPACK.md`n" -ForegroundColor Cyan
