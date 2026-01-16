package com.franciscoalro.maxseries.utils

import android.util.Log

/**
 * Logger centralizado com níveis e contexto estruturado
 * Facilita debugging em produção e análise de problemas
 * 
 * Features:
 * - Níveis de log estruturados (DEBUG, INFO, WARNING, ERROR)
 * - Contexto adicional para cada log
 * - Formatação consistente e legível
 * - Logs especializados para extractors
 * - Suporte a exceptions com stack trace
 */
object ErrorLogger {
    
    /**
     * Níveis de logging
     */
    enum class Level(val emoji: String, val priority: Int) {
        DEBUG("🔍", Log.DEBUG),
        INFO("ℹ️", Log.INFO),
        WARNING("⚠️", Log.WARN),
        ERROR("❌", Log.ERROR)
    }
    
    /**
     * Log genérico com contexto
     * 
     * @param tag Tag para filtrar logs
     * @param level Nível do log
     * @param message Mensagem principal
     * @param context Mapa de contexto adicional
     * @param error Exception associada (opcional)
     */
    fun log(
        tag: String,
        level: Level,
        message: String,
        context: Map<String, Any> = emptyMap(),
        error: Throwable? = null
    ) {
        val formattedMessage = buildString {
            append("${level.emoji} $message")
            
            if (context.isNotEmpty()) {
                append("\n")
                context.forEach { (key, value) ->
                    append("  ├─ $key: $value\n")
                }
            }
        }
        
        when (level.priority) {
            Log.DEBUG -> Log.d(tag, formattedMessage, error)
            Log.INFO -> Log.i(tag, formattedMessage, error)
            Log.WARN -> Log.w(tag, formattedMessage, error)
            Log.ERROR -> Log.e(tag, formattedMessage, error)
        }
    }
    
    /**
     * Log de extração de vídeo
     * Formato especializado para extractors
     * 
     * @param extractor Nome do extractor
     * @param url URL sendo extraída
     * @param success Se extração foi bem-sucedida
     * @param videoUrl URL do vídeo extraída (se sucesso)
     * @param quality Qualidade detectada (se sucesso)
     * @param error Exception (se falha)
     */
    fun logExtraction(
        extractor: String,
        url: String,
        success: Boolean,
        videoUrl: String? = null,
        quality: Int? = null,
        error: Throwable? = null
    ) {
        val level = if (success) Level.INFO else Level.ERROR
        val message = if (success) {
            "Extração bem-sucedida"
        } else {
            "Falha na extração"
        }
        
        val context = mutableMapOf<String, Any>(
            "Extractor" to extractor,
            "URL" to truncateUrl(url)
        )
        
        if (success && videoUrl != null) {
            context["VideoURL"] = truncateUrl(videoUrl)
        }
        
        if (success && quality != null) {
            context["Quality"] = QualityDetector.getQualityLabel(quality)
        }
        
        if (!success && error != null) {
            context["Error"] = error.message ?: "Unknown error"
        }
        
        log("MaxSeries-Extraction", level, message, context, error)
    }
    
    /**
     * Log de requisição HTTP
     * 
     * @param url URL da requisição
     * @param method Método HTTP (GET, POST, etc.)
     * @param statusCode Código de status HTTP
     * @param duration Duração da requisição em ms
     * @param error Exception (se falha)
     */
    fun logHttpRequest(
        url: String,
        method: String = "GET",
        statusCode: Int? = null,
        duration: Long? = null,
        error: Throwable? = null
    ) {
        val success = statusCode != null && statusCode in 200..299
        val level = when {
            error != null -> Level.ERROR
            success -> Level.DEBUG
            else -> Level.WARNING
        }
        
        val message = if (success) {
            "Requisição HTTP bem-sucedida"
        } else {
            "Falha na requisição HTTP"
        }
        
        val context = mutableMapOf<String, Any>(
            "Method" to method,
            "URL" to truncateUrl(url)
        )
        
        statusCode?.let { context["StatusCode"] = it }
        duration?.let { context["Duration"] = "${it}ms" }
        error?.let { context["Error"] = it.message ?: "Unknown error" }
        
        log("MaxSeries-HTTP", level, message, context, error)
    }
    
    /**
     * Log de cache hit/miss
     * 
     * @param key Chave do cache
     * @param hit Se foi cache hit ou miss
     * @param stats Estatísticas do cache (opcional)
     */
    fun logCache(
        key: String,
        hit: Boolean,
        stats: VideoUrlCache.CacheStats? = null
    ) {
        val level = Level.DEBUG
        val message = if (hit) "Cache HIT ✅" else "Cache MISS"
        
        val context = mutableMapOf<String, Any>(
            "Key" to truncateUrl(key),
            "Result" to if (hit) "Hit" else "Miss"
        )
        
        stats?.let {
            context["HitRate"] = String.format("%.1f%%", it.hitRate * 100)
            context["TotalEntries"] = it.totalEntries
        }
        
        log("MaxSeries-Cache", level, message, context)
    }
    
    /**
     * Log de retry
     * 
     * @param operation Nome da operação
     * @param attempt Tentativa atual
     * @param maxAttempts Total de tentativas
     * @param nextDelayMs Delay até próxima tentativa (se aplicável)
     * @param error Exception da tentativa falha
     */
    fun logRetry(
        operation: String,
        attempt: Int,
        maxAttempts: Int,
        nextDelayMs: Long? = null,
        error: Throwable? = null
    ) {
        val level = Level.WARNING
        val message = "Retry $attempt/$maxAttempts"
        
        val context = mutableMapOf<String, Any>(
            "Operation" to operation,
            "Attempt" to "$attempt/$maxAttempts"
        )
        
        nextDelayMs?.let { context["NextRetryIn"] = "${it}ms" }
        error?.let { context["Error"] = it.message ?: "Unknown error" }
        
        log("MaxSeries-Retry", level, message, context, error)
    }
    
    /**
     * Log de qualidade detectada
     * 
     * @param url URL analisada
     * @param quality Qualidade detectada
     * @param source Fonte da detecção (URL, M3U8, etc.)
     */
    fun logQualityDetection(
        url: String,
        quality: Int,
        source: String = "URL"
    ) {
        val level = Level.DEBUG
        val message = "Qualidade detectada"
        
        val context = mapOf(
            "URL" to truncateUrl(url),
            "Quality" to QualityDetector.getQualityLabel(quality),
            "Source" to source
        )
        
        log("MaxSeries-Quality", level, message, context)
    }
    
    /**
     * Log de performance
     * 
     * @param operation Nome da operação
     * @param durationMs Duração em ms
     * @param details Detalhes adicionais
     */
    fun logPerformance(
        operation: String,
        durationMs: Long,
        details: Map<String, Any> = emptyMap()
    ) {
        val level = if (durationMs > 5000) Level.WARNING else Level.DEBUG
        val message = "Performance: $operation"
        
        val context = mutableMapOf<String, Any>(
            "Duration" to "${durationMs}ms",
            "Operation" to operation
        )
        context.putAll(details)
        
        log("MaxSeries-Performance", level, message, context)
    }
    
    /**
     * Trunca URL muito longa para melhor legibilidade
     * 
     * @param url URL completa
     * @param maxLength Tamanho máximo
     * @return URL truncada
     */
    private fun truncateUrl(url: String, maxLength: Int = 80): String {
        return if (url.length > maxLength) {
            url.take(maxLength - 3) + "..."
        } else {
            url
        }
    }
    
    /**
     * Log debug simplificado
     */
    fun d(tag: String, message: String, context: Map<String, Any> = emptyMap()) {
        log(tag, Level.DEBUG, message, context)
    }
    
    /**
     * Log info simplificado
     */
    fun i(tag: String, message: String, context: Map<String, Any> = emptyMap()) {
        log(tag, Level.INFO, message, context)
    }
    
    /**
     * Log warning simplificado
     */
    fun w(tag: String, message: String, context: Map<String, Any> = emptyMap(), error: Throwable? = null) {
        log(tag, Level.WARNING, message, context, error)
    }
    
    /**
     * Log error simplificado
     */
    fun e(tag: String, message: String, context: Map<String, Any> = emptyMap(), error: Throwable? = null) {
        log(tag, Level.ERROR, message, context, error)
    }
}
