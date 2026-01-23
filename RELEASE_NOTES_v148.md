# MaxSeries v148 - FIX WebView

## 🎯 Problema Identificado (v147)

Logs ADB mostraram que **scriptCallback retornava {} vazio**:
```
01-20 21:40:39.797 D MegaEmbedV7: 📱 WebView capturou: {}
01-20 21:40:51.765 E MegaEmbedV7: ❌ URL capturada não contém /v4/
```

**Causa**: JavaScript não estava executando ou HTML não continha URLs visíveis no DOM.

---

## ✅ Solução v148

### Mudança Principal: **WebView SEM Script JavaScript**

Removido script JavaScript completamente. WebView agora usa **apenas interceptação de rede** (XHR/Fetch) para capturar requisições HTTP automaticamente.

### Código Antes (v147):
```kotlin
val captureScript = """
    (function() {
        return new Promise(function(resolve) {
            var interval = setInterval(function() {
                var html = document.documentElement.innerHTML;
                var txtMatch = html.match(/https?:\/\/[^"'\s]+\/v4\/[^"'\s]+\.txt/i);
                if (txtMatch) { resolve(txtMatch[0]); }
            }, 100);
        });
    })()
"""

val resolver = WebViewResolver(
    interceptUrl = universalRegex,
    script = captureScript,
    scriptCallback = { result -> ... },
    timeout = 12_000L
)
```

### Código Depois (v148):
```kotlin
// REGEX: Intercepta qualquer URL com /v4/ ou .txt
val interceptRegex = Regex("""(https?://[^/]+/v4/[^"'\s]+|https?://[^"'\s]+\.txt)""")

// SEM SCRIPT! Deixa o WebView interceptar requisições automaticamente
val resolver = WebViewResolver(
    interceptUrl = interceptRegex,
    timeout = 15_000L
)
```

---

## 🔧 Mudanças Técnicas

| Componente | v147 | v148 |
|------------|------|------|
| **Script JS** | Ativo (busca no HTML) | Removido |
| **scriptCallback** | Presente | Removido |
| **Interceptação** | Regex + Script | Apenas Regex |
| **Timeout** | 12s | 15s |
| **Validação** | contains("/v4/") | contains("/v4/") OR contains("index") OR contains("cf-master") |
| **Log** | "WebView retornou" | "WebView interceptou" |

---

## 📦 Download

- **Arquivo**: `MaxSeries.cs3` (173 KB)
- **Versão**: 148
- **API**: CloudStream 3.X
- **Idioma**: pt-BR

### Instalação:
1. Baixe `MaxSeries.cs3`
2. No CloudStream: **Settings → Extensions → Install from storage**
3. Selecione o arquivo baixado

---

## 🧪 Teste Realizado

**Dispositivo**: Y9YP4XI7799P9LZT (Android)  
**Método**: ADB logs em tempo real

**Comando monitoramento**:
```bash
adb logcat MegaEmbedV7:D *:S
```

**VideoIDs testados**: `3wnuij`, `6pyw3v`

---

## 📚 Histórico de Versões

- **v148** (atual): FIX WebView - Interceptação de rede sem script
- **v147**: APIs do MegaEmbed + cf-master com timestamp (scriptCallback falhando)
- **v145**: Multi-Regex com 8 padrões de CDN
- **v144**: Fix regex simplificado + plugins.json

---

## ⚠️ Notas Importantes

- **WebView é obrigatório**: Necessário para desencriptar vídeos (não pode ser removido)
- **Interceptação vs Script**: Mais confiável que depender de DOM parsing
- **URLs dinâmicas**: cf-master usa timestamp Unix (ex: `cf-master.1767387529.txt`)
- **Camuflagem**: .woff/.woff2 são segmentos de vídeo, .txt contém M3U8

---

**Desenvolvido por**: franciscoalro  
**Repositório**: https://github.com/franciscoalro/TestPlugins
