# FASE 4: Otimizações - Plano de Implementação

**Data**: 16 Janeiro 2026  
**Status**: 🚧 Em Progresso  
**Prioridade**: MÉDIA  
**Tempo Estimado**: 4h

---

## 📋 OBJETIVO

Melhorar performance, confiabilidade e experiência do usuário do MaxSeries plugin através de:
- Cache inteligente de URLs extraídas
- Retry logic para falhas de rede
- Quality detection automática
- Error handling aprimorado
- Logs estruturados para debugging

---

## ✅ PRÉ-REQUISITOS ATENDIDOS

### Utilities Implementadas (Fases 1-3)
- ✅ `HeadersBuilder.kt` - Headers HTTP customizados
- ✅ `LinkDecryptor.kt` - Decriptação de links
- ✅ `RateLimiter.kt` - Rate limiting
- ✅ `RegexPatterns.kt` - Padrões regex
- ✅ `ServerPriority.kt` - Priorização de servidores

### Extractors Implementados
- ✅ `MediaFireExtractor.kt`
- ✅ `MegaEmbedExtractor.kt` (+ V3, V6)
- ✅ `MyVidPlayExtractor.kt`
- ✅ `PlayerEmbedAPIExtractor.kt`
- ✅ `AjaxPlayerExtractor.kt`

---

## 🎯 TAREFAS DA FASE 4

### 1. Cache de URLs Extraídas (2h)

**Objetivo**: Evitar re-extração de URLs já processadas

#### 1.1 Criar `VideoUrlCache.kt`
```kotlin
package com.franciscoalro.maxseries.utils

/**
 * Cache em memória para URLs de vídeo extraídas
 * Reduz chamadas redundantes aos servidores
 */
object VideoUrlCache {
    private val cache = mutableMapOf<String, CachedUrl>()
    private const val CACHE_DURATION_MS = 5 * 60 * 1000L // 5 minutos
    
    data class CachedUrl(
        val url: String,
        val quality: Int,
        val timestamp: Long
    )
    
    fun get(key: String): CachedUrl?
    fun put(key: String, url: String, quality: Int)
    fun clear()
    fun clearExpired()
}
```

**Localização**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/VideoUrlCache.kt`

**Integração**:
- Modificar extractors para verificar cache antes de extrair
- Adicionar cache após extração bem-sucedida

---

### 2. Retry Logic para Falhas (1h)

**Objetivo**: Aumentar confiabilidade em caso de falhas temporárias

#### 2.1 Criar `RetryHelper.kt`
```kotlin
package com.franciscoalro.maxseries.utils

import kotlinx.coroutines.delay

/**
 * Utilitário para retry de operações com backoff exponencial
 */
object RetryHelper {
    suspend fun <T> withRetry(
        maxAttempts: Int = 3,
        initialDelayMs: Long = 500,
        maxDelayMs: Long = 3000,
        factor: Double = 2.0,
        block: suspend (attempt: Int) -> T
    ): T
}
```

**Localização**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/RetryHelper.kt`

**Integração**:
- Aplicar em requisições HTTP críticas
- Aplicar em extractors que falham frequentemente
- Logs de tentativas de retry

---

### 3. Quality Detection Automática (30min)

**Objetivo**: Detectar qualidade de vídeo automaticamente

#### 3.1 Criar `QualityDetector.kt`
```kotlin
package com.franciscoalro.maxseries.utils

/**
 * Detector de qualidade de vídeo por URL/nome de arquivo
 */
object QualityDetector {
    fun detectFromUrl(url: String): Int
    fun detectFromFilename(filename: String): Int
    fun detectFromM3u8Content(content: String): List<Pair<String, Int>>
}
```

**Localização**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/QualityDetector.kt`

**Patterns de Detecção**:
- `1080p`, `1920x1080` → 1080
- `720p`, `1280x720` → 720
- `480p`, `854x480` → 480
- `360p` → 360
- Defaulto → Qualities.Unknown.value

---

### 4. Error Handling Melhorado (30min)

**Objetivo**: Mensagens de erro mais claras e úteis

#### 4.1 Criar `ErrorLogger.kt`
```kotlin
package com.franciscoalro.maxseries.utils

import android.util.Log

/**
 * Logger centralizado com níveis e contexto
 */
object ErrorLogger {
    enum class Level { DEBUG, INFO, WARNING, ERROR }
    
    fun log(
        tag: String,
        level: Level,
        message: String,
        context: Map<String, Any> = emptyMap(),
        error: Throwable? = null
    )
    
    fun logExtraction(
        extractor: String,
        url: String,
        success: Boolean,
        error: Throwable? = null
    )
}
```

**Localização**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/ErrorLogger.kt`

**Integração**:
- Substituir `Log.d/e/w` dispersos
- Adicionar contexto estruturado
- Facilitar debugging em produção

---

## 📊 MELHORIAS NOS EXTRACTORS

### Aplicar Otimizações em Todos os Extractors

#### Template de Integração:
```kotlin
override suspend fun getUrl(
    url: String,
    referer: String?,
    subtitleCallback: (SubtitleFile) -> Unit,
    callback: (ExtractorLink) -> Unit
) {
    ErrorLogger.logExtraction(name, url, success = false) // Início
    
    // 1. Verificar cache
    val cached = VideoUrlCache.get(url)
    if (cached != null && !cached.isExpired()) {
        callback.invoke(createLink(cached.url, cached.quality))
        ErrorLogger.logExtraction(name, url, success = true)
        return
    }
    
    // 2. Aplicar retry logic
    RetryHelper.withRetry(maxAttempts = 3) { attempt ->
        runCatching {
            // Extração normal aqui
            val videoUrl = extractVideoUrl(url)
            
            // 3. Detectar qualidade
            val quality = QualityDetector.detectFromUrl(videoUrl)
            
            // 4. Salvar no cache
            VideoUrlCache.put(url, videoUrl, quality)
            
            // 5. Invocar callback
            callback.invoke(createLink(videoUrl, quality))
            
            ErrorLogger.logExtraction(name, url, success = true)
        }.getOrElse { error ->
            ErrorLogger.logExtraction(name, url, success = false, error = error)
            if (attempt == 3) throw error // Re-lançar na última tentativa
        }
    }
}
```

---

## 🔧 ARQUIVOS A MODIFICAR

### Criar Novos:
1. `utils/VideoUrlCache.kt`
2. `utils/RetryHelper.kt`
3. `utils/QualityDetector.kt`
4. `utils/ErrorLogger.kt`

### Modificar Existentes:
1. `extractors/MediaFireExtractor.kt` - Aplicar otimizações
2. `extractors/MegaEmbedExtractor.kt` - Aplicar otimizações
3. `extractors/MyVidPlayExtractor.kt` - Aplicar otimizações
4. `extractors/PlayerEmbedAPIExtractor.kt` - Aplicar otimizações
5. `extractors/AjaxPlayerExtractor.kt` - Aplicar otimizações
6. `MaxSeriesProvider.kt` - Aplicar cache no loadLinks e logs estruturados

---

## 📈 MÉTRICAS DE SUCESSO

### Performance
- ⏱️ **Tempo de extração**: Redução de 30% com cache
- 🔄 **Taxa de sucesso**: Aumento de 20% com retry
- 📦 **Uso de memória**: Cache limitado a 100 entradas

### Qualidade
- 🎯 **Detecção de qualidade**: 90%+ de acurácia
- 📝 **Logs estruturados**: 100% dos extractors
- ⚠️ **Error handling**: 100% dos catch blocks

---

## 🚀 PLANO DE EXECUÇÃO

### Etapa 1: Criar Utilities (2h)
1. ✅ Criar `VideoUrlCache.kt`
2. ✅ Criar `RetryHelper.kt`
3. ✅ Criar `QualityDetector.kt`
4. ✅ Criar `ErrorLogger.kt`

### Etapa 2: Integrar nos Extractors (1h30)
1. ⏳ Aplicar em `MediaFireExtractor.kt`
2. ⏳ Aplicar em `MegaEmbedExtractor.kt`
3. ⏳ Aplicar em `MyVidPlayExtractor.kt`
4. ⏳ Aplicar em `PlayerEmbedAPIExtractor.kt`
5. ⏳ Aplicar em `AjaxPlayerExtractor.kt`

### Etapa 3: Testing e Refinamento (30min)
1. ⏳ Testar cache hit/miss
2. ⏳ Testar retry em falhas simuladas
3. ⏳ Validar detecção de qualidade
4. ⏳ Verificar logs estruturados

---

## ⚠️ CONSIDERAÇÕES

### Limitações do Cache
- Cache é volátil (memória)
- Limpar ao reiniciar app
- Limpar entradas expiradas periodicamente

### Retry Logic
- Não aplicar retry em erros de validação (400, 404)
- Apenas em erros de rede ou timeouts
- Backoff exponencial para não sobrecarregar servidores

### Quality Detection
- Fallback para `Qualities.Unknown.value` quando incerto
- Priorizar qualidade maior quando múltiplas opções

---

## 📝 PRÓXIMOS PASSOS

Após completar FASE 4, seguir para:

**FASE 5: Deploy e Validação**
- Build e testes locais
- Deploy via GitHub Actions
- Validação em produção
- Monitoramento de métricas

---

**Status Atual**: Utilities base criadas (Fases 1-3) ✅  
**Próximo**: Implementar utilities de otimização 🚧  
**Versão Alvo**: v81
