# Script de Release Automático - MaxSeries
param(
    [Parameter(Mandatory=$true)]
    [int]$NewVersion,
    
    [Parameter(Mandatory=$false)]
    [string]$Description = "Atualização automática"
)

Write-Host "🚀 Iniciando release automático para MaxSeries v$NewVersion" -ForegroundColor Green

# 1. Atualizar versão no build.gradle.kts
Write-Host "📝 Atualizando versão no build.gradle.kts..." -ForegroundColor Yellow
$buildFile = "MaxSeries/build.gradle.kts"
$content = Get-Content $buildFile
$content = $content -replace "version = \d+", "version = $NewVersion"
$content = $content -replace "description = `".*`"", "description = `"$Description (v$NewVersion)`""
$content | Set-Content $buildFile

# 2. Atualizar plugins.json
Write-Host "📝 Atualizando plugins.json..." -ForegroundColor Yellow
$pluginsFile = "plugins.json"
$pluginsContent = Get-Content $pluginsFile -Raw | ConvertFrom-Json
$pluginsContent[1].url = "https://github.com/franciscoalro/TestPlugins/releases/download/v$NewVersion.0/MaxSeries.cs3"
$pluginsContent[1].version = $NewVersion
$pluginsContent[1].description = "$Description (v$NewVersion)."
$pluginsContent | ConvertTo-Json -Depth 10 | Set-Content $pluginsFile

# 3. Commit das mudanças
Write-Host "💾 Fazendo commit das mudanças..." -ForegroundColor Yellow
git add .
git commit -m "MaxSeries v$NewVersion`: $Description"

# 4. Criar e enviar tag
Write-Host "🏷️ Criando tag v$NewVersion.0..." -ForegroundColor Yellow
git tag "v$NewVersion.0"
git push origin "v$NewVersion.0"

# 5. Push das mudanças
Write-Host "📤 Enviando mudanças para GitHub..." -ForegroundColor Yellow
git push

# 6. Aguardar build do GitHub Actions
Write-Host "⏳ Aguardando GitHub Actions completar o build..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# 7. Verificar se release foi criado
Write-Host "🔍 Verificando se release foi criado..." -ForegroundColor Yellow
$releaseUrl = "https://api.github.com/repos/franciscoalro/TestPlugins/releases/tags/v$NewVersion.0"

$maxAttempts = 10
$attempt = 1

do {
    try {
        $response = Invoke-RestMethod -Uri $releaseUrl -Method Get
        Write-Host "✅ Release v$NewVersion.0 criado com sucesso!" -ForegroundColor Green
        Write-Host "📦 Assets disponíveis:" -ForegroundColor Cyan
        
        foreach ($asset in $response.assets) {
            Write-Host "  - $($asset.name) ($($asset.size) bytes)" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "🎯 DOWNLOAD DIRETO:" -ForegroundColor Yellow
        Write-Host "https://github.com/franciscoalro/TestPlugins/releases/download/v$NewVersion.0/MaxSeries.cs3" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "📱 REPOSITÓRIO CLOUDSTREAM:" -ForegroundColor Yellow
        Write-Host "https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/plugins.json" -ForegroundColor Green
        
        $success = $true
        break
        
    } catch {
        Write-Host "⏳ Tentativa $attempt/$maxAttempts - Release ainda não disponível..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        $attempt++
    }
} while ($attempt -le $maxAttempts)

if (-not $success) {
    Write-Host "❌ Release não foi criado após $maxAttempts tentativas" -ForegroundColor Red
    Write-Host "🔧 Verifique manualmente: https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "🎉 RELEASE AUTOMÁTICO CONCLUÍDO!" -ForegroundColor Green
    Write-Host "✅ MaxSeries v$NewVersion está disponível no CloudStream" -ForegroundColor Green
}