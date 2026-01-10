#!/usr/bin/env python3
"""
Captura MegaEmbed SEM ADS - Bloqueia ads e intercepta API diretamente
"""

import json
import time
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

VIDEO_ID = "3wnuij"
MEGAEMBED_URL = f"https://megaembed.link/e/{VIDEO_ID}"

# Lista de domínios de ads para bloquear
AD_DOMAINS = [
    'doubleclick', 'googlesyndication', 'googleadservices', 'google-analytics',
    'facebook', 'fbcdn', 'twitter', 'analytics', 'adservice', 'adsense',
    'popads', 'popcash', 'propellerads', 'exoclick', 'juicyads', 'trafficjunky',
    'adsterra', 'hilltopads', 'clickadu', 'pushground', 'evadav', 'monetag',
    'yandex.ru/watch', 'mc.yandex', 'entrapsoorki', 'cdn-cgi/rum'
]

def block_ads(request):
    """Intercepta e bloqueia requisições de ads"""
    url = request.url.lower()
    
    # Bloquear domínios de ads
    for ad in AD_DOMAINS:
        if ad in url:
            request.abort()
            return
    
    # Bloquear por padrão de URL
    if any(x in url for x in ['/ads/', '/ad/', 'banner', 'popup', 'popunder']):
        request.abort()
        return

def capture_without_ads():
    print("="*70)
    print("CAPTURA MEGAEMBED - SEM ADS")
    print("="*70)
    
    seleniumwire_options = {
        'disable_encoding': True,
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Bloquear notificações e popups
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.popups": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    # Configurar interceptador de ads
    driver.request_interceptor = block_ads
    
    # Remover webdriver flag
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // Bloquear popups
            window.open = function() { return null; };
            // Bloquear alerts
            window.alert = function() {};
            window.confirm = function() { return true; };
        '''
    })
    
    results = {
        "api_response": None,
        "video_urls": [],
        "decrypted_data": None
    }
    
    try:
        # 1. Carregar página
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(3)
        
        # 2. Remover overlays de ads via JavaScript
        print("\n[2] Removendo overlays de ads...")
        driver.execute_script("""
            // Remover elementos de ads
            var adSelectors = [
                '[class*="ad"]', '[id*="ad"]', '[class*="popup"]', '[id*="popup"]',
                '[class*="overlay"]', '[class*="banner"]', 'iframe[src*="ad"]',
                '[class*="modal"]', '[style*="z-index: 9999"]', '[style*="z-index:9999"]'
            ];
            adSelectors.forEach(function(sel) {
                document.querySelectorAll(sel).forEach(function(el) {
                    if (!el.querySelector('video')) {
                        el.remove();
                    }
                });
            });
            
            // Remover event listeners de click que abrem popups
            document.body.onclick = null;
            document.onclick = null;
        """)
        
        # 3. Interceptar chamada da API via JavaScript
        print("\n[3] Interceptando API via JavaScript...")
        
        api_data = driver.execute_script("""
            return new Promise(function(resolve) {
                // Fazer chamada direta à API
                var videoId = window.location.pathname.split('/').pop() || '""" + VIDEO_ID + """';
                
                fetch('/api/v1/info?id=' + videoId)
                    .then(function(r) { return r.text(); })
                    .then(function(data) {
                        resolve({
                            id: videoId,
                            raw_response: data,
                            url: '/api/v1/info?id=' + videoId
                        });
                    })
                    .catch(function(e) {
                        resolve({error: e.toString()});
                    });
            });
        """)
        
        if api_data:
            print(f"\n[API Response]")
            print(f"  ID: {api_data.get('id')}")
            print(f"  Raw: {str(api_data.get('raw_response', ''))[:200]}...")
            results["api_response"] = api_data
        
        # 4. Tentar extrair URL do vídeo via JavaScript do player
        print("\n[4] Extraindo URL do vídeo via JS...")
        
        video_data = driver.execute_script("""
            // Aguardar player carregar
            return new Promise(function(resolve) {
                var attempts = 0;
                var maxAttempts = 30;
                
                function checkVideo() {
                    attempts++;
                    
                    // Verificar elemento video
                    var video = document.querySelector('video');
                    if (video && (video.src || video.currentSrc)) {
                        var src = video.src || video.currentSrc;
                        if (src.startsWith('http')) {
                            resolve({
                                type: 'video_element',
                                url: src,
                                duration: video.duration
                            });
                            return;
                        }
                    }
                    
                    // Verificar se há player Vidstack
                    var mediaPlayer = document.querySelector('media-player');
                    if (mediaPlayer) {
                        var src = mediaPlayer.getAttribute('src');
                        if (src) {
                            resolve({
                                type: 'media_player',
                                url: src
                            });
                            return;
                        }
                    }
                    
                    // Verificar variáveis globais
                    if (window.playerConfig) {
                        resolve({
                            type: 'playerConfig',
                            data: window.playerConfig
                        });
                        return;
                    }
                    
                    if (window.videoUrl) {
                        resolve({
                            type: 'videoUrl',
                            url: window.videoUrl
                        });
                        return;
                    }
                    
                    if (attempts < maxAttempts) {
                        setTimeout(checkVideo, 1000);
                    } else {
                        resolve({type: 'timeout', attempts: attempts});
                    }
                }
                
                // Simular clique para iniciar
                setTimeout(function() {
                    var video = document.querySelector('video');
                    if (video) video.click();
                    
                    var playBtn = document.querySelector('media-play-button, .vds-play-button');
                    if (playBtn) playBtn.click();
                }, 2000);
                
                checkVideo();
            });
        """)
        
        print(f"\n[Video Data] {video_data}")
        
        if video_data and video_data.get('url'):
            results["video_urls"].append(video_data['url'])
        
        # 5. Monitorar requisições de rede
        print("\n[5] Monitorando requisições (30s)...")
        
        for i in range(30):
            time.sleep(1)
            
            for req in driver.requests:
                url = req.url
                
                # Verificar URLs de vídeo
                if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                    if '.js' not in url and url not in results["video_urls"]:
                        # Verificar se não é ad
                        is_ad = any(ad in url.lower() for ad in AD_DOMAINS)
                        if not is_ad:
                            results["video_urls"].append(url)
                            print(f"\n  [VIDEO] {url}")
                            
                            # Capturar headers
                            if req.headers:
                                print(f"    Referer: {req.headers.get('Referer', 'N/A')}")
                
                # Capturar resposta da API
                if '/api/' in url and req.response and req.response.body:
                    try:
                        body = req.response.body.decode('utf-8')
                        print(f"\n  [API] {url}")
                        print(f"    Response: {body[:300]}...")
                        results["api_response"] = {
                            "url": url,
                            "body": body
                        }
                    except:
                        pass
            
            if results["video_urls"] and i > 10:
                break
            
            if i % 5 == 0:
                print(f"    ... {i}s")
        
        # 6. Resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        if results["api_response"]:
            print(f"\n[API]")
            print(f"  {results['api_response']}")
        
        valid_urls = [u for u in results["video_urls"] if '.m3u8' in u or '.mp4' in u]
        
        if valid_urls:
            print(f"\n[Video URLs] {len(valid_urls)}")
            for v in valid_urls:
                print(f"  {v}")
            
            # VLC
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, valid_urls[0]])
                print("\n[+] VLC aberto!")
            except:
                print(f"\n  vlc \"{valid_urls[0]}\"")
        else:
            print("\n[!] Nenhuma URL de vídeo encontrada")
        
        # Salvar
        with open("capture_no_ads_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        input("\nENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    capture_without_ads()
