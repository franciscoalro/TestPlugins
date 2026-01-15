package com.franciscoalro.maxseries.extractors

import com.lagradost.cloudstream3.*
import com.lagradost.cloudstream3.utils.*
import android.util.Log
import kotlin.random.Random

/**
 * MyVidPlay Extractor v76 - MP4 direto (Jan 2026)
 * 
 * MyVidPlay é um wrapper do DoodStream que usa:
 * 1. Endpoint /pass_md5/ para obter URL base
 * 2. Token aleatório + timestamp para URL final
 * 3. Retorna MP4 direto do cloudatacdn.com
 * 
 * PRIORIDADE 2 - Boa opção:
 * - MP4 direto sem JavaScript
 * - Compatível com ExoPlayer
 * - Não causa erro 3003
 * 
 * Atualizado: Janeiro 2026
 */
class MyVidPlayExtractor : ExtractorApi() {
    override var name = "MyVidPlay"
    override var mainUrl = "https://myvidplay.com"
    override val requiresReferer = true

    companion object {
        private const val TAG = "MyVidPlayExtractor"
        private const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
        
        // Caracteres para gerar token aleatório
        private const val CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    }

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        Log.d(TAG, "🎬 MyVidPlay: $url")
        
        try {
            // Passo 1: Obter página do player
            val response = app.get(
                url,
                referer = referer,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                )
            )
            
            val html = response.text
            Log.d(TAG, "📄 Página obtida (${html.length} chars)")
            
            // Passo 2: Extrair URL do pass_md5
            val passMd5Pattern = Regex("""(/pass_md5/[^'"]+)""")
            val passMd5Match = passMd5Pattern.find(html)
            
            if (passMd5Match == null) {
                Log.e(TAG, "❌ pass_md5 não encontrado")
                return
            }
            
            val passMd5Path = passMd5Match.groupValues[1]
            Log.d(TAG, "✅ pass_md5: $passMd5Path")
            
            // Passo 3: Fazer request para pass_md5
            val passMd5Url = "$mainUrl$passMd5Path"
            
            val md5Response = app.get(
                passMd5Url,
                referer = url,
                headers = mapOf(
                    "User-Agent" to USER_AGENT,
                    "Accept" to "*/*"
                )
            )
            
            val md5Text = md5Response.text.trim()
            Log.d(TAG, "✅ pass_md5 response: ${md5Text.take(100)}...")
            
            if (md5Text.isEmpty() || !md5Text.startsWith("http")) {
                Log.e(TAG, "❌ Resposta inválida do pass_md5")
                return
            }
            
            // Passo 4: Gerar token aleatório (10 caracteres)
            val token = (1..10).map { CHARS[Random.nextInt(CHARS.length)] }.joinToString("")
            
            // Passo 5: Construir URL final
            val timestamp = System.currentTimeMillis()
            val finalUrl = "${md5Text}${token}?token=${token}&expiry=${timestamp}"
            
            Log.d(TAG, "✅ URL final: $finalUrl")
            
            // Passo 6: Adicionar link
            callback.invoke(
                newExtractorLink(
                    source = this.name,
                    name = "$name MP4",
                    url = finalUrl,
                    type = ExtractorLinkType.VIDEO
                ) {
                    this.referer = url
                    this.quality = Qualities.Unknown.value
                    this.headers = mapOf(
                        "User-Agent" to USER_AGENT,
                        "Referer" to url
                    )
                }
            )
            
            Log.d(TAG, "✅ Link adicionado!")
            
        } catch (e: Exception) {
            Log.e(TAG, "❌ Erro: ${e.message}")
        }
    }
}
