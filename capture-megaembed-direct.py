#!/usr/bin/env python3
"""
Captura direta do MegaEmbed - vai direto para o player e monitora a API
"""

import json
import time
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains

# ID do vídeo descoberto
VIDEO_ID = "3wnuij"
MEGAEMBED_URL = f"https://megaembed.link/e/{VIDEO_ID}"

def capture_megaembed():
    print("="*70)
    print(f"CAPTURA DIRETA MEGAEMBED - ID: {VIDEO_ID}")
    print("="*70)
    
    seleniumwire_options = {
        'disable_encoding': True,
    }
    
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
    
    results = {
        "api_info": None,
        "video_urls": [],
        "all_requests": []
    }
    
    try:
        # 1. Carregar MegaEmbed diretamente
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(3)
        
        # 2. Analisar página
        print("\n[2] Analisando página...")
        
        page_html = driver.page_source[:2000]
        print(f"  HTML (preview): {page_html[:500]}...")
        
        # 3. Verificar requisições iniciais
        print("\n[3] Requisições iniciais:")
        
        for req in driver.requests:
            url = req.url
            print(f"  [{req.method}] {url[:80]}")
            
            # Capturar API info
            if '/api/' in url or '/info' in url:
                req_data = {
                    "url": url,
                    "method": req.method,
                    "headers": dict(req.headers) if req.headers else {}
                }
                if req.response and req.response.body:
                    try:
                        body = req.response.body.decode('utf-8')
                        req_data["response"] = body
                        print(f"\n  [API RESPONSE] {body[:500]}")
                    except:
                        pass
                results["api_info"] = req_data
        
        # 4. Clicar para iniciar o player
        print("\n[4] Iniciando player...")
        
        # Limpar requisições
        del driver.requests
        
        # Clicar no player
        try:
            # Tentar clicar no botão de play do Vidstack
            play_btn = driver.find_element(By.CSS_SELECTOR, "media-play-button, .vds-play-button, button[aria-label*='Play']")
            play_btn.click()
            print("  [+] Clicou no botão play")
        except:
            # Clicar no centro
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                ActionChains(driver).move_to_element(body).click().perform()
                print("  [+] Clicou no body")
            except:
                pass
        
        time.sleep(3)
        
        # 5. Monitorar requisições após clique
        print("\n[5] Requisições após clique:")
        
        for req in driver.requests:
            url = req.url
            
            # Ignorar analytics e ads
            if any(x in url for x in ['yandex', 'google', 'facebook', 'analytics']):
                continue
                
            print(f"  [{req.method}] {url[:80]}")
            
            req_data = {
                "url": url,
                "method": req.method
            }
            
            if req.response:
                req_data["status"] = req.response.status_code
                content_type = ""
                if req.response.headers:
                    content_type = req.response.headers.get('Content-Type', '')
                req_data["content_type"] = content_type
                
                # Capturar body de APIs
                if req.response.body and ('/api/' in url or '.m3u8' in url or '.mp4' in url):
                    try:
                        body = req.response.body.decode('utf-8', errors='ignore')
                        req_data["body"] = body[:2000]
                        print(f"    Body: {body[:200]}...")
                    except:
                        pass
            
            results["all_requests"].append(req_data)
            
            # Verificar se é URL de vídeo
            if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                if '.js' not in url:
                    results["video_urls"].append(url)
                    print(f"\n  [VIDEO URL] {url}")
        
        # 6. Aguardar e monitorar mais
        print("\n[6] Monitorando por 45 segundos...")
        
        for i in range(45):
            time.sleep(1)
            
            # Verificar elemento video
            try:
                video_info = driver.execute_script("""
                    var v = document.querySelector('video');
                    if (v) {
                        return {
                            src: v.src,
                            currentSrc: v.currentSrc,
                            duration: v.duration,
                            paused: v.paused
                        };
                    }
                    return null;
                """)
                
                if video_info:
                    src = video_info.get('src') or video_info.get('currentSrc')
                    if src and src.startswith('http') and src not in results["video_urls"]:
                        results["video_urls"].append(src)
                        print(f"\n  [VIDEO ELEMENT] {src}")
                        print(f"    Duration: {video_info.get('duration')}")
            except:
                pass
            
            # Verificar novas requisições
            for req in driver.requests:
                url = req.url
                if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master', '/hls/', 'video']):
                    if '.js' not in url and 'yandex' not in url and url not in results["video_urls"]:
                        results["video_urls"].append(url)
                        print(f"\n  [NET] {url}")
                        
                        # Capturar headers da requisição
                        if req.headers:
                            print(f"    Headers: {dict(req.headers)}")
            
            if results["video_urls"] and i > 15:
                # Filtrar URLs válidas
                valid_urls = [u for u in results["video_urls"] if '.m3u8' in u or '.mp4' in u]
                if valid_urls:
                    print("\n  [+] URL de vídeo válida encontrada!")
                    break
            
            if i % 10 == 0:
                print(f"    ... {i}s")
        
        # 7. Resultado
        print("\n" + "="*70)
        print("RESULTADO")
        print("="*70)
        
        if results["api_info"]:
            print(f"\n[API Info]")
            print(f"  URL: {results['api_info'].get('url')}")
            if 'response' in results['api_info']:
                print(f"  Response: {results['api_info']['response'][:500]}")
        
        # Filtrar URLs de vídeo válidas
        valid_video_urls = [u for u in results["video_urls"] 
                          if ('.m3u8' in u or '.mp4' in u) and 'yandex' not in u]
        
        if valid_video_urls:
            print(f"\n[Video URLs] {len(valid_video_urls)}")
            for v in valid_video_urls:
                print(f"  {v}")
            
            # Testar no VLC
            print("\n[*] Testando no VLC...")
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, valid_video_urls[0]])
                print("[+] VLC aberto!")
            except Exception as e:
                print(f"[!] Erro VLC: {e}")
                print(f"  Comando: vlc \"{valid_video_urls[0]}\"")
        else:
            print("\n[!] Nenhuma URL de vídeo válida encontrada")
            print("\nTodas as URLs capturadas:")
            for u in results["video_urls"]:
                print(f"  {u[:100]}")
        
        # Salvar
        with open("megaembed_direct_capture.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Salvo em megaembed_direct_capture.json")
        
        return results
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    capture_megaembed()
