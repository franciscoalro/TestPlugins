# Script para criar release v149 no GitHub
# MaxSeries v149 - WebView Hibrido: Interceptacao + Script + additionalUrls

$ErrorActionPreference = "Stop"

Write-Host "=== CRIANDO RELEASE v149 ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se o arquivo .cs3 existe
if (-not (Test-Path "MaxSeries\build\MaxSeries.cs3")) {
    Write-Host "ERRO: MaxSeries.cs3 nao encontrado!" -ForegroundColor Red
    Write-Host "Execute: .\gradlew.bat MaxSeries:make" -ForegroundColor Yellow
    exit 1
}

# Obter tamanho do arquivo
$fileSize = (Get-Item "MaxSeries\build\MaxSeries.cs3").Length
Write-Host "Tamanho do arquivo: $fileSize bytes" -ForegroundColor Green

# Verificar se gh esta instalado
try {
    gh --version | Out-Null
} catch {
    Write-Host "ERRO: GitHub CLI (gh) nao esta instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Verificar se esta autenticado
try {
    gh auth status | Out-Null
} catch {
    Write-Host "ERRO: Nao esta autenticado no GitHub!" -ForegroundColor Red
    Write-Host "Execute: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== CRIANDO RELEASE v149 ===" -ForegroundColor Cyan

# Criar release usando arquivo de notas
$releaseNotes = @"
MaxSeries v149 - WebView Hibrido: Interceptacao + Script + additionalUrls

PROBLEMA v148:
- WebView timeout 15s, retorna URL original
- Interceptacao NAO captura requisicoes de rede
- Logs ADB confirmaram falha em 2 videos (xez5rx, hkmfvu)

SOLUCAO v149 - ABORDAGEM HIBRIDA:

1. Script JavaScript COMPLETO:
   - Busca variaveis globais: __PLAYER_CONFIG__, playlistUrl
   - 3 regex no HTML: cf-master, index, .txt
   - Retorna primeira URL valida encontrada

2. additionalUrls (6 padroes):
   - /api/v1/info
   - /api/v1/video
   - /v4/.*/cf-master
   - /v4/.*/index
   - /v4/.*\.txt
   - /v4/.*\.woff

3. Prioridade:
   Script > additionalUrls > Interceptacao

4. Timeout aumentado:
   15s -> 20s

5. Validacao melhorada:
   - Aceita: /v4/ OR index OR cf-master OR .txt
   - Rejeita: URL original sem /v4/

6. Logs detalhados:
   - response.url (interceptacao)
   - scriptResult (JavaScript)
   - Qual metodo funcionou

MUDANCAS TECNICAS:

MegaEmbedExtractorV7.kt:
- hybridScript: Busca completa no HTML
- additionalUrls: Lista de 6 padroes
- scriptCallback: Captura URL do script
- Logs: response.url + scriptResult
- Validacao: /v4/ OR index OR cf-master OR .txt

build.gradle.kts:
- version = 149
- description: WebView Hibrido

COMO TESTAR:

1. Atualizar no Cloudstream
2. Testar videos: xez5rx, hkmfvu
3. Verificar logs: adb logcat | findstr MegaEmbedV7
4. Procurar: Script capturou ou WebView interceptou

INSTALACAO:
- Via Cloudstream: Settings > Extensions > Update MaxSeries
- Manual: adb install -r MaxSeries.cs3

Build: SUCCESSFUL
Tamanho: $fileSize bytes
Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm')
"@

gh release create v149 `
    "MaxSeries\build\MaxSeries.cs3" `
    --title "MaxSeries v149 - WebView Hibrido" `
    --notes $releaseNotes

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== RELEASE v149 CRIADO COM SUCESSO! ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL: https://github.com/franciscoalro/TestPlugins/releases/tag/v149" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "1. Atualizar plugins.json para v149" -ForegroundColor White
    Write-Host "2. Commit e push" -ForegroundColor White
    Write-Host "3. Atualizar no Cloudstream app" -ForegroundColor White
    Write-Host "4. Testar com: xez5rx, hkmfvu" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "ERRO ao criar release!" -ForegroundColor Red
    exit 1
}
