package com.franciscoalro.maxseries.utils

import com.lagradost.cloudstream3.utils.Qualities

/**
 * Detector automático de qualidade de vídeo
 * Analisa URLs, nomes de arquivo e conteúdo M3U8 para determinar qualidade
 * 
 * Estratégias de detecção:
 * - Padrões em URLs (1080p, 720p, etc.)
 * - Resoluções em formato WxH (1920x1080, 1280x720)
 * - Parsing de playlists M3U8 com múltiplas qualidades
 * - Fallback inteligente para Unknown quando incerto
 */
object QualityDetector {
    
    /**
     * Padrões regex para detecção de qualidade
     */
    private val QUALITY_PATTERNS = mapOf(
        2160 to listOf(
            Regex("""2160p?""", RegexOption.IGNORE_CASE),
            Regex("""4k""", RegexOption.IGNORE_CASE),
            Regex("""3840x2160""", RegexOption.IGNORE_CASE),
            Regex("""uhd""", RegexOption.IGNORE_CASE)
        ),
        1080 to listOf(
            Regex("""1080p?""", RegexOption.IGNORE_CASE),
            Regex("""1920x1080""", RegexOption.IGNORE_CASE),
            Regex("""fhd""", RegexOption.IGNORE_CASE),
            Regex("""fullhd""", RegexOption.IGNORE_CASE)
        ),
        720 to listOf(
            Regex("""720p?""", RegexOption.IGNORE_CASE),
            Regex("""1280x720""", RegexOption.IGNORE_CASE),
            Regex("""hd""", RegexOption.IGNORE_CASE)
        ),
        480 to listOf(
            Regex("""480p?""", RegexOption.IGNORE_CASE),
            Regex("""854x480""", RegexOption.IGNORE_CASE),
            Regex("""640x480""", RegexOption.IGNORE_CASE),
            Regex("""sd""", RegexOption.IGNORE_CASE)
        ),
        360 to listOf(
            Regex("""360p?""", RegexOption.IGNORE_CASE),
            Regex("""640x360""", RegexOption.IGNORE_CASE)
        ),
        240 to listOf(
            Regex("""240p?""", RegexOption.IGNORE_CASE),
            Regex("""426x240""", RegexOption.IGNORE_CASE)
        )
    )
    
    /**
     * Detecta qualidade a partir de URL
     * 
     * @param url URL do vídeo/stream
     * @return Valor de qualidade (CloudStream Qualities.value)
     */
    fun detectFromUrl(url: String): Int {
        // Tentar detectar por padrões
        for ((quality, patterns) in QUALITY_PATTERNS) {
            if (patterns.any { it.containsMatchIn(url) }) {
                return quality
            }
        }
        
        // Fallback: Unknown
        return Qualities.Unknown.value
    }
    
    /**
     * Detecta qualidade a partir de nome de arquivo
     * 
     * @param filename Nome do arquivo
     * @return Valor de qualidade
     */
    fun detectFromFilename(filename: String): Int {
        return detectFromUrl(filename) // Mesma lógica
    }
    
    /**
     * Extrai múltiplas qualidades de playlist M3U8
     * 
     * Formato esperado:
     * #EXT-X-STREAM-INF:BANDWIDTH=...,RESOLUTION=1920x1080
     * https://example.com/1080p/playlist.m3u8
     * 
     * @param content Conteúdo do arquivo M3U8
     * @return Lista de pares (URL, Qualidade)
     */
    fun detectFromM3u8Content(content: String): List<Pair<String, Int>> {
        val results = mutableListOf<Pair<String, Int>>()
        val lines = content.lines()
        
        var currentQuality = Qualities.Unknown.value
        
        for (i in lines.indices) {
            val line = lines[i].trim()
            
            // Procurar por RESOLUTION em EXT-X-STREAM-INF
            if (line.startsWith("#EXT-X-STREAM-INF")) {
                currentQuality = extractQualityFromStreamInfo(line)
            }
            
            // Próxima linha não-comentada é a URL
            if (!line.startsWith("#") && line.isNotEmpty()) {
                // Se não detectou por RESOLUTION, tentar pela própria URL
                val quality = if (currentQuality == Qualities.Unknown.value) {
                    detectFromUrl(line)
                } else {
                    currentQuality
                }
                
                results.add(Pair(line, quality))
                currentQuality = Qualities.Unknown.value // Reset
            }
        }
        
        // Ordenar por qualidade (maior primeiro)
        return results.sortedByDescending { it.second }
    }
    
    /**
     * Extrai qualidade de linha EXT-X-STREAM-INF
     * 
     * @param line Linha do M3U8
     * @return Qualidade detectada
     */
    private fun extractQualityFromStreamInfo(line: String): Int {
        // Procurar por RESOLUTION=WxH
        val resolutionMatch = Regex("""RESOLUTION=(\d+)x(\d+)""").find(line)
        if (resolutionMatch != null) {
            val height = resolutionMatch.groupValues[2].toIntOrNull() ?: 0
            return height
        }
        
        // Fallback: procurar padrões na linha inteira
        return detectFromUrl(line)
    }
    
    /**
     * Converte valor numérico para Qualities do CloudStream
     * 
     * @param value Valor numérico de qualidade
     * @return Qualities correspondente
     */
    fun toCloudstreamQuality(value: Int): Int {
        return when (value) {
            2160 -> Qualities.P2160.value
            1080 -> Qualities.P1080.value
            720 -> Qualities.P720.value
            480 -> Qualities.P480.value
            360 -> Qualities.P360.value
            240 -> Qualities.P240.value
            else -> Qualities.Unknown.value
        }
    }
    
    /**
     * Obtém label legível para qualidade
     * 
     * @param quality Valor de qualidade
     * @return String formatada (ex: "1080p")
     */
    fun getQualityLabel(quality: Int): String {
        return when (quality) {
            Qualities.P2160.value, 2160 -> "2160p (4K)"
            Qualities.P1080.value, 1080 -> "1080p (Full HD)"
            Qualities.P720.value, 720 -> "720p (HD)"
            Qualities.P480.value, 480 -> "480p (SD)"
            Qualities.P360.value, 360 -> "360p"
            Qualities.P240.value, 240 -> "240p"
            else -> "Unknown"
        }
    }
    
    /**
     * Detecta melhor qualidade de lista de URLs
     * 
     * @param urls Lista de URLs
     * @return Par de (URL, Qualidade) com melhor qualidade
     */
    fun detectBestQuality(urls: List<String>): Pair<String, Int>? {
        return urls
            .map { url -> Pair(url, detectFromUrl(url)) }
            .maxByOrNull { it.second }
    }
    
    /**
     * Verifica se qualidade é HD ou superior
     * 
     * @param quality Valor de qualidade
     * @return true se >= 720p
     */
    fun isHdOrBetter(quality: Int): Boolean {
        return quality >= 720
    }
    
    /**
     * Verifica se qualidade é Full HD ou superior
     * 
     * @param quality Valor de qualidade
     * @return true se >= 1080p
     */
    fun isFullHdOrBetter(quality: Int): Boolean {
        return quality >= 1080
    }
}
