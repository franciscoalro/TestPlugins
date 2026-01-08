# Script para atualizar automaticamente o CloudstreamRepo
param(
    [string]$CloudstreamRepoPath = "../CloudstreamRepo"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Auto Update CloudstreamRepo Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar se o CloudstreamRepo existe
if (-not (Test-Path $CloudstreamRepoPath)) {
    Write-Host "❌ CloudstreamRepo não encontrado em: $CloudstreamRepoPath" -ForegroundColor Red
    Write-Host "Clone o repositório primeiro:" -ForegroundColor Yellow
    Write-Host "git clone https://github.com/franciscoalro/CloudstreamRepo.git" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 CloudstreamRepo encontrado: $CloudstreamRepoPath" -ForegroundColor Green

# Verificar se há arquivos .cs3 na pasta atual
$cs3Files = Get-ChildItem -Path "." -Filter "*.cs3" -ErrorAction SilentlyContinue

if ($cs3Files.Count -eq 0) {
    Write-Host "⚠️  Nenhum arquivo .cs3 encontrado na pasta atual" -ForegroundColor Yellow
    Write-Host "Baixe os artifacts do GitHub Actions primeiro:" -ForegroundColor Yellow
    Write-Host "https://github.com/franciscoalro/TestPlugins/actions" -ForegroundColor Yellow
    
    # Tentar baixar automaticamente (se gh CLI estiver disponível)
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        Write-Host "🔄 Tentando baixar artifacts automaticamente..." -ForegroundColor Blue
        try {
            gh run download --repo franciscoalro/TestPlugins -n "Built plugins"
            Write-Host "✅ Artifacts baixados com sucesso!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Erro ao baixar artifacts. Baixe manualmente." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "💡 Instale o GitHub CLI (gh) para download automático" -ForegroundColor Blue
        exit 1
    }
}

# Copiar arquivos .cs3 para o CloudstreamRepo
Write-Host "📦 Copiando arquivos .cs3..." -ForegroundColor Blue
$cs3Files = Get-ChildItem -Path "." -Filter "*.cs3"
foreach ($file in $cs3Files) {
    Copy-Item $file.FullName -Destination $CloudstreamRepoPath -Force
    Write-Host "  ✅ Copiado: $($file.Name)" -ForegroundColor Green
}

# Copiar plugins.json atualizado
Write-Host "📝 Atualizando plugins.json..." -ForegroundColor Blue
if (Test-Path "plugins.json") {
    Copy-Item "plugins.json" -Destination $CloudstreamRepoPath -Force
    Write-Host "  ✅ plugins.json atualizado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  plugins.json não encontrado" -ForegroundColor Yellow
}

# Navegar para o CloudstreamRepo e fazer commit
Write-Host "🔄 Fazendo commit no CloudstreamRepo..." -ForegroundColor Blue
Push-Location $CloudstreamRepoPath

try {
    # Verificar status do git
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        git add .
        git commit -m "Update plugins - MaxSeries v8 CloudStream v9.0 compatibility"
        
        Write-Host "✅ Commit realizado com sucesso!" -ForegroundColor Green
        Write-Host "🚀 Fazendo push..." -ForegroundColor Blue
        
        git push
        Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
        
        # Mostrar informações do repositório
        Write-Host "`n📊 Informações do repositório:" -ForegroundColor Cyan
        Write-Host "URL: https://github.com/franciscoalro/CloudstreamRepo" -ForegroundColor Blue
        Write-Host "Plugins JSON: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json" -ForegroundColor Blue
        
    } else {
        Write-Host "ℹ️  Nenhuma alteração detectada no CloudstreamRepo" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Erro durante o commit/push: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Pop-Location
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Processo concluído!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Mostrar próximos passos
Write-Host "`n📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "1. Verificar se os plugins aparecem no CloudStream" -ForegroundColor White
Write-Host "2. Testar o MaxSeries v8 com CloudStream v9.0" -ForegroundColor White
Write-Host "3. Reportar qualquer problema encontrado" -ForegroundColor White