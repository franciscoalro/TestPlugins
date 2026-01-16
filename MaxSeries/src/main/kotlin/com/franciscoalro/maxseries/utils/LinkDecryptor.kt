package com.franciscoalro.maxseries.utils

import com.lagradost.cloudstream3.base64Decode
import java.net.URLDecoder

/**
 * Utilitário para decriptação de links
 * Implementa padrões de decriptação dos providers brasileiros (especialmente Vizer)
 */
object LinkDecryptor {
    
    /**
     * Decripta links usando Base64 + reversão (padrão Vizer)
     * 
     * Algoritmo:
     * 1. Remove prefixo "redirect/"
     * 2. Decodifica Base64
     * 3. Remove espaços
     * 4. Reverte string
     * 5. Pega últimos 5 caracteres e reverte
     * 6. Remove últimos 5 da string principal
     * 7. Concatena
     * 
     * @param encrypted String encriptada
     * @return String decriptada ou vazia se falhar
     */
    fun decryptBase64Reversed(encrypted: String): String {
        if (encrypted.isEmpty()) return ""
        
        return runCatching {
            var decoded = base64Decode(encrypted.replace("redirect/", ""))
            decoded = decoded.trim()
            decoded = decoded.reversed()
            val last = decoded.takeLast(5).reversed()
            decoded = decoded.dropLast(5)
            decoded + last
        }.getOrElse { "" }
    }
    
    /**
     * Extrai URL de parâmetro MediaFire (padrão FilmesOn)
     * 
     * Exemplo: "?url=https%3A%2F%2Fmediafire.com%2Ffile.mp4" 
     *       -> "https://mediafire.com/file.mp4"
     * 
     * @param apiUrl URL com parâmetro encriptado
     * @return URL decriptada ou null se não encontrar
     */
    fun decryptMediaFireUrl(apiUrl: String): String? {
        return RegexPatterns.urlParam("url")
            .find(apiUrl)?.groupValues?.get(1)
            ?.let { URLDecoder.decode(it, "UTF-8") }
    }
    
    /**
     * Extrai parâmetro de URL genérico
     * 
     * @param url URL completa
     * @param paramName Nome do parâmetro
     * @return Valor do parâmetro decodificado ou null
     */
    fun extractUrlParam(url: String, paramName: String): String? {
        return RegexPatterns.urlParam(paramName)
            .find(url)?.groupValues?.get(1)
            ?.let { URLDecoder.decode(it, "UTF-8") }
    }
    
    /**
     * Limpa URL removendo escape de barras
     * 
     * @param url URL com escapes
     * @return URL limpa
     */
    fun cleanUrl(url: String): String {
        return url.replace("\\/", "/")
    }
    
    /**
     * Valida se string é uma URL válida
     * 
     * @param text Texto para validar
     * @return true se for URL válida
     */
    fun isUrl(text: String): Boolean {
        return RegexPatterns.IS_URL.matches(text)
    }
    
    /**
     * Valida se URL é de vídeo
     * 
     * @param url URL para validar
     * @return true se for URL de vídeo
     */
    fun isVideoUrl(url: String): Boolean {
        return RegexPatterns.IS_VIDEO_URL.containsMatchIn(url)
    }
}
