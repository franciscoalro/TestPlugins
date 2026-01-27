package com.franciscoalro.maxseries.utils

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import kotlinx.serialization.*
import kotlinx.serialization.json.*

/**
 * PersistentVideoCache - Cache persistente com LRU e TTL
 * 
 * Features:
 * - TTL: 30min (vs 5min volátil do VideoUrlCache)
 * - Persistence: SharedPreferences (sobrevive restart do app)
 * - Max size: 100 URLs
 * - LRU eviction: Remove menos acessados quando cheio
 * - Hit rate tracking: Estatísticas de performance
 * 
 * Performance:
 * - Hit: <1ms (leitura de SharedPreferences)
 * - Miss: ~2-5s (precisa extrair)
 * - Target hit rate: >60%
 * 
 * @since v217
 */
class PersistentVideoCache private constructor(context: Context) {
    
    companion object {
        private const val TAG = "PersistentVideoCache"
        private const val PREFS_NAME = "video_cache_v217"
        private const val MAX_SIZE = 100
        private const val TTL_MINUTES = 30L
        
        @Volatile
        private var instance: PersistentVideoCache? = null
        
        /**
         * Obtém instância singleton do cache
         * 
         * @param context Application context
         * @return Instância única do cache
         */
        fun getInstance(context: Context): PersistentVideoCache {
            return instance ?: synchronized(this) {
                instance ?: PersistentVideoCache(context.applicationContext).also {
                    instance = it
                    Log.d(TAG, "✅ PersistentVideoCache inicializado")
                }
            }
        }
    }
    
    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val json = Json { ignoreUnknownKeys = true }
    
    // Estatísticas
    private var hits = 0
    private var misses = 0
    
    /**
     * Entrada do cache com metadados
     * 
     * @property videoUrl URL do vídeo extraída
     * @property quality Qualidade do vídeo (720, 1080, etc)
     * @property extractor Nome do extractor usado
     * @property timestamp Timestamp de criação (ms)
     * @property accessCount Contador de acessos (para LRU)
     */
    @Serializable
    data class CacheEntry(
        val videoUrl: String,
        val quality: Int,
        val extractor: String,
        val timestamp: Long,
        val accessCount: Int = 0
    )
    
    /**
     * Salva URL no cache com LRU eviction
     * 
     * @param sourceUrl URL da fonte (chave)
     * @param videoUrl URL do vídeo extraída
     * @param quality Qualidade do vídeo
     * @param extractor Nome do extractor
     */
    @Synchronized
    fun put(sourceUrl: String, videoUrl: String, quality: Int, extractor: String) {
        val startTime = System.currentTimeMillis()
        
        // Limpar expirados antes de adicionar
        cleanExpired()
        
        // LRU: remover mais antigo se cheio
        if (size() >= MAX_SIZE) {
            removeOldest()
        }
        
        // Criar entry
        val entry = CacheEntry(
            videoUrl = videoUrl,
            quality = quality,
            extractor = extractor,
            timestamp = System.currentTimeMillis(),
            accessCount = 0
        )
        
        // Salvar
        val key = hashKey(sourceUrl)
        val jsonString = json.encodeToString(entry)
        prefs.edit().putString(key, jsonString).apply()
        
        val duration = System.currentTimeMillis() - startTime
        Log.d(TAG, "💾 Cache PUT: $extractor (${duration}ms) - size: ${size()}/$MAX_SIZE")
    }
    
    /**
     * Obtém URL do cache com TTL check
     * 
     * @param sourceUrl URL da fonte (chave)
     * @return CacheEntry se encontrada e válida, null caso contrário
     */
    @Synchronized
    fun get(sourceUrl: String): CacheEntry? {
        val startTime = System.currentTimeMillis()
        val key = hashKey(sourceUrl)
        
        val jsonString = prefs.getString(key, null)
        if (jsonString == null) {
            misses++
            val duration = System.currentTimeMillis() - startTime
            Log.d(TAG, "❌ Cache MISS (${duration}ms) - hit rate: ${getHitRate()}%")
            return null
        }
        
        val entry = try {
            json.decodeFromString<CacheEntry>(jsonString)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao decodificar cache: ${e.message}")
            prefs.edit().remove(key).apply()
            misses++
            return null
        }
        
        // Verificar expiração (TTL)
        val age = System.currentTimeMillis() - entry.timestamp
        val ttlMs = TTL_MINUTES * 60 * 1000
        
        if (age > ttlMs) {
            val ageMinutes = age / 60000
            Log.d(TAG, "⏰ Cache expirado (age: ${ageMinutes}min, TTL: ${TTL_MINUTES}min)")
            prefs.edit().remove(key).apply()
            misses++
            return null
        }
        
        // Atualizar access count (LRU)
        val updatedEntry = entry.copy(accessCount = entry.accessCount + 1)
        prefs.edit().putString(key, json.encodeToString(updatedEntry)).apply()
        
        hits++
        val duration = System.currentTimeMillis() - startTime
        val ageMinutes = age / 60000
        Log.d(TAG, "✅ Cache HIT: ${entry.extractor} (${duration}ms, age: ${ageMinutes}min, hit rate: ${getHitRate()}%)")
        
        return updatedEntry
    }
    
    /**
     * Limpa entradas expiradas (TTL check)
     */
    @Synchronized
    fun cleanExpired() {
        val startTime = System.currentTimeMillis()
        val ttlMs = TTL_MINUTES * 60 * 1000
        val now = System.currentTimeMillis()
        var removed = 0
        
        val editor = prefs.edit()
        
        prefs.all.forEach { (key, value) ->
            if (value is String) {
                try {
                    val entry = json.decodeFromString<CacheEntry>(value)
                    val age = now - entry.timestamp
                    
                    if (age > ttlMs) {
                        editor.remove(key)
                        removed++
                    }
                } catch (e: Exception) {
                    // Entry inválido, remover
                    editor.remove(key)
                    removed++
                }
            }
        }
        
        editor.apply()
        
        if (removed > 0) {
            val duration = System.currentTimeMillis() - startTime
            Log.d(TAG, "🧹 Limpeza: $removed expirados (${duration}ms)")
        }
    }
    
    /**
     * Remove entrada mais antiga (LRU)
     */
    @Synchronized
    fun removeOldest() {
        val entries = prefs.all.mapNotNull { (key, value) ->
            if (value is String) {
                try {
                    val entry = json.decodeFromString<CacheEntry>(value)
                    key to entry
                } catch (e: Exception) {
                    null
                }
            } else null
        }
        
        // Ordenar por accessCount (LRU) - menor = menos usado
        val oldest = entries.minByOrNull { it.second.accessCount }
        
        if (oldest != null) {
            prefs.edit().remove(oldest.first).apply()
            Log.d(TAG, "🗑️ LRU: Removido ${oldest.second.extractor} (acessos: ${oldest.second.accessCount})")
        }
    }
    
    /**
     * Tamanho atual do cache
     * 
     * @return Número de entradas no cache
     */
    @Synchronized
    fun size(): Int = prefs.all.size
    
    /**
     * Limpar todo o cache
     */
    @Synchronized
    fun clear() {
        prefs.edit().clear().apply()
        hits = 0
        misses = 0
        Log.d(TAG, "🧹 Cache limpo completamente")
    }
    
    /**
     * Taxa de hit do cache
     * 
     * @return Porcentagem de hits (0-100)
     */
    fun getHitRate(): Int {
        val total = hits + misses
        return if (total > 0) (hits * 100 / total) else 0
    }
    
    /**
     * Estatísticas do cache
     * 
     * @return Map com métricas do cache
     */
    fun getStats(): Map<String, Any> {
        return mapOf(
            "size" to size(),
            "maxSize" to MAX_SIZE,
            "hits" to hits,
            "misses" to misses,
            "hitRate" to getHitRate(),
            "ttlMinutes" to TTL_MINUTES
        )
    }
    
    /**
     * Hash da chave (simples hashCode)
     * 
     * @param url URL para hash
     * @return String hash
     */
    private fun hashKey(url: String): String {
        return url.hashCode().toString()
    }
}
