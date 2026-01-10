# 🎬 Playwright Video Extractor

Ferramenta para capturar links de vídeo, tokens e cookies de players embarcados usando Playwright.

## 📋 Características

✅ **Captura automática** de links de vídeo (.m3u8, .mp4, etc.)  
✅ **Extração de tokens** de URLs (auth, signature, etc.)  
✅ **Captura de cookies** com todos os atributos  
✅ **Captura de headers** HTTP completos  
✅ **Detecção automática** de botões de play  
✅ **Suporte a múltiplos players** (Abyss, Filemoon, StreamTape, etc.)  
✅ **Exportação JSON** de todos os dados capturados  

## 🚀 Instalação

### Versão Node.js

```bash
# Instalar Playwright
npm install playwright

# Ou globalmente
npm install -g playwright

# Instalar browsers
npx playwright install chromium
```

### Versão Python

```bash
# Instalar Playwright
pip install playwright

# Instalar browsers
playwright install chromium
```

## 📖 Uso

### Node.js

```bash
node playwright-video-extractor.js <URL>
```

**Exemplo:**
```bash
node playwright-video-extractor.js "https://playerthree.online/embed/12345"
```

### Python

```bash
python playwright_video_extractor.py <URL>
```

**Exemplo:**
```bash
python playwright_video_extractor.py "https://playerthree.online/embed/12345"
```

## 🎯 Casos de Uso

### 1. Capturar vídeo do MaxSeries

```bash
# Pegar URL do iframe do player
node playwright-video-extractor.js "https://playerthree.online/embed/..."
```

### 2. Capturar vídeo do PlayerEmbedAPI

```bash
node playwright-video-extractor.js "https://playerembedapi.link/..."
```

### 3. Capturar vídeo do MegaEmbed

```bash
node playwright-video-extractor.js "https://megaembed.link/..."
```

## 📊 Saída

O script irá:

1. **Abrir o navegador** (modo visível para debug)
2. **Navegar** para a URL fornecida
3. **Tentar clicar** no botão de play automaticamente
4. **Capturar** todas as requisições de vídeo
5. **Exibir** resultados no console
6. **Salvar** em arquivo JSON com timestamp

### Exemplo de Saída no Console

```
🚀 Playwright Video Extractor
================================================================================

🔍 Navegando para: https://playerthree.online/embed/12345

✅ Página carregada

🎬 Procurando botão de play...
🎬 Tentando clicar em: button.play-button

⏳ Aguardando links de vídeo (30s)...

✅ VÍDEO CAPTURADO!
📹 URL: https://abyss.to/playlist.m3u8?token=abc123&sig=xyz789
🔧 Method: GET

📥 RESPOSTA DE VÍDEO:
📹 URL: https://abyss.to/playlist.m3u8?token=abc123&sig=xyz789
📊 Status: 200
📦 Content-Type: application/vnd.apple.mpegurl

================================================================================
📊 RESULTADOS DA CAPTURA
================================================================================

✅ 1 link(s) de vídeo capturado(s)

────────────────────────────────────────────────────────────────────────────────
📹 VÍDEO #1
────────────────────────────────────────────────────────────────────────────────

🔗 URL:
https://abyss.to/playlist.m3u8?token=abc123&sig=xyz789

🎫 TOKENS EXTRAÍDOS:
  token: abc123
  sig: xyz789

📋 HEADERS:
  user-agent: Mozilla/5.0 ...
  referer: https://playerthree.online/
  origin: https://playerthree.online

────────────────────────────────────────────────────────────────────────────────
🍪 COOKIES CAPTURADOS (3)
────────────────────────────────────────────────────────────────────────────────

📌 session_id
   Domain: .abyss.to
   Value: xyz789abc123
   Path: /
   Secure: true
   HttpOnly: true

💾 Resultados salvos em: video-capture-1704902400000.json
================================================================================
```

### Exemplo de Arquivo JSON

```json
{
  "timestamp": "2026-01-10T13:30:00.000Z",
  "totalVideos": 1,
  "videos": [
    {
      "url": "https://abyss.to/playlist.m3u8?token=abc123&sig=xyz789",
      "tokens": {
        "token": "abc123",
        "sig": "xyz789"
      },
      "headers": {
        "user-agent": "Mozilla/5.0 ...",
        "referer": "https://playerthree.online/",
        "origin": "https://playerthree.online"
      },
      "method": "GET"
    }
  ],
  "cookies": [
    {
      "name": "session_id",
      "value": "xyz789abc123",
      "domain": ".abyss.to",
      "path": "/",
      "secure": true,
      "httpOnly": true
    }
  ]
}
```

## ⚙️ Configurações

Edite as constantes no início do arquivo:

```javascript
const CONFIG = {
  headless: false,      // true = sem interface gráfica
  timeout: 60000,       // Timeout de navegação (ms)
  waitForVideo: 30000,  // Tempo de espera por vídeos (ms)
};
```

## 🔍 Padrões de Vídeo Detectados

O script detecta automaticamente:

- `.m3u8` (HLS streams)
- `.mp4` (MP4 files)
- `.mkv` (MKV files)
- `.avi` (AVI files)
- `playlist.m3u8` (HLS playlists)
- `master.m3u8` (HLS master playlists)
- URLs de players conhecidos:
  - `abyss.to`
  - `filemoon`
  - `streamtape`
  - `doodstream`
  - `mixdrop`

## 🛠️ Troubleshooting

### Nenhum vídeo capturado?

1. **Aumente o tempo de espera:**
   ```javascript
   waitForVideo: 60000  // 60 segundos
   ```

2. **Verifique se o player carregou:**
   - O script abre o navegador visível por padrão
   - Observe se o vídeo começa a carregar

3. **Clique manualmente no play:**
   - Se o script não encontrar o botão, clique você mesmo
   - O script continuará capturando

### Erro de timeout?

```javascript
timeout: 120000  // 2 minutos
```

### Player com anti-bot?

O script já inclui:
- User-Agent realista
- Desabilita flags de automação
- Desabilita web security (para iframes)

## 📝 Integração com Cloudstream

Use os dados capturados para:

1. **Criar extractors** com os headers corretos
2. **Adicionar tokens** necessários nas requisições
3. **Configurar cookies** para autenticação
4. **Entender fluxos** de redirecionamento

### Exemplo de uso no Kotlin:

```kotlin
// Usando dados capturados
val videoUrl = "https://abyss.to/playlist.m3u8"
val headers = mapOf(
    "Referer" to "https://playerthree.online/",
    "Origin" to "https://playerthree.online",
    "User-Agent" to "Mozilla/5.0 ..."
)

callback.invoke(
    ExtractorLink(
        source = "Abyss",
        name = "Abyss",
        url = videoUrl,
        referer = "https://playerthree.online/",
        quality = Qualities.Unknown.value,
        isM3u8 = true,
        headers = headers
    )
)
```

## 🎓 Dicas Avançadas

### Capturar múltiplas páginas

Crie um arquivo `urls.txt`:
```
https://playerthree.online/embed/12345
https://playerthree.online/embed/67890
```

Execute:
```bash
# Node.js
cat urls.txt | while read url; do node playwright-video-extractor.js "$url"; done

# PowerShell
Get-Content urls.txt | ForEach-Object { node playwright-video-extractor.js $_ }
```

### Modo headless (sem interface)

Edite o arquivo:
```javascript
headless: true
```

### Adicionar novos padrões de vídeo

```javascript
const VIDEO_PATTERNS = [
  // ... padrões existentes
  /seu-novo-pattern/i,
];
```

## 📄 Licença

Ferramenta criada para análise e desenvolvimento de plugins Cloudstream.

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas!

---

**Criado com ❤️ para o projeto EstampaPro/Cloudstream**
