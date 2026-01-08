# Script para criar o CloudstreamRepo corretamente
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Criando CloudstreamRepo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar se gh CLI está disponível
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ GitHub CLI (gh) não encontrado" -ForegroundColor Red
    Write-Host "Instale em: https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Criar repositório no GitHub
Write-Host "🔄 Criando repositório CloudstreamRepo..." -ForegroundColor Blue
try {
    gh repo create franciscoalro/CloudstreamRepo --public --description "CloudStream Extensions Repository" --clone
    Write-Host "✅ Repositório criado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Repositório pode já existir, tentando clonar..." -ForegroundColor Yellow
    git clone https://github.com/franciscoalro/CloudstreamRepo.git
}

# Navegar para o repositório
cd CloudstreamRepo

# Criar estrutura básica
Write-Host "📁 Criando estrutura básica..." -ForegroundColor Blue

# Criar repo.json
@"
{
    "name": "CloudstreamRepo",
    "description": "Repositório oficial de extensões CloudStream",
    "manifestVersion": 1,
    "pluginLists": [
        "https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json"
    ]
}
"@ | Out-File -FilePath "repo.json" -Encoding UTF8

# Criar plugins.json inicial
@"
[
    {
        "name": "MaxSeries",
        "internalName": "MaxSeries",
        "description": "Assista séries online em HD no MaxSeries. Compatível com CloudStream v9.0 (v8).",
        "version": 8,
        "authors": [
            "franciscoalro"
        ],
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "status": 1,
        "language": "pt-BR",
        "tvTypes": [
            "TvSeries",
            "Movie"
        ],
        "iconUrl": "https://www.maxseries.one/wp-content/themes/dooplay/assets/img/favicon.png",
        "apiVersion": 1,
        "isAdult": false,
        "fileSize": 15000,
        "url": "https://github.com/franciscoalro/TestPlugins/releases/download/v9.0/MaxSeries.cs3"
    },
    {
        "name": "AnimesOnlineCC",
        "internalName": "AnimesOnlineCC",
        "description": "Assista animes online grátis em HD no AnimesOnlineCC. Grande catálogo de animes legendados e dublados.",
        "version": 6,
        "authors": [
            "franciscoalro"
        ],
        "repositoryUrl": "https://github.com/franciscoalro/TestPlugins",
        "status": 1,
        "language": "pt-BR",
        "tvTypes": [
            "Anime",
            "OVA",
            "AnimeMovie"
        ],
        "iconUrl": "https://animesonlinecc.to/wp-content/uploads/2020/01/cropped-favicon-32x32.png",
        "apiVersion": 1,
        "isAdult": false,
        "fileSize": 15000,
        "url": "https://github.com/franciscoalro/TestPlugins/releases/download/v9.0/AnimesOnlineCC.cs3"
    }
]
"@ | Out-File -FilePath "plugins.json" -Encoding UTF8

# Criar README
@"
# CloudstreamRepo

Repositório oficial de extensões CloudStream por franciscoalro.

## 📦 Como Usar

1. Abra o CloudStream
2. Vá em **Configurações** → **Extensões** → **Adicionar Repositório**
3. Cole a URL: ``https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json``
4. Instale os plugins desejados

## 🔌 Plugins Disponíveis

- **MaxSeries v8**: Séries e filmes em HD
- **AnimesOnlineCC v6**: Animes legendados e dublados

## 🔗 Links

- **Desenvolvimento**: https://github.com/franciscoalro/TestPlugins
- **Plugin JSON**: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/plugins.json
"@ | Out-File -FilePath "README.md" -Encoding UTF8

# Fazer commit inicial
Write-Host "💾 Fazendo commit inicial..." -ForegroundColor Blue
git add .
git commit -m "Initial commit: CloudStream repository setup"
git push -u origin main

# Habilitar GitHub Pages
Write-Host "🌐 Habilitando GitHub Pages..." -ForegroundColor Blue
try {
    gh api repos/franciscoalro/CloudstreamRepo/pages -X POST -f source.branch=main -f source.path=/
    Write-Host "✅ GitHub Pages habilitado!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao habilitar GitHub Pages automaticamente" -ForegroundColor Yellow
    Write-Host "Habilite manualmente em: https://github.com/franciscoalro/CloudstreamRepo/settings/pages" -ForegroundColor Blue
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " CloudstreamRepo criado com sucesso!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📋 URLs para usar no CloudStream:" -ForegroundColor Yellow
Write-Host "🔗 Raw GitHub: https://raw.githubusercontent.com/franciscoalro/CloudstreamRepo/main/repo.json" -ForegroundColor Green
Write-Host "🔗 GitHub Pages: https://franciscoalro.github.io/CloudstreamRepo/repo.json" -ForegroundColor Green
Write-Host "`n💡 Use a URL Raw GitHub se GitHub Pages não funcionar imediatamente" -ForegroundColor Blue