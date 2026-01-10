# 🚀 GUIA RÁPIDO - Playwright Video Extractor

## ⚡ Início Rápido (3 passos)

### 1️⃣ Instalação (já feita!)
```bash
✅ npm install playwright
✅ npx playwright install chromium
```

### 2️⃣ Uso Básico
```bash
node playwright-video-extractor.js "URL_DO_PLAYER"
```

### 3️⃣ Exemplo
```bash
node playwright-video-extractor.js "https://playerthree.online/embed/abc123"
```

## 📁 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `playwright-video-extractor.js` | Script principal (Node.js) |
| `playwright_video_extractor.py` | Script Python (alternativa) |
| `PLAYWRIGHT_README.md` | Documentação completa |
| `test-example.js` | Exemplo de teste |

## 🎯 Casos de Uso Comuns

### Capturar vídeo do MaxSeries
```bash
# 1. Abra o site maxseries.one no navegador
# 2. Inspecione o iframe do player
# 3. Copie a URL do iframe (playerthree.online/embed/...)
# 4. Execute:

node playwright-video-extractor.js "https://playerthree.online/embed/SEU_ID_AQUI"
```

### Capturar com Python
```bash
python playwright_video_extractor.py "URL_DO_PLAYER"
```

## 📊 O que será capturado?

✅ **URL do vídeo** (.m3u8, .mp4, etc.)  
✅ **Tokens** (auth, signature, etc.)  
✅ **Headers HTTP** (referer, origin, user-agent)  
✅ **Cookies** (session, auth, etc.)  
✅ **Arquivo JSON** com todos os dados  

## 🔍 Exemplo de Saída

```json
{
  "videos": [
    {
      "url": "https://abyss.to/playlist.m3u8?token=abc123",
      "tokens": {
        "token": "abc123"
      },
      "headers": {
        "referer": "https://playerthree.online/"
      }
    }
  ]
}
```

## ⚙️ Configurações Rápidas

Edite o arquivo `.js` ou `.py`:

```javascript
const CONFIG = {
  headless: false,      // true = sem janela
  timeout: 60000,       // 60 segundos
  waitForVideo: 30000,  // 30 segundos
};
```

## 🛠️ Troubleshooting

### ❌ Nenhum vídeo capturado?
- Aumente `waitForVideo: 60000` (60s)
- Clique manualmente no play
- Verifique se o player carregou

### ❌ Erro de timeout?
- Aumente `timeout: 120000` (2min)

### ❌ Player não abre?
- Verifique se Chromium foi instalado:
  ```bash
  npx playwright install chromium
  ```

## 📝 Próximos Passos

1. **Teste com URL real** do MaxSeries
2. **Analise o JSON** gerado
3. **Use os dados** no plugin Cloudstream

## 🎓 Integração com Cloudstream

Use os dados capturados para criar extractors:

```kotlin
val headers = mapOf(
    "Referer" to "https://playerthree.online/",
    "Origin" to "https://playerthree.online"
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

## 📞 Suporte

Leia a documentação completa em: `PLAYWRIGHT_README.md`

---

**✅ Tudo pronto! Execute agora:**
```bash
node playwright-video-extractor.js "SUA_URL_AQUI"
```
