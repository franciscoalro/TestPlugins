package com.franciscoalro.maxseries.utils

import android.content.Context

/**
 * Cache em memória para URLs de vídeo extraídas
 * Reduz chamadas redundantes aos servidores e melhora performance
 * 
 * Features v217:
 * - Cache persistente (30 minutos via PersistentVideoCache)
 * - Cache volátil (5 minutos em memória - fallback)
 * - Limpeza automática de entradas expiradas
 * - Thread-safe para uso concorrente
 * - Estatísticas de hit/miss para monitoramento
 * 
 * @since v217 - Integração com PersistentVideoCache
 */
object VideoUrlCache {
    private const val CACHE_DURATION_MS = 5 * 60 * 1000L // 5 minutos
    private const val MAX_CACHE_SIZE = 100 // Limitar memória
    
    private val cache = mutableMapOf<String, CachedUrl>()
    private var hitCount = 0
    private var missCount = 0
    
    // v217: Cache persistente
    private var persistentCache: PersistentVideoCache? = null
    
    /**
     * Inicializa cache persistente (v217)
     * 
     * @param context Application context
     */
    fun init(context: Context) {
        persistentCache = PersistentVideoCache.getInstance(context)
        android.util.Log.d("VideoUrlCache", "✅ Cache persistente inicializado")
    }
    
    /**
     * Representa uma URL cacheada com metadados
     */
    data class CachedUrl(
        val url: String,
        val quality: Int,
        val serverName: String,
        val timestamp: Long = System.currentTimeMillis()
    ) {
        fun isExpired(): Boolean {
            return (System.currentTimeMillis() - timestamp) > CACHE_DURATION_MS
        }
    }
    
    /**
     * Estatísticas do cache
     */
    data class CacheStats(
        val totalEntries: Int,
        val hits: Int,
        val misses: Int,
        val hitRate: Double
    )
    
    /**
     * Obtém URL do cache se existir e não estiver expirada
     * v217: Tenta cache persistente primeiro, depois cache em memória
     * 
     * @param key Chave única (normalmente URL do episódio)
     * @return CachedUrl se encontrada e válida, null caso contrário
     */
    @Synchronized
    fun get(key: String): CachedUrl? {
        // v217: Tentar cache persistente primeiro (30min TTL)
        persistentCache?.get(key)?.let { entry ->
            hitCount++
            return CachedUrl(entry.videoUrl, entry.quality, entry.extractor)
        }
        
        // Fallback: cache em memória (5min TTL)
        clearExpired() // Limpeza automática
        
        val cached = cache[key]
        return if (cached != null && !cached.isExpired()) {
            hitCount++
            cached
        } else {
            missCount++
            null
        }
    }
    
    /**
     * Salva URL no cache
     * v217: Salva em cache persistente E em memória
     * 
     * @param key Chave única
     * @param url URL do vídeo extraída
     * @param quality Qualidade detectada
     * @param serverName Nome do servidor/extractor
     */
    @Synchronized
    fun put(key: String, url: String, quality: Int, serverName: String = "Unknown") {
        // v217: Salvar em cache persistente (30min TTL)
        persistentCache?.put(key, url, quality, serverName)
        
        // Também salvar em memória (5min TTL - fallback rápido)
        // Limitar tamanho do cache
        if (cache.size >= MAX_CACHE_SIZE) {
            removeOldest()
        }
        
        cache[key] = CachedUrl(url, quality, serverName)
    }
    
    /**
     * Remove entrada específica do cache
     * 
     * @param key Chave a remover
     */
    @Synchronized
    fun remove(key: String) {
        cache.remove(key)
    }
    
    /**
     * Limpa todo o cache
     */
    @Synchronized
    fun clear() {
        cache.clear()
        hitCount = 0
        missCount = 0
    }
    
    /**
     * Remove apenas entradas expiradas
     */
    @Synchronized
    fun clearExpired() {
        val expired = cache.filter { it.value.isExpired() }.keys
        expired.forEach { cache.remove(it) }
    }
    
    /**
     * Remove entrada mais antiga (FIFO)
     */
    private fun removeOldest() {
        val oldest = cache.entries.minByOrNull { it.value.timestamp }
        oldest?.let { cache.remove(it.key) }
    }
    
    /**
     * Obtém estatísticas do cache
     * v217: Retorna estatísticas do cache persistente se disponível
     * 
     * @return CacheStats com métricas atuais
     */
    @Synchronized
    fun getStats(): CacheStats {
        // v217: Se cache persistente disponível, usar suas estatísticas
        persistentCache?.let { pCache ->
            val stats = pCache.getStats()
            return CacheStats(
                totalEntries = stats["size"] as? Int ?: 0,
                hits = stats["hits"] as? Int ?: 0,
                misses = stats["misses"] as? Int ?: 0,
                hitRate = (stats["hitRate"] as? Int ?: 0) / 100.0
            )
        }
        
        // Fallback: estatísticas do cache em memória
        val total = hitCount + missCount
        val hitRate = if (total > 0) hitCount.toDouble() / total else 0.0
        
        return CacheStats(
            totalEntries = cache.size,
            hits = hitCount,
            misses = missCount,
            hitRate = hitRate
        )
    }
    
    /**
     * Verifica se cache contém chave
     * 
     * @param key Chave a verificar
     * @return true se chave existe e não está expirada
     */
    @Synchronized
    fun contains(key: String): Boolean {
        val cached = cache[key]
        return cached != null && !cached.isExpired()
    }
    
    /**
     * Obtém tamanho atual do cache (apenas entradas válidas)
     * 
     * @return Número de entradas não expiradas
     */
    @Synchronized
    fun size(): Int {
        clearExpired()
        return cache.size
    }
}
