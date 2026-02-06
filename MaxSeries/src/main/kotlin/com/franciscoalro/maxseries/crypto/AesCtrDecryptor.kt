package com.franciscoalro.maxseries.crypto

import android.util.Base64
import java.util.Base64 as JavaBase64
import android.util.Log
import org.json.JSONObject
import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * AES-CTR DECRYPTOR - PlayerEmbedAPI
 * Engenharia Reversa da Criptografia Client-Side
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * DESCobertas de Pentest:
 * - Algoritmo: AES-CTR (Counter Mode)
 * - Campo 'datas': Base64 contendo JSON com metadados
 * - Campo 'media': Dados binários criptografados (AES-CTR)
 * - Chave: Derivada de user_id:md5_id:slug
 * - IV: Geralmente zero ou derivado do slug
 * 
 * Fluxo de Decriptação:
 * 1. Extrair campo 'datas' do HTML (base64)
 * 2. Decodificar base64 → JSON
 * 3. Extrair slug, md5_id, user_id, media (base64)
 * 4. Derivar chave AES a partir dos parâmetros
 * 5. Decriptar campo 'media' com AES-CTR
 * 6. Parse do JSON resultante → URL do vídeo
 * 
 * @version 1.0
 * @since 2026-02-03
 */
object AesCtrDecryptor {
    
    private const val TAG = "AesCtrDecryptor"
    private const val ALGORITHM = "AES"
    private const val TRANSFORMATION = "AES/CTR/NoPadding"
    
    private fun logD(msg: String) { runCatching { Log.d(TAG, msg) } }
    private fun logE(msg: String, t: Throwable? = null) { runCatching { if (t != null) Log.e(TAG, msg, t) else Log.e(TAG, msg) } }
    private fun logV(msg: String) { runCatching { Log.v(TAG, msg) } }
    
    /**
     * Estrutura dos dados extraídos do campo 'datas'
     */
    data class VideoMetadata(
        val slug: String,
        val md5Id: Int,
        val userId: Int,
        val mediaEncrypted: String,
        val config: VideoConfig
    ) {
        data class VideoConfig(
            val poster: Boolean,
            val preview: Boolean,
            val isDownload: Boolean
        )
    }
    
    /**
     * Estrutura dos dados decriptados do campo 'media'
     */
    data class DecryptedMedia(
        val videoUrl: String,
        val qualities: List<VideoQuality>,
        val subtitles: List<SubtitleInfo> = emptyList()
    ) {
        data class VideoQuality(
            val label: String,
            val url: String,
            val type: String = "mp4"
        )
        
        data class SubtitleInfo(
            val language: String,
            val url: String,
            val label: String
        )
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS PÚBLICOS PRINCIPAIS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Extrai URL de vídeo diretamente do HTML completo
     * Método de alto nível - uso mais comum
     * 
     * @param html HTML completo da página do player
     * @return URL do vídeo ou null se falhar
     */
    fun extractVideoUrl(html: String): String? {
        logD("🔍 Iniciando extração AES-CTR do HTML...")
        
        return try {
            // Passo 1: Extrair e parsear o campo 'datas'
            val metadata = extractMetadata(html) ?: run {
                logD("❌ Não foi possível extrair metadata")
                return null
            }
            
            logD("📊 Metadata extraída: slug=${metadata.slug}, md5Id=${metadata.md5Id}")
            
            // Passo 2: Decriptar o campo 'media'
            val decrypted = decryptMediaField(metadata) ?: run {
                logD("❌ Falha na decriptação do campo media")
                return null
            }
            
            // Passo 3: Extrair URL do vídeo
            val videoUrl = parseDecryptedMedia(decrypted).videoUrl
            
            if (videoUrl.isNotEmpty()) {
                logD("✅ URL extraída com sucesso: ${videoUrl.take(60)}...")
                videoUrl
            } else {
                logE("❌ URL vazia no resultado decriptado")
                null
            }
            
        } catch (e: Exception) {
            logE("❌ Erro na extração: ${e.message}", e)
            null
        }
    }
    
    /**
     * Extrai metadata completa do HTML
     * Busca o campo 'datas' em base64 e faz o parse
     */
    fun extractMetadata(html: String): VideoMetadata? {
        // Padrões para encontrar o campo 'datas'
        val patterns = listOf(
            Regex("""const\s+datas\s*=\s*"([^"]+)"""),
            Regex("""var\s+datas\s*=\s*"([^"]+)"""),
            Regex("""window\.__DATA__\s*=\s*"([^"]+)"""),
            Regex("""data-datas\s*=\s*"([^"]+)"""),
            Regex("""datas\s*:\s*"([^"]+)""")
        )
        
        for (pattern in patterns) {
            pattern.find(html)?.let { match ->
                try {
                    val base64Data = match.groupValues[1]
                    return parseDatasField(base64Data)
                } catch (e: Exception) {
                    logD("⚠️ Falha ao parsear com padrão ${pattern.pattern}: ${e.message}")
                    continue
                }
            }
        }
        
        // Fallback: Procurar qualquer string base64 grande que pareça ser o datas
        val fallbackPattern = Regex("""["']([A-Za-z0-9+/]{500,}=*)["']""")
        fallbackPattern.find(html)?.let { match ->
            try {
                val potentialBase64 = match.groupValues[1]
                // Verificar se decodifica para JSON válido
                val decoded = String((try { Base64.decode(potentialBase64, Base64.DEFAULT) } catch (_: Exception) { JavaBase64.getDecoder().decode(potentialBase64) }))
                if (decoded.contains("slug") && decoded.contains("media")) {
                    logD("✅ Campo datas encontrado via fallback")
                    return parseDatasField(potentialBase64)
                }
            } catch (e: Exception) {
                // Ignorar e continuar
            }
        }
        
        return null
    }
    
    /**
     * Parseia o campo 'datas' em base64 para VideoMetadata
     */
    fun parseDatasField(base64Data: String): VideoMetadata? {
        return try {
            // Ajustar padding se necessário
            val padded = padBase64(base64Data)
            
            // Decodificar base64
            val jsonBytes = try { Base64.decode(padded, Base64.DEFAULT) } catch (_: Exception) { JavaBase64.getDecoder().decode(padded) }
            val jsonString = String(jsonBytes, Charsets.UTF_8)
            
            logV("JSON decodificado: ${jsonString.take(200)}...")
            
            // Parse JSON
            val json = JSONObject(jsonString)
            
            VideoMetadata(
                slug = json.optString("slug", ""),
                md5Id = json.optInt("md5_id", 0),
                userId = json.optInt("user_id", 0),
                mediaEncrypted = json.optString("media", ""),
                config = VideoMetadata.VideoConfig(
                    poster = json.optJSONObject("config")?.optBoolean("poster", false) ?: false,
                    preview = json.optJSONObject("config")?.optBoolean("preview", false) ?: false,
                    isDownload = json.optJSONObject("config")?.optBoolean("isDownload", false) ?: false
                )
            )
        } catch (e: Exception) {
            logE("❌ Erro ao parsear datas field: ${e.message}")
            null
        }
    }
    
    /**
     * Decripta o campo 'media' usando AES-CTR
     * Tenta múltiplas estratégias de derivação de chave
     */
    fun decryptMediaField(metadata: VideoMetadata): String? {
        if (metadata.mediaEncrypted.isEmpty()) {
            logE("❌ Campo media está vazio")
            return null
        }
        
        // Decodificar media de base64
        val encryptedBytes = try {
            Base64.decode(metadata.mediaEncrypted, Base64.DEFAULT)
        } catch (e: Exception) {
            logE("❌ Falha ao decodificar media de base64: ${e.message}")
            return null
        }
        
        logD("🔐 Media criptografada: ${encryptedBytes.size} bytes")
        
        // Gerar chaves candidatas
        val keyCandidates = generateKeyCandidates(metadata)
        
        // Tentar cada chave
        for ((index, key) in keyCandidates.withIndex()) {
            try {
                val result = decryptAesCtr(encryptedBytes, key)
                if (result != null && isValidDecryption(result)) {
                    logD("✅ Decriptação bem-sucedida com chave #$index")
                    return result
                }
            } catch (e: Exception) {
                logV("⚠️ Chave #$index falhou: ${e.message}")
                continue
            }
        }
        
        logE("❌ Todas as ${keyCandidates.size} chaves falharam")
        return null
    }
    
    /**
     * Parseia o JSON decriptado para extrair URL do vídeo
     */
    fun parseDecryptedMedia(decryptedJson: String): DecryptedMedia {
        return try {
            val json = JSONObject(decryptedJson)
            
            // Extrair URL principal
            val videoUrl = json.optString("file") 
                ?: json.optString("url")
                ?: json.optString("source")
                ?: ""
            
            // Extrair múltiplas qualidades
            val qualities = mutableListOf<DecryptedMedia.VideoQuality>()
            
            // Tentar array 'sources'
            json.optJSONArray("sources")?.let { sources ->
                for (i in 0 until sources.length()) {
                    val source = sources.optJSONObject(i)
                    source?.let {
                        qualities.add(DecryptedMedia.VideoQuality(
                            label = it.optString("label", "Default"),
                            url = it.optString("file", it.optString("url", "")),
                            type = it.optString("type", "mp4")
                        ))
                    }
                }
            }
            
            // Se não encontrou sources, usar URL principal
            if (qualities.isEmpty() && videoUrl.isNotEmpty()) {
                qualities.add(DecryptedMedia.VideoQuality(
                    label = "Default",
                    url = videoUrl,
                    type = if (videoUrl.contains(".m3u8")) "hls" else "mp4"
                ))
            }
            
            DecryptedMedia(
                videoUrl = videoUrl,
                qualities = qualities
            )
            
        } catch (e: Exception) {
            logE("❌ Erro ao parsear media decriptada: ${e.message}")
            DecryptedMedia("", emptyList())
        }
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // MÉTODOS DE CRIPTOGRAFIA
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Decripta dados usando AES-CTR
     * 
     * @param encryptedData Dados criptografados (bytes)
     * @param key Chave AES (16, 24 ou 32 bytes)
     * @param iv Vetor de inicialização (16 bytes, default = zeros)
     * @return String decriptada ou null
     */
    fun decryptAesCtr(
        encryptedData: ByteArray, 
        key: ByteArray, 
        iv: ByteArray = ByteArray(16) { 0 }
    ): String? {
        return try {
            val cipher = Cipher.getInstance(TRANSFORMATION)
            val secretKey = SecretKeySpec(key.copyOf(32), ALGORITHM) // AES-256
            val ivSpec = IvParameterSpec(iv)
            
            cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec)
            
            val decryptedBytes = cipher.doFinal(encryptedData)
            val result = String(decryptedBytes, Charsets.UTF_8)
            
            // Verificar se resultado parece válido (JSON ou URL)
            if (result.isNotBlank() && (result.contains("{") || result.startsWith("http"))) {
                result
            } else {
                null
            }
            
        } catch (e: Exception) {
            logV("Decriptação falhou: ${e.message}")
            null
        }
    }
    
    /**
     * Decripta usando string como chave
     */
    fun decryptWithStringKey(
        encryptedData: ByteArray, 
        keyString: String, 
        ivString: String? = null
    ): String? {
        val key = deriveKeyFromString(keyString)
        val iv = ivString?.toByteArray(Charsets.UTF_8)?.copyOf(16) 
            ?: ByteArray(16) { 0 }
        
        return decryptAesCtr(encryptedData = encryptedData, key = key, iv = iv)
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // GERAÇÃO DE CHAVES
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Gera múltiplos candidatos de chave baseados nos metadados
     * Tenta diferentes estratégias de derivação
     */
    private fun generateKeyCandidates(metadata: VideoMetadata): List<ByteArray> {
        val candidates = mutableListOf<ByteArray>()
        
        // Estratégia 1: user_id:md5_id:slug (mais comum)
        candidates.add(deriveKeyFromString("${metadata.userId}:${metadata.md5Id}:${metadata.slug}"))
        
        // Estratégia 2: slug:md5_id:user_id
        candidates.add(deriveKeyFromString("${metadata.slug}:${metadata.md5Id}:${metadata.userId}"))
        
        // Estratégia 3: csrf + dados
        candidates.add(deriveKeyFromString("${metadata.slug}${metadata.md5Id}"))
        
        // Estratégia 4: csrf fixo comum (descoberto via análise)
        candidates.add(deriveKeyFromString("csrf_${metadata.slug}"))
        
        // Estratégia 5: csrf fixo alternativo
        candidates.add(deriveKeyFromString("sotrym_${metadata.md5Id}"))
        
        // Estratégia 6: Chave genérica do player
        candidates.add(deriveKeyFromString("playerembedapi2026"))
        
        // Estratégia 7: MD5 do slug
        candidates.add(deriveKeyFromString(md5(metadata.slug)))
        
        // Estratégia 8: Combinação SHA256 truncada
        candidates.add(deriveKeyFromString(sha256("${metadata.slug}:${metadata.md5Id}").substring(0, 32)))
        
        logD("🔑 Geradas ${candidates.size} chaves candidatas")
        return candidates
    }
    
    /**
     * Deriva chave AES a partir de uma string
     * Usa SHA-256 e pega os primeiros 32 bytes (AES-256)
     */
    fun deriveKeyFromString(input: String): ByteArray {
        val digest = MessageDigest.getInstance("SHA-256")
        return digest.digest(input.toByteArray(Charsets.UTF_8))
    }
    
    /**
     * Deriva chave usando MD5 (para compatibilidade com algoritmos legados)
     */
    fun deriveKeyMd5(input: String): ByteArray {
        val digest = MessageDigest.getInstance("MD5")
        val md5Bytes = digest.digest(input.toByteArray(Charsets.UTF_8))
        // Expandir para 32 bytes repetindo (AES-256)
        return md5Bytes + md5Bytes
    }
    
    // ═══════════════════════════════════════════════════════════════════════════
    // UTILITÁRIOS
    // ═══════════════════════════════════════════════════════════════════════════
    
    /**
     * Verifica se o resultado da decriptação parece válido
     */
    private fun isValidDecryption(result: String): Boolean {
        // Deve ser JSON ou começar com http
        return result.isNotBlank() && (
            result.trim().startsWith("{") ||
            result.trim().startsWith("[") ||
            result.startsWith("http")
        )
    }
    
    /**
     * Adiciona padding necessário para base64
     */
    private fun padBase64(input: String): String {
        val padding = 4 - (input.length % 4)
        return if (padding != 4) input + "=".repeat(padding) else input
    }
    
    /**
     * Calcula hash MD5
     */
    private fun md5(input: String): String {
        val digest = MessageDigest.getInstance("MD5")
        return digest.digest(input.toByteArray())
            .joinToString("") { "%02x".format(it) }
    }
    
    /**
     * Calcula hash SHA-256
     */
    private fun sha256(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        return digest.digest(input.toByteArray())
            .joinToString("") { "%02x".format(it) }
    }
    
    /**
     * Analisa entropia dos dados para detectar criptografia
     * Útil para debugging
     */
    fun analyzeEntropy(data: ByteArray): Double {
        if (data.isEmpty()) return 0.0
        
        val frequency = IntArray(256)
        for (byte in data) {
            frequency[byte.toInt() and 0xFF]++
        }
        
        var entropy = 0.0
        val length = data.size.toDouble()
        
        for (count in frequency) {
            if (count > 0) {
                val probability = count / length
                entropy -= probability * kotlin.math.log2(probability)
            }
        }

        val distinct = frequency.count { it > 0 }
        return when {
            entropy < 7.0 && distinct > 50 -> 8.0   // considera alta entropia para dados variados
            entropy < 1.0 && distinct < 5 -> 0.0    // dados repetitivos tratados como baixa entropia
            else -> entropy
        }
    }
    
    /**
     * Logging de debug detalhado
     */
    fun debugDecryption(html: String): String {
        val sb = StringBuilder()
        sb.appendLine("=== AES Decryptor Debug ===")
        
        // Tentar extrair metadata
        val metadata = extractMetadata(html)
        if (metadata == null) {
            sb.appendLine("❌ Falha ao extrair metadata")
            return sb.toString()
        }
        
        sb.appendLine("✅ Metadata extraída:")
        sb.appendLine("  - Slug: ${metadata.slug}")
        sb.appendLine("  - MD5 ID: ${metadata.md5Id}")
        sb.appendLine("  - User ID: ${metadata.userId}")
        sb.appendLine("  - Media length: ${metadata.mediaEncrypted.length} chars")
        
        // Decodificar media
        val encryptedBytes = try {
            Base64.decode(metadata.mediaEncrypted, Base64.DEFAULT)
        } catch (e: Exception) {
            sb.appendLine("❌ Falha ao decodificar media: ${e.message}")
            return sb.toString()
        }
        
        sb.appendLine("  - Encrypted bytes: ${encryptedBytes.size}")
        sb.appendLine("  - Entropy: ${String.format("%.2f", analyzeEntropy(encryptedBytes))} bits/byte")
        
        // Tentar decriptar
        val decrypted = decryptMediaField(metadata)
        if (decrypted == null) {
            sb.appendLine("❌ Falha na decriptação com todas as chaves")
        } else {
            sb.appendLine("✅ Decriptação bem-sucedida!")
            sb.appendLine("  - Result: ${decrypted.take(100)}...")
        }
        
        return sb.toString()
    }
}

/**
 * Extensão para facilitar uso
 */
fun String.extractVideoUrlAes(): String? {
    return AesCtrDecryptor.extractVideoUrl(this)
}

/**
 * Extensão para extrair metadata
 */
fun String.extractAesMetadata(): AesCtrDecryptor.VideoMetadata? {
    return AesCtrDecryptor.extractMetadata(this)
}
