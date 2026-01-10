#!/usr/bin/env python3
"""
Captura stream de vídeo do MegaEmbed
Foca em encontrar URLs .m3u8 ou .mp4 reais
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

MEGAEMBED_URL = "https://megaembed.link/e/3wnuij"

def is_video_url(url):
    """Verifica se é URL de vídeo real"""
    url_lower = url.lower()
    
    # Excluir
    excludes = ['yandex', 'google', 'facebook', 'analytics', '.js', '.css', 
                '.png', '.jpg', '.gif', '.ico', '.woff', 'fonts', 'ads']
    if any(x in url_lower for x in excludes):
        return False
    
    # Incluir
    includes = ['.m3u8', '.mp4', '.ts', 'master.txt', '/hls/', 'playlist.m3u8', 
                'index.m3u8', '/video/', 'stream']
    return any(x in url_lower for x in includes)

def capture():
    print("="*70)
    print("CAPTURA DE STREAM - MEGAEMBED")
    print("="*70)
    
    # Configurar para capturar TUDO
    seleniumwire_options = {
        'disable_encoding': True,
        'ignore_http_methods': [],
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    video_urls = []
    api_responses = []
    
    try:
        # 1. Carregar player
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(5)
        
        # 2. Verificar requisições iniciais
        print("\n[2] Requisições iniciais:")
        for req in driver.requests:
            if '/api/' in req.url:
                print(f"  [API] {req.url}")
                if req.response and req.response.body:
                    try:
                        body = req.response.body.decode('utf-8')
                        api_responses.append({"url": req.url, "body": body})
                        print(f"    Response: {body[:100]}...")
                    except:
                        pass
        
        # 3. Clicar para iniciar
        print("\n[3] Iniciando player...")
        
        # Clicar no body
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            print("  [+] Clique body")
        except:
            pass
        
        time.sleep(2)
        
        # Clicar em botões de play
        for sel in ["media-play-button", ".vds-play-button", "[aria-label*='Play']", "button"]:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                ActionChains(driver).move_to_element(elem).click().perform()
                print(f"  [+] Clique: {sel}")
                time.sleep(1)
            except:
                pass
        
        # 4. Monitorar por 90 segundos
        print("\n[4] Monitorando requisições (90s)...")
        print("    Procurando: .m3u8, .mp4, .ts, /hls/")
        print("-"*50)
        
        seen = set()
        
        for i in range(90):
            time.sleep(1)
            
            # Verificar todas as requisições
            for req in driver.requests:
                url = req.url
                
                if url in seen:
                    continue
                seen.add(url)
                
                # Verificar se é vídeo
                if is_video_url(url):
                    video_urls.append(url)
                    print(f"\n*** VÍDEO *** {url}")
                    
                    # Mostrar headers
                    if req.response:
                        print(f"    Status: {req.response.status_code}")
                        if req.response.headers:
                            ct = req.response.headers.get('Content-Type', '')
                            print(f"    Content-Type: {ct}")
                
                # Verificar APIs
                elif '/api/' in url and url not in [a['url'] for a in api_responses]:
                    if req.response and req.response.body:
                        try:
                            body = req.response.body.decode('utf-8')
                            api_responses.append({"url": url, "body": body})
                            print(f"\n[API] {url}")
                            print(f"    Body: {body[:150]}...")
                        except:
                            pass
            
            # Verificar elemento video
            try:
                src = driver.execute_script("""
                    var v = document.querySelector('video');
                    if (!v) return null;
                    
                    // Tentar src direto
                    if (v.src && !v.src.startsWith('blob:')) return v.src;
                    if (v.currentSrc && !v.currentSrc.startsWith('blob:')) return v.currentSrc;
                    
                    // Verificar source elements
                    var sources = v.querySelectorAll('source');
                    for (var s of sources) {
                        if (s.src && !s.src.startsWith('blob:')) return s.src;
                    }
                    
                    // Verificar se está usando blob (MediaSource)
                    if (v.src && v.src.startsWith('blob:')) {
                        return 'BLOB:' + v.src;
                    }
                    
                    return null;
                """)
                
                if src:
                    if src.startswith('BLOB:'):
                        if i == 30:  # Só mostrar uma vez
                            print(f"\n[!] Vídeo usa MediaSource (blob URL)")
                            print("    O vídeo é carregado via JavaScript, não URL direta")
                    elif src.startswith('http') and src not in video_urls:
                        video_urls.append(src)
                        print(f"\n*** VIDEO ELEMENT *** {src}")
            except:
                pass
            
            # Parar se encontrou vídeo válido
            valid = [v for v in video_urls if '.m3u8' in v or '.mp4' in v]
            if valid and i > 30:
                break
            
            if i % 20 == 0 and i > 0:
                print(f"\n  ... {i}s - {len(video_urls)} URLs de vídeo")
        
        # 5. Resultado
        print("\n" + "="*70)
        print("RESULTADO FINAL")
        print("="*70)
        
        # URLs válidas
        valid_urls = [v for v in video_urls if '.m3u8' in v or '.mp4' in v]
        
        if valid_urls:
            print(f"\n✓ URLs de Vídeo Válidas ({len(valid_urls)}):")
            for v in valid_urls:
                print(f"  {v}")
            
            # Testar no VLC
            print("\n[*] Testando no VLC...")
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, valid_urls[0]])
                print("[+] VLC aberto!")
            except:
                print(f"  vlc \"{valid_urls[0]}\"")
        else:
            print("\n✗ Nenhuma URL de vídeo .m3u8/.mp4 encontrada")
            
            if video_urls:
                print(f"\nOutras URLs capturadas ({len(video_urls)}):")
                for v in video_urls[:10]:
                    print(f"  {v}")
            
            print("\n[!] O MegaEmbed provavelmente usa:")
            print("    - Blob URLs (MediaSource API)")
            print("    - Criptografia no cliente")
            print("    - O WebView do CloudStream é a melhor opção")
        
        # APIs
        if api_responses:
            print(f"\n[APIs Capturadas] {len(api_responses)}")
            for api in api_responses:
                print(f"\n  {api['url']}")
                print(f"    {api['body'][:200]}")
        
        # Salvar
        with open("stream_capture.json", "w", encoding="utf-8") as f:
            json.dump({
                "video_urls": video_urls,
                "valid_urls": valid_urls,
                "api_responses": api_responses
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Salvo em stream_capture.json")
        
        return valid_urls
        
    finally:
        input("\nPressione ENTER para fechar o navegador...")
        driver.quit()


if __name__ == "__main__":
    capture()
