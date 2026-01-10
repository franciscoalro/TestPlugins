#!/usr/bin/env python3
"""
Captura completa - Terra de Pecados -> MegaEmbed
"""

import json
import time
import re
import requests
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

SERIES_URL = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"

def run_full_capture():
    print("="*60)
    print("CAPTURA COMPLETA - TERRA DE PECADOS")
    print("="*60)
    
    seleniumwire_options = {'disable_encoding': True}
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    video_urls = []
    all_requests = []
    
    try:
        # 1. Carregar página da série
        print("\n[1] Carregando série...")
        driver.get(SERIES_URL)
        time.sleep(3)
        
        # 2. Encontrar e clicar em um episódio
        print("\n[2] Procurando episódios...")
        
        # Procurar links de episódio
        ep_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='episodio']")
        if not ep_links:
            ep_links = driver.find_elements(By.CSS_SELECTOR, ".episodiotitle a")
        if not ep_links:
            ep_links = driver.find_elements(By.CSS_SELECTOR, "ul.episodios a")
        
        if ep_links:
            ep_url = ep_links[0].get_attribute("href")
            print(f"[+] Episódio: {ep_url}")
            driver.get(ep_url)
            time.sleep(3)
        else:
            print("[!] Buscando via iframe direto...")

        # 3. Procurar iframe do player
        print("\n[3] Procurando player...")
        
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        player_url = None
        
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and ("playerthree" in src or "megaembed" in src):
                player_url = src
                print(f"[+] Player iframe: {src}")
                break
        
        # 4. Navegar para o player
        if player_url:
            print("\n[4] Abrindo player...")
            driver.get(player_url)
            time.sleep(5)
        
        # 5. Clicar em botões de fonte
        print("\n[5] Clicando em fontes...")
        
        for selector in ["[data-source]", ".source-btn", "button", "#play"]:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in btns[:5]:
                    try:
                        text = btn.text or btn.get_attribute("data-source") or ""
                        if "mega" in text.lower() or not text:
                            btn.click()
                            print(f"[+] Clicou: {text[:30] if text else selector}")
                            time.sleep(3)
                    except:
                        pass
            except:
                pass
        
        # 6. Aguardar e capturar
        print("\n[6] Aguardando requisições (30s)...")
        
        for i in range(30):
            time.sleep(1)
            
            # Verificar video element
            try:
                video_src = driver.execute_script("""
                    var v = document.querySelector('video');
                    if (v) return v.currentSrc || v.src;
                    return null;
                """)
                if video_src and video_src.startswith('http'):
                    if '.m3u8' in video_src or '.mp4' in video_src:
                        video_urls.append(video_src)
                        print(f"\n[VIDEO ELEMENT] {video_src}")
            except:
                pass
            
            # Verificar requisições
            for req in driver.requests:
                url = req.url.lower()
                if any(x in url for x in ['.m3u8', '.mp4', 'master.txt']):
                    if '.js' not in url:
                        if req.url not in video_urls:
                            video_urls.append(req.url)
                            print(f"\n[VIDEO NET] {req.url}")
            
            if video_urls and i > 10:
                break
            
            if i % 5 == 0:
                print(f"  ... {i}s")
        
        # 7. Capturar todas requisições importantes
        print("\n[7] Analisando requisições...")
        
        for req in driver.requests:
            if any(x in req.url for x in ['megaembed', 'playerthree', '/api/', '.m3u8', '.mp4']):
                req_data = {
                    "method": req.method,
                    "url": req.url,
                    "headers": dict(req.headers) if req.headers else {}
                }
                if req.response:
                    req_data["status"] = req.response.status_code
                    if req.response.body:
                        try:
                            body = req.response.body.decode('utf-8', errors='ignore')
                            req_data["body"] = body[:500]
                        except:
                            pass
                all_requests.append(req_data)
                print(f"  [{req.method}] {req.url[:60]}...")
        
        # 8. Resultado
        print("\n" + "="*60)
        print("RESULTADO")
        print("="*60)
        
        if video_urls:
            print(f"\n[+] URLs DE VÍDEO ENCONTRADAS ({len(video_urls)}):")
            for v in video_urls:
                print(f"  {v}")
            
            # Gerar código HTTP
            print("\n[+] CÓDIGO PARA REPLICAR:")
            print(f'''
import requests

headers = {{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://megaembed.link/",
}}

video_url = "{video_urls[0]}"
resp = requests.get(video_url, headers=headers, stream=True)
print(f"Status: {{resp.status_code}}")
''')
        else:
            print("\n[!] Nenhuma URL de vídeo encontrada")
        
        # Salvar
        result = {
            "video_urls": video_urls,
            "requests": all_requests[:30]
        }
        with open("terra_pecados_capture.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Salvo em terra_pecados_capture.json")
        
        return video_urls
        
    finally:
        driver.quit()


if __name__ == "__main__":
    run_full_capture()
