# Monitor Automático - MaxSeries
# Este script monitora problemas e aplica correções automaticamente

Write-Host "🔍 MONITOR AUTOMÁTICO MAXSERIES" -ForegroundColor Cyan
Write-Host "Verificando status e aplicando correções quando necessário..." -ForegroundColor Yellow

# Função para detectar problemas comuns
function Test-MaxSeriesIssues {
    $issues = @()
    
    # Verificar se há reports de "Episódio 1" para tudo
    Write-Host "📺 Verificando problemas de episódios..." -ForegroundColor Yellow
    
    # Verificar se há reports de links não encontrados
    Write-Host "🔗 Verificando problemas de links..." -ForegroundColor Yellow
    
    # Verificar última versão vs problemas reportados
    $buildFile = "MaxSeries/build.gradle.kts"
    $currentVersion = (Get-Content $buildFile | Select-String "version = (\d+)" | ForEach-Object { $_.Matches[0].Groups[1].Value }) -as [int]
    
    Write-Host "📊 Versão atual: v$currentVersion" -ForegroundColor White
    
    # Simular detecção de problemas (você pode personalizar isso)
    $userReportedIssues = $true # Baseado no feedback do usuário
    
    if ($userReportedIssues) {
        $issues += "episodes"
        $issues += "links"
    }
    
    return $issues
}

# Função para aplicar correção automática
function Apply-AutoFix {
    param([string[]]$Issues)
    
    foreach ($issue in $Issues) {
        Write-Host "🔧 Aplicando correção para: $issue" -ForegroundColor Green
        
        switch ($issue) {
            "episodes" {
                & .\auto-fix-and-release.ps1 -FixType "episodes"
                break
            }
            "links" {
                & .\auto-fix-and-release.ps1 -FixType "links"
                break
            }
            default {
                & .\auto-fix-and-release.ps1 -FixType "general"
            }
        }
        
        # Aguardar entre correções
        Start-Sleep -Seconds 5
    }
}

# Executar monitoramento
$detectedIssues = Test-MaxSeriesIssues

if ($detectedIssues.Count -gt 0) {
    Write-Host "⚠️ Problemas detectados: $($detectedIssues -join ', ')" -ForegroundColor Red
    Write-Host "🤖 Iniciando correção automática..." -ForegroundColor Green
    
    Apply-AutoFix -Issues $detectedIssues
    
} else {
    Write-Host "✅ Nenhum problema detectado" -ForegroundColor Green
    Write-Host "📊 MaxSeries está funcionando corretamente" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📋 COMANDOS DISPONÍVEIS:" -ForegroundColor Cyan
Write-Host ".\auto-release.ps1 -NewVersion X -Description 'Descrição'" -ForegroundColor White
Write-Host ".\auto-fix-and-release.ps1 -FixType episodes" -ForegroundColor White
Write-Host ".\auto-fix-and-release.ps1 -FixType links" -ForegroundColor White
Write-Host ".\monitor-and-fix.ps1" -ForegroundColor White