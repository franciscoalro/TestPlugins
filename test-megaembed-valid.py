#!/usr/bin/env python3
"""
Testa MegaEmbed com um vídeo válido
Primeiro busca um episódio no MaxSeries, depois testa o MegaEmbed
"""

import requests
import re
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def get_megaembed_from_maxseries():
    """Busca um link MegaEmbed válido do MaxSeries"""
    print("[*] Buscando episódio no MaxSeries...")
    
    # Página de uma série popular
    series_url = "https://www.maxseries.one/series/house-of-the-dragon/"
    
    resp = requests.get(series_url, headers=HEADERS)
    
    # Encontrar link de episódio
    ep_pattern = r'href="(https://www\.maxseries\.one/episodio/[^"]+)"'
    episodes = re.findall(ep_pattern, resp.text)
    
    if not episodes:
        print("[!] Nenhum episódio encontrado")
        return None
    
    ep_url = episodes[0]
    print(f"[+] Episódio: {ep_url}")
    
    # Buscar página do episódio
    ep_resp = requests.get(ep_url, headers=HEADERS)
    
    # Procurar link do PlayThree
    playthree_pattern = r'href="(https://playerthree\.online/embed/[^"]+)"'
    playthree_matches = re.findall(playthree_pattern, ep_resp.text)
    
    if playthree_matches:
        print(f"[+] PlayThree: {playthree_matches[0]}")
        return playthree_matches[0]
    
    # Procurar MegaEmbed direto
    mega_pattern = r'(https://megaembed\.[^"\']+)'
    mega_matches = re.findall(mega_pattern, ep_resp.text)
    
    if mega_matches:
        print(f"[+] MegaEmbed: {mega_matches[0]}")
        return mega_matches[0]
    
    return None


def capture_with_selenium(url):
    """Captura rede com Selenium"""
    print(f"\n[*] Capturando rede de: {url}")
    
    seleniumwire_options = {'disable_encoding': True}
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    video_urls = []
    api_data = []
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # Clicar em botões
        for selector in ["#play", ".play-button", "button[class*='play']", ".btn"]:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, selector)
                btn.click()
                print(f"  [+] Clicou: {selector}")
                time.sleep(2)
            except:
                pass
        
        print("[*] Aguardando 20s para carregar vídeo...")
        time.sleep(20)
        
        # Analisar requisições
        for req in driver.requests:
            url_lower = req.url.lower()
            
            # Capturar URLs de vídeo
            if any(ext in url_lower for ext in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                if '.js' not in url_lower:
                    video_urls.append(req.url)
                    print(f"  [VIDEO] {req.url}")
            
            # Capturar APIs
            if '/api/' in req.url and req.response:
                body = None
                if req.response.body:
                    try:
                        body = req.response.body.decode('utf-8', errors='ignore')
                    except:
                        pass
                api_data.append({
                    "url": req.url,
                    "status": req.response.status_code,
                    "body": body[:500] if body else None
                })
        
        # Capturar do elemento video
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            src = video.get_attribute("src") or video.get_attribute("currentSrc")
            if src and src.startswith("http"):
                video_urls.append(src)
                print(f"  [VIDEO ELEMENT] {src}")
        except:
            pass
        
        # JS variables
        js_vars = driver.execute_script("""
            var r = {};
            if (window.source) r.source = window.source;
            if (window.hls && window.hls.url) r.hlsUrl = window.hls.url;
            var v = document.querySelector('video');
            if (v) { r.videoSrc = v.src; r.currentSrc = v.currentSrc; }
            return r;
        """)
        
        return {
            "video_urls": list(set(video_urls)),
            "api_data": api_data,
            "js_vars": js_vars
        }
        
    finally:
        driver.quit()

def main():
    print("="*70)
    print("TESTE MEGAEMBED COM VÍDEO VÁLIDO")
    print("="*70)
    
    # Primeiro tentar buscar do MaxSeries
    source_url = get_megaembed_from_maxseries()
    
    if not source_url:
        # Usar URL de teste alternativa
        source_url = "https://megaembed.link/#YzEyMzQ1Njc4"
    
    result = capture_with_selenium(source_url)
    
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    
    if result["video_urls"]:
        print(f"\n[+] URLs de vídeo encontradas ({len(result['video_urls'])}):")
        for v in result["video_urls"]:
            print(f"  - {v}")
    else:
        print("\n[!] Nenhuma URL de vídeo encontrada")
    
    if result["api_data"]:
        print(f"\n[+] Dados da API:")
        for api in result["api_data"]:
            print(f"  URL: {api['url']}")
            print(f"  Status: {api['status']}")
            if api['body']:
                print(f"  Body: {api['body'][:100]}...")
    
    if result["js_vars"]:
        print(f"\n[+] Variáveis JS: {json.dumps(result['js_vars'], indent=2)}")
    
    # Salvar resultado
    with open("megaembed_valid_test.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n[*] Resultado salvo em megaembed_valid_test.json")

if __name__ == "__main__":
    main()
