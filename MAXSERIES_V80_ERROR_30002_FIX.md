# MaxSeries v80 - Correção do Erro 30002

## 🐛 Problema Identificado

**Erro no CloudStream:** `Error code parsing manifest malformed 30002`

**Causa:** O MegaEmbed serve arquivos HLS com extensão `.txt` (para burlar bloqueios), mas o ExoPlayer do CloudStream só aceita `.m3u8`.

Exemplo de URL problemática:
```
https://spo3.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
```

## ✅ Solução Implementada

### Arquivo: `MegaEmbedExtractor.kt` (linhas 388-445)

**Mudança:** Converter `.txt` para `.m3u8` antes de passar para o player.

```kotlin
// ANTES (linha 390):
val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl

if (videoUrl.contains(".m3u8") || videoUrl.contains("master.txt")) {
    val m3u8Links = M3u8Helper.generateM3u8(name, cleanUrl, effectiveReferer)
    ...
}

// DEPOIS (linhas 390-400):
val effectiveReferer = referer.takeIf { !it.isNullOrEmpty() } ?: mainUrl

// CRITICAL FIX: Converter .txt para .m3u8 para evitar erro 30002
val fixedUrl = if (cleanUrl.endsWith(".txt") && (cleanUrl.contains("master") || cleanUrl.contains("/v4/"))) {
    cleanUrl.replace(".txt", ".m3u8")
} else {
    cleanUrl
}

if (videoUrl.contains(".m3u8") || videoUrl.contains("master.txt") || videoUrl.contains(".txt")) {
    try {
        val m3u8Links = M3u8Helper.generateM3u8(name, fixedUrl, effectiveReferer)
        for (link in m3u8Links) {
            callback(link)
        }
    } catch (e: Exception) {
        // Fallback: enviar como link direto HLS
        callback.invoke(
            newExtractorLink(name, "$name - HLS", fixedUrl) {
                this.referer = effectiveReferer
                this.quality = quality
                this.isM3u8 = true
            }
        )
    }
}
```

## 🧪 Como Testar

1. Compile o plugin com a correção
2. Instale no CloudStream
3. Tente reproduzir um episódio
4. Verifique os logs:
   ```
   MegaEmbedExtractor: 📺 Processando como HLS: https://...cf-master.xxx.m3u8
   ```

## 📊 Resultado Esperado

- ✅ O vídeo deve começar a tocar
- ✅ Múltiplas qualidades disponíveis (se o M3u8Helper funcionar)
- ✅ Sem erro 30002

## 🔄 Versão

- **v79:** WebView + Autoplay funcionando, mas erro 30002
- **v80:** v79 + Correção do erro 30002 (.txt → .m3u8)

## 📝 Notas Técnicas

- O servidor aceita tanto `.txt` quanto `.m3u8` - o conteúdo é idêntico
- A mudança é puramente cosmética para o ExoPlayer
- Não afeta a performance ou qualidade do vídeo
