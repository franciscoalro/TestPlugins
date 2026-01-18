# 🐛 BUG CRÍTICO ENCONTRADO: MegaEmbed sem VideoId

## 📊 DESCOBERTA VIA INTERCEPTAÇÃO DE REDE

Ao interceptar as requisições HTTP do CloudStream, descobrimos que:

### ❌ PROBLEMA
```
GET https://megaembed.link/ → 200 2579 HTML "Loading..."
GET https://megaembed.link/ → 200 2571 HTML "Loading..."
GET https://megaembed.link/ → 200 2567 HTML "Loading..."
```

**TODAS as requisições do MegaEmbed estavam indo para a RAIZ (`/`) sem o videoId!**

### ✅ COMPARAÇÃO COM PlayerEmbedAPI (funcionando)
```
GET https://playerembedapi.link/?v=v3-9ESDlc → 200 9917 HTML "Stranger.Things.S01E08.Dublado.mp4"
GET https://playerembedapi.link/?v=ptjnNB9fM → 200 9960 HTML "Stranger.Things.S01E07.Dublado.mp4"
```

PlayerEmbedAPI recebia o videoId corretamente (`?v=v3-9ESDlc`)

---

## 🔍 CAUSA RAIZ

**Arquivo:** `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`  
**Linha:** 738-739

### Regex Problemático
```kotlin
val directUrlPatterns = listOf(
    // ... outros padrões ...
    Regex("""https?://megaembed\.link/?#[^"'\s<>\)]+"""),  // ✅ CORRETO: Com #videoId
    Regex("""https?://megaembed\.link[^"'\s<>\)]*""")      // ❌ ERRADO: Pega TUDO
)
```

O **segundo regex** estava capturando:
- ✅ `https://megaembed.link/#abc123` (correto)
- ❌ `https://megaembed.link/` (ERRADO - sem videoId)
- ❌ `https://megaembed.link` (ERRADO - sem videoId)

### Por que isso acontecia?

O regex `[^"'\s<>\)]*` permite **ZERO ou mais** caracteres, então:
- `https://megaembed.link` → Match! (zero chars após .link)
- `https://megaembed.link/` → Match! (zero chars após /)

Isso fazia o CloudStream adicionar URLs **INVÁLIDAS** às sources.

---

## ✅ SOLUÇÃO (v120)

### Regex Corrigido
```kotlin
val directUrlPatterns = listOf(
    // ... outros padrões ...
    Regex("""https?://megaembed\.link/?#[a-zA-Z0-9]+""")  // v120: APENAS com #videoId
)
```

**Mudanças:**
1. ❌ Removido segundo regex genérico
2. ✅ Mantido apenas regex que **EXIGE** `#videoId`
3. ✅ Especificado `[a-zA-Z0-9]+` (um ou mais caracteres alfanuméricos)

### Resultado Esperado
Agora o CloudStream só capturará URLs válidas:
- ✅ `https://megaembed.link/#abc123`
- ✅ `https://megaembed.link#xyz789`
- ❌ `https://megaembed.link/` (rejeitado)
- ❌ `https://megaembed.link` (rejeitado)

---

## 🎯 IMPACTO

### Antes (v119)
```
MegaEmbed recebia: https://megaembed.link/
Extractor tentava: GET https://megaembed.link/
Resultado: ❌ Página "Loading..." sem videoId
```

### Depois (v120)
```
MegaEmbed receberá: https://megaembed.link/#abc123
Extractor tentará: GET https://megaembed.link/#abc123
Resultado: ✅ Página com player e videoId correto
```

---

## 📝 LOGS ESPERADOS (v120)

### Interceptação de Rede
```
GET https://megaembed.link/#abc123 → 200 HTML (com player)
GET https://megaembed.link/assets/index-CZ_ja_1t.js → 200 JS
GET https://megaembed.link/api/v1/info?id=abc123 → 200 JSON (criptografado)
GET https://marvellaholdings.sbs/v4/x6b/abc123/cf-master.1768694011.txt → 200 M3U8
```

### Logs do Extractor
```
🎬 URL: https://megaembed.link/#abc123
🆔 VideoId: abc123
🔍 [1/4] Tentando HTML Regex...
🎯 HTML Regex capturou: https://marvellaholdings.sbs/.../cf-master.txt
✅ HTML Regex funcionou!
```

---

## 🧪 TESTE RECOMENDADO

1. **Atualizar para v120** no CloudStream
2. **Limpar cache** do app
3. **Testar episódio** que usa MegaEmbed
4. **Verificar logs ADB**:
   ```bash
   adb logcat | Select-String "MegaEmbed"
   ```
5. **Verificar interceptação** (se disponível)

### Resultado Esperado
- ✅ URL com `#videoId` nos logs
- ✅ Requisições para `/api/v1/info?id=abc123`
- ✅ Captura de URLs `.txt` com vídeo
- ✅ Playback funcionando

---

## 📊 COMPARAÇÃO DE VERSÕES

| Versão | Regex MegaEmbed | URLs Capturadas | Status |
|--------|-----------------|-----------------|--------|
| v119 | 2 regex (genérico + específico) | ❌ Com e sem #videoId | Bug |
| v120 | 1 regex (apenas com #) | ✅ Apenas com #videoId | Fix |

---

## 🎓 LIÇÃO APRENDIDA

**Interceptação de rede é ESSENCIAL para debug!**

Sem a interceptação, nunca teríamos descoberto que:
1. URLs estavam sendo capturadas sem videoId
2. CloudStream estava fazendo requests para `/` (raiz)
3. MegaEmbed retornava apenas "Loading..." sem player

**Ferramentas usadas:**
- Interceptação HTTP do CloudStream
- Logs ADB (`adb logcat`)
- Análise de regex patterns

---

**Data**: 2026-01-17  
**Versão**: v120  
**Status**: ✅ Bug corrigido e publicado
