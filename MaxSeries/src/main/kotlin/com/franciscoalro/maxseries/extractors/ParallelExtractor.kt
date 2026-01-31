package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import kotlinx.coroutines.*
import android.util.Log

/**
 * Extractor paralelo - executa múltiplos extractors simultaneamente
 * Retorna o primeiro resultado bem-sucedido
 */
class ParallelExtractor {
    companion object {
        private const val TAG = "ParallelExtractor"
        private const val TIMEOUT_MS = 8000L // 8 segundos máximo por extractor
        
        /**
         * Extrai URL de vídeo executando múltiplos extractors em paralelo
         * Retorna o primeiro resultado bem-sucedido
         */
        suspend fun extractParallel(
            sources: List<String>,
            referer: String?,
            subtitleCallback: (SubtitleFile) -> Unit,
            callback: (ExtractorLink) -> Unit
        ): Boolean {
            val startTime = System.currentTimeMillis()
            
            return coroutineScope {
                // Criar jobs para cada source
                val jobs = sources.map { source ->
                    async(Dispatchers.IO) {
                        try {
                            withTimeout(TIMEOUT_MS) {
                                extractFromSource(source, referer, subtitleCallback, callback)
                            }
                        } catch (e: TimeoutCancellationException) {
                            Log.w(TAG, "Timeout: $source")
                            false
                        } catch (e: Exception) {
                            Log.e(TAG, "Erro em $source: ${e.message}")
                            false
                        }
                    }
                }
                
                // Aguardar o primeiro resultado bem-sucedido
                var found = false
                for (job in jobs) {
                    if (job.await()) {
                        found = true
                        // Cancelar jobs pendentes
                        jobs.forEach { it.cancel() }
                        break
                    }
                }
                
                val duration = System.currentTimeMillis() - startTime
                Log.d(TAG, "Extração paralela: ${if (found) "SUCESSO" else "FALHA"} em ${duration}ms")
                
                found
            }
        }
        
        private suspend fun extractFromSource(
            source: String,
            referer: String?,
            subtitleCallback: (SubtitleFile) -> Unit,
            callback: (ExtractorLink) -> Unit
        ): Boolean {
            // Implementar lógica para cada tipo de servidor
            return when {
                source.contains("playerembedapi", ignoreCase = true) -> {
                    val extractor = PlayerEmbedAPIExtractor()
                    extractor.getUrl(source, referer, subtitleCallback, callback)
                    true
                }
                source.contains("megaembed", ignoreCase = true) -> {
                    val extractor = MegaEmbedExtractorV9()
                    extractor.getUrl(source, referer, subtitleCallback, callback)
                    true
                }
                source.contains("myvidplay", ignoreCase = true) -> {
                    val extractor = MyVidPlayExtractor()
                    extractor.getUrl(source, referer, subtitleCallback, callback)
                    true
                }
                // Adicionar outros extractors...
                else -> {
                    // Tentar loadExtractor do CloudStream
                    loadExtractor(source, referer, subtitleCallback, callback)
                    true
                }
            }
        }
    }
}
