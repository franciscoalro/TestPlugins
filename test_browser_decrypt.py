import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("="*60)
print("DECRIPTAR NO BROWSER - INTERCEPTAR RESULTADO")
print("="*60)

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

driver = webdriver.Chrome(options=chrome_options)

# Habilitar interceptação de rede
driver.execute_cdp_cmd("Network.enable", {})

# Interceptar e modificar respostas
driver.execute_cdp_cmd("Network.setRequestInterception", {"patterns": [{"urlPattern": "*"}]})

results = []

try:
    print("\n[1] Acessando MegaEmbed...")
    driver.get("https://megaembed.link/#3wnuij")
    time.sleep(3)
    
    # Injetar código para capturar a resposta decriptada
    print("\n[2] Injetando interceptador...")
    driver.execute_script("""
        // Interceptar fetch
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            const response = await originalFetch.apply(this, args);
            const url = args[0];
            
            if (url.includes('api/v1/video')) {
                const clone = response.clone();
                const text = await clone.text();
                console.log('MEGAEMBED_API_RAW:', text);
                
                // Armazenar para acesso posterior
                window.__megaembedRaw = text;
            }
            return response;
        };
        
        // Interceptar XMLHttpRequest
        const originalXHR = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            this._url = url;
            return originalXHR.apply(this, arguments);
        };
        
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            this.addEventListener('load', function() {
                if (this._url && this._url.includes('api/v1/video')) {
                    console.log('MEGAEMBED_XHR_RAW:', this.responseText);
                    window.__megaembedXHR = this.responseText;
                }
            });
            return originalSend.apply(this, arguments);
        };
        
        console.log('Interceptadores instalados!');
    """)
    
    # Recarregar para aplicar interceptadores
    print("\n[3] Recarregando pagina...")
    driver.refresh()
    time.sleep(5)
    
    # Verificar se capturou algo
    print("\n[4] Verificando capturas...")
    
    raw_response = driver.execute_script("return window.__megaembedRaw || window.__megaembedXHR || null;")
    if raw_response:
        print(f"  Resposta raw capturada: {raw_response[:200]}...")
    
    # Buscar nos logs do console
    logs = driver.get_log("browser")
    for log in logs:
        msg = log.get("message", "")
        if "MEGAEMBED" in msg:
            print(f"  Log: {msg[:300]}...")
    
    # Tentar extrair dados decriptados do player
    print("\n[5] Buscando dados do player...")
    
    player_data = driver.execute_script("""
        // Buscar variáveis globais do player
        var data = {};
        
        // Tentar diferentes variáveis conhecidas
        if (window.player) data.player = JSON.stringify(window.player);
        if (window.videoData) data.videoData = JSON.stringify(window.videoData);
        if (window.sources) data.sources = JSON.stringify(window.sources);
        if (window.hlsUrl) data.hlsUrl = window.hlsUrl;
        if (window.videoUrl) data.videoUrl = window.videoUrl;
        
        // Buscar no localStorage
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            if (key.includes('video') || key.includes('player') || key.includes('hls')) {
                data['ls_' + key] = localStorage.getItem(key);
            }
        }
        
        // Buscar elementos video
        var videos = document.querySelectorAll('video');
        data.videoElements = [];
        videos.forEach(function(v) {
            data.videoElements.push({
                src: v.src,
                currentSrc: v.currentSrc
            });
        });
        
        // Buscar sources em scripts
        var scripts = document.querySelectorAll('script');
        scripts.forEach(function(s) {
            var text = s.textContent || s.innerText;
            if (text.includes('.m3u8') || text.includes('cf-master')) {
                data.scriptWithM3u8 = text.substring(0, 500);
            }
        });
        
        return data;
    """)
    
    print(f"  Player data: {json.dumps(player_data, indent=2)}")
    
    # Aguardar mais e verificar network
    print("\n[6] Monitorando rede por 30s...")
    
    for i in range(15):
        time.sleep(2)
        
        # Verificar logs de performance
        perf_logs = driver.get_log("performance")
        for entry in perf_logs:
            try:
                msg = json.loads(entry["message"])["message"]
                if msg["method"] == "Network.responseReceived":
                    url = msg["params"]["response"]["url"]
                    if any(x in url for x in [".m3u8", "cf-master", "master.txt", ".ts"]):
                        print(f"\n  [M3U8 ENCONTRADO] {url}")
                        results.append(url)
            except:
                pass
        
        if results:
            break
        print(f"  Aguardando... ({i+1}/15)")
    
    # Resultado final
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    
    if results:
        print("\nURLs M3U8 encontradas:")
        for url in results:
            print(f"  {url}")
    else:
        print("\nNenhum M3U8 capturado via rede")
        print("O player pode usar blob: URLs")
        
        # Verificar blob URLs
        blob_src = driver.execute_script("""
            var video = document.querySelector('video');
            return video ? video.src : null;
        """)
        if blob_src:
            print(f"\nVideo src: {blob_src}")

except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("\nENTER para fechar...")
    driver.quit()
