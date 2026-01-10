#!/usr/bin/env python3
"""
Captura via Chrome DevTools Protocol - captura TODAS as requisições
"""

import json
import time
import subprocess
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

VIDEO_ID = "3wnuij"
MEGAEMBED_URL = f"https://megaembed.link/e/{VIDEO_ID}"

def capture_with_cdp():
    print("="*70)
    print("CAPTURA CDP - MEGAEMBED")
    print("="*70)
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Habilitar logging de performance
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.open = function() { return null; };
        '''
    })
    
    # Habilitar Network domain
    driver.execute_cdp_cmd('Network.enable', {})
    
    results = {"video_urls": [], "api_responses": [], "all_urls": []}
    
    try:
        # 1. Carregar página
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(5)
        
        # 2. Processar logs de performance
        print("\n[2] Analisando logs de rede...")
        
        def process_logs():
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    method = message.get('method', '')
                    params = message.get('params', {})
                    
                    if method == 'Network.requestWillBeSent':
                        url = params.get('request', {}).get('url', '')
                        if url:
                            results["all_urls"].append(url)
                            
                            # Verificar URLs de vídeo
                            if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master', '/hls/']):
                                if '.js' not in url and 'yandex' not in url:
                                    if url not in results["video_urls"]:
                                        results["video_urls"].append(url)
                                        print(f"\n  [VIDEO] {url}")
                            
                            # Verificar API
                            if '/api/' in url:
                                print(f"  [API] {url}")
                    
                    elif method == 'Network.responseReceived':
                        url = params.get('response', {}).get('url', '')
                        if '/api/' in url:
                            request_id = params.get('requestId')
                            try:
                                body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                results["api_responses"].append({
                                    "url": url,
                                    "body": body.get('body', '')[:1000]
                                })
                                print(f"  [API RESPONSE] {body.get('body', '')[:200]}...")
                            except:
                                pass
                                
                except Exception as e:
                    pass
        
        process_logs()
        
        # 3. Clicar para iniciar player
        print("\n[3] Iniciando player...")
        
        try:
            driver.execute_script("""
                // Remover overlays
                document.querySelectorAll('[class*="overlay"], [class*="popup"]').forEach(e => e.remove());
                
                // Clicar no player
                var playBtn = document.querySelector('media-play-button, .vds-play-button');
                if (playBtn) playBtn.click();
                
                var video = document.querySelector('video');
                if (video) {
                    video.click();
                    video.play();
                }
            """)
            print("  [+] Clique executado")
        except Exception as e:
            print(f"  [!] Erro: {e}")
        
        time.sleep(3)
        process_logs()
        
        # 4. Monitorar por mais tempo
        print("\n[4] Monitorando (45s)...")
        
        for i in range(45):
            time.sleep(1)
            process_logs()
            
            # Verificar video element
            video_src = driver.execute_script("""
                var v = document.querySelector('video');
                if (v && v.src && v.src.startsWith('http') && !v.src.startsWith('blob:')) {
                    return v.src;
                }
                return null;
            """)
            
            if video_src and video_src not in results["video_urls"]:
                results["video_urls"].append(video_src)
                print(f"\n  [VIDEO ELEMENT] {video_src}")
            
            if results["video_urls"] and i > 15:
                break
            
            if i % 10 == 0:
                print(f"  ... {i}s")
                # Tentar clicar novamente
                try:
                    driver.execute_script("""
                        var playBtn = document.querySelector('media-play-button');
                        if (playBtn) playBtn.click();
                    """)
                except:
                    pass
        
        # 5. Resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        print(f"\n[URLs capturadas] {len(results['all_urls'])} total")
        
        # Filtrar URLs interessantes
        interesting = [u for u in results["all_urls"] if any(x in u for x in ['megaembed', 'video', 'hls', 'm3u8', 'mp4', 'stream'])]
        print(f"\n[URLs interessantes] {len(interesting)}")
        for u in interesting[:20]:
            print(f"  {u[:100]}")
        
        valid_videos = [u for u in results["video_urls"] if '.m3u8' in u or '.mp4' in u]
        if valid_videos:
            print(f"\n[Video URLs] {len(valid_videos)}")
            for v in valid_videos:
                print(f"  {v}")
            
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, valid_videos[0]])
                print("\n[+] VLC aberto!")
            except:
                print(f"\n  vlc \"{valid_videos[0]}\"")
        else:
            print("\n[!] Nenhuma URL de vídeo encontrada")
        
        # Salvar
        with open("cdp_capture_result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        input("\nENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    capture_with_cdp()
