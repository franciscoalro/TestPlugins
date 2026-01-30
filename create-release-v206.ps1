# Script para criar release v206 no GitHub
# Requer GitHub CLI (gh) instalado

$VERSION = "v206"
$RELEASE_TITLE = "Release v206 - Kotlin 2.3.0 Upgrade (7 Providers)"
$RELEASE_NOTES = @"
# 🎉 Release v206 - Kotlin 2.3.0 Upgrade

## 7 Providers Disponíveis

Esta release inclui **7 providers** totalmente funcionais:

1. **AnimesOnlineCC** v10 (15.57 KB)
2. **MaxSeries** v206 (190.49 KB)
3. **MegaFlix** v2 (16.41 KB)
4. **NetCine** v2 (19.59 KB)
5. **OverFlix** v2 (25.50 KB)
6. **PobreFlix** v2 (22.88 KB)
7. **Vizer** v2 (25.75 KB)

## 🔧 Mudanças Técnicas

### Kotlin 2.3.0 Upgrade
- ✅ Atualizado de Kotlin 1.9.23 para 2.3.0
- ✅ Compatível com Cloudstream library (commit 8a4480dc42)
- ✅ Todas as dependências atualizadas

### Correções de API
- ✅ **Vizer**: Corrigido uso da API Score (de Int? para Score.from10())
- ✅ Todos os providers compilando sem erros
- ✅ Build otimizado e estável

## 📦 Instalação

### Via Repositório (Recomendado)
1. Abra o Cloudstream
2. Vá em **Configurações** → **Extensões**
3. Adicione o repositório:
   ``````
   https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/repo.json
   ``````
4. Instale os providers desejados

### Download Manual
Baixe os arquivos .cs3 desta release e instale via Cloudstream.

## 🙏 Créditos
Desenvolvido por **franciscoalro**
"@

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Criando Release v206 no GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gh está instalado
Write-Host "Verificando GitHub CLI..." -ForegroundColor Yellow
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ GitHub CLI (gh) não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ GitHub CLI encontrado" -ForegroundColor Green
Write-Host ""

# Verificar se está autenticado
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Não autenticado no GitHub!" -ForegroundColor Red
    Write-Host "Execute: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Autenticado no GitHub" -ForegroundColor Green
Write-Host ""

# Verificar se os arquivos .cs3 existem
Write-Host "Verificando arquivos .cs3..." -ForegroundColor Yellow
$files = @(
    "AnimesOnlineCC.cs3",
    "MaxSeries.cs3",
    "MegaFlix.cs3",
    "NetCine.cs3",
    "OverFlix.cs3",
    "PobreFlix.cs3",
    "Vizer.cs3"
)

$allFilesExist = $true
foreach ($file in $files) {
    if (Test-Path $file) {
        $size = [math]::Round((Get-Item $file).Length / 1KB, 2)
        Write-Host "  ✅ $file ($size KB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file não encontrado!" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "❌ Alguns arquivos .cs3 não foram encontrados!" -ForegroundColor Red
    Write-Host "Execute: ./gradlew make -x lint -x lintDebug -x lintRelease" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Criando Release $VERSION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Criar a release
Write-Host "Criando release no GitHub..." -ForegroundColor Yellow
$releaseCmd = "gh release create $VERSION " + ($files -join " ") + " --title `"$RELEASE_TITLE`" --notes `"$RELEASE_NOTES`""

try {
    Invoke-Expression $releaseCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ Release criada com sucesso!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Release: https://github.com/franciscoalro/TestPlugins/releases/tag/$VERSION" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Próximos passos:" -ForegroundColor Yellow
        Write-Host "1. Commit e push do plugins.json atualizado" -ForegroundColor White
        Write-Host "2. Verificar se a release está pública" -ForegroundColor White
        Write-Host "3. Testar instalação via repositório" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ Erro ao criar release!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erro ao criar release: $_" -ForegroundColor Red
    exit 1
}
