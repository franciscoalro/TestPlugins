from playwright.sync_api import sync_playwright
import time

USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36"

def test_autoplay_flow(url):
    """
    Simula o fluxo completo do WebViewResolver com autoplay
    Mostra exatamente quando cada requisição acontece
    """
    print(f"\n{'='*70}")
    print(f"🎬 TESTANDO AUTOPLAY FLOW")
    print(f"{'='*70}\n")
    print(f"📍 URL: {url}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 412, 'height': 915}
        )
        page = context.new_page()
        
        # Log de requisições
        request_timeline = []
        start_time = time.time()
        
        def log_request(request):
            elapsed = int((time.time() - start_time) * 1000)
            url_str = request.url
            
            # Filtrar apenas requisições importantes
            if any(x in url_str for x in ['.m3u8', '.mp4', '.txt', 'video', 'stream']):
                print(f"T+{elapsed:04d}ms: 📡 {request.resource_type.upper():8s} {url_str[:80]}")
                request_timeline.append({
                    'time': elapsed,
                    'type': request.resource_type,
                    'url': url_str
                })
        
        page.on("request", log_request)
        
        # Console logs da página
        def log_console(msg):
            elapsed = int((time.time() - start_time) * 1000)
            print(f"T+{elapsed:04d}ms: 💬 CONSOLE: {msg.text}")
        
        page.on("console", log_console)
        
        # Navegar
        print(f"T+0000ms: 🌐 Carregando página...")
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        
        elapsed = int((time.time() - start_time) * 1000)
        print(f"T+{elapsed:04d}ms: ✅ DOM carregado\n")
        
        # Injetar script de autoplay (igual ao MegaEmbedExtractor)
        autoplay_script = """
        (function() {
            console.log("🎯 Script de autoplay injetado");
            
            var attempts = 0;
            var maxAttempts = 50; // 10 segundos
            
            function tryPlayVideo() {
                var vids = document.getElementsByTagName('video');
                console.log("🔍 Tentativa " + attempts + ": " + vids.length + " videos encontrados");
                
                for(var i=0; i<vids.length; i++){
                    var v = vids[i];
                    if(v.paused) {
                        console.log("▶️ Forçando play() no video " + i);
                        v.muted = true;
                        v.play().then(function() {
                            console.log("✅ Play iniciado com sucesso!");
                        }).catch(function(e) {
                            console.log("❌ Erro no play: " + e);
                        });
                    }
                }
            }
            
            var interval = setInterval(function() {
                attempts++;
                tryPlayVideo();
                
                if (attempts >= maxAttempts) {
                    clearInterval(interval);
                    console.log("⏱️ Timeout: autoplay não conseguiu iniciar");
                }
            }, 200);
        })()
        """
        
        print(f"T+{elapsed:04d}ms: 💉 Injetando script de autoplay...\n")
        page.evaluate(autoplay_script)
        
        # Aguardar 15 segundos observando
        print("⏳ Aguardando 15 segundos para observar requisições...\n")
        time.sleep(15)
        
        elapsed = int((time.time() - start_time) * 1000)
        print(f"\nT+{elapsed:04d}ms: ⏹️ Teste finalizado\n")
        
        # Resumo
        print("="*70)
        print("📊 RESUMO DO TESTE")
        print("="*70)
        
        video_requests = [r for r in request_timeline if '.m3u8' in r['url'] or '.mp4' in r['url']]
        
        if video_requests:
            print(f"✅ AUTOPLAY FUNCIONOU!")
            print(f"   Total de requisições de vídeo: {len(video_requests)}")
            print(f"   Primeira requisição em: T+{video_requests[0]['time']}ms")
            print(f"   URL capturada: {video_requests[0]['url'][:80]}...")
        else:
            print(f"❌ AUTOPLAY NÃO FUNCIONOU")
            print(f"   Nenhuma requisição de vídeo detectada")
            print(f"   Possíveis causas:")
            print(f"   - Página não tem elemento <video>")
            print(f"   - Player usa tecnologia diferente (Flash, etc)")
            print(f"   - Bloqueio de autoplay do navegador")
        
        print("="*70)
        
        browser.close()

if __name__ == "__main__":
    # Teste com o link que descobrimos
    test_url = "https://saborcaseiro.org/midiaflixhd.php?contentId=DF89A8DE7AF54EC27A1C5115CFC787C1B5B058F99EF34D240309CCB40876791311AFF6CE55992D53FC6D9D43BAF8BB15"
    
    print("\n🧪 Este script mostra EXATAMENTE quando o autoplay acontece")
    print("   e quando as requisições de vídeo começam.\n")
    
    test_autoplay_flow(test_url)
