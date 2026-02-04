package com.franciscoalro.maxseries.session

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.lagradost.cloudstream3.utils.ExtractorLink
import java.util.concurrent.ConcurrentHashMap

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * VIDEO URL CACHE v2.0 - Cache Inteligente de URLs de Vídeo
 * Integrado com SessionManager
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Melhorias sobre v1.0:
 * - 💾 Cache persistente (SharedPreferences)
 * - ⏰ TTL configurável por URL
 * - 🔄 Integração com SessionManager
 * - 📊 Métricas de hit/miss
 * - 🎯 Cache por qualidade
 * 
 * @version 2.0
 * @since 2026-02-03
 */
class VideoUrlCache private constructor(
    context: Context,
    private val defaultTTLMinutes: Int = 30
) {
    companion object {
        private const val TAG = "VideoUrlCache"
        private const val PREFS_NAME = "maxseries_video_cache"
        private const val KEY_PREFIX = "video_"
        
        @Volatile
        private var instance: VideoUrlCache? = null
        
        fun getInstance(context: Context): VideoUrlCache {
            return instance ?: synchronized(this) {
                instance ?: VideoUrlCache(context.applicationContext).also {
                    instance = it
                }
            }
        }
        
        // Cache global acessível de qualquer lugar
        fun get(context: Context): VideoUrlCache = getInstance(context)
    }
    
    // Cache em memória
    private val memoryCache = ConcurrentHashMap<String, CachedVideo>()
    
    // Persistência
    private val prefs: SharedPreferences by lazy {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    // Métricas
    private var hits = 0
    private var misses = 0
    private var saves = 0
    
    /**
     * Dados de um vídeo cacheado
     */
    data class CachedVideo(
        val sourceUrl: String,      // URL original do player
        val videoUrl: String,       // URL direta do vídeo
        val quality: Int,           // Qualidade (720, 1080, etc)
        val serverName: String,     // Nome do servidor
        val timestamp: Long = System.currentTimeMillis(),
        val ttlMinutes: Int = 30,
        val headers: Map<String, String> = emptyMap()
    ) {
        /**
         * Verifica se o cache ainda é válido
         */
        fun isValid(): Boolean {
            val age = System.currentTimeMillis() - timestamp
            val maxAge = ttlMinutes * 60 * 1000
            return age < maxAge
        }
        
        /**
         * Tempo restante em minutos
         */
        fun remainingMinutes(): Int {
            val age = System.currentTimeMillis() - timestamp
            val maxAge = ttlMinutes * 60 * 1000
            return maxOf(0, ((maxAge - age) / (60 * 1000)).toInt())
        }
    }
    
    /**
     * Salva uma URL de vídeo no cache
     */
    fun put(
        sourceUrl: String,
        videoUrl: String,
        quality: Int,
        serverName: String,
        headers: Map<String, String> = emptyMap(),
        ttlMinutes: Int = defaultTTLMinutes
    ) {
        val cached = CachedVideo(
            sourceUrl = sourceUrl,
            videoUrl = videoUrl,
            quality = quality,
            serverName = serverName,
            ttlMinutes = ttlMinutes,
            headers = headers
        )
        
        // Salvar em memória
        memoryCache[sourceUrl] = cached
        
        // Salvar em disco
        saveToPrefs(sourceUrl, cached)
        
        saves++
        Log.d(TAG, "💾 URL cacheada: $sourceUrl -> ${videoUrl.take(50)}...")
    }
    
    /**
     * Obtém uma URL do cache
     */
    fun get(sourceUrl: String): CachedVideo? {
        // 1. Verificar memória
        memoryCache[sourceUrl]?.let { cached ->
            if (cached.isValid()) {
                hits++
                Log.d(TAG, "✅ Cache HIT (memória): $sourceUrl")
                return cached
            }
        }
        
        // 2. Verificar disco
        loadFromPrefs(sourceUrl)?.let { cached ->
            if (cached.isValid()) {
                memoryCache[sourceUrl] = cached  // Recarregar memória
                hits++
                Log.d(TAG, "✅ Cache HIT (disco): $sourceUrl")
                return cached
            }
        }
        
        misses++
        Log.d(TAG, "❌ Cache MISS: $sourceUrl")
        return null
    }
    
    /**
     * Verifica se existe no cache e é válido
     */
    fun hasValid(sourceUrl: String): Boolean {
        return get(sourceUrl) != null
    }
    
    /**
     * Invalida uma entrada específica
     */
    fun invalidate(sourceUrl: String) {
        memoryCache.remove(sourceUrl)
        prefs.edit().remove(KEY_PREFIX + sourceUrl.hashCode()).apply()
        Log.d(TAG, "🗑️ Cache invalidado: $sourceUrl")
    }
    
    /**
     * Limpa todo o cache
     */
    fun clear() {
        memoryCache.clear()
        prefs.edit().clear().apply()
        hits = 0
        misses = 0
        saves = 0
        Log.d(TAG, "🧹 Cache limpo completamente")
    }
    
    /**
     * Remove entradas expiradas
     */
    fun cleanup() {
        val before = memoryCache.size
        
        // Limpar memória
        memoryCache.entries.removeIf { (_, cached) ->
            !cached.isValid()
        }
        
        // Limpar disco
        prefs.all.forEach { (key, _) ->
            if (key.startsWith(KEY_PREFIX)) {
                val sourceUrl = key.removePrefix(KEY_PREFIX)
                loadFromPrefs(sourceUrl)?.let { cached ->
                    if (!cached.isValid()) {
                        prefs.edit().remove(key).apply()
                    }
                }
            }
        }
        
        val after = memoryCache.size
        Log.d(TAG, "🧹 Cleanup: $before -> $after entradas")
    }
    
    /**
     * Retorna métricas do cache
     */
    fun getMetrics(): CacheMetrics {
        val total = hits + misses
        return CacheMetrics(
            hits = hits,
            misses = misses,
            saves = saves,
            hitRate = if (total > 0) hits.toFloat() / total else 0f,
            memorySize = memoryCache.size,
            diskSize = prefs.all.size
        )
    }
    
    /**
     * Lista todas as entradas válidas
     */
    fun listValid(): List<CachedVideo> {
        return memoryCache.values.filter { it.isValid() }
    }
    
    /**
     * Obtém headers cacheados para uma URL
     */
    fun getHeaders(sourceUrl: String): Map<String, String> {
        return get(sourceUrl)?.headers ?: emptyMap()
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS PRIVADOS
    // ═══════════════════════════════════════════════════════════════════════════
    
    private fun saveToPrefs(sourceUrl: String, cached: CachedVideo) {
        try {
            val json = """
                {
                    "sourceUrl": "${cached.sourceUrl}",
                    "videoUrl": "${cached.videoUrl}",
                    "quality": ${cached.quality},
                    "serverName": "${cached.serverName}",
                    "timestamp": ${cached.timestamp},
                    "ttlMinutes": ${cached.ttlMinutes},
                    "headers": ${cached.headers.entries.joinToString(",", "{", "}") { "\"${it.key}\":\"${it.value}\"" }}
                }
            """.trimIndent()
            
            prefs.edit().putString(KEY_PREFIX + sourceUrl.hashCode(), json).apply()
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao salvar cache: ${e.message}")
        }
    }
    
    private fun loadFromPrefs(sourceUrl: String): CachedVideo? {
        val json = prefs.getString(KEY_PREFIX + sourceUrl.hashCode(), null) ?: return null
        
        return try {
            // Parse simples do JSON
            val map = parseSimpleJson(json)
            
            CachedVideo(
                sourceUrl = map["sourceUrl"] ?: return null,
                videoUrl = map["videoUrl"] ?: return null,
                quality = map["quality"]?.toIntOrNull() ?: 0,
                serverName = map["serverName"] ?: "Unknown",
                timestamp = map["timestamp"]?.toLongOrNull() ?: System.currentTimeMillis(),
                ttlMinutes = map["ttlMinutes"]?.toIntOrNull() ?: defaultTTLMinutes,
                headers = emptyMap()  // Simplificado
            )
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao carregar cache: ${e.message}")
            null
        }
    }
    
    private fun parseSimpleJson(json: String): Map<String, String> {
        val result = mutableMapOf<String, String>()
        val regex = Regex(""""([^"]+)":\s*"?([^",\}]+)"?""")
        
        regex.findAll(json).forEach { match ->
            result[match.groupValues[1]] = match.groupValues[2]
        }
        
        return result
    }
    
    /**
     * Métricas do cache
     */
    data class CacheMetrics(
        val hits: Int,
        val misses: Int,
        val saves: Int,
        val hitRate: Float,
        val memorySize: Int,
        val diskSize: Int
    ) {
        override fun toString(): String {
            return "CacheMetrics(hits=$hits, misses=$misses, hitRate=${"%.1f".format(hitRate * 100)}%, " +
                   "memory=$memorySize, disk=$diskSize)"
        }
    }
}

/**
 * Extensões para facilitar uso
 */
fun ExtractorLink.cacheKey(): String {
    return this.url
}

fun Context.videoCache(): VideoUrlCache {
    return VideoUrlCache.getInstance(this)
}
