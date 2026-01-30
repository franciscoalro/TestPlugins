# 🐛 Guia de Troubleshooting - Extractors CloudStream

## Fluxo de Diagnóstico

```
❌ Extractor não funciona
        ↓
┌─────────────────────┐
│ 1. Testar em Python │ ← Executar script de teste
└─────────────────────┘
        ↓
   ┌────────┴────────┐
   ↓                 ↓
Python OK          Python FALHOU
   ↓                 ↓
Site muda         Site mudou/
constante         bloqueou
   ↓                 ↓
Verificar         Atualizar
Kotlin            regex/headers
   ↓                 ↓
Build Test        Testar novamente
```

---

## 🔴 Problemas Comuns e Soluções

### **Problema 1: "No parameter with name 'referer' found"**

**Erro no build:**
```
No parameter with name 'referer' found in ExtractorLink
```

**Causa:** Usando `ExtractorLink()` em vez de `newExtractorLink()`

**❌ Errado:**
```kotlin
callback.invoke(
    ExtractorLink(
        source = name,
        name = "1080p",
        url = videoUrl,
        referer = url,  // ❌ Não existe este parâmetro!
        quality = 1080
    )
)
```

**✅ Correto:**
```kotlin
callback.invoke(
    newExtractorLink(
        source = name,
        name = "1080p",
        url = videoUrl,
        type = ExtractorLinkType.VIDEO  // ou M3U8
    ) {
        this.referer = url  // ✅ Dentro do lambda
        this.quality = Qualities.P1080.value
    }
)
```

---

### **Problema 2: Vídeo não inicia (Erro 3003)**

**Sintoma:** Player aparece, mas dá erro ao iniciar playback

**Causas comuns:**

| Causa | Verificação | Solução |
|-------|-------------|---------|
| URL expirada | Testar URL no navegador | Implementar cache curto |
| Headers faltando | Verificar Referer/Origin | Adicionar headers necessários |
| CORS bloqueado | Ver console do navegador | Usar WebView |
| Formato não suportado | Verificar extensão | Converter para M3U8/MP4 |

**Como debugar:**
```kotlin
// Adicione logs detalhados
Log.d(TAG, "URL gerada: $videoUrl")
Log.d(TAG, "Headers: $headers")

// Verifique se URL é válida antes de retornar
try {
    val testResponse = app.get(videoUrl, headers = headers, timeout = 5)
    Log.d(TAG, "Teste URL: ${testResponse.code}")
} catch (e: Exception) {
    Log.e(TAG, "URL inválida: ${e.message}")
}
```

---

### **Problema 3: Regex não encontra nada**

**Sintoma:** Retorna null ou lista vazia

**Debugging:**

```python
# 1. Salvar HTML para análise
with open('debug_html.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Testar regex passo a passo
import re

pattern = r'const datas = "([A-Za-z0-9+/=]+)"'
match = re.search(pattern, html)

if match:
    print(f"✅ Encontrado: {match.group(1)[:50]}...")
else:
    print("❌ Não encontrado")
    # Verificar se existe algo similar
    similar = re.findall(r'const \w+ = "([A-Za-z0-9+/=]{100,})"', html)
    print(f"🔍 Similares encontrados: {len(similar)}")
```

**Ferramenta online:** https://regex101.com

---

### **Problema 4: Timeout no WebView**

**Sintoma:** WebView demora muito ou não captura URL

**Soluções:**

```kotlin
// Aumentar timeout
val latch = CountDownLatch(1)
latch.await(90, TimeUnit.SECONDS)  // 90s ao invés de 60s

// Adicionar delays estratégicos
webView.webViewClient = object : WebViewClient() {
    override fun onPageFinished(view: WebView?, url: String?) {
        // Aguardar JS carregar
        Handler(Looper.getMainLooper()).postDelayed({
            view?.evaluateJavascript(script, null)
        }, 2000)  // 2s delay
    }
}

// Múltiplas tentativas
var attempts = 0
val maxAttempts = 3

while (finalUrl == null && attempts < maxAttempts) {
    attempts++
    Log.d(TAG, "Tentativa $attempts/$maxAttempts")
    // ... tentar novamente
}
```

---

### **Problema 5: API retorna dados criptografados**

**Sintoma:** JSON com strings hex ou base64 estranho

**Exemplo (MegaEmbed):**
```json
{
  "data": "7a3f9b2c..."  // Dados criptografados
}
```

**Solução:**
1. Analisar JavaScript do site para encontrar função de decriptação
2. Replicar em Kotlin usando `javax.crypto`
3. Ou usar WebView para executar JS nativo

```kotlin
// Exemplo de decriptação AES
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec
import javax.crypto.spec.IvParameterSpec

fun decryptAES(encrypted: ByteArray, key: ByteArray, iv: ByteArray): String {
    val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
    val keySpec = SecretKeySpec(key, "AES")
    val ivSpec = IvParameterSpec(iv)
    cipher.init(Cipher.DECRYPT_MODE, keySpec, ivSpec)
    return String(cipher.doFinal(encrypted))
}
```

---

## 🧪 Scripts de Debug

### **Debug com ADB (Android Debug Bridge)**

```powershell
# Ver logs do CloudStream em tempo real
adb logcat -s "PlayerEmbedAPI" "MegaEmbed*" "MaxSeriesProvider" -v color

# Filtrar apenas erros
adb logcat *:E -s "PlayerEmbedAPI" "MegaEmbed*"

# Salvar logs em arquivo
adb logcat -d > cloudstream_logs.txt
```

### **Debug no Próprio Código**

Adicione esta função de utilidade:

```kotlin
// MaxSeriesProvider.kt ou arquivo de utils
object DebugUtils {
    private const val TAG = "DebugUtils"
    
    fun logExtractorStart(extractorName: String, url: String) {
        Log.d(TAG, "═══════════════════════════════════════════")
        Log.d(TAG, "🎬 EXTRACTOR: $extractorName")
        Log.d(TAG, "🔗 URL: $url")
        Log.d(TAG, "═══════════════════════════════════════════")
    }
    
    fun logExtractorSuccess(extractorName: String, videoUrl: String, duration: Long) {
        Log.d(TAG, "✅ $extractorName SUCESSO (${duration}ms)")
        Log.d(TAG, "   URL: ${videoUrl.take(80)}...")
    }
    
    fun logExtractorFailure(extractorName: String, error: String) {
        Log.e(TAG, "❌ $extractorName FALHOU")
        Log.e(TAG, "   Erro: $error")
    }
    
    fun validateVideoUrl(url: String): Boolean {
        return when {
            url.isBlank() -> {
                Log.e(TAG, "❌ URL vazia")
                false
            }
            !url.startsWith("http") -> {
                Log.e(TAG, "❌ URL inválida (não é HTTP): $url")
                false
            }
            url.contains("example.com") -> {
                Log.w(TAG, "⚠️ URL parece ser placeholder")
                false
            }
            else -> true
        }
    }
}
```

---

## 📊 Checklist Pré-Build

Antes de fazer o build final, verifique:

### **Sintaxe e Estrutura**
- [ ] `override var name` (não `val`)
- [ ] `override var mainUrl` (não `val`)
- [ ] `override suspend fun getUrl`
- [ ] `newExtractorLink()` em vez de `ExtractorLink()`
- [ ] Parâmetros corretos no callback

### **Funcionalidade**
- [ ] Testou em Python e funcionou
- [ ] Regex foram testados em regex101.com
- [ ] URLs de vídeo são válidas (testar no navegador)
- [ ] Headers necessários estão definidos
- [ ] Tratamento de erros implementado (runCatching)

### **Performance**
- [ ] Timeout definido para requisições HTTP
- [ ] Cache implementado (VideoUrlCache)
- [ ] Logs adicionados para debugging
- [ ] Fallbacks configurados

---

## 🚀 Fluxo de Teste Completo

```bash
# 1. Teste Python (rápido)
python validar-extractor.py "https://site.com/embed/123"

# 2. Verificação de código (PowerShell)
.\verificar-kotlin.ps1 -ExtractorFile "MaxSeries\src\main\kotlin\...\MeuExtractor.kt"

# 3. Build do plugin
.\gradlew MaxSeries:make

# 4. Instalação no dispositivo
adb install -r MaxSeries\build\outputs\apk\debug\MaxSeries-debug.apk

# 5. Teste com logs
adb logcat -s "MeuExtractor" "MaxSeriesProvider" -v color
```

---

## 📞 Quando Pedir Ajuda

Inclua estas informações:

1. **URL de teste** que está usando
2. **Log completo** do ADB (com `adb logcat -d`)
3. **HTML salvo** (se possível)
4. **Resultado do teste Python**
5. **Código do extractor** (trecho relevante)

---

**Última atualização:** Janeiro 2026
