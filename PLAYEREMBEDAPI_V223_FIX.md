# 🔧 PlayerEmbedAPI v223 - Redirect Fix Completo

## O Problema

O PlayerEmbedAPI retorna uma **URL intermediária** que faz redirect 302 para a URL final do Google Storage:

```
1. ViewPlayer: https://viewplayer.online/filme/tt123456
2. Clique no botão → Abre iframe
3. PlayerEmbedAPI faz request
4. Retorna URL INTERMEDIÁRIA: https://xxx.sssrr.org/?timestamp=...&id=...
5. URL faz REDIRECT (302) → URL FINAL: https://storage.googleapis.com/.../video.mp4
```

### Erro no Player

Quando o CloudStream tenta reproduzir a URL intermediária:

```
ERROR_CODE_IO_BAD_HTTP_STATUS (2004)
```

Isso acontece porque o player não segue o redirect automaticamente.

---

## A Solução v223

### Passo 1: Capturar a URL intermediária

```kotlin
// No WebViewClient.shouldInterceptRequest
when {
    url.contains("sssrr.org") && url.contains("?timestamp=") -> {
        android.util.Log.wtf(TAG, "🎯 URL SSSRR CAPTURADA: $url")
        capturedUrls.add(url)
    }
}
```

### Passo 2: Seguir o Redirect

```kotlin
private suspend fun processCapturedUrls(): List<ExtractorLink> {
    return capturedUrls.mapNotNull { url ->
        
        // Se é URL do sssrr.org, seguir redirect
        val finalUrl = if (url.contains("sssrr.org")) {
            
            // Fazer request com allowRedirects = true
            val response = app.get(
                url = url,
                allowRedirects = true,  // ⭐ Segue o 302 automaticamente
                headers = mapOf(
                    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer" to "https://viewplayer.online/",
                    "Origin" to "https://viewplayer.online"
                ),
                timeout = 30
            )
            
            // Pegar URL final do response
            response.url  // ← URL do Google Storage!
            
        } else {
            url
        }
        
        // Criar ExtractorLink com URL final
        newExtractorLink(
            source = "PlayerEmbedAPI",
            name = "PlayerEmbedAPI HD",
            url = finalUrl,  // ← URL que funciona no player!
            type = ExtractorLinkType.VIDEO
        ) {
            this.referer = "https://viewplayer.online/"
            this.headers = mapOf(
                "User-Agent" to "Mozilla/5.0 ...",
                "Origin" to "https://viewviewer.online",
                "Referer" to "https://viewplayer.online/"
            )
        }
    }
}
```

### Passo 3: Headers Importantes

Para que o Google Storage aceite a requisição:

```kotlin
mapOf(
    "User-Agent" to "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin" to "https://viewplayer.online",
    "Referer" to "https://viewplayer.online/",
    "Accept" to "*/*",
    "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
    "Sec-Fetch-Dest" to "video",
    "Sec-Fetch-Mode" to "cors",
    "Sec-Fetch-Site" to "cross-site"
)
```

---

## Como Testar

### 1. Build

```powershell
.\build-maxseries-v223.ps1
```

### 2. Instalar no CloudStream

1. Copie o arquivo `MaxSeries.cs3` gerado para o dispositivo
2. No CloudStream: Configurações → Extensões → Instalar de arquivo
3. Selecione o arquivo `MaxSeries.cs3`

### 3. Testar

1. Abra o MaxSeries
2. Busque por um filme/série popular
3. Selecione o PlayerEmbedAPI
4. **Clique 3 vezes** no centro da tela quando o WebView abrir
5. O vídeo deve começar a reproduzir!

### 4. Verificar Logs

```bash
# Ver logs em tempo real
adb logcat -s "MaxSeriesProvider" "PlayerEmbedAPI" -v color

# Procurar por:
# 🎯🎯🎯 URL SSSRR CAPTURADA  ← URL intermediária
# 🔄 URL INTERMEDIÁRIA DETECTADA
# ✅✅✅ URL FINAL OBTIDA      ← URL do Google Storage
# 🎬 CRIANDO EXTRACTOR LINK
```

---

## Debug

### Problema: Redirect não funciona

**Verifique os logs:**
```
❌ Erro ao seguir redirect: <mensagem>
```

**Possíveis causas:**
1. URL expirou (timestamp antigo) → Timeout de 20s pode ser curto
2. Headers incorretos → Verificar `Referer` e `Origin`
3. IP bloqueado → Testar em outra rede

### Problema: URL final retorna 403

**Adicione mais headers:**
```kotlin
"Sec-Fetch-Dest" to "video",
"Sec-Fetch-Mode" to "cors", 
"Sec-Fetch-Site" to "cross-site"
```

### Problema: WebView não captura URL

**Verifique:**
1. Usuário clicou no botão PlayerEmbedAPI?
2. Usuário clicou no overlay (3 cliques)?
3. Verifique logs do WebView:
   ```bash
   adb logcat -s "WebView" -v color
   ```

---

## Comparativo: Antes vs Depois

| Aspecto | v222 | v223 (Fix) |
|---------|------|------------|
| URL Capturada | `sssrr.org/?timestamp=...` | `sssrr.org/?timestamp=...` |
| URL Retornada | `sssrr.org/...` ❌ | `googleapis.com/...` ✅ |
| Erro no Player | `ERROR_CODE_IO_BAD_HTTP_STATUS` | Reproduz normalmente |
| Headers | Básicos | Completos (Sec-Fetch-*) |

---

## Changelog

### v223 (28 Jan 2026)
- 🔄 FIX FINAL: Segue redirect sssrr.org → googleapis.com
- 🎯 Headers completos para Google Storage
- ✅ Verificação se redirect foi bem-sucedido
- 🐛 Corrige ERROR_CODE_IO_BAD_HTTP_STATUS (2004)

### v222 (28 Jan 2026)
- Tentativa inicial de fix do redirect

### v221 (28 Jan 2026)
- Detecção instantânea com MutationObserver
- Polling rápido (100ms nos primeiros 10s)

### v219 (27 Jan 2026)
- PlayerEmbedAPI re-adicionado via WebView
- Automação com JavaScript injection

---

## Arquivos Modificados

1. `MaxSeries/src/main/kotlin/.../extractors/PlayerEmbedAPIWebViewExtractor.kt` ← Principal
2. `MaxSeries/src/main/kotlin/.../MaxSeriesProvider.kt` ← Versão atualizada

---

## Comandos Úteis

```bash
# Build
.\gradlew.bat MaxSeries:make

# Logs do PlayerEmbedAPI
adb logcat -s "PlayerEmbedAPI" -v color

# Logs completos
adb logcat -s "MaxSeriesProvider","PlayerEmbedAPI","WebView" -v color

# Limpar logs
adb logcat -c
```

---

**Nota:** Este fix resolve o problema do redirect 302. O usuário ainda precisa clicar 3 vezes no WebView para ativar o player (limitação do site que detecta automação).
