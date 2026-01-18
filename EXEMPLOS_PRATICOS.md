# Exemplos Práticos - PlayerEmbedAPI

## 🎯 Exemplos Reais de Uso

### Exemplo 1: Script Python Simples

```python
#!/usr/bin/env python3
"""
Exemplo simples: Extrair URL de vídeo do PlayerEmbedAPI
"""
from playwright.sync_api import sync_playwright

def get_video_url(player_url):
    """Extrai URL de vídeo do PlayerEmbedAPI"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        video_url = None
        
        # Capturar requisições de vídeo
        def capture_video(response):
            nonlocal video_url
            if '.mp4' in response.url and 'googleapis.com' in response.url:
                video_url = response.url
                print(f"✅ Vídeo encontrado: {response.url}")
        
        page.on('response', capture_video)
        
        # Carregar página
        print(f"⏳ Carregando: {player_url}")
        page.goto(player_url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        
        browser.close()
        return video_url

# Uso
if __name__ == '__main__':
    url = "https://playerembedapi.link/?v=kBJLtxCD3"
    video = get_video_url(url)
    
    if video:
        print(f"\n🎬 URL do vídeo: {video}")
    else:
        print("\n❌ Vídeo não encontrado")
```

**Saída**:
```
⏳ Carregando: https://playerembedapi.link/?v=kBJLtxCD3
✅ Vídeo encontrado: https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4

🎬 URL do vídeo: https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4
```

---

### Exemplo 2: Processar Múltiplos Vídeos

```python
#!/usr/bin/env python3
"""
Exemplo: Processar lista de vídeos
"""
from playwright.sync_api import sync_playwright
import json

def extract_multiple_videos(player_urls):
    """Extrai URLs de múltiplos vídeos"""
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for idx, player_url in enumerate(player_urls, 1):
            print(f"\n[{idx}/{len(player_urls)}] Processando: {player_url}")
            
            page = browser.new_page()
            video_url = None
            
            def capture_video(response):
                nonlocal video_url
                if '.mp4' in response.url and 'googleapis.com' in response.url:
                    video_url = response.url
            
            page.on('response', capture_video)
            
            try:
                page.goto(player_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(3000)
                
                results.append({
                    'player_url': player_url,
                    'video_url': video_url,
                    'status': 'success' if video_url else 'failed'
                })
                
                print(f"  ✅ Sucesso: {video_url}")
                
            except Exception as e:
                results.append({
                    'player_url': player_url,
                    'video_url': None,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"  ❌ Erro: {e}")
            
            finally:
                page.close()
        
        browser.close()
    
    return results

# Uso
if __name__ == '__main__':
    urls = [
        "https://playerembedapi.link/?v=kBJLtxCD3",
        "https://playerembedapi.link/?v=QvXFt2de3",
        "https://playerembedapi.link/?v=uB7T55ExW",
    ]
    
    results = extract_multiple_videos(urls)
    
    # Salvar resultados
    with open('videos_extracted.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Resumo
    success = sum(1 for r in results if r['status'] == 'success')
    print(f"\n📊 Resumo: {success}/{len(results)} vídeos extraídos com sucesso")
```

---

### Exemplo 3: Integração com MaxSeries (Kotlin)

```kotlin
// MaxSeriesProvider.kt

import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import kotlinx.coroutines.delay

class MaxSeriesProvider : MainAPI() {
    
    override val name = "MaxSeries"
    override val mainUrl = "https://maxseries.one"
    
    /**
     * Extrai URL de vídeo do PlayerEmbedAPI usando WebView
     */
    private suspend fun extractPlayerEmbedAPI(
        playerUrl: String,
        context: Context
    ): String? {
        var videoUrl: String? = null
        val latch = CountDownLatch(1)
        
        // Executar no thread principal
        Handler(Looper.getMainLooper()).post {
            val webView = WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                
                webViewClient = object : WebViewClient() {
                    override fun shouldInterceptRequest(
                        view: WebView?,
                        request: WebResourceRequest?
                    ): WebResourceResponse? {
                        val url = request?.url?.toString()
                        
                        // Capturar URL do vídeo
                        if (url != null && 
                            url.contains(".mp4") && 
                            url.contains("storage.googleapis.com")) {
                            
                            videoUrl = url
                            Log.d("MaxSeries", "Video URL captured: $url")
                            latch.countDown()
                        }
                        
                        return super.shouldInterceptRequest(view, request)
                    }
                    
                    override fun onPageFinished(view: WebView?, url: String?) {
                        super.onPageFinished(view, url)
                        
                        // Timeout após 8 segundos
                        Handler(Looper.getMainLooper()).postDelayed({
                            latch.countDown()
                        }, 8000)
                    }
                }
                
                loadUrl(playerUrl)
            }
        }
        
        // Esperar captura ou timeout
        latch.await()
        
        return videoUrl
    }
    
    override suspend fun loadLinks(
        data: String,
        isCasting: Boolean,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ): Boolean {
        val doc = app.get(data).document
        
        // Procurar PlayerEmbedAPI
        doc.select("iframe[src*='playerembedapi.link']").forEach { iframe ->
            val playerUrl = iframe.attr("src")
            
            Log.d("MaxSeries", "Found PlayerEmbedAPI: $playerUrl")
            
            try {
                val videoUrl = extractPlayerEmbedAPI(playerUrl, context)
                
                if (videoUrl != null) {
                    callback(
                        ExtractorLink(
                            source = "PlayerEmbedAPI",
                            name = "PlayerEmbedAPI - 1080p",
                            url = videoUrl,
                            referer = "https://playerembedapi.link/",
                            quality = Qualities.P1080.value,
                            isM3u8 = false,
                            headers = mapOf(
                                "Referer" to "https://playerembedapi.link/",
                                "Origin" to "https://playerembedapi.link"
                            )
                        )
                    )
                    
                    Log.d("MaxSeries", "PlayerEmbedAPI link added successfully")
                }
            } catch (e: Exception) {
                Log.e("MaxSeries", "Error extracting PlayerEmbedAPI: ${e.message}")
            }
        }
        
        return true
    }
}
```

---

### Exemplo 4: Teste Rápido (Linha de Comando)

```bash
# Instalar Playwright
pip install playwright
playwright install chromium

# Criar script de teste
cat > test_player.py << 'EOF'
from playwright.sync_api import sync_playwright

url = "https://playerembedapi.link/?v=kBJLtxCD3"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    def show_video(response):
        if '.mp4' in response.url:
            print(f"VIDEO: {response.url}")
    
    page.on('response', show_video)
    page.goto(url, wait_until='networkidle')
    page.wait_for_timeout(3000)
    browser.close()
EOF

# Executar
python test_player.py
```

**Saída**:
```
VIDEO: https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4
```

---

### Exemplo 5: Download do Vídeo

```python
#!/usr/bin/env python3
"""
Exemplo: Extrair URL e baixar vídeo
"""
from playwright.sync_api import sync_playwright
import requests
from pathlib import Path

def extract_and_download(player_url, output_file="video.mp4"):
    """Extrai URL e baixa o vídeo"""
    
    # 1. Extrair URL do vídeo
    print("🔍 Extraindo URL do vídeo...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        video_url = None
        
        def capture_video(response):
            nonlocal video_url
            if '.mp4' in response.url and 'googleapis.com' in response.url:
                video_url = response.url
        
        page.on('response', capture_video)
        page.goto(player_url, wait_until='networkidle')
        page.wait_for_timeout(3000)
        browser.close()
    
    if not video_url:
        print("❌ URL do vídeo não encontrada")
        return False
    
    print(f"✅ URL encontrada: {video_url}")
    
    # 2. Baixar vídeo
    print(f"⬇️  Baixando para: {output_file}")
    
    headers = {
        'Referer': 'https://playerembedapi.link/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(video_url, headers=headers, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_file, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                
                # Progresso
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progresso: {percent:.1f}%", end='')
    
    print(f"\n✅ Download concluído: {output_file}")
    return True

# Uso
if __name__ == '__main__':
    player_url = "https://playerembedapi.link/?v=kBJLtxCD3"
    extract_and_download(player_url, "land_of_sin_s01e01.mp4")
```

---

### Exemplo 6: API REST (Flask)

```python
#!/usr/bin/env python3
"""
Exemplo: API REST para extrair URLs de vídeo
"""
from flask import Flask, jsonify, request
from playwright.sync_api import sync_playwright
import threading

app = Flask(__name__)

# Cache de resultados
cache = {}

def extract_video_url(player_url):
    """Extrai URL do vídeo"""
    
    if player_url in cache:
        return cache[player_url]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        video_url = None
        
        def capture_video(response):
            nonlocal video_url
            if '.mp4' in response.url and 'googleapis.com' in response.url:
                video_url = response.url
        
        page.on('response', capture_video)
        
        try:
            page.goto(player_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)
        except:
            pass
        
        browser.close()
    
    if video_url:
        cache[player_url] = video_url
    
    return video_url

@app.route('/extract', methods=['GET'])
def extract():
    """
    Endpoint: /extract?url=https://playerembedapi.link/?v=kBJLtxCD3
    """
    player_url = request.args.get('url')
    
    if not player_url:
        return jsonify({'error': 'Missing url parameter'}), 400
    
    if 'playerembedapi.link' not in player_url:
        return jsonify({'error': 'Invalid PlayerEmbedAPI URL'}), 400
    
    video_url = extract_video_url(player_url)
    
    if video_url:
        return jsonify({
            'success': True,
            'player_url': player_url,
            'video_url': video_url
        })
    else:
        return jsonify({
            'success': False,
            'player_url': player_url,
            'error': 'Video URL not found'
        }), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 API iniciada em http://localhost:5000")
    print("📝 Exemplo: http://localhost:5000/extract?url=https://playerembedapi.link/?v=kBJLtxCD3")
    app.run(debug=True, port=5000)
```

**Uso da API**:
```bash
# Testar
curl "http://localhost:5000/extract?url=https://playerembedapi.link/?v=kBJLtxCD3"

# Resposta
{
  "success": true,
  "player_url": "https://playerembedapi.link/?v=kBJLtxCD3",
  "video_url": "https://storage.googleapis.com/mediastorage/1768755384966/az8sfdbewst/81347747.mp4"
}
```

---

## 🎓 Resumo dos Exemplos

1. **Exemplo 1**: Script Python básico
2. **Exemplo 2**: Processar múltiplos vídeos
3. **Exemplo 3**: Integração Kotlin (MaxSeries)
4. **Exemplo 4**: Teste rápido CLI
5. **Exemplo 5**: Extrair e baixar vídeo
6. **Exemplo 6**: API REST com Flask

Todos os exemplos estão prontos para uso! 🚀
