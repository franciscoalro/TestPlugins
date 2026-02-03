Write-Host "=== Criando Alternativas na Nuvem ===" -ForegroundColor Green
Write-Host ""

# Criar estrutura para diferentes provedores de nuvem
$cloudProviders = @{
    "Netlify" = "https://netlify.app"
    "Vercel" = "https://vercel.app" 
    "GitHub Pages" = "https://github.io"
    "Firebase" = "https://firebase.app"
    "Surge.sh" = "https://surge.sh"
    "Render" = "https://render.com"
}

Write-Host "Opcoes de hospedagem gratuita:" -ForegroundColor Cyan
foreach ($provider in $cloudProviders.GetEnumerator()) {
    Write-Host "  - $($provider.Key): $($provider.Value)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Preparando arquivos para deploy na nuvem ===" -ForegroundColor Green

# Criar pasta para deploy
$deployDir = "cloud-deploy"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copiar arquivos necessarios
Copy-Item "builds/*" $deployDir -Recurse -Force

# Criar index.html para visualizacao
$indexHtml = @"
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BRCloudStream Repository</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .url-box { background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .url { font-family: monospace; background: #000; padding: 10px; border-radius: 4px; word-break: break-all; }
        .plugin-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .plugin { background: #2d2d2d; padding: 15px; border-radius: 8px; }
        .plugin h3 { margin: 0 0 10px 0; color: #4CAF50; }
        .size { color: #888; font-size: 0.9em; }
        .copy-btn { background: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-left: 10px; }
        .copy-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇧🇷 BRCloudStream Repository</h1>
            <p>Repositório brasileiro para Cloudstream com 11 plugins</p>
        </div>

        <div class="url-box">
            <h2>📱 URL para Cloudstream:</h2>
            <div class="url" id="repoUrl">https://SEU-DOMINIO.com/repo.json</div>
            <button class="copy-btn" onclick="copyUrl()">Copiar URL</button>
        </div>

        <div class="url-box">
            <h2>🔗 URLs Alternativas:</h2>
            <div class="url">https://SEU-DOMINIO.com/repo-alternative.json</div>
            <div class="url" style="margin-top: 10px;">https://SEU-DOMINIO.com/plugins.json</div>
        </div>

        <h2>🎮 Plugins Disponíveis:</h2>
        <div class="plugin-list" id="pluginList">
            <!-- Plugins serão carregados via JavaScript -->
        </div>

        <div style="margin-top: 40px; text-align: center; color: #888;">
            <p>Atualizado automaticamente • Hospedado na nuvem</p>
        </div>
    </div>

    <script>
        function copyUrl() {
            const url = document.getElementById('repoUrl').textContent;
            navigator.clipboard.writeText(url).then(() => {
                alert('URL copiada!');
            });
        }

        // Carregar plugins dinamicamente
        fetch('./plugins.json')
            .then(response => response.json())
            .then(plugins => {
                const container = document.getElementById('pluginList');
                plugins.forEach(plugin => {
                    const div = document.createElement('div');
                    div.className = 'plugin';
                    div.innerHTML = `
                        <h3>${plugin.name}</h3>
                        <p>${plugin.description}</p>
                        <div class="size">Versão: ${plugin.version} • Tamanho: ${Math.round(plugin.fileSize/1024)} KB</div>
                    `;
                    container.appendChild(div);
                });
            })
            .catch(err => console.error('Erro ao carregar plugins:', err));
    </script>
</body>
</html>
"@

Set-Content -Path "$deployDir/index.html" -Value $indexHtml -Encoding UTF8

# Criar README para deploy
$deployReadme = @"
# Deploy do BRCloudStream Repository

## Opções de Hospedagem Gratuita

### 1. Netlify (Recomendado)
1. Acesse https://netlify.com
2. Faça login com GitHub
3. Arraste a pasta `cloud-deploy` para o site
4. Sua URL será: `https://SEU-SITE.netlify.app/repo.json`

### 2. Vercel
1. Acesse https://vercel.com
2. Faça login com GitHub
3. Importe este projeto
4. Sua URL será: `https://SEU-SITE.vercel.app/repo.json`

### 3. GitHub Pages
1. Crie um novo repositório no GitHub
2. Faça upload dos arquivos desta pasta
3. Ative GitHub Pages nas configurações
4. Sua URL será: `https://SEU-USUARIO.github.io/SEU-REPO/repo.json`

### 4. Firebase Hosting
1. Instale Firebase CLI: `npm install -g firebase-tools`
2. Execute: `firebase login`
3. Execute: `firebase init hosting`
4. Execute: `firebase deploy`

### 5. Surge.sh
1. Instale Surge: `npm install -g surge`
2. Na pasta cloud-deploy, execute: `surge`
3. Sua URL será: `https://SEU-DOMINIO.surge.sh/repo.json`

## Arquivos Incluídos
- `repo.json` - Configuração principal do repositório
- `repo-alternative.json` - Versão alternativa
- `plugins.json` - Lista de plugins
- `plugins-minimal.json` - Versão minimalista
- `*.cs3` - Arquivos dos plugins (11 plugins)
- `*.jar` - Arquivos JAR dos plugins
- `index.html` - Página web para visualização

## Teste
Após o deploy, teste a URL no Cloudstream:
`https://SEU-DOMINIO/repo.json`
"@

Set-Content -Path "$deployDir/README.md" -Value $deployReadme -Encoding UTF8

# Criar arquivo de configuração para Netlify
$netlifyToml = @"
[build]
  publish = "."

[[headers]]
  for = "*.json"
  [headers.values]
    Content-Type = "application/json"
    Access-Control-Allow-Origin = "*"

[[headers]]
  for = "*.cs3"
  [headers.values]
    Content-Type = "application/octet-stream"
    Access-Control-Allow-Origin = "*"

[[headers]]
  for = "*.jar"
  [headers.values]
    Content-Type = "application/java-archive"
    Access-Control-Allow-Origin = "*"
"@

Set-Content -Path "$deployDir/netlify.toml" -Value $netlifyToml -Encoding UTF8

# Criar vercel.json
$vercelJson = @{
    "headers" = @(
        @{
            "source" = "/(.*)"
            "headers" = @(
                @{
                    "key" = "Access-Control-Allow-Origin"
                    "value" = "*"
                }
            )
        }
    )
}

$vercelJson | ConvertTo-Json -Depth 10 | Set-Content -Path "$deployDir/vercel.json" -Encoding UTF8

Write-Host "✅ Arquivos preparados em: $deployDir" -ForegroundColor Green
Write-Host ""

# Listar arquivos criados
Write-Host "Arquivos criados:" -ForegroundColor Cyan
Get-ChildItem $deployDir | ForEach-Object {
    $size = if ($_.PSIsContainer) { "pasta" } else { "$([math]::Round($_.Length/1024, 1)) KB" }
    Write-Host "  📄 $($_.Name) - $size" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Próximos Passos ===" -ForegroundColor Green
Write-Host "1. Escolha um provedor de nuvem (Netlify recomendado)" -ForegroundColor Cyan
Write-Host "2. Faça upload da pasta 'cloud-deploy'" -ForegroundColor Cyan
Write-Host "3. Anote a URL do seu site" -ForegroundColor Cyan
Write-Host "4. Use: https://SEU-SITE/repo.json no Cloudstream" -ForegroundColor Cyan