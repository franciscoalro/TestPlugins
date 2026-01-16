package com.franciscoalro.maxseries.utils

import kotlinx.coroutines.delay
import android.util.Log

/**
 * Utilitário para retry de operações com backoff exponencial
 * Aumenta confiabilidade do plugin em caso de falhas temporárias de rede
 * 
 * Estratégias implementadas:
 * - Backoff exponencial (delays crescentes)
 * - Retry condicional (apenas para erros recuperáveis)
 * - Logging

 detalhado de tentativas
 * - Limite de tentativas configurável
 */
object RetryHelper {
    private const val TAG = "RetryHelper"
    
    /**
     * Executa bloco de código com retry automático
     * 
     * @param T Tipo de retorno
     * @param maxAttempts Número máximo de tentativas (padrão: 3)
     * @param initialDelayMs Delay inicial em ms (padrão: 500ms)
     * @param maxDelayMs Delay máximo em ms (padrão: 3000ms)
     * @param factor Fator de multiplicação do delay (padrão: 2.0)
     * @param shouldRetry Função que determina se deve tentar novamente baseado na exceção
     * @param block Bloco de código a executar
     * @return Resultado do bloco se bem-sucedido
     * @throws Exception Se todas as tentativas falharem
     */
    suspend fun <T> withRetry(
        maxAttempts: Int = 3,
        initialDelayMs: Long = 500,
        maxDelayMs: Long = 3000,
        factor: Double = 2.0,
        shouldRetry: (Exception) -> Boolean = ::isRetriableError,
        block: suspend (attempt: Int) -> T
    ): T {
        var currentDelay = initialDelayMs
        var lastException: Exception? = null
        
        repeat(maxAttempts) { attempt ->
            try {
                Log.d(TAG, "Tentativa ${attempt + 1}/$maxAttempts")
                return block(attempt + 1)
            } catch (e: Exception) {
                lastException = e
                
                // Verificar se deve fazer retry
                if (!shouldRetry(e)) {
                    Log.w(TAG, "❌ Erro não recuperável, abortando retry: ${e.message}")
                    throw e
                }
                
                // Última tentativa, não fazer delay
                if (attempt == maxAttempts - 1) {
                    Log.e(TAG, "❌ Todas as $maxAttempts tentativas falharam")
                    throw e
                }
                
                Log.w(TAG, "⚠️ Tentativa ${attempt + 1} falhou: ${e.message}. Tentando novamente em ${currentDelay}ms...")
                delay(currentDelay)
                
                // Aumentar delay exponencialmente
                currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMs)
            }
        }
        
        // Fallback: nunca deve chegar aqui, mas para satisfazer compilador
        throw lastException ?: Exception("Erro desconhecido no retry")
    }
    
    /**
     * Variante simplificada com delay fixo
     * 
     * @param T Tipo de retorno
     * @param maxAttempts Número máximo de tentativas
     * @param fixedDelayMs Delay fixo entre tentativas
     * @param block Bloco a executar
     * @return Resultado do bloco
     */
    suspend fun <T> withFixedRetry(
        maxAttempts: Int = 3,
        fixedDelayMs: Long = 1000,
        block: suspend (attempt: Int) -> T
    ): T {
        return withRetry(
            maxAttempts = maxAttempts,
            initialDelayMs = fixedDelayMs,
            factor = 1.0, // Sem crescimento
            block = block
        )
    }
    
    /**
     * Determina se erro é recuperável e deve tentar novamente
     * 
     * Erros recuperáveis:
     * - Timeout
     * - Connection refused/reset
     * - Unknown host (pode ser DNS temporário)
     * - Socket exceptions
     * 
     * Erros não recuperáveis:
     * - 404 Not Found
     * - 400 Bad Request
     * - 401 Unauthorized
     * - Parse errors
     * 
     * @param error Exceção capturada
     * @return true se deve tentar novamente
     */
    private fun isRetriableError(error: Exception): Boolean {
        val message = error.message?.lowercase() ?: ""
        
        // Erros de rede recuperáveis
        val retriable = listOf(
            "timeout",
            "timed out",
            "connection refused",
            "connection reset",
            "socket",
            "unknown host",
            "unable to resolve host",
            "network",
            "503", // Service Unavailable
            "502", // Bad Gateway
            "504"  // Gateway Timeout
        )
        
        // Erros não recuperáveis
        val nonRetriable = listOf(
            "404",
            "400",
            "401",
            "403", // Forbidden
            "parse",
            "json",
            "illegal"
        )
        
        // Verificar se é erro não recuperável
        if (nonRetriable.any { message.contains(it) }) {
            return false
        }
        
        // Verificar se é erro recuperável
        return retriable.any { message.contains(it) }
    }
    
    /**
     * Wrapper para requisições HTTP com retry
     * Uso específico para extractors
     * 
     * @param T Tipo de retorno
     * @param url URL da requisição
     * @param maxAttempts Máximo de tentativas
     * @param block Bloco de requisição
     * @return Resultado da requisição
     */
    suspend fun <T> httpRequest(
        url: String,
        maxAttempts: Int = 3,
        block: suspend (attempt: Int) -> T
    ): T {
        Log.d(TAG, "🌐 Requisição HTTP com retry: $url")
        return withRetry(maxAttempts = maxAttempts) { attempt ->
            try {
                block(attempt)
            } catch (e: Exception) {
                Log.w(TAG, "⚠️ Falha na requisição (tentativa $attempt): ${e.message}")
                throw e
            }
        }
    }
    
    /**
     * Calcula delay para tentativa específica
     * Útil para visualização/logging
     * 
     * @param attempt Número da tentativa (1-indexed)
     * @param initialDelay Delay inicial
     * @param factor Fator de crescimento
     * @param maxDelay Delay máximo
     * @return Delay calculado em ms
     */
    fun calculateDelay(
        attempt: Int,
        initialDelay: Long = 500,
        factor: Double = 2.0,
        maxDelay: Long = 3000
    ): Long {
        val delay = (initialDelay * Math.pow(factor, (attempt - 1).toDouble())).toLong()
        return delay.coerceAtMost(maxDelay)
    }
}
