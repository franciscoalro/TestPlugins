#!/usr/bin/env pwsh
# Script para atualizar MaxSeries v79 no repositório GitHub
# ATENÇÃO: NÃO USAMOS '&&' NO POWERSHELL. O SCRIPT DEVE SER ROBUSTO.

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     MaxSeries v79 - Atualização do Repositório GitHub        ║" -ForegroundColor Cyan
Write-Host "║      Correções de WebView + Autoplay + Interceptação         ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 0. Limpar builds antigos e recompilar
Write-Host "🧹 Limpando e Compilando MaxSeries v79..." -ForegroundColor Yellow
$compile = Start-Process -FilePath "./gradlew.bat" -ArgumentList ":MaxSeries:make" -Wait -PassThru -NoNewWindow

if ($compile.ExitCode -ne 0) {
    Write-Host "❌ Erro na compilação!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Compilação bem sucedida!" -ForegroundColor Green

# 1. Verificar se o arquivo .cs3 existe
Write-Host "📦 Verificando arquivo MaxSeries.cs3..." -ForegroundColor Yellow
$cs3Path = "MaxSeries\build\MaxSeries.cs3"

if (Test-Path $cs3Path) {
    Write-Host "✅ Arquivo encontrado!" -ForegroundColor Green
    
    # Copiar para raiz para fácil acesso
    Copy-Item $cs3Path "MaxSeries.cs3" -Force
    Write-Host "✅ Copiado para raiz (MaxSeries.cs3)" -ForegroundColor Green
} else {
    Write-Host "❌ Arquivo MaxSeries.cs3 não encontrado após build!" -ForegroundColor Red
    exit 1
}

# 1.5 ATUALIZAR PLUGINS.JSON
# Este passo é crucial para o CloudStream detectar a atualização
Write-Host ""
Write-Host "📝 Atualizando plugins.json..." -ForegroundColor Yellow
try {
    $jsonPath = "plugins.json"
    $jsonContent = Get-Content $jsonPath -Raw | ConvertFrom-Json
    
    # Encontrar MaxSeries e atualizar
    foreach ($plugin in $jsonContent) {
        if ($plugin.name -eq "MaxSeries") {
            $plugin.version = 79
            $plugin.url = "https://raw.githubusercontent.com/franciscoalro/TestPlugins/master/MaxSeries.cs3"
            $plugin.description = "MaxSeries v79 - Fixed WebView Interception and Autoplay (Jan 2026)"
            Write-Host "   -> Atualizado: v79" -ForegroundColor Green
        }
    }
    
    $jsonContent | ConvertTo-Json -Depth 5 -EscapeHandling EscapeNonAscii | Set-Content $jsonPath -Encoding UTF8
    Write-Host "✅ plugins.json salvo!" -ForegroundColor Green

} catch {
    Write-Host "⚠️ Erro ao atualizar plugins.json: $_" -ForegroundColor Red
    # Não sair, permitir commit manual se necessário
}


# 2. Git Automation
Write-Host ""
Write-Host "🔧 Iniciando operações Git..." -ForegroundColor Yellow

# Adicionar tudo (simples e eficaz)
git add .

$commitMsg = "MaxSeries v79: Critical Fixes for MegaEmbed & PlayerEmbedAPI (WebView Interception + Autoplay)"
git commit -m $commitMsg

# 3. Push
Write-Host "🚀 Enviando para GitHub..." -ForegroundColor Yellow
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Falha no push para master. Tentando main..." -ForegroundColor Yellow
    git push origin main
}

Write-Host ""
Write-Host "✅ SCRIPT CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "Versão 79 deve estar disponível em instantes."
Write-Host ""
