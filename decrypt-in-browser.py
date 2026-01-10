#!/usr/bin/env python3
"""
Descriptografa dados do MegaEmbed executando o JavaScript no navegador
e captura a URL do vídeo após descriptografia
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

def decrypt_and_capture():
    print("="*70)
    print("DESCRIPTOGRAFIA NO NAVEGADOR - MEGAEMBED")
    print("="*70)
    
    seleniumwire_options = {'disable_encoding': True}
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    results = {"video_url": None, "decrypted_data": None}
    
    try:
        # 1. Carregar página
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(5)
        
        # 2. Injetar interceptador para capturar dados descriptografados
        print("\n[2] Injetando interceptador...")
        
        driver.execute_script("""
            // Interceptar quando o player receber a URL do vídeo
            window.__capturedVideoUrl = null;
            window.__capturedData = null;
            
            // Interceptar fetch para capturar resposta descriptografada
            const originalFetch = window.fetch;
            window.fetch = async function(...args) {
                const response = await originalFetch.apply(this, args);
                const url = args[0];
                
                // Clonar response para ler o body
                const clone = response.clone();
                
                if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('master')) {
                    window.__capturedVideoUrl = url;
                    console.log('[INTERCEPTED VIDEO URL]', url);
                }
                
                return response;
            };
            
            // Interceptar XMLHttpRequest
            const originalXHR = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url) {
                this._url = url;
                if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('master')) {
                    window.__capturedVideoUrl = url;
                    console.log('[XHR VIDEO URL]', url);
                }
                return originalXHR.apply(this, arguments);
            };
            
            // Observar mudanças no DOM para capturar video src
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.tagName === 'VIDEO' || node.tagName === 'SOURCE') {
                            var src = node.src || node.currentSrc;
                            if (src && src.startsWith('http')) {
                                window.__capturedVideoUrl = src;
                                console.log('[DOM VIDEO]', src);
                            }
                        }
                    });
                });
            });
            observer.observe(document.body, {childList: true, subtree: true});
            
            // Interceptar atribuição de src em video
            const videoProto = HTMLVideoElement.prototype;
            const srcDescriptor = Object.getOwnPropertyDescriptor(videoProto, 'src');
            if (srcDescriptor) {
                Object.defineProperty(videoProto, 'src', {
                    set: function(value) {
                        if (value && value.startsWith('http')) {
                            window.__capturedVideoUrl = value;
                            console.log('[VIDEO SRC SET]', value);
                        }
                        return srcDescriptor.set.call(this, value);
                    },
                    get: srcDescriptor.get
                });
            }
        """)
        
        # 3. Aguardar carregamento e capturar
        print("\n[3] Aguardando descriptografia (60s)...")
        
        for i in range(60):
            time.sleep(1)
            
            # Verificar URL capturada via interceptador
            captured = driver.execute_script("return window.__capturedVideoUrl;")
            if captured:
                print(f"\n[+] URL CAPTURADA: {captured}")
                results["video_url"] = captured
                break
            
            # Verificar elemento video diretamente
            video_src = driver.execute_script("""
                var v = document.querySelector('video');
                if (v) {
                    var src = v.src || v.currentSrc;
                    if (src && src.startsWith('http') && !src.startsWith('blob:')) {
                        return src;
                    }
                }
                // Verificar media-player (Vidstack)
                var mp = document.querySelector('media-player');
                if (mp) {
                    var src = mp.getAttribute('src');
                    if (src && src.startsWith('http')) return src;
                }
                return null;
            """)
            
            if video_src:
                print(f"\n[+] VIDEO ELEMENT: {video_src}")
                results["video_url"] = video_src
                break
            
            # Verificar requisições de rede
            for req in driver.requests:
                url = req.url.lower()
                if any(x in url for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                    if '.js' not in url and 'yandex' not in url:
                        print(f"\n[+] NET REQUEST: {req.url}")
                        results["video_url"] = req.url
                        break
            
            if results["video_url"]:
                break
            
            if i % 10 == 0:
                print(f"  ... {i}s")
                
                # Tentar clicar para iniciar
                if i == 10 or i == 20:
                    try:
                        driver.execute_script("""
                            // Clicar no player
                            var playBtn = document.querySelector('media-play-button, .vds-play-button, [aria-label*="Play"]');
                            if (playBtn) playBtn.click();
                            
                            var video = document.querySelector('video');
                            if (video) video.click();
                        """)
                        print("  [clique no player]")
                    except:
                        pass
        
        # 4. Tentar extrair dados descriptografados do JavaScript
        print("\n[4] Extraindo dados do player...")
        
        player_data = driver.execute_script("""
            // Tentar encontrar dados do player
            var data = {};
            
            // Verificar variáveis globais comuns
            if (window.playerConfig) data.playerConfig = window.playerConfig;
            if (window.videoConfig) data.videoConfig = window.videoConfig;
            if (window.sources) data.sources = window.sources;
            if (window.hlsUrl) data.hlsUrl = window.hlsUrl;
            if (window.videoUrl) data.videoUrl = window.videoUrl;
            
            // Verificar Vidstack player
            var mp = document.querySelector('media-player');
            if (mp) {
                data.mediaPlayer = {
                    src: mp.getAttribute('src'),
                    currentSrc: mp.currentSrc,
                    state: mp.state
                };
            }
            
            // Verificar video element
            var v = document.querySelector('video');
            if (v) {
                data.video = {
                    src: v.src,
                    currentSrc: v.currentSrc,
                    duration: v.duration,
                    readyState: v.readyState
                };
            }
            
            return data;
        """)
        
        print(f"  Player data: {json.dumps(player_data, indent=2)}")
        results["decrypted_data"] = player_data
        
        # 5. Resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        if results["video_url"]:
            print(f"\n✓ VIDEO URL: {results['video_url']}")
            
            # Abrir no VLC
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, results["video_url"]])
                print("[+] VLC aberto!")
            except:
                print(f"\n  vlc \"{results['video_url']}\"")
        else:
            print("\n✗ URL não encontrada")
            print("\nO MegaEmbed pode estar usando:")
            print("  - Blob URLs (não interceptáveis)")
            print("  - MSE (Media Source Extensions)")
            print("  - DRM protection")
        
        # Salvar
        with open("decrypt_browser_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        input("\nENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    decrypt_and_capture()
