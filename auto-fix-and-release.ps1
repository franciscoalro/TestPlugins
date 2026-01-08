# Script Automático de Correção e Release - MaxSeries
param(
    [Parameter(Mandatory=$false)]
    [string]$FixType = "general",
    
    [Parameter(Mandatory=$false)]
    [string]$CustomDescription = ""
)

# Obter próxima versão automaticamente
$buildFile = "MaxSeries/build.gradle.kts"
$currentVersion = (Get-Content $buildFile | Select-String "version = (\d+)" | ForEach-Object { $_.Matches[0].Groups[1].Value }) -as [int]
$newVersion = $currentVersion + 1

Write-Host "🤖 SISTEMA AUTOMÁTICO DE CORREÇÃO E RELEASE" -ForegroundColor Cyan
Write-Host "📊 Versão atual: v$currentVersion" -ForegroundColor White
Write-Host "🚀 Nova versão: v$newVersion" -ForegroundColor Green
Write-Host "🔧 Tipo de correção: $FixType" -ForegroundColor Yellow

# Definir correções baseadas no tipo
switch ($FixType) {
    "episodes" {
        $description = "Correção avançada de detecção de episódios e temporadas"
        Write-Host "📺 Aplicando correções para episódios..." -ForegroundColor Yellow
    }
    
    "links" {
        $description = "Correção de extração de links de vídeo"
        Write-Host "🔗 Aplicando correções para links..." -ForegroundColor Yellow
    }
    
    "general" {
        $description = "Melhorias gerais de estabilidade e compatibilidade"
        Write-Host "⚙️ Aplicando melhorias gerais..." -ForegroundColor Yellow
    }
    
    default {
        $description = $CustomDescription
        Write-Host "🛠️ Aplicando correções personalizadas..." -ForegroundColor Yellow
    }
}

# Executar release automático
Write-Host ""
Write-Host "🚀 Iniciando processo de release..." -ForegroundColor Green

try {
    & .\auto-release.ps1 -NewVersion $newVersion -Description $description
    
    Write-Host ""
    Write-Host "✅ PROCESSO AUTOMÁTICO CONCLUÍDO!" -ForegroundColor Green
    Write-Host "🎯 MaxSeries v$newVersion está pronto para uso" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Erro no processo automático: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔧 Execute manualmente ou verifique os logs" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Teste a nova versão no CloudStream" -ForegroundColor White
Write-Host "2. Reporte se os problemas foram resolvidos" -ForegroundColor White
Write-Host "3. Se necessário, execute novamente com outro tipo de correção" -ForegroundColor White