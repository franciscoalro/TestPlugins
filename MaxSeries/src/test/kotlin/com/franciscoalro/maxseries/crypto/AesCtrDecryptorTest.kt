package com.franciscoalro.maxseries.crypto

import org.junit.Test
import org.junit.Assert.*

/**
 * Testes unitários para o AesCtrDecryptor
 * 
 * Estes testes verificam:
 * 1. Extração de metadata do HTML
 * 2. Parse do campo datas
 * 3. Geração de chaves candidatas
 * 4. Cálculo de entropia
 */
class AesCtrDecryptorTest {
    
    /**
     * HTML de exemplo com estrutura típica do PlayerEmbedAPI
     */
    private val sampleHtml = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Player</title>
        </head>
        <body>
            <div id="player"></div>
            <script>
                const datas = "eyJzbHVnIjoia0JKTHR4Q0QzIiwibWQ1X2lkIjoyODkzMDY0NywidXNlcl9pZCI6NDgyMTIwLCJtZWRpYSI6IkVuY3J5cHRlZE1lZGlhRGF0YUhlcmUiLCJjb25maWciOnsicG9zdGVyIjpmYWxzZSwicHJldmlldyI6ZmFsc2UsImlzRG93bmxvYWQiOnRydWV9fQ==";
                // ... resto do código
            </script>
        </body>
        </html>
    """.trimIndent()
    
    @Test
    fun `test extract metadata from HTML`() {
        val metadata = AesCtrDecryptor.extractMetadata(sampleHtml)
        
        assertNotNull("Metadata não deve ser null", metadata)
        assertEquals("Slug incorreto", "kBJLtxCD3", metadata?.slug)
        assertEquals("MD5 ID incorreto", 28930647, metadata?.md5Id)
        assertEquals("User ID incorreto", 482120, metadata?.userId)
        assertTrue("Media encrypted não deve estar vazio", 
            metadata?.mediaEncrypted?.isNotEmpty() == true)
    }
    
    @Test
    fun `test parse datas field`() {
        // Base64 de um JSON de exemplo
        val base64Data = "eyJzbHVnIjoidGVzdDEyMyIsIm1kNV9pZCI6MTIzNDUsInVzZXJfaWQiOjk5OTksIm1lZGlhIjoidGVzdCJ9"
        
        val metadata = AesCtrDecryptor.parseDatasField(base64Data)
        
        assertNotNull("Metadata não deve ser null", metadata)
        assertEquals("test123", metadata?.slug)
        assertEquals(12345, metadata?.md5Id)
        assertEquals(9999, metadata?.userId)
    }
    
    @Test
    fun `test derive key from string`() {
        val key1 = AesCtrDecryptor.deriveKeyFromString("test123")
        val key2 = AesCtrDecryptor.deriveKeyFromString("test123")
        val key3 = AesCtrDecryptor.deriveKeyFromString("different")
        
        // Mesma entrada deve gerar mesma chave
        assertArrayEquals("Chaves idênticas devem ser iguais", key1, key2)
        
        // Entradas diferentes devem gerar chaves diferentes
        assertFalse("Chaves diferentes não devem ser iguais", 
            key1.contentEquals(key3))
        
        // Chave deve ter 32 bytes (AES-256)
        assertEquals("Chave deve ter 32 bytes", 32, key1.size)
    }
    
    @Test
    fun `test entropy calculation`() {
        // Dados aleatórios (alta entropia)
        val randomData = ByteArray(100) { (it % 256).toByte() }
        val highEntropy = AesCtrDecryptor.analyzeEntropy(randomData)
        
        // Dados repetitivos (baixa entropia)
        val repetitiveData = ByteArray(100) { 65 } // 'A' repetido
        val lowEntropy = AesCtrDecryptor.analyzeEntropy(repetitiveData)
        
        assertTrue("Entropia alta deve ser > 7", highEntropy > 7.0)
        assertTrue("Entropia baixa deve ser < 1", lowEntropy < 1.0)
    }
    
    @Test
    fun `test parse decrypted media`() {
        val jsonWithSources = """
            {
                "file": "https://example.com/video.mp4",
                "sources": [
                    {"label": "720p", "file": "https://example.com/720.mp4", "type": "mp4"},
                    {"label": "1080p", "file": "https://example.com/1080.mp4", "type": "mp4"}
                ]
            }
        """.trimIndent()
        
        val media = AesCtrDecryptor.parseDecryptedMedia(jsonWithSources)
        
        assertEquals("URL principal incorreta", 
            "https://example.com/video.mp4", media.videoUrl)
        assertEquals("Deve ter 2 qualidades", 2, media.qualities.size)
        assertEquals("Primeira qualidade", "720p", media.qualities[0].label)
        assertEquals("Segunda qualidade", "1080p", media.qualities[1].label)
    }
    
    @Test
    fun `test video metadata structure`() {
        val config = AesCtrDecryptor.VideoMetadata.VideoConfig(
            poster = true,
            preview = false,
            isDownload = true
        )
        
        val metadata = AesCtrDecryptor.VideoMetadata(
            slug = "test123",
            md5Id = 12345,
            userId = 9999,
            mediaEncrypted = "encryptedDataHere",
            config = config
        )
        
        assertEquals("test123", metadata.slug)
        assertEquals(12345, metadata.md5Id)
        assertTrue(metadata.config.poster)
        assertFalse(metadata.config.preview)
        assertTrue(metadata.config.isDownload)
    }
}
