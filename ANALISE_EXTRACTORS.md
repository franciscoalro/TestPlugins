# Análise de Engenharia Reversa - Extractors MaxSeries

## Resumo da Análise (Atualizado Jan 2026)

### 1. PlayerEmbedAPI ✅ RESOLVIDO
**Cadeia de redirecionamentos:**
```
playerembedapi.link → short.icu → abyss.to → storage.googleapis.com
```

**DESCOBERTA IMPORTANTE:**
O vídeo final é servido do **Google Cloud Storage**!
```
URL: https://storage.googleapis.com/mediastorage/{timestamp}/{hash}/{id}.mp4
Exemplo: https://storage.googleapis.com/mediastorage/1767974518939/j4oqvaszmo9/307308779.mp4
```

**Características:**
- MP4 direto, sem necessidade de decriptação
- Parâmetros de chunk/qualidade na URL (360p, 720p, etc.)
- Referer necessário: `https://abyss.to/`

**Viabilidade para Kotlin:** ✅ Viável com WebView
- WebView navega pelos iframes e captura `video.currentSrc`
- URL do GCS é um MP4 direto que funciona com headers corretos

---

### 2. MegaEmbed ⚠️ PARCIALMENTE RESOLVIDO
**Estrutura:**
```
megaembed.link/#ID → API /api/v1/info?id=ID → Dados criptografados
```

**Características:**
- Tem API JSON: `https://megaembed.link/api/v1/info?id={ID}`
- Usa VidStack player com HLS
- **API retorna dados criptografados** (hex string)
- Decriptação usa AES-CBC com chave/IV gerados dinamicamente

**Função de decriptação (do JavaScript):**
```javascript
// Chave gerada baseada em window.location.hash
v = () => { /* gera chave de 16 bytes */ }

// IV gerado baseado em window.location
T = () => { /* gera IV de 16 bytes */ }

// Decriptação
S = async (data) => {
    const key = await crypto.subtle.importKey("raw", v(), {name: "AES-CBC"}, true, ["decrypt"]);
    const decrypted = await crypto.subtle.decrypt({name: "AES-CBC", iv: T()}, key, hexToBytes(data));
    return decrypted;
}
```

**Viabilidade para Kotlin nativo:** ⚠️ Parcialmente viável
- Seria necessário replicar a lógica de geração de chave/IV
- A chave depende de `window.location.hash` - difícil de replicar sem contexto de navegador

---

### 3. PlayerthreeOnline (Agregador)
**Estrutura:**
```
playerthree.online/embed/{slug}/ → Lista episódios → Botões com data-source
```

**Formato dos botões:**
```html
<button data-source="https://playerembedapi.link/?v=xxx" data-type="iframe">Player #1</button>
<button data-source="https://megaembed.link/#xxx" data-type="iframe">Player #2</button>
```

**Viabilidade:** ✅ Fácil de parsear
- Basta extrair `data-source` dos botões para obter URLs dos players

---

### 4. MyVidPlay/DoodStream
**Status:** ✅ Funciona
- CloudStream já tem extractor nativo
- Endpoint HTTP direto disponível

---

## Conclusões

### Fontes que funcionam (referência):
- DoodStream/MyVidPlay - padrão simples, endpoint direto

### Fontes problemáticas:
1. **PlayerEmbedAPI** - cadeia de redirects + JS ofuscado
2. **MegaEmbed** - API criptografada com chave dinâmica

### Recomendação para Extractors Kotlin:

1. **PlayerEmbedAPIExtractor**: Usar WebView como método principal
   - Não há como replicar a decriptação do `core.bundle.js` nativamente
   
2. **MegaEmbedExtractor**: Tentar duas abordagens:
   - Método 1: Tentar replicar a geração de chave/IV (complexo)
   - Método 2: WebView como fallback

### Padrão observado nas fontes que funcionam:
```
URL embed → Request HTTP simples → Resposta com .m3u8/.mp4 direto
Headers necessários: Referer, User-Agent
```

### Padrão das fontes problemáticas:
```
URL embed → Múltiplos redirects/iframes → JS ofuscado → Token/decriptação → URL final
```

---

## Arquivos de Análise Gerados
- `megaembed_index.js` - JavaScript principal do MegaEmbed
- `megaembed_prod.js` - JavaScript de produção
- `playerthree_response.html` - HTML do agregador
- `deep_capture.json` - Captura de requisições de rede
- `sources_capture.json` - Fontes extraídas dos episódios
