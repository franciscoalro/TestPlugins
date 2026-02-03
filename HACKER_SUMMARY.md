# PLAYEREMBEDAPI - HACKER SUMMARY (White Hat)

## Ferramentas Criadas

### 1. playerembedapi_final_extractor.py [PRINCIPAL]
Extrator unificado - use este primeiro!

```bash
python playerembedapi_final_extractor.py playerembedapi_kBJLtxCD3.html
python playerembedapi_final_extractor.py https://playerembedapi.link/?v=xxx
```

**O que faz:**
- Extrai campo 'datas' base64
- Decodifica JSON com slug/md5_id/user_id
- Constroi URLs de CDN
- Lista scripts carregados
- Gera recomendacao

### 2. hacker_analyzer.py
Analisador estatico avancado

```bash
python hacker_analyzer.py <arquivo.html>
```

**O que faz:**
- Analise de entropia do campo 'media'
- Busca de URLs de video no HTML
- Identificacao de scripts
- Gera relatorio JSON

### 3. PlayerEmbedAPIExtractor.kt
Implementacao para MaxSeries Provider

**Integracao:**
```kotlin
// Em MaxSeriesProvider.kt
private val playerEmbedExtractor = PlayerEmbedAPIExtractor()

override suspend fun loadLinks(...) {
    playerEmbedExtractor.extract(playerUrl, callback)
}
```

**Tecnicas implementadas:**
1. HTTP direto (regex)
2. Parse do campo 'datas'
3. WebView com interceptacao sssrr.org
4. JavaScript injection (jwplayer)

### 4. hacker_network_interceptor.py
Interceptacao de rede com Playwright

```bash
# Requer: pip install playwright && playwright install
python hacker_network_interceptor.py https://playerembedapi.link/?v=xxx
```

**O que faz:**
- Abre browser headless
- Intercepta todas as requisicoes
- Captura URLs de video
- Extrai de jwplayer.getPlaylist()
- Salva headers e cookies

### 5. hacker_crypto_breaker.py
Criptoanalise do campo 'media'

```bash
python hacker_crypto_breaker.py <arquivo.html>
```

**O que faz:**
- Calcula entropia de Shannon
- Detecta algoritmo de criptografia
- Tenta decriptacao AES (brute force)
- Analisa core.bundle.js

### 6. hacker_playerembedapi_advanced.py
Suite completa de engenharia reversa

**Modulos:**
- PlayerEmbedAPIAnalyzer
- AdvancedVideoExtractor
- EntropyAnalyzer
- Virtual DOM manipulation

---

## Arquitetura do PlayerEmbedAPI

```
Usuario
   |
   v
MaxSeries (Provider)
   |
   v
PlayerEmbedAPI Page
   |-- HTML com: const datas = "base64..."
   |-- Scripts: jwplayer + core.bundle.js
   |
   v
JavaScript Execution
   |-- window.SoTrym(JSON.parse(atob(datas)))
   |-- Decripta campo 'media'
   |-- Configura JWPlayer
   |
   v
CDN (sssrr.org)
   |-- https://{slug}.sssrr.org/sora/{md5_id}/
   |-- Retorna playlist/video
```

---

## Dados Extraidos

### Estrutura do JSON
```json
{
    "slug": "kBJLtxCD3",
    "md5_id": 28930647,
    "user_id": 482120,
    "media": "{dados_criptografados}",
    "config": {
        "poster": false,
        "preview": false,
        "isDownload": true
    }
}
```

### URLs Construidas
```
https://{slug}.sssrr.org/sora/{md5_id}/
https://cdn.sssrr.org/sora/{md5_id}/
https://{slug}.sssrr.org/future
```

### Scripts Criticos
```
https://statics.sssrr.org/player/jwplayer.min.js
https://iamcdn.net/player-v2/core.bundle.js  (contem SoTrym)
```

---

## Tecnicas de Extrasao (Prioridade)

### 1. HTTP Direto [Rapido]
- Procura por URLs de video no HTML
- Sucesso: Baixo (nao estao no HTML)

### 2. Parse 'datas' [Rapido]
- Decodifica base64
- Obtem slug + md5_id
- Constroi URLs CDN

### 3. WebView Intercept [Confiavel]
```kotlin
WebViewResolver(
    interceptUrl = Regex("""(?i)(sssrr\.org|\.m3u8|\.mp4)"""),
    timeout = 35_000L
)
```

### 4. JavaScript Injection [Confiavel]
```javascript
var jw = jwplayer();
var playlist = jw.getPlaylist();
return playlist[0].file;
```

### 5. Browser Automation [Mais confiavel]
- Playwright/Selenium
- Network monitoring
- Captura todas as requisicoes

---

## Headers Obrigatorios

```kotlin
val HEADERS = mapOf(
    "Referer" to "https://playerembedapi.link/",
    "Origin" to "https://playerembedapi.link",
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

---

## Exemplo de Uso (MaxSeries)

```kotlin
class MaxSeriesProvider : MainAPI() {
    
    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        
        // Obter player URL
        val doc = app.get(data).document
        val iframe = doc.selectFirst("iframe")?.attr("src") ?: return false
        
        // Verificar se eh PlayerEmbedAPI
        if (iframe.contains("playerembedapi")) {
            extractPlayerEmbedAPI(iframe, callback)
        }
        
        return true
    }
    
    private suspend fun extractPlayerEmbedAPI(
        url: String, 
        callback: (ExtractorLink) -> Unit
    ) {
        // Tecnica 1: WebView com interceptacao
        val resolver = WebViewResolver(
            interceptUrl = Regex("""(?i)(sssrr\.org|\.m3u8|\.mp4)"""),
            timeout = 35_000L
        )
        
        val response = app.get(url, interceptor = resolver)
        
        if (response.url.contains(".m3u8")) {
            M3u8Helper.generateM3u8("PlayerEmbedAPI", response.url, url)
                .forEach { callback(it) }
        }
    }
}
```

---

## Resultados Obtidos

### Analise do Arquivo kBJLtxCD3.html
- **Slug**: kBJLtxCD3
- **MD5 ID**: 28930647
- **User ID**: 482120
- **Entropia**: 7.8/8.0 (criptografado)
- **Scripts**: JWPlayer + core.bundle.js
- **URLs Construidas**: 3
- **URLs no HTML**: 0 (carregadas dinamicamente)

### Conclusao
O campo 'media' esta criptografado e requer:
1. WebView para executar JavaScript
2. Interceptacao de sssrr.org
3. Headers Referer/Origin

---

## Proximos Passos

1. **Testar URLs construidas** com WebView
2. **Analisar core.bundle.js** para entender SoTrym
3. **Implementar extrator** no MaxSeries Provider
4. **Adicionar fallback** para outros players

---

## Arquivos Criados

```
hacker_analyzer.py                    # Analisador estatico
hacker_crypto_breaker.py              # Criptoanalise
hacker_network_interceptor.py         # Interceptacao de rede
hacker_playerembedapi_advanced.py     # Suite avancada
hacker_master_extractor.py            # Orquestrador completo
playerembedapi_final_extractor.py     # Extrator unificado [USAR ESTE]
PlayerEmbedAPIExtractor.kt            # Implementacao Kotlin
HACKER_REPORT_PLAYEREMBEDAPI.md       # Relatorio tecnico
HACKER_SUMMARY.md                     # Este arquivo
```

---

## Comandos Rapidos

```bash
# Analise rapida
python playerembedapi_final_extractor.py playerembedapi_kBJLtxCD3.html

# Analise completa
python hacker_analyzer.py playerembedapi_kBJLtxCD3.html

# Interceptacao de rede (requer Playwright)
python hacker_network_interceptor.py https://playerembedapi.link/?v=xxx

# Criptoanalise
python hacker_crypto_breaker.py playerembedapi_kBJLtxCD3.html
```

---

*White Hat Security Research*
*Para uso educacional e pesquisa de seguranca*
