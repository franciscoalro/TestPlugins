# PLAYEREMBEDAPI - RELATORIO DE ENGENHARIA REVERSA (White Hat)

## RESUMO EXECUTIVO

Este documento apresenta uma analise completa do PlayerEmbedAPI com tecnicas avancadas de engenharia reversa para extracao de video.

---

## 1. ARQUITETURA DO SISTEMA

### 1.1 Fluxo de Dados
```
Usuario -> MaxSeries -> PlayerEmbedAPI -> JWPlayer -> CDN (sssrr.org)
                     |
                     +-> JSON Base64 (datas)
                     +-> core.bundle.js (SoTrym decrypt)
                     +-> JWPlayer setup
```

### 1.2 Estrutura do HTML
```html
<!DOCTYPE html>
<html>
<head>
    <title>{nome_do_video}</title>
    <script src="https://statics.sssrr.org/player/jwplayer.min.js"></script>
    <script src="https://iamcdn.net/player-v2/core.bundle.js"></script>
</head>
<body>
    <script>
        const datas = "{base64_encoded_json}";
        window.SoTrym(JSON.parse(atob(datas)));
    </script>
</body>
</html>
```

### 1.3 Estrutura do JSON Decodificado
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

---

## 2. ANALISE CRIPTOGRAFICA

### 2.1 Campo 'media'
- **Tamanho**: ~2500 bytes
- **Entropia**: ~7.8/8.0 (alta - indica criptografia)
- **Algoritmo Suspeito**: AES-CTR ou AES-CBC
- **Chave de Derivacao**: Possivelmente `user_id:md5_id:slug`

### 2.2 Funcao SoTrym
- Localizada em: `core.bundle.js`
- Responsavel por:
  1. Decodificar campo `media`
  2. Extrair URLs de video
  3. Configurar JWPlayer

### 2.3 Padrões de URL Detectados
```
https://{slug}.sssrr.org/sora/{md5_id}/{token_base64}
https://{subdomain}.sssrr.org/{path}/{hash}.{md5_id}.{quality}.fd
https://{subdomain}.sssrr.org/future
```

---

## 3. TECNICAS DE EXTRACAO IMPLEMENTADAS

### 3.1 Tecnica 1: HTTP Direto (Fase 1)
- **Metodo**: Regex em HTML
- **Sucesso**: Baixo (URLs nao estao no HTML)
- **Velocidade**: Alta
- **Confiabilidade**: Baixa

### 3.2 Tecnica 2: Parse do Campo 'datas' (Fase 2)
- **Metodo**: Base64 decode + JSON parse
- **Sucesso**: Parcial (obtem metadados)
- **Velocidade**: Alta
- **Confiabilidade**: Media

### 3.3 Tecnica 3: Construcao de URL (Fase 3)
- **Metodo**: Construir URLs a partir de slug + md5_id
- **Sucesso**: Media (requer validacao)
- **Velocidade**: Alta
- **Confiabilidade**: Media

### 3.4 Tecnica 4: WebView com Interceptacao (Fase 4)
- **Metodo**: WebViewResolver + regex sssrr.org
- **Sucesso**: Alta (quando funciona)
- **Velocidade**: Media (~10-15s)
- **Confiabilidade**: Alta

### 3.5 Tecnica 5: JavaScript Injection (Fase 5)
- **Metodo**: Executar JS no WebView para extrair de jwplayer.getPlaylist()
- **Sucesso**: Alta
- **Velocidade**: Media
- **Confiabilidade**: Alta

### 3.6 Tecnica 6: Browser Automation (Fase 6)
- **Metodo**: Playwright/Selenium com network monitoring
- **Sucesso**: Muito Alta
- **Velocidade**: Lenta (~15-30s)
- **Confiabilidade**: Muito Alta

---

## 4. IMPLEMENTACAO RECOMENDADA (MaxSeries Provider)

### 4.1 Ordem de Tentativas (Cascata)
```kotlin
suspend fun loadLinks(data: String, ...): Boolean {
    // 1. Tentar HTTP direto (rapido)
    if (extractDirectHTTP(data)) return true
    
    // 2. Tentar parse do campo datas
    if (extractFromDatasField(data)) return true
    
    // 3. Tentar WebView com interceptacao
    if (extractWithWebView(data)) return true
    
    return false
}
```

### 4.2 Regex de Interceptacao (WebView)
```kotlin
val INTERCEPT_PATTERN = Regex(
    """(?i)(?:sssrr\.org|googleapis\.com/mediastorage|\.m3u8|\.mp4)"""
)
```

### 4.3 Headers Obrigatorios
```kotlin
val HEADERS = mapOf(
    "Referer" to "https://playerembedapi.link/",
    "Origin" to "https://playerembedapi.link",
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

---

## 5. FERRAMENTAS CRIADAS

### 5.1 hacker_analyzer.py
Analise estatica do HTML e extracao de metadados.

**Uso:**
```bash
python hacker_analyzer.py playerembedapi_kBJLtxCD3.html
```

**Output:**
- Dados decodificados (slug, md5_id, user_id)
- Analise de entropia
- URLs potenciais
- Scripts carregados

### 5.2 PlayerEmbedAPIExtractor.kt
Extrator completo para MaxSeries Provider.

**Features:**
- Multi-tecnicas de extracao
- Fallback automatico
- Headers corretos
- Suporte a M3U8 e MP4

### 5.3 hacker_network_interceptor.py
Interceptacao de rede com Playwright.

**Uso:**
```bash
python hacker_network_interceptor.py https://playerembedapi.link/?v=xxx
```

**Output:**
- URLs de video interceptadas
- Headers e cookies
- Analise de chamadas de rede

### 5.4 hacker_crypto_breaker.py
Criptoanalise do campo 'media'.

**Features:**
- Calculo de entropia
- Tentativas de decriptacao AES
- Analise de padroes

---

## 6. ATAQUES TESTADOS

### 6.1 Ataque 1: Forca Bruta de Chaves AES
- **Chaves Testadas**: 30+ derivacoes
- **Modos Testados**: ECB, CBC, CTR
- **Resultado**: Nao bem-sucedido (chave correta desconhecida)
- **Conclusao**: Requer analise dinamica do core.bundle.js

### 6.2 Ataque 2: Replay de Requisicoes
- **Metodo**: Reproduzir chamadas sssrr.org capturadas
- **Problema**: Tokens sao temporarios
- **Resultado**: 403 Forbidden apos expiracao

### 6.3 Ataque 3: Manipulacao de DOM
- **Metodo**: Modificar JavaScript no browser
- **Resultado**: Possivel - permite extrair URLs em tempo real
- **Ferramenta**: DevTools + console.log override

---

## 7. RECOMENDACOES FINAIS

### 7.1 Para Producao (MaxSeries)
1. **Usar WebViewResolver** como metodo principal
2. **Interceptar sssrr.org** com regex especifico
3. **Timeout de 30s** para carregamento
4. **Headers Referer/Origin** obrigatorios

### 7.2 Para Desenvolvimento
1. **Analisar core.bundle.js** com mais profundidade
2. **Extrair funcao SoTrym** completa
3. **Replicar decriptacao** em Python/Kotlin
4. **Criar extrator HTTP puro** (sem WebView)

### 7.3 Limitacoes Conhecidas
1. URLs expiram (token temporario)
2. Protecao anti-bot (Cloudflare)
3. Criptografia do campo media
4. Dependencia de JavaScript

---

## 8. CONCLUSAO

O PlayerEmbedAPI eh mais simples que o MegaEmbed (sem chaves aleatorias), mas ainda requer browser automation para extracao confiavel devido a:

1. Campo `media` criptografado
2. Carregamento dinamico de URLs
3. Dependencia do JWPlayer

**Solucao Recomendada**: WebView com interceptacao de sssrr.org

---

## APENDICE: URLs de Exemplo

```
Player: https://playerembedapi.link/?v=kBJLtxCD3
CDN:    https://kBJLtxCD3.sssrr.org/sora/28930647/
API:    https://iamcdn.net/player-v2/core.bundle.js
JW:     https://statics.sssrr.org/player/jwplayer.min.js
```

---

*Relatorio gerado por: White Hat Security Research*
*Data: 2026-02-02*
*Versao: 1.0*
