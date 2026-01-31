package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import com.franciscoalro.maxseries.utils.*
import android.util.Log
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.util.zip.GZIPInputStream

/**
 * PlayerEmbedAPI Extractor v4.4 - LATIN-1 FIX (Jan 2026)
 * 
 * v4.4 Changes (30 Jan 2026):
 * - 🔧 CORRECAO: Usa ISO-8859-1 (Latin-1) para preservar bytes 0x00-0xFF
 * - 🎯 Extracao manual do campo 'media' via regex para evitar problemas de JSON
 * - 🐍 PORTE: Equivalente ao bytes(string, 'latin-1') do Python
 * 
 * v4.3 Changes (30 Jan 2026):
 * - 🔧 Suporte a HTML gzipado (detecta e descompacta automaticamente)
 * - 🎯 Múltiplos padrões de regex para encontrar base64 'datas'
 * 
 * v4.0 Changes (30 Jan 2026):
 * - 🐍 PORTE: Algoritmo AES-CTR do PlayerEmbedAPI portado do Python
 * - 🎯 MULTI-QUALITY: Suporte a 360p, 720p, 1080p simultâneos
 * - 🚀 FALLBACK: Múltiplos métodos de extração
 * - ⚡ CACHE: Cache por qualidade individual
 */
class PlayerEmbedAPIExtractor : ExtractorApi() {
    override var name = "PlayerEmbedAPI"
    override var mainUrl = "https://playerembedapi.link"
    override val requiresReferer = true

    companion object {
        private const val TAG = "PlayerEmbedAPI"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        
        // Mapeamento de res_id para qualidade
        private val RES_ID_QUALITY = mapOf(
            2 to Qualities.P360,
            4 to Qualities.P720,
            5 to Qualities.P1080
        )
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        val startTime = System.currentTimeMillis()
        
        Log.wtf(TAG, "=== PlayerEmbedAPI v4.4 - Latin-1 Fix ===")
        Log.d(TAG, "URL: $url")
        
        // 1. VERIFICAR CACHE
        val cached = VideoUrlCache.get(url)
        if (cached != null) {
            Log.d(TAG, "✅ Cache HIT")
            
            callback.invoke(
                newExtractorLink(
                    source = name,
                    name = "$name ${QualityDetector.getQualityLabel(cached.quality)} (Cached)",
                    url = cached.url,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = "https://playerembedapi.link/"
                    this.quality = cached.quality
                }
            )
            return
        }
        
        // 2. BUSCAR HTML
        val html = try {
            val response = app.get(url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language" to "en-US,en;q=0.5",
                    "Referer" to (referer ?: mainUrl)
                )
            )
            response.text
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no request: ${e.message}")
            return
        }
        
        Log.d(TAG, "HTML recebido: ${html.length} chars")
        
        // 3. ENCONTRAR base64 'datas'
        Log.d(TAG, "Procurando base64 'datas'...")
        val base64Data = findBase64Datas(html)
        
        if (base64Data == null) {
            Log.e(TAG, "❌ Nao encontrou base64 'datas'")
            return
        }
        
        Log.d(TAG, "Base64 encontrado: ${base64Data.take(50)}...")
        
        // 4. DECODIFICAR E DECRIPTAR (v4.4 - ISO-8859-1 FIX)
        try {
            // Decodificar base64 -> bytes (igual ao Python)
            val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
            
            // Converter bytes para String usando ISO-8859-1 (Latin-1)
            // Isso preserva valores 0x00-0xFF 1:1 (equivalente ao Python bytes(string, 'latin-1'))
            val decodedString = String(decodedBytes, Charsets.ISO_8859_1)
            
            Log.d(TAG, "Decoded string length: ${decodedString.length}")
            
            // Extrair campos simples via regex
            val userIdRegex = """"user_id"\s*:\s*(\d+)""".toRegex()
            val slugRegex = """"slug"\s*:\s*"([^"]+)"""".toRegex()
            val md5IdRegex = """"md5_id"\s*:\s*(\d+)""".toRegex()
            
            val userId = userIdRegex.find(decodedString)?.groupValues?.get(1)
            val slug = slugRegex.find(decodedString)?.groupValues?.get(1)
            val md5Id = md5IdRegex.find(decodedString)?.groupValues?.get(1)
            
            // Extrair campo 'media' - contem dados binarios criptografados
            // Usa regex para pegar conteudo entre aspas
            val mediaRegex = """"media"\s*:\s*"((?:[^"\\\\]|\\\\.)*)"""".toRegex()
            val mediaMatch = mediaRegex.find(decodedString)
            val mediaEscaped = mediaMatch?.groupValues?.get(1)
            
            if (mediaEscaped == null) {
                Log.e(TAG, "❌ Nao encontrou campo 'media'")
                return
            }
            
            // Processar escapes JSON e converter para ByteArray
            // Cada caractere no resultado representa um byte (0-255)
            val mediaBytes = processJsonStringToBytes(mediaEscaped)
            
            Log.d(TAG, "=== Campos extraidos ===")
            Log.d(TAG, "   userId: $userId")
            Log.d(TAG, "   slug: $slug")
            Log.d(TAG, "   md5Id: $md5Id")
            Log.d(TAG, "   media: ${mediaEscaped.length} chars escapados -> ${mediaBytes.size} bytes")
            Log.d(TAG, "   media first 20 bytes (hex): ${mediaBytes.take(20).joinToString(" ") { "%02x".format(it) }}")
            
            if (userId == null || slug == null || md5Id == null || mediaBytes.isEmpty()) {
                Log.w(TAG, "⚠️ Campos obrigatorios faltantes")
                return
            }
            
            Log.d(TAG, "🔓 Decriptando media com AES-CTR...")
            val decrypted = LinkDecryptor.decryptPlayerEmbedMedia(mediaBytes, userId, slug, md5Id)
            
            if (decrypted == null) {
                Log.e(TAG, "❌ Falha na decriptacao AES-CTR")
                return
            }
            
            // 5. EXTRAIR URLs
            var foundAny = false
            
            // Extrair multiplas qualidades do sources[]
            decrypted.sources?.let { sources ->
                Log.d(TAG, "📺 Encontradas ${sources.size} fontes:")
                
                sources.forEachIndexed { index, source ->
                    Log.d(TAG, "   [$index] ${source.label} - ${source.file.take(60)}...")
                    
                    val quality = when (source.label) {
                        "360p" -> Qualities.P360
                        "720p" -> Qualities.P720
                        "1080p" -> Qualities.P1080
                        else -> Qualities.Unknown
                    }
                    
                    VideoUrlCache.put("${url}_${source.label}", source.file, quality.value, name)
                    
                    callback.invoke(
                        newExtractorLink(
                            source = name,
                            name = "$name ${source.label ?: "Auto"}",
                            url = source.file,
                            type = ExtractorLinkType.VIDEO
                        ) {
                            this.referer = "https://playerembedapi.link/"
                            this.quality = quality.value
                        }
                    )
                    foundAny = true
                }
            }
            
            // Fallback: HLS direto
            decrypted.hls?.let { hlsUrl ->
                Log.d(TAG, "📺 HLS: ${hlsUrl.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(hlsUrl)
                VideoUrlCache.put(url, hlsUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (HLS)",
                        url = hlsUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
            
            // Fallback: MP4 direto
            decrypted.mp4?.let { mp4Url ->
                Log.d(TAG, "📺 MP4: ${mp4Url.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(mp4Url)
                VideoUrlCache.put(url, mp4Url, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (MP4)",
                        url = mp4Url,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                foundAny = true
            }
            
            if (foundAny) {
                Log.wtf(TAG, "✅✅✅ SUCESSO: ${System.currentTimeMillis() - startTime}ms ✅✅✅")
            } else {
                Log.w(TAG, "⚠️ Nenhuma URL encontrada no JSON decriptado")
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro no processamento: ${e.message}")
            e.printStackTrace()
        }
    }
    
    /**
     * Processa uma string JSON escapada e retorna os bytes correspondentes
     * Equivalente ao Python: bytes(string, 'latin-1')
     * 
     * Cada caractere Unicode (0-255) no resultado vira um byte
     */
    private fun processJsonStringToBytes(escaped: String): ByteArray {
        val result = java.io.ByteArrayOutputStream()
        var i = 0
        
        while (i < escaped.length) {
            if (escaped[i] == '\\' && i + 1 < escaped.length) {
                when (escaped[i + 1]) {
                    '"' -> { result.write(0x22); i += 2 }
                    '\\' -> { result.write(0x5C); i += 2 }
                    '/' -> { result.write(0x2F); i += 2 }
                    'b' -> { result.write(0x08); i += 2 }
                    'f' -> { result.write(0x0C); i += 2 }
                    'n' -> { result.write(0x0A); i += 2 }
                    'r' -> { result.write(0x0D); i += 2 }
                    't' -> { result.write(0x09); i += 2 }
                    'u' -> {
                        // \uXXXX -> converte para byte (low byte do Unicode)
                        if (i + 5 < escaped.length) {
                            val hex = escaped.substring(i + 2, i + 6)
                            try {
                                val code = hex.toInt(16)
                                result.write(code and 0xFF)  // Apenas o byte baixo
                            } catch (e: Exception) {
                                result.write(0x5C); result.write(0x75)
                            }
                            i += 6
                        } else {
                            result.write(escaped[i].code); i++
                        }
                    }
                    else -> {
                        // \x -> apenas x
                        result.write(escaped[i + 1].code)
                        i += 2
                    }
                }
            } else {
                // Caractere normal: converte diretamente para byte
                // ISO-8859-1 garante que char.code esta entre 0-255
                result.write(escaped[i].code and 0xFF)
                i++
            }
        }
        
        return result.toByteArray()
    }
    
    /**
     * v4.3: Procura base64 'datas' com múltiplos padrões
     */
    private fun findBase64Datas(html: String): String? {
        val patterns = listOf(
            // Padrão 1: const datas = "..."
            Regex("""const\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 2: var datas = "..."
            Regex("""var\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 3: let datas = "..."
            Regex("""let\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 4: datas = "..." (sem const/var)
            Regex("""datas\s*=\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 5: data="..." (atributo)
            Regex("""data[=:]\s*"([A-Za-z0-9+/=]{200,})"""),
            // Padrão 6: Qualquer string base64 grande que comece com eyJ (eyJ = {")
            Regex(""""(eyJ[A-Za-z0-9+/=]{100,})"""),
        )
        
        for ((index, pattern) in patterns.withIndex()) {
            val match = pattern.find(html)
            if (match != null) {
                val candidate = match.groupValues[1]
                // Validar se é base64 válido
                try {
                    android.util.Base64.decode(candidate, android.util.Base64.DEFAULT)
                    Log.d(TAG, "✅ Pattern $index funcionou! Base64 válido.")
                    return candidate
                } catch (e: Exception) {
                    Log.d(TAG, "⚠️ Pattern $index encontrou match mas não é base64 válido")
                    continue
                }
            }
        }
        
        return null
    }
    
    /**
     * Fallback: Extrair URLs direto do HTML via regex
     */
    private suspend fun tryRegexFallback(
        html: String, 
        url: String, 
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "[3/5] Tentando HTML Regex fallback...")
        
        val patterns = listOf(
            Regex(""""(https?://[^"]+\.sssrr\.org/[^"]+)"""),
            Regex(""""(https?://[^"]+\.m3u8[^"]*)"""),
            Regex("""file:\s*["']([^"']+\.m3u8[^"']*)["']"""),
            Regex("""src:\s*["']([^"']+\.m3u8[^"']*)["']"""),
        )
        
        for (pattern in patterns) {
            val match = pattern.find(html)
            if (match != null) {
                val videoUrl = match.groupValues[1]
                Log.d(TAG, "✅ Fallback encontrou URL: ${videoUrl.take(60)}...")
                
                val quality = QualityDetector.detectFromUrl(videoUrl)
                VideoUrlCache.put(url, videoUrl, quality, name)
                
                callback.invoke(
                    newExtractorLink(
                        source = name,
                        name = "$name ${QualityDetector.getQualityLabel(quality)} (Fallback)",
                        url = videoUrl,
                        type = ExtractorLinkType.VIDEO
                    ) {
                        this.referer = "https://playerembedapi.link/"
                        this.quality = quality
                    }
                )
                return
            }
        }
    }
}
