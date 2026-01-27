# MegaEmbed Fix v217 - Diagnóstico e Solução

## 🔍 PROBLEMA IDENTIFICADO

O MegaEmbedExtractorV9 parou de funcionar após as otimizações do v217.

### Causas Prováveis:

1. **Não usa WebViewPool** ❌
   - Cria WebView diretamente: `val webView = WebView(context)`
   - PlayerEmbedAPI funciona porque usa `WebViewPool.acquire(context)`
   
2. **Timeout muito longo** ⚠️
   - MegaEmbed: 90 segundos
   - PlayerEmbedAPI: 30s + 15s retry = 45s max
   - Pode estar causando bloqueio

3. **Possível conflito de contexto** ⚠️
   - Ambos usam reflection para obter contexto
   - Pode haver race condition

## 🔧 SOLUÇÃO PROPOSTA

### Opção 1: Integrar MegaEmbed com WebViewPool (RECOMENDADO)

**Vantagens:**
- ✅ Consistência com PlayerEmbedAPI
- ✅ Melhor performance (reuso de WebView)
- ✅ Menos memory leaks
- ✅ Timeout mais curto e eficiente

**Mudanças necessárias:**

```kotlin
// ANTES (linha ~76)
val webView = WebView(context)

// DEPOIS
import com.franciscoalro.maxseries.utils.WebViewPool

val webView = WebViewPool.acquire(context)

// E no cleanup (substituir destroy direto):
WebViewPool.release(webView)
```

**Timeout adaptativo:**

```kotlin
// ANTES (linha ~305)
val captured = latch.await(90, TimeUnit.SECONDS)

// DEPOIS
companion object {
    private const val TAG = "MegaEmbedV9"
    private const val TIMEOUT_SECONDS = 45L  // Alinhado com PlayerEmbedAPI
    private const val QUICK_TIMEOUT_SECONDS = 20L  // Para retry
    private const val MAX_RETRIES = 2
}

// Implementar retry loop similar ao PlayerEmbedAPI
var attempt = 0
var success = false

while (attempt < MAX_RETRIES && !success) {
    attempt++
    val timeout = if (attempt == 1) TIMEOUT_SECONDS else QUICK_TIMEOUT_SECONDS
    
    val captured = latch.await(timeout, TimeUnit.SECONDS)
    
    if (captured && finalUrl != null) {
        success = true
        // callback...
    } else {
        Log.w(TAG, "⏱️ Timeout após ${timeout}s (tentativa $attempt)")
    }
}
```

---

### Opção 2: Manter MegaEmbed separado mas otimizar

**Se preferir não usar WebViewPool:**

1. Reduzir timeout de 90s para 60s
2. Adicionar retry logic
3. Melhorar cleanup do WebView
4. Adicionar cache check antes de criar WebView

---

## 📊 Comparação

| Aspecto | MegaEmbed Atual | PlayerEmbedAPI v217 | MegaEmbed Otimizado |
|---------|-----------------|---------------------|---------------------|
| WebView | Cria direto | WebViewPool | WebViewPool |
| Timeout | 90s | 30s + 15s retry | 45s + 20s retry |
| Retry | Não | Sim (2x) | Sim (2x) |
| Cleanup | destroy() | release() + pool | release() + pool |
| Performance | Lento | Rápido | Rápido |

---

## 🚀 IMPLEMENTAÇÃO RECOMENDADA

### Passo 1: Adicionar imports

```kotlin
import com.franciscoalro.maxseries.utils.WebViewPool
```

### Passo 2: Adicionar constantes de timeout

```kotlin
companion object {
    private const val TAG = "MegaEmbedV9"
    private const val TIMEOUT_SECONDS = 45L
    private const val QUICK_TIMEOUT_SECONDS = 20L
    private const val MAX_RETRIES = 2
}
```

### Passo 3: Substituir criação de WebView

```kotlin
// Linha ~76
val webView = WebViewPool.acquire(context)
```

### Passo 4: Atualizar cleanup

```kotlin
val cleanup = {
    handler.post {
        try {
            Log.d(TAG, "🧹 [MegaEmbedV9] Liberando WebView para o pool...")
            WebViewPool.release(webView)
        } catch (e: Exception) {
            Log.e(TAG, "Erro no cleanup: ${e.message}")
        }
    }
}
```

### Passo 5: Implementar retry loop

```kotlin
var attempt = 0
var success = false

while (attempt < MAX_RETRIES && !success) {
    attempt++
    val timeout = if (attempt == 1) TIMEOUT_SECONDS else QUICK_TIMEOUT_SECONDS
    
    Log.d(TAG, "🔄 Tentativa $attempt/$MAX_RETRIES (timeout: ${timeout}s)")
    
    // ... lógica do WebView ...
    
    val captured = latch.await(timeout, TimeUnit.SECONDS)
    
    if (captured && finalUrl != null) {
        success = true
        Log.d(TAG, "✅ Sucesso na tentativa $attempt!")
        // callback...
    } else {
        Log.w(TAG, "⏱️ Timeout após ${timeout}s (tentativa $attempt)")
        cleanup()
        
        if (attempt < MAX_RETRIES) {
            Log.d(TAG, "🔄 Tentando novamente...")
            // Reset latch para próxima tentativa
            latch = CountDownLatch(1)
        }
    }
}
```

---

## 🧪 TESTE

Após implementar as mudanças:

1. Build: `./gradlew.bat :MaxSeries:assembleRelease`
2. Instalar no dispositivo
3. Testar MegaEmbed com um vídeo
4. Verificar logs:
   - `WebViewPool` deve mostrar "Reusando WebView do pool"
   - Timeout deve ser 45s (não 90s)
   - Retry deve funcionar se primeira tentativa falhar

---

## 📝 DIAGNÓSTICO

Use o script criado para capturar logs:

```powershell
.\diagnose-megaembed-v217.ps1
```

Isso vai:
- Capturar logs do MegaEmbed
- Verificar se WebView foi criado
- Verificar se URL foi capturada
- Identificar timeouts ou erros

---

## ✅ CHECKLIST

- [ ] Adicionar import do WebViewPool
- [ ] Adicionar constantes de timeout
- [ ] Substituir `WebView(context)` por `WebViewPool.acquire(context)`
- [ ] Atualizar cleanup para usar `WebViewPool.release()`
- [ ] Implementar retry loop
- [ ] Testar em dispositivo real
- [ ] Verificar logs
- [ ] Confirmar que funciona

---

**Prioridade:** 🔴 ALTA  
**Impacto:** MegaEmbed é usado em ~95% dos vídeos  
**Tempo estimado:** 15-20 minutos

