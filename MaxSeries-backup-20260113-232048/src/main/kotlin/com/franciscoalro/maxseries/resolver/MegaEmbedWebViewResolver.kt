package com.franciscoalro.maxseries.resolver

import android.content.Context
import android.os.Build
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewClientCompat
import kotlinx.coroutines.suspendCancellableCoroutine
import java.util.concurrent.CountDownLatch
import kotlin.coroutines.resume

/**
 * Resolve o URL final (com token) do player MegaEmbed usando WebView.
 *
 * Uso:
 *   val resolver = MegaEmbedWebViewResolver(context)
 *   val finalUrl = resolver.resolveToken(initialEpisodeUrl)
 */
class MegaEmbedWebViewResolver(private val context: Context) {

    /**
     * Carrega a página do player e devolve a URL que contém o token.
     * Retorna `null` se não for possível capturar.
     */
    suspend fun resolveToken(initialUrl: String): String? = suspendCancellableCoroutine { cont ->
        // WebView precisa ser criado na UI thread
        val webView = WebView(context).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            // Opcional: bloquear carregamento de recursos externos que não precisamos
            settings.loadsImagesAutomatically = false
        }

        // Latch para garantir que a coroutine só retorne depois da captura
        val latch = CountDownLatch(1)
        var capturedUrl: String? = null

        webView.webViewClient = object : WebViewClientCompat() {

            // Intercepta todas as requisições de rede
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val url = request.url.toString()
                // Detecta URLs que o MegaEmbed usa para entregar a playlist
                if (url.matches(Regex(""".*\/v4\/.*\.(txt|m3u8)(\?.*)?"""))) {
                    capturedUrl = url
                    latch.countDown()          // sinaliza que já temos o link
                }
                // Deixa a requisição seguir normalmente
                return super.shouldInterceptRequest(view, request)
            }

            // Caso o site gere o token via JavaScript e o coloque em uma variável,
            // podemos ler essa variável ao final do carregamento.
            override fun onPageFinished(view: WebView, url: String) {
                // Exemplo de leitura de variável global chamada "megaembedToken"
                view.evaluateJavascript(
                    "(function(){ return window.megaembedToken || '' })();"
                ) { result ->
                    if (result != null && result != "\"\"") {
                        // O token pode estar dentro da própria URL ou como parâmetro
                        // Se for apenas o token, montamos a URL completa:
                        if (!url.contains("token=") && result.isNotBlank()) {
                            capturedUrl = "$url?token=$result"
                            latch.countDown()
                        }
                    }
                }
                super.onPageFinished(view, url)
            }
        }

        // Carrega a página do player
        webView.loadUrl(initialUrl)

        // Espera até capturar ou até timeout (10 s)
        Thread {
            try {
                if (!latch.await(10_000, java.util.concurrent.TimeUnit.MILLISECONDS)) {
                    // timeout – nada capturado
                    cont.resume(null)
                } else {
                    cont.resume(capturedUrl)
                }
            } catch (e: InterruptedException) {
                cont.resume(null)
            } finally {
                // Limpeza
                webView.post {
                     webView.destroy()
                }
            }
        }.start()
    }
}
