package com.franciscoalro.maxseries.utils

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.extractors.*
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import android.util.Log

/**
 * Gerenciador de Pre-fetching de URLs de vídeo
 * 
 * Carrega URLs em background assim que o usuário abre a página de episódios,
 * garantindo reprodução instantânea quando clicar para assistir.
 * 
 * Features:
 * - Pre-fetching paralelo com limite de concorrência
 * - Cache inteligente usando VideoUrlCache
 * - Priorização de servidores (mais rápidos primeiro)
 * - Cancelamento automático de jobs antigos
 * - Timeout configurável por servidor
 */
object PreFetchManager {
    private const val TAG = "PreFetchManager"
    
    // Configurações
    private const val MAX_CONCURRENT_PREFETCH = 3 // Máximo de requisições simultâneas
    private const val PREFETCH_TIMEOUT_MS = 15_000L // Timeout por episódio
    private const val MAX_PREFETCH_QUEUE = 20 // Máximo de episódios na fila
    
    // Scope para coroutines de background
    private val prefetchScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    // Semáforo para limitar concorrência
    private val semaphore = Semaphore(MAX_CONCURRENT_PREFETCH)
    
    // Cache de jobs em andamento (evita duplicatas)
    private val activeJobs = ConcurrentHashMap<String, Job>()
    
    // Estatísticas
    private val stats = PreFetchStats()
    
    /**
     * Estatísticas de pre-fetching
     */
    data class PreFetchStats(
        var totalRequested: Int = 0,
        var totalCompleted: Int = 0,
        var totalFailed: Int = 0,
        var totalCached: Int = 0,
        var averageTimeMs: Long = 0
    ) {
        private val timeMeasurements = mutableListOf<Long>()
        
        @Synchronized
        fun recordSuccess(timeMs: Long) {
            totalCompleted++
            timeMeasurements.add(timeMs)
            if (timeMeasurements.size > 100) timeMeasurements.removeAt(0)
            averageTimeMs = timeMeasurements.average().toLong()
        }
        
        @Synchronized
        fun recordFailed() {
            totalFailed++
        }
        
        @Synchronized
        fun recordCached() {
            totalCached++
        }
        
        @Synchronized
        fun getStats(): PreFetchStats = this.copy()
    }
    
    /**
     * Inicia pre-fetching de múltiplos episódios em paralelo
     * Chamado quando o usuário abre a página de episódios
     * 
     * @param episodes Lista de dados dos episódios (formato: "url|episodio|episodeId|seasonId" ou URL direta)
     * @param referer URL de referência para os requests
     */
    fun prefetchEpisodes(
        episodes: List<String>,
        referer: String? = null
    ) {
        if (episodes.isEmpty()) return
        
        // Limitar tamanho da fila
        val episodesToProcess = episodes.take(MAX_PREFETCH_QUEUE)
        
        Log.d(TAG, "🚀 Iniciando pre-fetching de ${episodesToProcess.size}/${episodes.size} episódios")
        stats.totalRequested += episodesToProcess.size
        
        episodesToProcess.forEach { episodeData ->
            val key = generateKey(episodeData)
            
            // Evita duplicatas
            if (activeJobs.containsKey(key)) {
                Log.d(TAG, "⏭️ Job já existe para: $key")
                return@forEach
            }
            
            // Já está no cache?
            if (VideoUrlCache.contains(key)) {
                Log.d(TAG, "💾 Já em cache: $key")
                stats.recordCached()
                return@forEach
            }
            
            // Cria novo job de pre-fetch
            val job = prefetchScope.launch {
                semaphore.withPermit {
                    try {
                        withTimeout(PREFETCH_TIMEOUT_MS) {
                            prefetchSingleEpisode(episodeData, referer)
                        }
                    } catch (e: TimeoutCancellationException) {
                        Log.w(TAG, "⏱️ Timeout no pre-fetch: $key")
                        stats.recordFailed()
                    } catch (e: CancellationException) {
                        Log.d(TAG, "🛑 Pre-fetch cancelado: $key")
                    } catch (e: Exception) {
                        Log.w(TAG, "❌ Pre-fetch falhou para $key: ${e.message}")
                        stats.recordFailed()
                    } finally {
                        activeJobs.remove(key)
                    }
                }
            }
            
            activeJobs[key] = job
        }
        
        logStats()
    }
    
    /**
     * Faz pre-fetch de um único episódio
     */
    private suspend fun prefetchSingleEpisode(
        episodeData: String,
        referer: String?
    ) {
        val startTime = System.currentTimeMillis()
        val key = generateKey(episodeData)
        
        Log.d(TAG, "⏳ Pre-fetching: $key")
        
        // Parse dos dados do episódio
        val (playerthreeUrl, episodeId, seasonId) = parseEpisodeData(episodeData)
        
        // Construir URL do episódio
        val episodeUrl = if (episodeId != null) {
            "https://playerthree.online/episodio/$episodeId"
        } else {
            playerthreeUrl
        }
        
        // Buscar página do episódio
        val html = try {
            val response = app.get(
                episodeUrl,
                headers = HeadersBuilder.standard(referer ?: playerthreeUrl),
                timeout = 10_000L
            )
            response.text
        } catch (e: Exception) {
            Log.w(TAG, "Falha ao obter página: ${e.message}")
            return
        }
        
        // Extrair sources
        val sources = extractSourcesFromHtml(html)
        
        if (sources.isEmpty()) {
            Log.w(TAG, "Nenhuma source encontrada para: $key")
            return
        }
        
        Log.d(TAG, "📊 ${sources.size} sources encontradas para: $key")
        
        // Tentar extrair de cada source (priorizando os mais rápidos)
        var found = false
        for (source in sortSourcesByPriority(sources)) {
            if (found) break
            
            try {
                found = tryExtractSource(source, episodeUrl, key)
            } catch (e: Exception) {
                Log.d(TAG, "Extractor falhou para ${getSourceType(source)}: ${e.message}")
                continue
            }
        }
        
        if (found) {
            val elapsed = System.currentTimeMillis() - startTime
            stats.recordSuccess(elapsed)
            Log.d(TAG, "✅ Pre-fetch OK (${elapsed}ms): $key")
        } else {
            stats.recordFailed()
            Log.w(TAG, "❌ Todos os extractors falharam: $key")
        }
    }
    
    /**
     * Parse dos dados do episódio
     * Formato: "url|episodio|episodeId|seasonId" ou URL direta
     */
    private fun parseEpisodeData(data: String): Triple<String, String?, String?> {
        return if (data.contains("|episodio|")) {
            val parts = data.split("|episodio|")
            val playerthreeUrl = parts[0]
            val params = parts[1].split("|")
            val episodeId = params.getOrNull(0)
            val seasonId = params.getOrNull(1)
            Triple(playerthreeUrl, episodeId, seasonId)
        } else {
            Triple(data, null, null)
        }
    }
    
    /**
     * Extrai lista de sources do HTML
     */
    private fun extractSourcesFromHtml(html: String): List<String> {
        val sources = mutableListOf<String>()
        
        // Padrão 1: data-source="url"
        Regex("""data-source\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
            .findAll(html).forEach { match ->
                val url = match.groupValues[1].trim()
                if (url.startsWith("http") && !sources.contains(url)) {
                    sources.add(url)
                }
            }
        
        // Padrão 2: data-src="url"
        Regex("""data-src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
            .findAll(html).forEach { match ->
                val url = match.groupValues[1].trim()
                if (url.startsWith("http") && !sources.contains(url)) {
                    sources.add(url)
                }
            }
        
        // Padrão 3: href/src diretos
        val playerPatterns = listOf(
            Regex("""https?://playerembedapi\.link[^"'\s<>\)]+"""),
            Regex("""https?://myvidplay\.com[^"'\s<>\)]+"""),
            Regex("""https?://dood[a-z0-9]*\.[a-z]+/e/[^"'\s<>\)]+""", RegexOption.IGNORE_CASE),
            Regex("""https?://megaembed\.link/?#[a-zA-Z0-9]+"""),
            Regex("""https?://streamtape\.com/e/[^"'\s<>\)]+"""),
            Regex("""https?://mixdrop\.[a-z]+/e/[^"'\s<>\)]+"""),
            Regex("""https?://filemoon\.[a-z]+/e/[^"'\s<>\)]+""")
        )
        
        playerPatterns.forEach { pattern ->
            pattern.findAll(html).forEach { match ->
                val url = match.value.trim().trimEnd(')', '"', '\'', '<', '>')
                if (url.length > 15 && !sources.contains(url)) {
                    sources.add(url)
                }
            }
        }
        
        return sources.distinct()
    }
    
    /**
     * Ordena sources por prioridade (mais rápidos primeiro)
     */
    private fun sortSourcesByPriority(sources: List<String>): List<String> {
        return sources.sortedBy { source ->
            when {
                source.contains("myvidplay", ignoreCase = true) -> 1 // Mais rápido
                source.contains("playerembedapi", ignoreCase = true) -> 2
                source.contains("megaembed", ignoreCase = true) -> 3
                source.contains("streamtape", ignoreCase = true) -> 4
                source.contains("mixdrop", ignoreCase = true) -> 5
                source.contains("dood", ignoreCase = true) -> 6
                source.contains("filemoon", ignoreCase = true) -> 7
                else -> 99
            }
        }
    }
    
    /**
     * Retorna o tipo de source para logging
     */
    private fun getSourceType(source: String): String {
        return when {
            source.contains("myvidplay", ignoreCase = true) -> "MyVidPlay"
            source.contains("playerembedapi", ignoreCase = true) -> "PlayerEmbedAPI"
            source.contains("megaembed", ignoreCase = true) -> "MegaEmbed"
            source.contains("streamtape", ignoreCase = true) -> "StreamTape"
            source.contains("mixdrop", ignoreCase = true) -> "MixDrop"
            source.contains("dood", ignoreCase = true) -> "DoodStream"
            source.contains("filemoon", ignoreCase = true) -> "FileMoon"
            else -> "Unknown"
        }
    }
    
    /**
     * Tenta extrair URL de uma source
     * @return true se conseguiu extrair
     */
    private suspend fun tryExtractSource(
        source: String,
        referer: String,
        cacheKey: String
    ): Boolean {
        var extracted = false
        
        val extractor = getExtractorForSource(source) ?: return false
        
        try {
            withTimeout(8_000L) {
                extractor.getUrl(source, referer, { /* subtitle */ }) { link ->
                    if (!extracted) {
                        extracted = true
                        VideoUrlCache.put(cacheKey, link.url, link.quality, extractor.name)
                    }
                }
            }
        } catch (e: Exception) {
            Log.d(TAG, "Extractor ${extractor.name} falhou: ${e.message}")
        }
        
        return extracted
    }
    
    /**
     * Retorna o extractor apropriado para uma source
     */
    private fun getExtractorForSource(source: String): ExtractorApi? {
        return when {
            source.contains("playerembedapi", ignoreCase = true) -> 
                PlayerEmbedAPIExtractor()
            source.contains("megaembed", ignoreCase = true) -> 
                MegaEmbedExtractorV9()
            source.contains("myvidplay", ignoreCase = true) -> 
                MyVidPlayExtractor()
            source.contains("dood", ignoreCase = true) -> 
                DoodStreamExtractor()
            source.contains("streamtape", ignoreCase = true) -> 
                StreamtapeExtractor()
            source.contains("mixdrop", ignoreCase = true) -> 
                MixdropExtractor()
            source.contains("filemoon", ignoreCase = true) -> 
                FilemoonExtractor()
            else -> null
        }
    }
    
    /**
     * Gera chave única para cache baseada nos dados do episódio
     */
    private fun generateKey(episodeData: String): String {
        return if (episodeData.contains("|episodio|")) {
            val parts = episodeData.split("|episodio|")
            val params = parts[1].split("|")
            "${params[0]}" // episodeId como chave
        } else {
            episodeData.hashCode().toString()
        }
    }
    
    /**
     * Cancela todos os jobs de pre-fetch ativos
     */
    fun cancelAll() {
        val count = activeJobs.size
        Log.d(TAG, "🛑 Cancelando $count jobs de pre-fetch")
        
        activeJobs.values().forEach { job ->
            job.cancel()
        }
        activeJobs.clear()
    }
    
    /**
     * Cancela pre-fetch de episódios específicos
     */
    fun cancelForEpisodes(episodeKeys: List<String>) {
        episodeKeys.forEach { key ->
            activeJobs[key]?.cancel()
            activeJobs.remove(key)
        }
    }
    
    /**
     * Verifica se um episódio já foi pré-carregado
     */
    fun isPrefetched(episodeData: String): Boolean {
        val key = generateKey(episodeData)
        return VideoUrlCache.contains(key)
    }
    
    /**
     * Obtém URL cacheada para um episódio
     */
    fun getCachedUrl(episodeData: String): VideoUrlCache.CachedUrl? {
        val key = generateKey(episodeData)
        return VideoUrlCache.get(key)
    }
    
    /**
     * Limpa jobs concluídos da lista de ativos
     */
    fun cleanupCompletedJobs() {
        val completed = activeJobs.filter { it.value.isCompleted }.keys
        completed.forEach { activeJobs.remove(it) }
        if (completed.isNotEmpty()) {
            Log.d(TAG, "🧹 Limpando ${completed.size} jobs concluídos")
        }
    }
    
    /**
     * Retorna estatísticas atuais
     */
    fun getStats(): PreFetchStats {
        return stats.getStats()
    }
    
    /**
     * Log das estatísticas
     */
    fun logStats() {
        val currentStats = stats.getStats()
        Log.d(TAG, """
            📊 PreFetch Stats:
            ├─ Requested: ${currentStats.totalRequested}
            ├─ Completed: ${currentStats.totalCompleted}
            ├─ Failed: ${currentStats.totalFailed}
            ├─ Cached: ${currentStats.totalCached}
            ├─ Active Jobs: ${activeJobs.size}
            └─ Avg Time: ${currentStats.averageTimeMs}ms
        """.trimIndent())
    }
    
    /**
     * Pre-fetch prioritário para o próximo episódio
     * Útil quando o usuário está assistindo um episódio
     */
    fun prefetchNextEpisode(currentEpisodeData: String, nextEpisodeData: String?) {
        if (nextEpisodeData == null) return
        
        // Cancela jobs de baixa prioridade
        if (activeJobs.size >= MAX_CONCURRENT_PREFETCH) {
            cleanupCompletedJobs()
        }
        
        // Prioriza o próximo episódio
        prefetchEpisodes(listOf(nextEpisodeData))
        
        Log.d(TAG, "⏭️ Pre-fetch prioritário para próximo episódio")
    }
    
    /**
     * Pre-fetch em batch para uma temporada inteira
     */
    fun prefetchSeason(episodes: List<String>, referer: String?) {
        Log.d(TAG, "📺 Pre-fetching temporada: ${episodes.size} episódios")
        prefetchEpisodes(episodes, referer)
    }
}

/**
 * ConcurrentHashMap simples para Kotlin (compatibilidade)
 */
class ConcurrentHashMap<K, V> {
    private val map = mutableMapOf<K, V>()
    private val lock = Any()
    
    operator fun get(key: K): V? = synchronized(lock) { map[key] }
    operator fun set(key: K, value: V) = synchronized(lock) { map[key] = value }
    fun remove(key: K): V? = synchronized(lock) { map.remove(key) }
    fun containsKey(key: K): Boolean = synchronized(lock) { map.containsKey(key) }
    val size: Int get() = synchronized(lock) { map.size }
    fun values(): Collection<V> = synchronized(lock) { map.values.toList() }
    fun filter(predicate: (Map.Entry<K, V>) -> Boolean): Map<K, V> = synchronized(lock) { map.filter(predicate) }
    fun clear() = synchronized(lock) { map.clear() }
}
