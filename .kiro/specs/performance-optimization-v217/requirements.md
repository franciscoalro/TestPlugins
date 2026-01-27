# Performance Optimization v217 - Requirements

## 🎯 Objetivo

Otimizar performance do MaxSeries v216 aplicando o skill **performance-profiling** em 3 áreas críticas:

1. **WebView Loading** - Reduzir tempo de carregamento
2. **PlayerEmbedAPI Timeout** - 60s → 30s
3. **Cache Persistente** - Além dos 5min atuais

---

## 📋 User Stories

### US1: Como usuário, quero que o PlayerEmbedAPI carregue mais rápido
**Valor:** Reduzir frustração de espera

**Critérios de Aceitação:**
- [ ] 1.1 WebView deve carregar em <2s (atualmente ~3-5s)
- [ ] 1.2 Script de hooks deve injetar em <500ms
- [ ] 1.3 Overlay deve ser removido em <1s
- [ ] 1.4 Logs devem mostrar tempo de cada etapa

### US2: Como usuário, quero timeout mais curto no PlayerEmbedAPI
**Valor:** Fallback mais rápido se não funcionar

**Critérios de Aceitação:**
- [ ] 2.1 Timeout deve ser 30s (atualmente 60s)
- [ ] 2.2 Mensagem clara após timeout
- [ ] 2.3 Fallback automático para próximo extractor
- [ ] 2.4 Configurável via constante

### US3: Como usuário, quero que URLs extraídas sejam cacheadas por mais tempo
**Valor:** Evitar re-extração desnecessária

**Critérios de Aceitação:**
- [ ] 3.1 Cache deve persistir por 30min (atualmente 5min)
- [ ] 3.2 Cache deve sobreviver a restart do app
- [ ] 3.3 Cache deve ter limite de tamanho (100 URLs)
- [ ] 3.4 Cache deve ser limpo automaticamente (LRU)
- [ ] 3.5 Estatísticas de hit/miss devem ser logadas

---

## 🔍 Análise de Performance Atual

### Baseline (v216)

| Métrica | Valor Atual | Meta v217 | Melhoria |
|---------|-------------|-----------|----------|
| WebView Loading | 3-5s | <2s | 40-60% |
| PlayerEmbed Timeout | 60s | 30s | 50% |
| Cache Duration | 5min | 30min | 500% |
| Cache Persistence | ❌ Não | ✅ Sim | N/A |
| Cache Hit Rate | ~20% | ~60% | 200% |

### Gargalos Identificados

1. **WebView Initialization** (~1-2s)
   - Criação do contexto
   - Configuração de settings
   - Layout forçado

2. **Script Injection** (~500ms-1s)
   - Espera por DOMContentLoaded
   - Execução de JavaScript

3. **Overlay Removal** (~500ms-1s)
   - Polling a cada 1s
   - Múltiplas tentativas

4. **Cache Volátil** (5min)
   - Perde dados ao fechar app
   - Expira muito rápido
   - Sem LRU

---

## 🎯 Requisitos Técnicos

### RT1: WebView Optimization

**Objetivo:** Reduzir tempo de loading de 3-5s para <2s

**Implementação:**
```kotlin
// 1. Pre-warm WebView (singleton)
object WebViewPool {
    private var cachedWebView: WebView? = null
    
    fun getOrCreate(context: Context): WebView {
        return cachedWebView ?: createWebView(context).also {
            cachedWebView = it
        }
    }
}

// 2. Otimizar settings
webView.settings.apply {
    blockNetworkImage = true  // Não carregar imagens
    cacheMode = WebSettings.LOAD_NO_CACHE  // Sem cache HTTP
    setRenderPriority(WebSettings.RenderPriority.HIGH)
}

// 3. Injetar script antes de carregar
webView.evaluateJavascript(injectedScript, null)
webView.loadUrl(url, headers)
```

**Métricas:**
- [ ] Tempo de criação: <500ms
- [ ] Tempo de injeção: <200ms
- [ ] Tempo total: <2s

---

### RT2: Timeout Reduction

**Objetivo:** Reduzir timeout de 60s para 30s

**Implementação:**
```kotlin
companion object {
    private const val TIMEOUT_SECONDS = 30L  // Era 60L
    private const val QUICK_TIMEOUT_SECONDS = 15L  // Para retry
}

// Timeout adaptativo
val timeout = if (attempt == 1) TIMEOUT_SECONDS else QUICK_TIMEOUT_SECONDS
val captured = latch.await(timeout, TimeUnit.SECONDS)
```

**Métricas:**
- [ ] Timeout padrão: 30s
- [ ] Timeout retry: 15s
- [ ] Fallback: <1s

---

### RT3: Persistent Cache

**Objetivo:** Cache persistente de 30min com LRU

**Implementação:**
```kotlin
// 1. SharedPreferences para persistência
class PersistentVideoCache(context: Context) {
    private val prefs = context.getSharedPreferences("video_cache", MODE_PRIVATE)
    private val maxSize = 100
    private val ttlMinutes = 30L
    
    data class CacheEntry(
        val url: String,
        val quality: Int,
        val extractor: String,
        val timestamp: Long
    )
    
    fun put(key: String, entry: CacheEntry) {
        // Limpar expirados
        cleanExpired()
        
        // LRU: remover mais antigo se cheio
        if (size() >= maxSize) {
            removeOldest()
        }
        
        // Salvar
        val json = Json.encodeToString(entry)
        prefs.edit().putString(key, json).apply()
    }
    
    fun get(key: String): CacheEntry? {
        val json = prefs.getString(key, null) ?: return null
        val entry = Json.decodeFromString<CacheEntry>(json)
        
        // Verificar expiração
        val age = System.currentTimeMillis() - entry.timestamp
        if (age > ttlMinutes * 60 * 1000) {
            remove(key)
            return null
        }
        
        return entry
    }
}
```

**Métricas:**
- [ ] TTL: 30min
- [ ] Max size: 100 URLs
- [ ] Hit rate: >60%
- [ ] Persist: ✅

---

## 📊 Métricas de Sucesso

### Performance Targets

| Métrica | v216 | v217 | Melhoria |
|---------|------|------|----------|
| **WebView Load** | 3-5s | <2s | 40-60% ⬇️ |
| **PlayerEmbed Timeout** | 60s | 30s | 50% ⬇️ |
| **Cache Duration** | 5min | 30min | 500% ⬆️ |
| **Cache Hit Rate** | 20% | 60% | 200% ⬆️ |
| **Memory Usage** | ~50MB | <60MB | <20% ⬆️ |

### User Experience

| Métrica | v216 | v217 | Melhoria |
|---------|------|------|----------|
| **Tempo até vídeo** | 5-65s | 2-32s | 50% ⬇️ |
| **Taxa de sucesso** | 98% | 98% | Mantém |
| **Frustração** | Alta | Baixa | ⬇️⬇️⬇️ |

---

## 🔧 Implementação

### Fase 1: WebView Optimization
- [ ] Criar WebViewPool singleton
- [ ] Otimizar settings (block images, etc)
- [ ] Pre-inject script
- [ ] Medir tempo de cada etapa

### Fase 2: Timeout Reduction
- [ ] Reduzir TIMEOUT_SECONDS para 30L
- [ ] Adicionar QUICK_TIMEOUT_SECONDS (15L)
- [ ] Implementar timeout adaptativo
- [ ] Melhorar mensagens de erro

### Fase 3: Persistent Cache
- [ ] Criar PersistentVideoCache class
- [ ] Implementar SharedPreferences storage
- [ ] Adicionar LRU eviction
- [ ] Implementar TTL (30min)
- [ ] Adicionar estatísticas

### Fase 4: Testing & Validation
- [ ] Medir performance antes/depois
- [ ] Validar cache hit rate
- [ ] Testar em dispositivo real
- [ ] Gerar relatório de performance

---

## 🎓 Skills Aplicados

### performance-profiling ⭐⭐⭐⭐⭐

**Técnicas:**
1. **Profiling** - Medir tempo de cada operação
2. **Bottleneck Analysis** - Identificar gargalos
3. **Optimization** - Aplicar melhorias
4. **Benchmarking** - Comparar antes/depois
5. **Monitoring** - Logs de performance

**Ferramentas:**
- `measureTimeMillis` - Medir duração
- `Log.d` - Logs estruturados
- `SharedPreferences` - Cache persistente
- `LRU` - Eviction policy

---

## 📝 Notas

### Riscos

1. **WebView Pool** - Pode causar memory leak se não limpar
2. **Timeout Curto** - Pode aumentar falhas em redes lentas
3. **Cache Grande** - Pode consumir muito storage

### Mitigações

1. **Cleanup** - Destruir WebView ao sair
2. **Timeout Adaptativo** - 30s normal, 15s retry
3. **LRU + Limite** - Max 100 URLs, ~1MB

---

## ✅ Definition of Done

- [ ] WebView carrega em <2s
- [ ] Timeout é 30s (50% redução)
- [ ] Cache persiste por 30min
- [ ] Cache hit rate >60%
- [ ] Testes manuais passam
- [ ] Documentação atualizada
- [ ] Release notes criadas

---

**Versão:** 217  
**Skill:** performance-profiling  
**Prioridade:** Alta  
**Estimativa:** 2-3 horas
