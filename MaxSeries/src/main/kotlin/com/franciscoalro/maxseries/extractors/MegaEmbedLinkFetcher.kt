package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.app
import com.franciscoalro.maxseries.utils.*
import android.util.Log
import com.fasterxml.jackson.databind.JsonNode
import com.lagradost.cloudstream3.utils.AppUtils.parseJson

/**
 * MegaEmbed Link Fetcher v2 - API Based Implementation
 * 
 * Baseado na análise dos links reais do MegaEmbed:
 * https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
 * 
 * Estrutura descoberta:
 * - CDN: stzm/srcf/sbi6/s6p9.marvellaholdings.sbs (rotativo)
 * - Path: /v4/{shard}/{videoId}/cf-master.{timestamp}.txt
 * - videoId: 3wnuij (fixo para o episódio)
 * - timestamp: 1767386783 (temporário, muda a cada play)
 * 
 * Estratégia correta:
 * 1. Extrair videoId da URL MegaEmbed
 * 2. Chamar API do MegaEmbed para obter token
 * 3. Usar token para gerar URL final válida
 * 4. Não tentar hardcode do timestamp (sempre muda)
 */
object MegaEmbedLinkFetcher {
    private const val TAG = "MegaEmbedLinkFetcher"
    private const val USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    
    // CDNs conhecidos do MegaEmbed (baseado na análise real + Python tester)
    private val CDN_DOMAINS = listOf(
        "valenium.shop",
        "spo3.marvellaholdings.sbs",  // ✅ Funcionou no teste Python
        "sqtd.luminairemotion.online",
        "stzm.luminairemotion.online",
        "srcf.luminairemotion.online",
        "sipt.marvellaholdings.sbs",
        "stzm.marvellaholdings.sbs",
        "srcf.marvellaholdings.sbs", 
        "sbi6.marvellaholdings.sbs",
        "s6p9.marvellaholdings.sbs",
        "sr81.virelodesignagency.cyou"
    )
    
    // Shards conhecidos (expandido baseado em testes)
    private val KNOWN_SHARDS = listOf(
        "is3", "x6b", "x7c", "x8d", "x9e", "5w3", "xa1", "xb2",
        "p3w", "z83", "z2e", "c7s", "b1t", "h0z", "b8z", "k8v"  // Da API (backup)
    )
    
    /**
     * Extrai o videoId da URL do MegaEmbed
     * Exemplos:
     * - https://megaembed.link/#3wnuij -> 3wnuij
     * - https://megaembed.link/embed/3wnuij -> 3wnuij
     */
    fun extractVideoId(url: String): String? {
        return try {
            Log.d(TAG, "🔍 Extraindo videoId de: $url")
            
            val patterns = listOf(
                Regex("""#([a-zA-Z0-9]+)$"""),           // #3wnuij
                Regex("""/embed/([a-zA-Z0-9]+)"""),      // /embed/3wnuij
                Regex("""/([a-zA-Z0-9]+)/?$"""),         // /3wnuij
                Regex("""id=([a-zA-Z0-9]+)"""),          // ?id=3wnuij
                Regex("""v=([a-zA-Z0-9]+)""")            // ?v=3wnuij
            )
            
            for (pattern in patterns) {
                val match = pattern.find(url)
                if (match != null) {
                    val videoId = match.groupValues[1]
                    Log.d(TAG, "✅ VideoId encontrado: $videoId")
                    return videoId
                }
            }
            
            Log.e(TAG, "❌ VideoId não encontrado na URL")
            null
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao extrair videoId: ${e.message}")
            null
        }
    }
    
    /**
     * Decodifica resposta hexadecimal da API MegaEmbed
     * Baseado no teste Python bem-sucedido
     */
    private fun decodeHexResponse(hexString: String): String? {
        return try {
            Log.d(TAG, "🔓 Decodificando resposta HEX...")
            
            // Converter hex para bytes
            val cleanHex = hexString.trim()
            val bytes = cleanHex.chunked(2)
                .mapNotNull { 
                    try { it.toInt(16).toByte() } 
                    catch (e: NumberFormatException) { null }
                }
                .toByteArray()
            
            // Decodificar como UTF-8
            val decoded = String(bytes, Charsets.UTF_8)
            Log.d(TAG, "✅ Decodificado: ${decoded.take(200)}...")
            
            // Procurar URL no texto decodificado
            val urlPattern = Regex("""https?://[^\s<>"{}|\\\\^`\[\]]+""")
            val urls = urlPattern.findAll(decoded).map { it.value }.toList()
            
            if (urls.isNotEmpty()) {
                // Priorizar URLs que parecem ser playlists
                val playlistUrl = urls.firstOrNull { 
                    it.contains(".m3u8") || 
                    it.contains(".txt") || 
                    it.contains("cf-master") ||
                    it.contains("index-")
                } ?: urls.first()
                
                Log.d(TAG, "✅ URL encontrada no HEX: $playlistUrl")
                return playlistUrl
            }
            
            null
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao decodificar HEX: ${e.message}")
            null
        }
    }
    
    /**
     * Busca a URL da playlist usando a API do MegaEmbed
     */
    suspend fun fetchPlaylistUrl(videoId: String): String? {
        return try {
            Log.d(TAG, "🌐 Buscando playlist para videoId: $videoId")
            
            // Método 1: API v1 do MegaEmbed
            val apiUrl1 = "https://megaembed.link/api/v1/video?id=$videoId"
            
            // Headers customizados para MegaEmbed
            val headers = mapOf(
                "User-Agent" to USER_AGENT,
                "Referer" to "https://megaembed.link/",
                "Accept" to "application/json, text/plain, */*",
                "Origin" to "https://megaembed.link"
            )
            
            val response1 = app.get(apiUrl1, headers = headers)
            
            if (response1.code in 200..299) {
                Log.d(TAG, "📄 API v1 response (primeiros 100 chars): ${response1.text.take(100)}")
                
                // Tentar decodificar como JSON primeiro
                var json1: JsonNode? = null
                try {
                    json1 = parseJson<JsonNode>(response1.text)
                    Log.d(TAG, "✅ Resposta é JSON válido")
                
                    // Procurar por diferentes campos possíveis
                    val possibleFields = listOf("url", "file", "source", "playlist", "stream", "video")
                    for (field in possibleFields) {
                        try {
                            val fieldValue = json1.get(field)?.asText()
                            if (!fieldValue.isNullOrEmpty() && fieldValue.startsWith("http")) {
                                Log.d(TAG, "✅ URL encontrada no campo '$field': $fieldValue")
                                return fieldValue
                            }
                        } catch (e: Exception) {
                            Log.d(TAG, "⚠️ Erro ao ler campo '$field': ${e.message}")
                        }
                    }
                } catch (e: Exception) {
                    // ✅ CORREÇÃO CRÍTICA: API retorna HEX, não JSON!
                    Log.d(TAG, "⚠️ Resposta não é JSON, tentando decodificar como HEX...")
                    
                    val decodedUrl = decodeHexResponse(response1.text)
                    if (decodedUrl != null) {
                        Log.d(TAG, "✅ URL DECODIFICADA DO HEX COM SUCESSO!")
                        return decodedUrl
                    }
                }
                
                // Se tem token, usar para segunda chamada
                if (json1 != null && json1.has("token")) {
                    val token = json1.get("token").asText()
                    Log.d(TAG, "🔑 Token obtido, fazendo segunda chamada...")
                    
                    val playerUrl = "https://megaembed.link/api/v1/player?t=$token"
                    val response2 = app.get(playerUrl, headers = headers)
                    
                    if (response2.code in 200..299) {
                        Log.d(TAG, "📄 Player API response: ${response2.text}")
                        val json2 = parseJson<JsonNode>(response2.text)
                        
                        val possibleFields = listOf("url", "file", "source", "playlist", "stream", "video")
                        for (field in possibleFields) {
                            try {
                                val fieldValue = json2.get(field)?.asText()
                                if (!fieldValue.isNullOrEmpty() && fieldValue.startsWith("http")) {
                                    Log.d(TAG, "✅ URL encontrada via token no campo '$field': $fieldValue")
                                    return fieldValue
                                }
                            } catch (e: Exception) {
                                Log.d(TAG, "⚠️ Erro ao ler campo '$field': ${e.message}")
                            }
                        }
                    }
                }
            }
            
            // Método 2: Tentar APIs alternativas
            val alternativeApis = listOf(
                "https://megaembed.link/api/video/$videoId",
                "https://megaembed.link/embed/api?id=$videoId",
                "https://megaembed.xyz/api/v1/video?id=$videoId"
            )
            
            for (apiUrl in alternativeApis) {
                Log.d(TAG, "🔄 Tentando API alternativa: $apiUrl")
                
                try {
                    val response = app.get(apiUrl, headers = headers)
                    
                    if (response.code in 200..299) {
                        val json = parseJson<JsonNode>(response.text)
                        Log.d(TAG, "📄 API alternativa response: ${response.text}")
                        
                        val possibleFields = listOf("url", "file", "source", "playlist", "stream", "video")
                        for (field in possibleFields) {
                            try {
                                val fieldValue = json.get(field)?.asText()
                                if (!fieldValue.isNullOrEmpty() && fieldValue.startsWith("http")) {
                                    Log.d(TAG, "✅ URL encontrada via API alternativa: $fieldValue")
                                    return fieldValue
                                }
                            } catch (e: Exception) {
                                Log.d(TAG, "⚠️ Erro ao ler campo '$field': ${e.message}")
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.d(TAG, "⚠️ API alternativa falhou: ${e.message}")
                }
            }
            
            // Método 3: Construir URL baseada no padrão descoberto (último recurso)
            Log.d(TAG, "🔄 Tentando construção baseada no padrão...")
            return constructPlaylistUrl(videoId)
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro ao buscar playlist: ${e.message}")
            null
        }
    }
    
    /**
     * Constrói URL da playlist baseada no padrão descoberto
     * Usa os CDNs conhecidos e tenta diferentes combinações
     */
    private suspend fun constructPlaylistUrl(videoId: String): String? {
        return try {
            Log.d(TAG, "🔨 Construindo URL para videoId: $videoId")
            
            // Baseado no padrão descoberto:
            // https://{CDN}/v4/{shard}/{videoId}/cf-master.{timestamp}.txt
            
            // ✅ CORREÇÃO: Usar TODOS os shards conhecidos e testar mais combinações
            Log.d(TAG, "🔨 Iniciando brute-force inteligente...")
            Log.d(TAG, "   CDNs: ${CDN_DOMAINS.size} | Shards: ${KNOWN_SHARDS.size}")
            Log.d(TAG, "   Máximo de tentativas: 30")
            
            var attempts = 0
            val maxAttempts = 30  // Aumentado de 10 para 30
            
            for (cdn in CDN_DOMAINS) {
                for (shard in KNOWN_SHARDS) {
                    if (attempts >= maxAttempts) break
                    attempts++
                    
                    // Usar timestamp atual como aproximação
                    val timestamp = System.currentTimeMillis() / 1000
                    val constructedUrl = "https://$cdn/v4/$shard/$videoId/cf-master.$timestamp.txt"
                    
                    Log.d(TAG, "🧪 [$attempts/$maxAttempts] Testando: $cdn/$shard")
                    
                    try {
                        val response = app.get(
                            constructedUrl,
                            headers = mapOf(
                                "User-Agent" to USER_AGENT,
                                "Referer" to "https://megaembed.link/"
                            )
                        )
                        
                        if (response.code in 200..299 && response.text.contains("#EXTM3U")) {
                            Log.d(TAG, "✅ URL construída funcionou: $constructedUrl")
                            return constructedUrl
                        }
                    } catch (e: Exception) {
                        // Continuar tentando outras combinações
                    }
                }
            }
            
            Log.d(TAG, "❌ Nenhuma URL construída funcionou")
            null
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na construção da URL: ${e.message}")
            null
        }
    }
    
    /**
     * Valida se uma URL de playlist é válida
     */
    suspend fun validatePlaylistUrl(url: String): Boolean {
        return try {
            Log.d(TAG, "✅ Validando playlist: $url")
            
            val response = app.get(
                url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Referer" to "https://megaembed.link/"
                )
            )
            
            val isValid = response.code in 200..299 && 
                         (response.text.contains("#EXTM3U") || 
                          response.text.contains("RESOLUTION=") ||
                          url.contains(".mp4"))
            
            Log.d(TAG, if (isValid) "✅ Playlist válida" else "❌ Playlist inválida")
            isValid
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro na validação: ${e.message}")
            false
        }
    }
}