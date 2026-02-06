# Script de Deploy para GitHub - FranciscoAlro TestPlugins
# Este script prepara e envia os arquivos atualizados para o repositório GitHub

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY PARA GITHUB - TestPlugins" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "builds")) {
    Write-Host "❌ ERRO: Diretório 'builds' não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script na raiz do projeto (brcloudstream)" -ForegroundColor Yellow
    exit 1
}

# Verificar arquivos essenciais
$requiredFiles = @(
    "builds/plugins.json",
    "builds/repo.json",
    "builds/MaxSeries.cs3",
    "builds/MegaFlix.cs3",
    "builds/PobreFlix.cs3",
    "builds/NetCine.cs3",
    "builds/DonghuaNoSekai.cs3",
    "builds/Doramas.cs3",
    "builds/NovelasFlix.cs3",
    "builds/Streamberry.cs3",
    "builds/TopFilmes.cs3",
    "builds/AnimesCloud.cs3",
    "builds/AnimesDigital.cs3",
    "builds/Anroll.cs3",
    "builds/BetterAnime.cs3",
    "builds/EmbedCanais.cs3",
    "builds/FilmesOn.cs3",
    "builds/GoFlix.cs3",
    "builds/OverFlix.cs3",
    "builds/UltraCine.cs3",
    "builds/VisionCine.cs3"
)

Write-Host "📁 Verificando arquivos..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  ✅ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - NÃO ENCONTRADO" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ ERRO: Arquivos ausentes!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RESUMO DOS ARQUIVOS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Listar tamanhos dos arquivos .cs3
Get-ChildItem -Path "builds" -Filter "*.cs3" | Sort-Object Name | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1KB, 2)
    Write-Host ("  {0,-30} {1,10} KB" -f $_.Name, $sizeKB) -ForegroundColor White
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  PRÓXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Os arquivos estão prontos para serem enviados ao GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "Execute os seguintes comandos Git:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. git add builds/" -ForegroundColor Cyan
Write-Host "  2. git add plugins.json repo.json MaxSeries/build.gradle.kts" -ForegroundColor Cyan
Write-Host "  3. git commit -m \"Atualizar plugins para v265 - corrigir tamanhos dos arquivos\"" -ForegroundColor Cyan
Write-Host "  4. git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ou, se preferir, use o GitHub Desktop para fazer o commit e push." -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  URL DO REPOSITÓRIO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  https://github.com/franciscoalro/TestPlugins" -ForegroundColor White
Write-Host ""
Write-Host "  URL para adicionar no CloudStream:" -ForegroundColor Yellow
Write-Host "  https://raw.githubusercontent.com/franciscoalro/TestPlugins/main/builds/repo.json" -ForegroundColor Green
Write-Host ""
