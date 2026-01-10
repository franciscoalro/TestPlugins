#!/usr/bin/env python3
"""
Captura avançada de vídeo - Terra de Pecados
Simula interação completa com o player
"""

import json
import time
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains

# URL do episódio direto
EPISODE_URL = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"

def capture_video():
    print("="*60)
    print("CAPTURA AVANÇADA - TERRA DE PECADOS")
    print("="*60)
    
    seleniumwire_options = {
        'disable_encoding': True,
        'ignore_http_methods': ['OPTIONS']
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    # Remover webdriver flag
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        '''
    })
    
    video_urls = []
    all_requests = []
    
    try:
        # 1. Carregar episódio
        print(f"\n[1] Carregando: {EPISODE_URL}")
        driver.get(EPISODE_URL)
        time.sleep(5)
        
        # 2. Encontrar iframe do player
        print("\n[2] Procurando player iframe...")
        
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        player_url = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            print(f"  iframe: {src[:60]}...")
            if "playerthree" in src or "megaembed" in src or "embed" in src:
                player_url = src
                break
        
        if not player_url:
            # Tentar via JavaScript
            player_url = driver.execute_script("""
                var iframes = document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    var src = iframes[i].src || '';
                    if (src.includes('player') || src.includes('embed')) {
                        return src;
                    }
                }
                return null;
            """)
        
        if player_url:
            print(f"\n[+] Player: {player_url}")
            
            # 3. Navegar para o player
            print("\n[3] Abrindo player...")
            driver.get(player_url)
            time.sleep(5)
            
            # 4. Procurar e clicar em botões de fonte
            print("\n[4] Procurando fontes...")
            
            # Listar todos os botões
            buttons = driver.find_elements(By.CSS_SELECTOR, "button, [data-source], .btn, a.btn")
            print(f"  Encontrados {len(buttons)} botões")
            
            for btn in buttons:
                try:
                    text = btn.text or btn.get_attribute("data-source") or ""
                    onclick = btn.get_attribute("onclick") or ""
                    print(f"    - {text[:30]} | onclick: {onclick[:30]}")
                except:
                    pass
            
            # Clicar em botões que parecem fontes
            for btn in buttons:
                try:
                    text = (btn.text or "").lower()
                    data = (btn.get_attribute("data-source") or "").lower()
                    if "mega" in text or "mega" in data or "play" in text:
                        print(f"\n[+] Clicando: {text or data}")
                        ActionChains(driver).move_to_element(btn).click().perform()
                        time.sleep(3)
                        break
                except Exception as e:
                    print(f"  Erro: {e}")
            
            # 5. Verificar se há novo iframe
            print("\n[5] Verificando iframes internos...")
            
            inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in inner_iframes:
                src = iframe.get_attribute("src") or ""
                if src and "megaembed" in src:
                    print(f"  [+] MegaEmbed iframe: {src}")
                    driver.get(src)
                    time.sleep(5)
                    break
            
            # 6. Clicar no player para iniciar
            print("\n[6] Tentando iniciar player...")
            
            # Clicar no centro da página
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                ActionChains(driver).move_to_element(body).click().perform()
                time.sleep(2)
            except:
                pass
            
            # Procurar botão play
            play_selectors = [
                ".jw-icon-display",
                ".vjs-big-play-button", 
                "#play",
                ".play-btn",
                "[class*='play']",
                "video"
            ]
            
            for sel in play_selectors:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, sel)
                    ActionChains(driver).move_to_element(elem).click().perform()
                    print(f"  [+] Clicou: {sel}")
                    time.sleep(2)
                except:
                    pass
        
        # 7. Monitorar requisições por 60 segundos
        print("\n[7] Monitorando requisições (60s)...")
        
        for i in range(60):
            time.sleep(1)
            
            # Verificar elemento video
            try:
                video_src = driver.execute_script("""
                    var videos = document.querySelectorAll('video');
                    for (var v of videos) {
                        if (v.src && v.src.startsWith('http')) return v.src;
                        if (v.currentSrc && v.currentSrc.startsWith('http')) return v.currentSrc;
                    }
                    // Verificar source dentro de video
                    var sources = document.querySelectorAll('video source');
                    for (var s of sources) {
                        if (s.src && s.src.startsWith('http')) return s.src;
                    }
                    return null;
                """)
                if video_src and video_src not in video_urls:
                    if '.m3u8' in video_src or '.mp4' in video_src or 'master' in video_src:
                        video_urls.append(video_src)
                        print(f"\n[VIDEO] {video_src}")
            except:
                pass
            
            # Verificar requisições de rede
            for req in driver.requests:
                url = req.url
                if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master.txt', '/hls/', '/video/']):
                    if '.js' not in url.lower() and url not in video_urls:
                        video_urls.append(url)
                        print(f"\n[NET] {url}")
                        
                        # Capturar headers
                        if req.headers:
                            print(f"  Headers: {dict(req.headers)}")
            
            if video_urls and i > 15:
                print("\n[+] Vídeo encontrado!")
                break
            
            if i % 10 == 0:
                print(f"  ... {i}s")
        
        # 8. Capturar requisições importantes
        print("\n[8] Requisições capturadas:")
        
        for req in driver.requests:
            if any(x in req.url for x in ['megaembed', 'playerthree', '/api/', '.m3u8', '.mp4', 'master', 'hls']):
                req_info = {
                    "method": req.method,
                    "url": req.url,
                    "headers": dict(req.headers) if req.headers else {}
                }
                if req.response:
                    req_info["status"] = req.response.status_code
                    content_type = req.response.headers.get('Content-Type', '') if req.response.headers else ''
                    req_info["content_type"] = content_type
                    
                    # Capturar body de APIs
                    if '/api/' in req.url and req.response.body:
                        try:
                            body = req.response.body.decode('utf-8', errors='ignore')
                            req_info["body"] = body[:1000]
                        except:
                            pass
                
                all_requests.append(req_info)
                print(f"  [{req.method}] {req.url[:80]}")
        
        # 9. Resultado
        print("\n" + "="*60)
        print("RESULTADO FINAL")
        print("="*60)
        
        if video_urls:
            print(f"\n✓ URLs DE VÍDEO ({len(video_urls)}):")
            for v in video_urls:
                print(f"  {v}")
            
            # Testar com VLC
            print("\n[*] Testando com VLC...")
            try:
                import subprocess
                vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc_path, video_urls[0]], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                print("[+] VLC aberto!")
            except Exception as e:
                print(f"[!] VLC: {e}")
                print(f"\nComando manual: vlc \"{video_urls[0]}\"")
        else:
            print("\n✗ Nenhuma URL de vídeo encontrada")
            print("\nPossíveis causas:")
            print("  - Player usa DRM/proteção")
            print("  - Vídeo carrega via blob URL")
            print("  - Precisa de mais interação")
        
        # Salvar resultado
        result = {
            "video_urls": video_urls,
            "requests": all_requests
        }
        
        with open("video_capture_final.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Salvo em video_capture_final.json")
        
        return video_urls
        
    finally:
        input("\nPressione ENTER para fechar o navegador...")
        driver.quit()


if __name__ == "__main__":
    capture_video()
