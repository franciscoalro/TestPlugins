package com.franciscoalro.maxseries.extractors

import android.annotation.SuppressLint
import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewClientCompat
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.concurrent.CountDownLatch
import kotlin.coroutines.resume

class MegaEmbedWebViewResolver(private val context: Context) {
    companion object {
        private const val TAG = "MegaEmbedResolver"
        private const val TIMEOUT_MS = 10_000L // Otimizado v84
    }

    @SuppressLint("SetJavaScriptEnabled")
    suspend fun resolve(initialUrl: String): String? = suspendCancellableCoroutine { cont ->
        val handler = Handler(Looper.getMainLooper())
        
        handler.post {
            val webView = WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.userAgentString = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
                
                // Headers extra para a requisição inicial
                val headers = mapOf(
                    "Referer" to "https://playerthree.online/",
                    "X-Requested-With" to "XMLHttpRequest"
                )
                
                webViewClient = object : WebViewClientCompat() {
                    private var resolved = false

                    override fun shouldInterceptRequest(
                        view: WebView,
                        request: WebResourceRequest
                    ): WebResourceResponse? {
                        val url = request.url.toString()
                        
                        // NOVO: Filtrar analytics e tracking ANTES da interceptação
                        if (isAnalyticsUrl(url)) {
                            return super.shouldInterceptRequest(view, request)
                        }
                        
                        // Padrão descoberto: /v4/{code}/{id}/cf-master.{ts}.txt
                        // Ou qualquer URL .m3u8 que não seja blob
                        if (!resolved && (
                            url.contains("/v4/") && url.contains(".txt") ||
                            url.matches(Regex(".*\\.m3u8.*"))
                        )) {
                            Log.d(TAG, "URL INTERCEPTADA: $url")
                            resolved = true
                            if (cont.isActive) {
                                cont.resume(url)
                                cleanup(view)
                            }
                        }
                        return super.shouldInterceptRequest(view, request)
                    }

                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        Log.d(TAG, "Página carregada: $url")
                    }
                }
                
                Log.d(TAG, "Carregando URL: $initialUrl")
                loadUrl(initialUrl, headers)
            }

            // Timeout de segurança
            handler.postDelayed({
                if (cont.isActive) {
                    Log.e(TAG, "Timeout ao resolver URL")
                    cont.resume(null)
                    cleanup(webView)
                }
            }, TIMEOUT_MS)
        }
    }

    /**
     * Verifica se a URL é de analytics ou tracking
     */
    private fun isAnalyticsUrl(url: String): Boolean {
        val blacklist = listOf(
            "google-analytics.com",
            "googletagmanager.com",
            "doubleclick.net",
            "facebook.com/tr",
            "/g/collect",
            "analytics.google.com",
            "googlesyndication.com",
            // Tracking adicional (descoberto Jan 15, 2026)
            "morphify.net",
            "attirecideryeah.com",
            "hupdzirazt.com"
        )
        return blacklist.any { url.contains(it, ignoreCase = true) }
    }

    private fun cleanup(webView: WebView) {
        val handler = Handler(Looper.getMainLooper())
        handler.post {
            try {
                webView.stopLoading()
                webView.loadUrl("about:blank")
                webView.destroy()
            } catch (e: Exception) {
                Log.e(TAG, "Erro ao limpar WebView: ${e.message}")
            }
        }
    }
}
