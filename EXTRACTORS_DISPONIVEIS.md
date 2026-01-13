# Extractors Disponíveis no CloudStream (Jan 2026)

## ✅ Extractors Built-in (via `loadExtractor`)

Estes extractors já estão incluídos no CloudStream e podem ser usados chamando `loadExtractor(url, referer, subtitleCallback, callback)`:

### 🟢 Funcionais e Testados

| Extractor | Domínios | Tipo | Status | Prioridade |
|-----------|----------|------|--------|------------|
| **DoodStream** | dood.*, doodstream.* | MP4 | ✅ Funciona | Alta |
| **StreamTape** | streamtape.com, strtape.* | MP4 | ✅ Funciona | Alta |
| **Mixdrop** | mixdrop.* | MP4/HLS | ✅ Funciona | Média |
| **Uqload** | uqload.* | MP4 | ✅ Funciona | Média |
| **FileMoon** | filemoon.* | MP4 | ✅ Funciona | Média |
| **StreamSB** | lvturbo.com, streamsb.* | MP4/HLS | ⚠️ Instável | Baixa |
| **VidCloud** | vidcloud.* | HLS | ✅ Funciona | Média |
| **UpStream** | upstream.* | MP4 | ✅ Funciona | Média |
| **Voe** | voe.sx | MP4 | ⚠️ Instável | Baixa |

### 🔴 Não Recomendados (Problemas Conhecidos)

| Extractor | Motivo |
|-----------|--------|
| StreamSB | Mudou algoritmo de ofuscação (Jan 2026) |
| Voe | Requer captcha frequentemente |
| JeniusPlay | Descontinuado |

---

## 🛠️ Extractors Customizados (Já Implementados no MaxSeries)

| Extractor | Arquivo | Status |
|-----------|---------|--------|
| PlayerEmbedAPI | `PlayerEmbedAPIExtractor.kt` | ✅ v76 (WebView) |
| MyVidPlay | `MyVidPlayExtractor.kt` | ✅ v76 (MP4 direto) |
| MegaEmbed | `MegaEmbedSimpleExtractor.kt` | ✅ v75 (HLS) |

---

## 📋 Extractors Recomendados para Adicionar

### 1. **StreamTape** (Alta Prioridade)
```kotlin
// Uso simples via loadExtractor
if (url.contains("streamtape", ignoreCase = true)) {
    loadExtractor(url, referer, subtitleCallback, callback)
}
```
- **Vantagens**: MP4 direto, sem JavaScript, rápido
- **Desvantagens**: Limite de velocidade para free users

### 2. **Mixdrop** (Média Prioridade)
```kotlin
if (url.contains("mixdrop", ignoreCase = true)) {
    loadExtractor(url, referer, subtitleCallback, callback)
}
```
- **Vantagens**: MP4/HLS, boa velocidade
- **Desvantagens**: Ads agressivos

### 3. **FileMoon** (Média Prioridade)
```kotlin
if (url.contains("filemoon", ignoreCase = true)) {
    loadExtractor(url, referer, subtitleCallback, callback)
}
```
- **Vantagens**: Servidores de alta qualidade, sem cap de velocidade
- **Desvantagens**: Pode requerer MediaFlow Proxy

### 4. **Uqload** (Média Prioridade)
```kotlin
if (url.contains("uqload", ignoreCase = true)) {
    loadExtractor(url, referer, subtitleCallback, callback)
}
```
- **Vantagens**: MP4 direto, estável
- **Desvantagens**: Velocidade média

---

## 🎯 Priorização Recomendada para MaxSeries

```kotlin
val priorityOrder = listOf(
    "playerembedapi",  // 1. MP4 direto (Google Cloud Storage)
    "myvidplay",       // 2. MP4 direto (cloudatacdn)
    "streamtape",      // 3. MP4 direto (novo)
    "dood",            // 4. MP4/HLS normal
    "mixdrop",         // 5. MP4/HLS (novo)
    "filemoon",        // 6. MP4 (novo)
    "uqload",          // 7. MP4 (novo)
    "megaembed"        // 8. HLS ofuscado (último recurso)
)
```

---

## 📝 Implementação Sugerida

### Adicionar ao `MaxSeriesProvider.kt`:

```kotlin
when {
    // PRIORIDADE 1: PlayerEmbedAPI
    source.contains("playerembedapi", ignoreCase = true) -> {
        val extractor = PlayerEmbedAPIExtractor()
        extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
        linksFound++
    }
    
    // PRIORIDADE 2: MyVidPlay
    source.contains("myvidplay", ignoreCase = true) -> {
        val extractor = MyVidPlayExtractor()
        extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
        linksFound++
    }
    
    // PRIORIDADE 3-7: Built-in extractors
    source.contains("streamtape", ignoreCase = true) ||
    source.contains("dood", ignoreCase = true) ||
    source.contains("mixdrop", ignoreCase = true) ||
    source.contains("filemoon", ignoreCase = true) ||
    source.contains("uqload", ignoreCase = true) -> {
        Log.d(TAG, "🎬 [BUILT-IN] loadExtractor")
        loadExtractor(source, playerthreeUrl, subtitleCallback, callback)
        linksFound++
    }
    
    // PRIORIDADE 8: MegaEmbed (último recurso)
    source.contains("megaembed", ignoreCase = true) -> {
        val extractor = MegaEmbedSimpleExtractor()
        extractor.getUrl(source, playerthreeUrl, subtitleCallback, callback)
        linksFound++
    }
}
```

---

## 🔍 Como Verificar se um Extractor Funciona

1. **Teste Python** (verificar se o site responde):
```python
import requests
url = "https://streamtape.com/e/XXXXX"
response = requests.get(url)
print(f"Status: {response.status_code}")
```

2. **Teste no CloudStream**:
   - Adicionar URL manualmente no player
   - Verificar logs do Logcat
   - Testar playback

3. **Verificar Issues do GitHub**:
   - https://github.com/recloudstream/cloudstream/issues
   - Procurar por nome do extractor

---

## 📚 Referências

- CloudStream Docs: https://recloudstream.github.io/csdocs/
- CloudStream Extensions: https://codeberg.org/cloudstream/cloudstream-extensions
- Stremio Extractors (referência): https://stremio-addons.net/addons?categories=http%20streams

---

## ⚠️ Notas Importantes

1. **Nem todos os extractors funcionam em todos os países** - alguns são geo-restritos
2. **Extractors podem quebrar** - sites mudam frequentemente
3. **Sempre testar antes de publicar** - usar episódios reais do MaxSeries
4. **Priorizar MP4 direto** - evita erro 3003 do ExoPlayer
5. **WebView só quando necessário** - consome mais recursos

---

**Última atualização**: Janeiro 2026
