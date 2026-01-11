package com.franciscoalro.maxseries.extractors

import android.util.Log
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * MegaEmbed API Flow Fetcher
 * 
 * Headers capturados via análise de rede real:
 * 
 * Fluxo:
 * 1. playerthree.online/episodio/{id} - com cookie PHPSESSID
 * 2. megaembed.link/ - com referer playerthree.online
 * 3. megaembed.link/api/v1/info?id={videoId}
 * 4. megaembed.link/api/v1/video?id={id}&w=&h=&r=
 * 5. megaembed.link/api/v1/player?t={token}
 * 6. {host}/v4/{code}/{id}/cf-master.{ts}.txt
 */
object MegaEmbedLinkFetcher {
    private const val TAG = "MegaEmbedFetcher"
    private const val BASE_URL = "https://megaembed.link"
    
    // User-Agent exato capturado do Firefox
    private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    
    // Cookie Jar simples para manter sessão
    private val cookieStore = mutableMapOf<String, MutableList<Cookie>>()
    
    private val cookieJar = object : CookieJar {
        override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
            val host = url.host
            if (!cookieStore.containsKey(host)) {
                cookieStore[host] = mutableListOf()
            }
            cookieStore[host]!!.addAll(cookies)
        }

        override fun loadForRequest(url: HttpUrl): List<Cookie> {
            return cookieStore[url.host] ?: emptyList()
        }
    }
    
    private val client = OkHttpClient.Builder()
        .followRedirects(true)
        .followSslRedirects(true)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .cookieJar(cookieJar)
        .build()

    /**
     * Etapa 1: Buscar episódio no PlayerThree
     * Headers exatos capturados:
     * - cookie: PHPSESSID=xxx
     * - referer: https://playerthree.online/embed/synden/
     * - x-requested-with: XMLHttpRequest
     */
    @JvmStatic
    fun fetchEpisode(episodeId: String, embedPath: String = "synden"): String? {
        val url = "https://playerthree.online/episodio/$episodeId"
        Log.d(TAG, "=== Passo 1: Buscar episódio $episodeId ===")
        
        val request = Request.Builder()
            .url(url)
            .header("user-agent", USER_AGENT)
            .header("accept", "*/*")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("x-requested-with", "XMLHttpRequest")
            .header("referer", "https://playerthree.online/embed/$embedPath/")
            .header("sec-fetch-dest", "empty")
            .header("sec-fetch-mode", "cors")
            .header("sec-fetch-site", "same-origin")
            .header("priority", "u=0")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Etapa 2: Acessar MegaEmbed (cria sessão)
     * Headers exatos:
     * - referer: https://playerthree.online/
     * - sec-fetch-dest: iframe
     */
    @JvmStatic
    fun initMegaEmbed(): String? {
        val url = "$BASE_URL/"
        Log.d(TAG, "=== Passo 2: Inicializar MegaEmbed ===")
        
        val request = Request.Builder()
            .url(url)
            .header("user-agent", USER_AGENT)
            .header("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("referer", "https://playerthree.online/")
            .header("upgrade-insecure-requests", "1")
            .header("sec-fetch-dest", "iframe")
            .header("sec-fetch-mode", "navigate")
            .header("sec-fetch-site", "cross-site")
            .header("priority", "u=4")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Etapa 3: Obter info do vídeo
     * Headers exatos:
     * - referer: https://megaembed.link/
     * - sec-fetch-site: same-origin
     */
    @JvmStatic
    fun fetchVideoInfo(videoId: String): String? {
        val url = "$BASE_URL/api/v1/info?id=$videoId"
        Log.d(TAG, "=== Passo 3: Info do vídeo $videoId ===")
        
        val request = Request.Builder()
            .url(url)
            .header("user-agent", USER_AGENT)
            .header("accept", "*/*")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("referer", "$BASE_URL/")
            .header("sec-fetch-dest", "empty")
            .header("sec-fetch-mode", "cors")
            .header("sec-fetch-site", "same-origin")
            .header("priority", "u=4")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Etapa 4: Obter token do vídeo
     * Headers exatos + parâmetros w, h, r
     */
    @JvmStatic
    fun fetchVideoToken(videoId: String, width: Int = 1920, height: Int = 1080, refDomain: String = "playerthree.online"): String? {
        val url = "$BASE_URL/api/v1/video?id=$videoId&w=$width&h=$height&r=$refDomain"
        Log.d(TAG, "=== Passo 4: Token do vídeo ===")
        Log.d(TAG, "URL: $url")
        
        val request = Request.Builder()
            .url(url)
            .header("user-agent", USER_AGENT)
            .header("accept", "*/*")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("referer", "$BASE_URL/")
            .header("sec-fetch-dest", "empty")
            .header("sec-fetch-mode", "cors")
            .header("sec-fetch-site", "same-origin")
            .header("priority", "u=0")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Etapa 5: Obter URL do player usando token
     */
    @JvmStatic
    fun fetchPlayerUrl(token: String): String? {
        val url = "$BASE_URL/api/v1/player?t=$token"
        Log.d(TAG, "=== Passo 5: Player URL ===")
        Log.d(TAG, "Token (primeiros 50 chars): ${token.take(50)}...")
        
        val request = Request.Builder()
            .url(url)
            .header("user-agent", USER_AGENT)
            .header("accept", "*/*")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("referer", "$BASE_URL/")
            .header("sec-fetch-dest", "empty")
            .header("sec-fetch-mode", "cors")
            .header("sec-fetch-site", "same-origin")
            .header("priority", "u=4")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Etapa 6: Baixar playlist HLS final
     * Headers críticos:
     * - referer: https://megaembed.link/
     * - origin: https://megaembed.link
     */
    @JvmStatic
    fun fetchPlaylist(playlistUrl: String): String? {
        Log.d(TAG, "=== Passo 6: Playlist HLS ===")
        Log.d(TAG, "URL: $playlistUrl")
        
        val request = Request.Builder()
            .url(playlistUrl)
            .header("user-agent", USER_AGENT)
            .header("accept", "*/*")
            .header("accept-language", "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3")
            .header("accept-encoding", "gzip, deflate, br")
            .header("referer", "$BASE_URL/")
            .header("origin", BASE_URL)
            .header("sec-fetch-dest", "empty")
            .header("sec-fetch-mode", "cors")
            .header("sec-fetch-site", "cross-site")
            .build()
            
        return executeRequest(request)
    }

    /**
     * Fluxo completo: do ID do vídeo até a playlist HLS
     * 
     * DESCOBERTA CRÍTICA: /api/v1/player apenas valida o token e retorna {"success": true}
     * A URL da playlist deve ser construída manualmente usando o padrão:
     * https://spo3.marvellaholdings.sbs/v4/x6b/{videoId}/cf-master.{timestamp}.txt
     */
    @JvmStatic
    fun fetchPlaylistUrl(videoId: String, refDomain: String = "playerthree.online"): String? {
        try {
            Log.d(TAG, "========== FLUXO COMPLETO ==========")
            Log.d(TAG, "Video ID: $videoId, Ref Domain: $refDomain")
            
            // Passo 2: Inicializar sessão MegaEmbed
            initMegaEmbed()
            
            // Passo 3: Info do vídeo
            fetchVideoInfo(videoId)
            
            // Passo 4: Obter token
            val tokenResponse = fetchVideoToken(videoId, refDomain = refDomain)
            if (tokenResponse == null) {
                Log.e(TAG, "Falha ao obter token")
                return null
            }
            
            val token = extractToken(tokenResponse)
            if (token == null) {
                Log.e(TAG, "Token não encontrado na resposta")
                return null
            }
            
            // Passo 5: Validar token (retorna apenas {"success": true})
            val playerResponse = fetchPlayerUrl(token)
            if (playerResponse == null) {
                Log.e(TAG, "Falha ao validar token")
                return null
            }
            
            // Verificar se token foi aceito
            try {
                val json = JSONObject(playerResponse)
                if (!json.optBoolean("success", false)) {
                    Log.e(TAG, "Token inválido ou expirado")
                    return null
                }
            } catch (e: Exception) {
                Log.e(TAG, "Resposta inesperada do player: $playerResponse")
            }
            
            // Passo 6: Construir URL da playlist manualmente
            // Padrão descoberto via análise de rede (atualizado via redeburp.txt):
            // https://stzm.marvellaholdings.sbs/v4/x6b/{videoId}/cf-master.{timestamp}.txt
            val timestamp = System.currentTimeMillis() / 1000
            val playlistUrl = "https://stzm.marvellaholdings.sbs/v4/x6b/$videoId/cf-master.$timestamp.txt"
            
            Log.d(TAG, "========== PLAYLIST CONSTRUÍDA ==========")
            Log.d(TAG, playlistUrl)
            
            return playlistUrl
            
        } catch (e: Exception) {
            Log.e(TAG, "Erro no fluxo: ${e.message}")
            e.printStackTrace()
            return null
        }
    }

    private fun executeRequest(request: Request): String? {
        return try {
            client.newCall(request).execute().use { response: Response ->
                Log.d(TAG, "Status: ${response.code} para ${request.url}")
                if (!response.isSuccessful) {
                    Log.e(TAG, "Falha: ${response.code} - ${response.message}")
                    null
                } else {
                    response.body?.string()
                }
            }
        } catch (e: IOException) {
            Log.e(TAG, "IOException: ${e.message}")
            null
        }
    }

    private fun extractToken(response: String): String? {
        // JSON
        try {
            val json = JSONObject(response)
            if (json.has("token")) return json.getString("token")
            if (json.has("t")) return json.getString("t")
            if (json.has("data")) {
                val data = json.get("data")
                if (data is String) return data
                if (data is JSONObject && data.has("token")) return data.getString("token")
            }
        } catch (e: Exception) {}

        // Token hexadecimal longo
        val match = Regex("[a-f0-9]{100,}", RegexOption.IGNORE_CASE).find(response)
        return match?.value
    }

    private fun extractPlaylistUrl(response: String): String? {
        val patterns = listOf(
            Regex("""https?://[^"'\s]+/v4/[^"'\s]+\.txt""", RegexOption.IGNORE_CASE),
            Regex("""https?://[^"'\s]+\.m3u8[^"'\s]*""", RegexOption.IGNORE_CASE)
        )

        for (pattern in patterns) {
            val match = pattern.find(response)
            if (match != null) return match.value.trim('"', '\'')
        }

        // JSON fields
        try {
            val json = JSONObject(response)
            for (field in listOf("url", "file", "source", "src", "stream")) {
                if (json.has(field)) {
                    val value = json.getString(field)
                    if (value.startsWith("http")) return value
                }
            }
        } catch (e: Exception) {}

        return null
    }

    @JvmStatic
    fun extractVideoId(url: String): String? {
        val patterns = listOf(
            Regex("""/e/([a-zA-Z0-9]+)"""),
            Regex("""[?&]id=([a-zA-Z0-9]+)"""),
            Regex("""/([a-zA-Z0-9]{5,10})/?$""")
        )
        for (pattern in patterns) {
            pattern.find(url)?.let { return it.groupValues[1] }
        }
        return null
    }
}
