package com.franciscoalro.maxseries.utils

import kotlinx.coroutines.delay

/**
 * Utilitário para rate limiting de requisições
 * Evita bloqueios por requisições excessivas (padrão Vizer)
 * 
 * Estratégia de delays:
 * - A cada 5 requisições: 1 segundo
 * - A cada 10 requisições: 2 segundos  
 * - A cada 15 requisições: 3 segundos
 */
object RateLimiter {
    
    /**
     * Aplica delay baseado no índice da requisição
     * 
     * @param index Índice da requisição atual (0-based)
     * @param block Bloco de código a executar após delay
     */
    suspend fun withRateLimit(index: Int, block: suspend () -> Unit) {
        when {
            index % 15 == 5 -> delay(1000)
            index % 15 == 10 -> delay(2000)
            index % 15 == 0 && index != 0 -> delay(3000)
        }
        block()
    }
    
    /**
     * Processa lista de itens com rate limiting automático
     * 
     * @param T Tipo genérico do item
     * @param items Lista de itens para processar
     * @param processor Função que processa cada item
     */
    suspend fun <T> processWithRateLimit(
        items: List<T>,
        processor: suspend (T) -> Unit
    ) {
        items.forEachIndexed { index, item ->
            withRateLimit(index) {
                processor(item)
            }
        }
    }
    
    /**
     * Aplica delay customizado
     * 
     * @param delayMs Delay em milissegundos
     * @param block Bloco de código a executar
     */
    suspend fun withCustomDelay(delayMs: Long, block: suspend () -> Unit) {
        delay(delayMs)
        block()
    }
    
    /**
     * Processa lista com delay fixo entre itens
     * 
     * @param T Tipo genérico do item
     * @param items Lista de itens
     * @param delayMs Delay em milissegundos
     * @param processor Função processadora
     */
    suspend fun <T> processWithFixedDelay(
        items: List<T>,
        delayMs: Long,
        processor: suspend (T) -> Unit
    ) {
        items.forEach { item ->
            processor(item)
            delay(delayMs)
        }
    }
}
