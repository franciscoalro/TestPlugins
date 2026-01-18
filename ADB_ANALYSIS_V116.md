# 🔍 Análise ADB - MaxSeries v116

## 📅 Data: 17/01/2026 21:48-21:49

## ✅ Versão Confirmada: v116

```
MegaEmbedExtractorV5_v116: === MEGAEMBED V5 WEBVIEW-ONLY (v116) ===
```

**Status**: ✅ v116 está ativa e rodando!

---

## 🎯 Teste 1: Episódio com MegaEmbed #3wnuij

### Logs Capturados

```
21:48:41.577  MegaEmbedExtractorV5_v116: 🔍 URL final do WebView: https://megaembed.link/#3wnuij
21:48:41.578  MegaEmbedExtractorV5_v116: ⚠️ Interceptação direta falhou, tentando injeção JS...
21:48:41.578  MegaEmbedExtractorV5_v116: ❌ FALHA TOTAL: WebView não conseguiu capturar o vídeo.
21:48:41.578  MaxSeriesProvider: 🔗 Links encontrados: 1
```

### ❌ Resultado: Falhou

**Motivo**: WebView não conseguiu interceptar a URL do vídeo.

**Observações**:
- ✅ v116 está ativa (TAG correto)
- ✅ Sem tentativas de `MegaEmbedLinkFetcher` (API tradicional desabilitada)
- ❌ WebView carregou a página mas não capturou a URL `.txt`
- ✅ Fallback funcionou (PlayerThree foi tentado)

---

## 🎯 Teste 2: Episódio com PlayerThree + MegaEmbed

### PlayerEmbedAPI Tentado Primeiro

```
21:48:50.528  MaxSeriesProvider: 🔄 Processando: https://playerembedapi.link/?v=QvXFt2de3
21:48:50.529  MaxSeriesProvider: 🎬 [P1] PlayerEmbedAPIExtractor - MP4 direto (WebView)
21:49:17.284  MaxSeriesProvider: ⚠️ Erro no extractor para https://playerembedapi.link/?v=QvXFt2de3: 
                                  Falha ao interceptar URL de vídeo. Final: https://playerembedapi.link/?v=QvXFt2de3
```

**Resultado**: PlayerEmbedAPI falhou (timeout de 27 segundos)

### MegaEmbed Tentado em Seguida

```
21:49:17.285  MaxSeriesProvider: 🔄 Processando: https://megaembed.link/#xez5rx
21:49:17.286  MegaEmbedExtractorV5_v116: === MEGAEMBED V5 WEBVIEW-ONLY (v116) ===
21:49:17.286  MegaEmbedExtractorV5_v116: 🎬 URL: https://megaembed.link/#xez5rx
21:49:17.286  MegaEmbedExtractorV5_v116: 🔗 Referer: https://playerthree.online/embed/synden/
21:49:17.286  MegaEmbedExtractorV5_v116: 🚀 Iniciando WebView Interception (Modo Exclusivo)...
21:49:17.287  MegaEmbedExtractorV5_v116: 🆔 VideoId alvo: xez5rx
```

### WebView Carregando Recursos

```
21:49:17.293  WebViewResolver: Initial web-view request: https://megaembed.link/#xez5rx
21:49:17.369  WebViewResolver: Loading WebView URL: https://megaembed.link/#xez5rx
21:49:17.720  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/index-CZ_ja_1t.js
21:49:17.722  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/index-DsSvO8OB.css
21:49:17.986  WebViewResolver: Loading WebView URL: https://megaembed.link/api/v1/info?id=xez5rx ✅
21:49:17.995  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/vidstack-player-default-layout-BpV3Dvv2.js
21:49:17.997  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/vidstack-CwTj4H1w-BCQqYYxA.js
21:49:18.181  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/prod-cvEtvBo1.js
21:49:18.232  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/vidstack-hls-BcPzC22e.js ✅
21:49:18.233  WebViewResolver: Loading WebView URL: https://megaembed.link/assets/vidstack-video-BEihePK7.js
21:49:18.310  WebViewResolver: Loading WebView URL: https://megaembed.link/nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/poster.png
21:49:19.126  WebViewResolver: Loading WebView URL: https://megaembed.link/favicon.png
```

### 🔍 Análise Detalhada

**Recursos carregados**:
- ✅ API call: `https://megaembed.link/api/v1/info?id=xez5rx`
- ✅ HLS player: `vidstack-hls-BcPzC22e.js`
- ✅ Video player: `vidstack-video-BEihePK7.js`
- ✅ Poster image: `nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/poster.png`

**Problema identificado**:
- ❌ Nenhuma URL `.txt` foi interceptada
- ❌ Nenhuma URL `.m3u8` foi interceptada
- ❌ O timeout de 60s foi atingido

### ⚠️ Resultado: Timeout

O comando ADB foi interrompido após 60 segundos, mas o WebView ainda estava carregando recursos.

---

## 📊 Análise Comparativa

### v115 (Com API Tradicional)

```
⏱️ Tempo: ~9 segundos
├─ MegaEmbedLinkFetcher: 9s (30 tentativas, 0 sucesso) ❌
└─ WebView: NÃO TENTADO ❌
```

### v116 (Só WebView)

```
⏱️ Tempo: ~30 segundos (timeout)
└─ WebView: Tentado mas não capturou ⚠️
```

**Observação**: v116 está funcionando corretamente (sem API tradicional), mas o WebView não está conseguindo interceptar as URLs.

---

## 🔍 Problema Identificado

### WebView Não Está Interceptando

O WebView está carregando todos os recursos do MegaEmbed, mas:

1. ❌ Regex não está capturando a URL `.txt`
2. ❌ JavaScript callback não está retornando nada
3. ❌ Timeout de 30s é atingido

### Possíveis Causas

#### 1. URL `.txt` Não Está no HTML

O MegaEmbed pode estar carregando a URL via JavaScript assíncrono, e o regex no HTML não consegue capturar.

#### 2. Regex Não Está Correto

Regex atual:
```regex
/v4/[a-z0-9]+/[a-z0-9]+/(?:cf-master|index-).*?\.txt
```

Mas a URL pode estar em formato diferente:
```
nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/poster.png
```

Parece que o path mudou de `/v4/` para um hash aleatório.

#### 3. JavaScript Não Está Sendo Executado

O JavaScript pode estar sendo bloqueado ou não está rodando no momento certo.

---

## 💡 Soluções Propostas

### Opção 1: Melhorar Regex (Recomendado)

Atualizar regex para capturar qualquer `.txt` ou `.m3u8`:

```kotlin
interceptUrl = Regex("""\.txt(?:\?.*)?$"""),
additionalUrls = listOf(
    Regex("""\.m3u8(?:\?.*)?$"""),
    Regex("""/[a-z0-9_-]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+/.*?\.txt"""),
    Regex("""marvellaholdings\.sbs.*?\.txt"""),
    Regex("""valenium\.shop.*?\.txt""")
)
```

### Opção 2: Aumentar Timeout

Aumentar de 30s para 45s:

```kotlin
timeout = 45_000L
```

### Opção 3: Melhorar JavaScript

Adicionar mais estratégias de captura:

```javascript
// Procurar em fetch/XHR
var originalFetch = window.fetch;
window.fetch = function() {
    var url = arguments[0];
    if (url.includes('.txt') || url.includes('.m3u8')) {
        console.log('🎯 Fetch interceptado:', url);
        resolve(url);
    }
    return originalFetch.apply(this, arguments);
};
```

### Opção 4: Interceptar API Call

A API call `https://megaembed.link/api/v1/info?id=xez5rx` pode retornar a URL do vídeo:

```kotlin
interceptUrl = Regex("""/api/v1/info\?id=[a-z0-9]+""")
```

E então parsear o JSON response.

---

## 🎯 Próximos Passos

### 1. Testar API Call

Fazer request manual para:
```
https://megaembed.link/api/v1/info?id=xez5rx
```

E verificar se retorna a URL do vídeo.

### 2. Melhorar Regex

Atualizar regex para ser mais permissivo e capturar qualquer `.txt` ou `.m3u8`.

### 3. Adicionar Logs

Adicionar mais logs no JavaScript para ver o que está sendo capturado:

```javascript
console.log('🔍 HTML:', document.documentElement.innerHTML.substring(0, 1000));
```

### 4. Testar Outro Episódio

Testar com outro episódio para ver se o problema é específico deste vídeo.

---

## ✅ Pontos Positivos da v116

1. ✅ API tradicional desabilitada (sem bruteforce de 30 hosts)
2. ✅ WebView é tentado imediatamente
3. ✅ TAG v116 confirmada nos logs
4. ✅ Fallback para PlayerThree funcionando
5. ✅ Sem erros de compilação ou crashes

## ❌ Pontos a Melhorar

1. ❌ WebView não está interceptando URLs `.txt`
2. ❌ Regex pode estar muito específico
3. ❌ JavaScript callback não está retornando nada
4. ❌ Timeout pode ser muito curto

---

## 📝 Conclusão

A v116 está funcionando corretamente (sem API tradicional), mas o WebView precisa de ajustes para interceptar as URLs do MegaEmbed.

**Recomendação**: Implementar Opção 4 (interceptar API call) como método principal, pois a API `/api/v1/info` provavelmente retorna a URL do vídeo em JSON.

---

## 🔗 URLs Importantes Capturadas

### API Call
```
https://megaembed.link/api/v1/info?id=xez5rx
```

### Poster Image (indica estrutura do CDN)
```
https://megaembed.link/nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/poster.png
```

**Padrão observado**: `/{hash}/{shard}/{video_id}/{quality}/poster.png`

Isso sugere que a URL do vídeo pode ser:
```
https://megaembed.link/nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/cf-master.*.txt
```

Ou em um CDN externo:
```
https://spo3.marvellaholdings.sbs/nu2vNHsW4avuze-VZn6h_g/is9/r8c1nmni/9crq35/cf-master.*.txt
```

---

**Status**: v116 ativa, mas WebView precisa de ajustes para capturar URLs.
