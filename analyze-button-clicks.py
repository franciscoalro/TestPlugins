#!/usr/bin/env python3
"""
Analisa o que dispara ao clicar nos botões do player MegaEmbed
Foca em capturar a requisição /api/v1/info e o fluxo completo
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

# URL direta do MegaEmbed (baseado na captura)
MEGAEMBED_URL = "https://megaembed.link/"

def analyze_clicks():
    print("="*70)
    print("ANÁLISE DE CLIQUES - MEGAEMBED")
    print("="*70)
    
    seleniumwire_options = {
        'disable_encoding': True,
        'ignore_http_methods': ['OPTIONS']
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    captured_data = {
        "api_calls": [],
        "video_urls": [],
        "click_events": []
    }
    
    try:
        # 1. Primeiro, ir para o episódio e pegar o iframe do MegaEmbed
        print("\n[1] Carregando episódio...")
        driver.get("https://www.maxseries.one/episodio/terra-de-pecados-1x1/")
        time.sleep(4)
        
        # Encontrar iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        megaembed_url = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src") or ""
            if "playerthree" in src or "megaembed" in src:
                megaembed_url = src
                print(f"[+] Player encontrado: {src}")
                break
        
        if not megaembed_url:
            print("[!] Player não encontrado na página")
            return
        
        # 2. Navegar para o player
        print(f"\n[2] Abrindo player: {megaembed_url}")
        driver.get(megaembed_url)
        time.sleep(3)
        
        # Limpar requisições anteriores
        del driver.requests
        
        # 3. Analisar estrutura da página
        print("\n[3] Analisando estrutura...")
        
        page_info = driver.execute_script("""
            var info = {
                buttons: [],
                iframes: [],
                scripts: []
            };
            
            // Botões
            document.querySelectorAll('button, [data-source], [onclick]').forEach(function(el) {
                info.buttons.push({
                    tag: el.tagName,
                    text: el.innerText.substring(0, 50),
                    class: el.className,
                    dataSource: el.getAttribute('data-source'),
                    onclick: el.getAttribute('onclick')
                });
            });
            
            // Iframes
            document.querySelectorAll('iframe').forEach(function(el) {
                info.iframes.push(el.src);
            });
            
            return info;
        """)
        
        print(f"\n  Botões encontrados: {len(page_info['buttons'])}")
        for btn in page_info['buttons'][:10]:
            print(f"    - {btn}")
        
        print(f"\n  Iframes: {page_info['iframes']}")
        
        # 4. Verificar se há iframe do MegaEmbed dentro
        inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in inner_iframes:
            src = iframe.get_attribute("src") or ""
            if "megaembed" in src:
                print(f"\n[4] Entrando no iframe MegaEmbed: {src}")
                driver.get(src)
                time.sleep(3)
                del driver.requests
                break
        
        # 5. Agora estamos no MegaEmbed - analisar
        print("\n[5] Analisando MegaEmbed...")
        
        current_url = driver.current_url
        print(f"  URL atual: {current_url}")
        
        # Extrair ID do vídeo da URL
        video_id = None
        if "megaembed" in current_url:
            parts = current_url.split("/")
            for i, p in enumerate(parts):
                if p == "e" and i+1 < len(parts):
                    video_id = parts[i+1].split("?")[0]
                    break
        
        print(f"  Video ID: {video_id}")
        
        # 6. Monitorar cliques e requisições
        print("\n[6] Clicando no player e monitorando...")
        
        # Clicar no centro da página (geralmente inicia o player)
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            ActionChains(driver).move_to_element(body).click().perform()
            print("  [+] Clique no body")
            time.sleep(2)
        except:
            pass
        
        # Procurar e clicar em elementos de play
        play_selectors = [
            "media-play-button",
            ".vds-play-button",
            "[data-media-play-button]",
            "button[aria-label*='Play']",
            ".play-button",
            "video"
        ]
        
        for sel in play_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, sel)
                ActionChains(driver).move_to_element(elem).click().perform()
                print(f"  [+] Clique em: {sel}")
                time.sleep(2)
            except:
                pass
        
        # 7. Capturar requisições após cliques
        print("\n[7] Requisições capturadas após cliques:")
        
        for req in driver.requests:
            url = req.url
            
            # Filtrar requisições importantes
            if any(x in url for x in ['/api/', '/info', '.m3u8', '.mp4', 'master', 'hls', 'video']):
                req_data = {
                    "method": req.method,
                    "url": url,
                    "headers": dict(req.headers) if req.headers else {}
                }
                
                if req.response:
                    req_data["status"] = req.response.status_code
                    
                    # Capturar body da resposta
                    if req.response.body:
                        try:
                            body = req.response.body.decode('utf-8', errors='ignore')
                            req_data["response_body"] = body[:2000]
                            
                            # Se for JSON, parsear
                            if body.startswith('{') or body.startswith('['):
                                try:
                                    req_data["response_json"] = json.loads(body)
                                except:
                                    pass
                        except:
                            pass
                
                captured_data["api_calls"].append(req_data)
                
                print(f"\n  [{req.method}] {url}")
                if req.response:
                    print(f"    Status: {req.response.status_code}")
                if "response_body" in req_data:
                    print(f"    Body: {req_data['response_body'][:200]}...")
        
        # 8. Aguardar mais e verificar vídeo
        print("\n[8] Aguardando carregamento do vídeo (30s)...")
        
        for i in range(30):
            time.sleep(1)
            
            # Verificar elemento video
            video_src = driver.execute_script("""
                var v = document.querySelector('video');
                if (v) {
                    return {
                        src: v.src,
                        currentSrc: v.currentSrc,
                        readyState: v.readyState
                    };
                }
                return null;
            """)
            
            if video_src:
                src = video_src.get('src') or video_src.get('currentSrc')
                if src and src.startswith('http') and src not in captured_data["video_urls"]:
                    captured_data["video_urls"].append(src)
                    print(f"\n  [VIDEO] {src}")
            
            # Verificar novas requisições
            for req in driver.requests:
                url = req.url
                if any(x in url.lower() for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                    if '.js' not in url and url not in captured_data["video_urls"]:
                        captured_data["video_urls"].append(url)
                        print(f"\n  [NET VIDEO] {url}")
            
            if captured_data["video_urls"] and i > 10:
                break
            
            if i % 5 == 0:
                print(f"    ... {i}s")
        
        # 9. Resultado final
        print("\n" + "="*70)
        print("RESULTADO DA ANÁLISE")
        print("="*70)
        
        print(f"\n[API Calls] {len(captured_data['api_calls'])} requisições importantes")
        for api in captured_data['api_calls']:
            print(f"\n  {api['method']} {api['url']}")
            if 'response_json' in api:
                print(f"    JSON: {json.dumps(api['response_json'], indent=2)[:500]}")
        
        print(f"\n[Video URLs] {len(captured_data['video_urls'])}")
        for v in captured_data["video_urls"]:
            print(f"  {v}")
        
        # Salvar
        with open("button_click_analysis.json", "w", encoding="utf-8") as f:
            json.dump(captured_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Salvo em button_click_analysis.json")
        
        # Se encontrou vídeo, abrir no VLC
        if captured_data["video_urls"]:
            print("\n[*] Abrindo no VLC...")
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, captured_data["video_urls"][0]])
            except:
                print(f"  Comando: vlc \"{captured_data['video_urls'][0]}\"")
        
        return captured_data
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    analyze_clicks()
