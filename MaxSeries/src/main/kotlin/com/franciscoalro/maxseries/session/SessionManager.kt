package com.franciscoalro.maxseries.session

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.lagradost.cloudstream3.app
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withTimeoutOrNull
import org.json.JSONObject
import java.util.concurrent.ConcurrentHashMap

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * SESSION MANAGER - Gerenciamento de Sessões com Cache Persistente
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Funcionalidades:
 * - 💾 Cache persistente (SharedPreferences)
 * - 🔄 Renovação automática de tokens expirados
 * - ⏰ Detecção de expiração (TTL)
 * - 🎯 Sessões por domínio/player
 * - 📊 Métricas de cache hit/miss
 * 
 * Fluxo de Uso:
 * 1. Verificar sessão em cache
 * 2. Se válida → Usar
 * 3. Se expirada → Renovar
 * 4. Se não existir → Criar nova
 * 
 * @version 1.0
 * @since 2026-02-03
 */
class SessionManager(
    private val context: Context,
    private val defaultTTLMinutes: Int = 55  // 55 minutos (padrão de expiração)
) {
    companion object {
        private const val TAG = "SessionManager"
        private const val PREFS_NAME = "maxseries_sessions"
        private const val KEY_PREFIX = "session_"
        
        // Headers de bypass comuns (descobertos via pentest)
        val BYPASS_HEADERS = mapOf(
            "X-Requested-With" to "XMLHttpRequest",
            "Accept" to "application/json, text/plain, */*",
            "Accept-Language" to "pt-BR,pt;q=0.9,en;q=0.8",
            "X-Forwarded-For" to "127.0.0.1"
        )
        
        // User-Agents rotativos
        val USER_AGENTS = listOf(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        )
    }
    
    // Cache em memória (Thread-safe)
    private val memoryCache = ConcurrentHashMap<String, SessionData>()
    private val mutex = Mutex()
    
    // Persistência
    private val prefs: SharedPreferences by lazy {
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    // Métricas
    private val metrics = SessionMetrics()
    
    /**
     * Dados de uma sessão
     */
    data class SessionData(
        val domain: String,
        val cookies: Map<String, String>,
        val tokens: Map<String, String>,
        val headers: Map<String, String>,
        val timestamp: Long = System.currentTimeMillis(),
        val ttlMinutes: Int = 55,
        val metadata: SessionMetadata = SessionMetadata()
    ) {
        /**
         * Verifica se a sessão ainda é válida
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
            val remaining = (maxAge - age) / (60 * 1000)
            return maxOf(0, remaining.toInt())
        }
    }
    
    /**
     * Metadados adicionais da sessão
     */
    data class SessionMetadata(
        val playerType: PlayerType = PlayerType.UNKNOWN,
        val videoId: String = "",
        val slug: String = "",
        val sourceUrl: String = ""
    ) {
        enum class PlayerType {
            PLAYEREMBEDAPI,
            MEGAEMBED,
            MYVIDPLAY,
            DOODSTREAM,
            STREAMTAPE,
            UNKNOWN
        }
    }
    
    /**
     * Métricas de uso do cache
     */
    data class SessionMetrics(
        var cacheHits: Int = 0,
        var cacheMisses: Int = 0,
        var renewals: Int = 0,
        var creations: Int = 0
    ) {
        fun hitRate(): Float {
            val total = cacheHits + cacheMisses
            return if (total > 0) cacheHits.toFloat() / total else 0f
        }
        
        override fun toString(): String {
            return "Cache Hits: $cacheHits | Misses: $cacheMisses | " +
                   "Hit Rate: ${"%.1f".format(hitRate() * 100)}% | " +
                   "Renewals: $renewals | Creations: $creations"
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS PÚBLICOS PRINCIPAIS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Obtém uma sessão válida (cache ou nova)
     * 
     * @param domain Domínio do player (ex: "playerembedapi.link")
     * @param referer URL de referência
     * @param metadata Metadados opcionais
     * @return Sessão válida
     */
    suspend fun getSession(
        domain: String,
        referer: String,
        metadata: SessionMetadata = SessionMetadata()
    ): SessionData {
        val cacheKey = generateCacheKey(domain, metadata)
        
        // 1. Verificar cache em memória
        memoryCache[cacheKey]?.let { cached ->
            if (cached.isValid()) {
                Log.d(TAG, "✅ Cache HIT (memória) para: $domain")
                metrics.cacheHits++
                return cached
            }
        }
        
        // 2. Verificar cache persistente
        loadFromPrefs(cacheKey)?.let { cached ->
            if (cached.isValid()) {
                Log.d(TAG, "✅ Cache HIT (disco) para: $domain")
                memoryCache[cacheKey] = cached
                metrics.cacheHits++
                return cached
            }
        }
        
        // 3. Criar nova sessão
        Log.d(TAG, "❌ Cache MISS para: $domain")
        metrics.cacheMisses++
        
        return createNewSession(domain, referer, metadata).also { session ->
            saveSession(cacheKey, session)
            metrics.creations++
        }
    }
    
    /**
     * Renova uma sessão expirada
     */
    suspend fun renewSession(
        domain: String,
        referer: String,
        metadata: SessionMetadata = SessionMetadata()
    ): SessionData {
        val cacheKey = generateCacheKey(domain, metadata)
        
        Log.d(TAG, "🔄 Renovando sessão para: $domain")
        
        // Invalidar cache antigo
        invalidateSession(cacheKey)
        
        // Criar nova
        return createNewSession(domain, referer, metadata).also { session ->
            saveSession(cacheKey, session)
            metrics.renewals++
        }
    }
    
    /**
     * Obtém headers com sessão válida
     */
    suspend fun getSessionHeaders(
        domain: String,
        referer: String,
        metadata: SessionMetadata = SessionMetadata()
    ): Map<String, String> {
        val session = getSession(domain, referer, metadata)
        
        return buildMap {
            // Headers da sessão
            putAll(session.headers)
            
            // Cookies
            if (session.cookies.isNotEmpty()) {
                put("Cookie", session.cookies.entries.joinToString("; ") { "${it.key}=${it.value}" })
            }
            
            // Tokens específicos
            session.tokens["csrf_token"]?.let { put("X-CSRF-Token", it) }
            session.tokens["api_key"]?.let { put("X-API-Key", it) }
            
            // Headers obrigatórios
            put("Referer", referer)
            put("User-Agent", USER_AGENTS.random())
            putAll(BYPASS_HEADERS)
        }
    }
    
    /**
     * Verifica se uma URL de vídeo ainda é válida
     */
    suspend fun isVideoUrlValid(
        videoUrl: String,
        session: SessionData,
        timeoutMs: Long = 5000
    ): Boolean {
        return try {
            val response = withTimeoutOrNull(timeoutMs) {
                app.head(
                    videoUrl,
                    headers = getHeadersForValidation(session),
                    timeout = 3
                )
            }
            
            response?.isSuccessful == true && 
            isValidContentType(response.headers["Content-Type"])
            
        } catch (e: Exception) {
            Log.d(TAG, "⚠️ Erro ao validar URL: ${e.message}")
            false
        }
    }
    
    /**
     * Retorna métricas atuais
     */
    fun getMetrics(): SessionMetrics = metrics
    
    /**
     * Limpa todo o cache
     */
    fun clearAllSessions() {
        memoryCache.clear()
        prefs.edit().clear().apply()
        Log.d(TAG, "🧹 Todo o cache limpo")
    }
    
    /**
     * Limpa sessões expiradas
     */
    fun cleanupExpiredSessions() {
        val now = System.currentTimeMillis()
        var cleaned = 0
        
        // Limpar memória
        memoryCache.entries.removeIf { (_, session) ->
            val expired = !session.isValid()
            if (expired) cleaned++
            expired
        }
        
        // Limpar disco
        prefs.all.forEach { (key, _) ->
            if (key.startsWith(KEY_PREFIX)) {
                loadFromPrefs(key.removePrefix(KEY_PREFIX))?.let { session ->
                    if (!session.isValid()) {
                        prefs.edit().remove(key).apply()
                        cleaned++
                    }
                }
            }
        }
        
        Log.d(TAG, "🧹 $cleaned sessões expiradas removidas")
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS PRIVADOS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Cria uma nova sessão via requisição HTTP
     */
    private suspend fun createNewSession(
        domain: String,
        referer: String,
        metadata: SessionMetadata
    ): SessionData = mutex.withLock {
        Log.d(TAG, "🆕 Criando nova sessão para: $domain")
        
        try {
            // Requisição inicial para obter cookies/tokens
            val response = app.get(
                "https://$domain/",
                headers = mapOf(
                    "Referer" to referer,
                    "User-Agent" to USER_AGENTS.random()
                ),
                timeout = 10
            )
            
            // Extrair cookies (converter Headers para Map)
            val headersMap = response.headers.toMultimap()
            val cookies = extractCookies(headersMap)
            
            // Extrair tokens do corpo
            val tokens = extractTokens(response.text)
            
            // Headers adicionais
            val headers = headersMap.mapValues { it.value.joinToString(", ") }
            
            SessionData(
                domain = domain,
                cookies = cookies,
                tokens = tokens,
                headers = headers,
                metadata = metadata
            ).also {
                Log.d(TAG, "✅ Sessão criada: ${cookies.size} cookies, ${tokens.size} tokens")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao criar sessão: ${e.message}")
            // Retornar sessão vazia em caso de erro
            SessionData(
                domain = domain,
                cookies = emptyMap(),
                tokens = emptyMap(),
                headers = emptyMap(),
                metadata = metadata
            )
        }
    }
    
    /**
     * Extrai cookies dos headers de resposta
     */
    private fun extractCookies(headers: Map<String, List<String>>): Map<String, String> {
        val cookies = mutableMapOf<String, String>()
        
        headers.filter { it.key.equals("Set-Cookie", ignoreCase = true) }
            .forEach { (_, values) ->
                values.forEach { cookie ->
                    val parts = cookie.split(";")[0].split("=", limit = 2)
                    if (parts.size == 2) {
                        cookies[parts[0].trim()] = parts[1].trim()
                    }
                }
            }
        
        return cookies
    }
    
    /**
     * Extrai tokens do HTML/JSON
     */
    private fun extractTokens(text: String): Map<String, String> {
        val tokens = mutableMapOf<String, String>()
        
        // CSRF token
        Regex("""csrf[_-]?token["']?\s*[:=]\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
            .find(text)?.let {
                tokens["csrf_token"] = it.groupValues[1]
            }
        
        // API key
        Regex("""api[_-]?key["']?\s*[:=]\s*["']([a-zA-Z0-9_-]{20,})["']""", RegexOption.IGNORE_CASE)
            .find(text)?.let {
                tokens["api_key"] = it.groupValues[1]
            }
        
        // JWT
        Regex("""eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*""")
            .find(text)?.let {
                tokens["jwt"] = it.value
            }
        
        // Bearer token
        Regex("""bearer\s+([a-zA-Z0-9_-]+)""", RegexOption.IGNORE_CASE)
            .find(text)?.let {
                tokens["bearer"] = it.groupValues[1]
            }
        
        return tokens
    }
    
    /**
     * Salva sessão em cache (memória + disco)
     */
    private fun saveSession(cacheKey: String, session: SessionData) {
        // Memória
        memoryCache[cacheKey] = session
        
        // Disco
        val json = sessionToJson(session)
        prefs.edit().putString(KEY_PREFIX + cacheKey, json).apply()
    }
    
    /**
     * Carrega sessão do cache persistente
     */
    private fun loadFromPrefs(cacheKey: String): SessionData? {
        val json = prefs.getString(KEY_PREFIX + cacheKey, null) ?: return null
        return try {
            jsonToSession(json)
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao carregar sessão: ${e.message}")
            null
        }
    }
    
    /**
     * Invalida uma sessão
     */
    private fun invalidateSession(cacheKey: String) {
        memoryCache.remove(cacheKey)
        prefs.edit().remove(KEY_PREFIX + cacheKey).apply()
    }
    
    /**
     * Gera chave de cache única
     */
    private fun generateCacheKey(domain: String, metadata: SessionMetadata): String {
        return "${domain}_${metadata.playerType}_${metadata.videoId}"
            .replace(".", "_")
            .replace(":", "_")
    }
    
    /**
     * Converte SessionData para JSON
     */
    private fun sessionToJson(session: SessionData): String {
        val json = JSONObject()
        json.put("domain", session.domain)
        json.put("cookies", JSONObject(session.cookies))
        json.put("tokens", JSONObject(session.tokens))
        json.put("headers", JSONObject(session.headers))
        json.put("timestamp", session.timestamp)
        json.put("ttlMinutes", session.ttlMinutes)
        json.put("playerType", session.metadata.playerType.name)
        json.put("videoId", session.metadata.videoId)
        json.put("slug", session.metadata.slug)
        return json.toString()
    }
    
    /**
     * Converte JSON para SessionData
     */
    private fun jsonToSession(json: String): SessionData {
        val obj = JSONObject(json)
        
        return SessionData(
            domain = obj.getString("domain"),
            cookies = jsonToMap(obj.optJSONObject("cookies")),
            tokens = jsonToMap(obj.optJSONObject("tokens")),
            headers = jsonToMap(obj.optJSONObject("headers")),
            timestamp = obj.optLong("timestamp", System.currentTimeMillis()),
            ttlMinutes = obj.optInt("ttlMinutes", 55),
            metadata = SessionMetadata(
                playerType = try {
                    SessionMetadata.PlayerType.valueOf(obj.optString("playerType", "UNKNOWN"))
                } catch (e: Exception) {
                    SessionMetadata.PlayerType.UNKNOWN
                },
                videoId = obj.optString("videoId", ""),
                slug = obj.optString("slug", "")
            )
        )
    }
    
    /**
     * Converte JSONObject para Map
     */
    private fun jsonToMap(json: JSONObject?): Map<String, String> {
        if (json == null) return emptyMap()
        
        return buildMap {
            json.keys().forEach { key ->
                put(key, json.optString(key, ""))
            }
        }
    }
    
    /**
     * Headers para validação de URL
     */
    private fun getHeadersForValidation(session: SessionData): Map<String, String> {
        return buildMap {
            putAll(session.headers)
            if (session.cookies.isNotEmpty()) {
                put("Cookie", session.cookies.entries.joinToString("; ") { "${it.key}=${it.value}" })
            }
            put("User-Agent", USER_AGENTS.random())
        }
    }
    
    /**
     * Valida Content-Type
     */
    private fun isValidContentType(contentType: String?): Boolean {
        if (contentType == null) return false
        
        return contentType.contains("video/") ||
               contentType.contains("application/x-mpegURL") ||
               contentType.contains("application/vnd.apple.mpegurl") ||
               contentType.contains("text/plain") ||
               contentType.contains("application/octet-stream")
    }
}

/**
 * Extensão para Context - obtém SessionManager singleton
 */
fun Context.sessionManager(): SessionManager {
    return SessionManager(this)
}
