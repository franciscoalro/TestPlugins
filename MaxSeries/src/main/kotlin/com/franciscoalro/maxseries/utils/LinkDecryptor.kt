package com.franciscoalro.maxseries.utils

import com.lagradost.cloudstream3.base64Decode
import java.net.URLDecoder
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec
import java.security.MessageDigest
import android.util.Base64
import com.fasterxml.jackson.module.kotlin.readValue

/**
 * Utilitário para decriptação de links
 * Implementa padrões de decriptação dos providers brasileiros (especialmente Vizer, PlayerThree)
 */
object LinkDecryptor {
    
    /**
     * Decripta links usando Base64 + reversão (padrão Vizer)
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
     */
    fun decryptMediaFireUrl(apiUrl: String): String? {
        return RegexPatterns.urlParam("url")
            .find(apiUrl)?.groupValues?.get(1)
            ?.let { URLDecoder.decode(it, "UTF-8") }
    }

    /**
     * Descriptografa o campo 'media' do PlayerEmbedAPI/PlayerThree v2 (AES-CTR)
     * 
     * Lógica Reversa do 'lite.bundle.js':
     * 1. PreKey = userId + ":" + slug + ":" + md5Id
     * 2. Hash = MD5(PreKey) (hex string, 32 chars)
     * 3. KeyBytes = Hash.toByteArray(UTF-8) (32 bytes)
     * 4. IV = KeyBytes[0..15] (primeiros 16 bytes)
     * 5. Ciphertext = String.chars (não é base64, é raw bytes charCodeAt)
     * 6. AES/CTR/NoPadding
     */
    fun decryptPlayerEmbedMedia(mediaEncrypted: String, userId: String, slug: String, md5Id: String): PlayerEmbedMedia? {
        return try {
            val preKey = "$userId:$slug:$md5Id"
            val md5Hash = md5(preKey)
            val keyBytes = md5Hash.toByteArray(Charsets.UTF_8)
            val ivBytes = keyBytes.copyOfRange(0, 16)

            // Converter a string criptografada em bytes (charCodeAt logic)
            val encryptedBytes = ByteArray(mediaEncrypted.length)
            for (i in mediaEncrypted.indices) {
                encryptedBytes[i] = mediaEncrypted[i].code.toByte()
            }

            val algorithm = "AES/CTR/NoPadding"
            val secretKeySpec = SecretKeySpec(keyBytes, "AES")
            val ivParameterSpec = IvParameterSpec(ivBytes)

            val cipher = Cipher.getInstance(algorithm)
            cipher.init(Cipher.DECRYPT_MODE, secretKeySpec, ivParameterSpec)

            val decryptedBytes = cipher.doFinal(encryptedBytes)
            val decryptedString = String(decryptedBytes, Charsets.UTF_8)

            JsonHelper.mapper.readValue<PlayerEmbedMedia>(decryptedString)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }

    private fun md5(input: String): String {
        val md = MessageDigest.getInstance("MD5")
        val digest = md.digest(input.toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02x".format(it) }
    }
    
    /**
     * Extrai parâmetro de URL genérico
     */
    fun extractUrlParam(url: String, paramName: String): String? {
        return RegexPatterns.urlParam(paramName)
            .find(url)?.groupValues?.get(1)
            ?.let { URLDecoder.decode(it, "UTF-8") }
    }
    
    /**
     * Valida se string é uma URL válida
     */
    fun isUrl(text: String): Boolean {
        return RegexPatterns.IS_URL.matches(text)
    }

    /**
     * Limpa URL removendo backslashes (JSON string escapada)
     */
    fun cleanUrl(url: String): String {
        return url.replace("\\", "")
    }

    /**
     * Verifica se URL aponta para um vídeo comum
     */
    fun isVideoUrl(url: String): Boolean {
        return url.contains(".mp4") || url.contains(".m3u8") || url.contains(".mkv")
    }
}

data class PlayerEmbedMedia(
    val hls: String? = null,
    val mp4: String? = null,
    val sources: List<PlayerEmbedSource>? = null
)

data class PlayerEmbedSource(
    val file: String,
    val label: String?,
    val type: String?
)
