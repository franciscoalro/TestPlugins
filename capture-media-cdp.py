#!/usr/bin/env python3
"""
Captura URLs de mídia usando Chrome DevTools Protocol
Monitora Network.responseReceived para encontrar .m3u8 e .mp4
"""

import json
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# Player MegaEmbed
MEGAEMBED_URL = "https://megaembed.link/e/3wnuij"

def capture_media():
    print("="*70)
    print("CAPTURA DE MÍDIA VIA CDP")
    print("="*70)
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    # Habilitar Network domain
    driver.execute_cdp_cmd('Network.enable', {})
    
    video_urls = []
    all_media = []
    
    try:
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(5)
        
        # Clicar para iniciar
        print("\n[2] Iniciando player...")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            time.sleep(2)
        except:
            pass
        
        # Clicar em play
        for sel in ["media-play-button", ".vds-play-button", "button"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                ActionChains(driver).move_to_element(elem).click().perform()
                print(f"  [+] Clique: {sel}")
                time.sleep(1)
            except:
                pass
        
        # Monitorar logs de performance
        print("\n[3] Monitorando requisições de mídia (60s)...")
        
        seen_urls = set()
        
        for i in range(60):
            time.sleep(1)
            
            # Pegar logs de performance
            logs = driver.get_log("performance")
            
            for log in logs:
                try:
                    msg = json.loads(log["message"])["message"]
                    method = msg.get("method", "")
                    params = msg.get("params", {})
                    
                    # Verificar requisições de rede
                    if method in ["Network.requestWillBeSent", "Network.responseReceived"]:
                        url = ""
                        if "request" in params:
                            url = params["request"].get("url", "")
                        elif "response" in params:
                            url = params["response"].get("url", "")
                        
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            
                            # Filtrar URLs de mídia
                            url_lower = url.lower()
                            
                            # Ignorar analytics e recursos
                            if any(x in url_lower for x in ['yandex', 'google', 'facebook', '.js', '.css', '.png', '.jpg', '.gif', '.ico']):
                                continue
                            
                            # Capturar mídia
                            if any(x in url_lower for x in ['.m3u8', '.mp4', '.ts', 'master', '/hls/', 'playlist', 'video', 'stream']):
                                video_urls.append(url)
                                print(f"\n  [MEDIA] {url}")
                                
                                # Capturar headers
                                if "response" in params:
                                    headers = params["response"].get("headers", {})
                                    content_type = headers.get("content-type", headers.get("Content-Type", ""))
                                    if content_type:
                                        print(f"    Content-Type: {content_type}")
                                
                                all_media.append({
                                    "url": url,
                                    "method": method
                                })
                            
                            # Capturar APIs
                            elif '/api/' in url or '/info' in url:
                                print(f"\n  [API] {url}")
                                all_media.append({"url": url, "type": "api"})
                                
                except Exception as e:
                    pass
            
            # Verificar elemento video
            try:
                video_src = driver.execute_script("""
                    var v = document.querySelector('video');
                    if (v) {
                        // Tentar pegar src de várias formas
                        var src = v.src || v.currentSrc;
                        
                        // Verificar MediaSource
                        if (!src || src.startsWith('blob:')) {
                            // Tentar pegar do player
                            if (window.player && window.player.getPlaylistItem) {
                                var item = window.player.getPlaylistItem();
                                if (item && item.file) return item.file;
                            }
                        }
                        return src;
                    }
                    return null;
                """)
                
                if video_src and video_src.startswith('http') and video_src not in video_urls:
                    video_urls.append(video_src)
                    print(f"\n  [VIDEO ELEMENT] {video_src}")
            except:
                pass
            
            # Verificar se encontrou vídeo válido
            valid = [v for v in video_urls if '.m3u8' in v or '.mp4' in v]
            if valid and i > 20:
                break
            
            if i % 15 == 0:
                print(f"  ... {i}s ({len(video_urls)} URLs)")
        
        # Resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        # Filtrar URLs válidas
        valid_urls = [v for v in video_urls if '.m3u8' in v or '.mp4' in v]
        
        print(f"\n[URLs de Vídeo] {len(valid_urls)}")
        for v in valid_urls:
            print(f"  {v}")
        
        if not valid_urls:
            print("\n[!] Nenhuma URL de vídeo encontrada")
            print("\nTodas as URLs capturadas:")
            for v in video_urls[:20]:
                print(f"  {v}")
        
        # Salvar
        with open("media_cdp_capture.json", "w", encoding="utf-8") as f:
            json.dump({
                "video_urls": video_urls,
                "valid_urls": valid_urls,
                "all_media": all_media
            }, f, indent=2)
        
        # Testar no VLC
        if valid_urls:
            print("\n[*] Abrindo no VLC...")
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, valid_urls[0]])
            except:
                print(f"  vlc \"{valid_urls[0]}\"")
        
        return valid_urls
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    capture_media()
