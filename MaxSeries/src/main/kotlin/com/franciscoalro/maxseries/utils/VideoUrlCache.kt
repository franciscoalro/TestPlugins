package com.franciscoalro.maxseries.utils

/**
 * Cache em memória para URLs de vídeo extraídas
 * Reduz chamadas redundantes aos servidores e melhora performance
 * 
 * Features:
 * - Cache temporal (5 minutos por padrão)
 * - Limpeza automática de entradas expiradas
 * - Thread-safe para uso concorrente
 * - Estatísticas de hit/miss para monitoramento
 */
object VideoUrlCache {
    private const val CACHE_DURATION_MS = 5 * 60 * 1000L // 5 minutos
    private const val MAX_CACHE_SIZE = 100 // Limitar memória
    
    private val cache = mutableMapOf<String, CachedUrl>()
    private var hitCount = 0
    private var missCount = 0
    
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
     * 
     * @param key Chave única (normalmente URL do episódio)
     * @return CachedUrl se encontrada e válida, null caso contrário
     */
    @Synchronized
    fun get(key: String): CachedUrl? {
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
     * 
     * @param key Chave única
     * @param url URL do vídeo extraída
     * @param quality Qualidade detectada
     * @param serverName Nome do servidor/extractor
     */
    @Synchronized
    fun put(key: String, url: String, quality: Int, serverName: String = "Unknown") {
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
     * 
     * @return CacheStats com métricas atuais
     */
    @Synchronized
    fun getStats(): CacheStats {
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
