#!/usr/bin/env python3
"""
Análise profunda do MegaEmbed - captura todas as requisições
"""

import subprocess
import time
import json
import re
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from seleniumwire import webdriver as wire_webdriver
except ImportError:
    print("Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium", "selenium-wire"], check=True)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from seleniumwire import webdriver as wire_webdriver

MEGAEMBED_URL = "https://megaembed.link/#Yzg0NjI0NjI="

def analyze_megaembed():
    print(f"\n[*] Analisando: {MEGAEMBED_URL}")
    
    options = {
        'disable_encoding': True,
        'suppress_connection_errors': True,
    }
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = wire_webdriver.Chrome(seleniumwire_options=options, options=chrome_options)
    
    try:
        driver.get(MEGAEMBED_URL)
        print("[*] Página carregada, aguardando...")
        time.sleep(5)
        
        # Clicar no play
        try:
            play = driver.find_element(By.CSS_SELECTOR, "#play, .play-button, button")
            play.click()
            print("[*] Clicou no play")
        except:
            pass
        
        time.sleep(10)
        
        print("\n[*] TODAS AS REQUISIÇÕES:")
        print("=" * 80)
        
        video_urls = []
        api_responses = []
        
        for req in driver.requests:
            url = req.url
            
            # Mostrar todas requisições relevantes
            if 'megaembed' in url or 'api' in url or '.m3u8' in url or '.mp4' in url:
                print(f"\n[REQ] {req.method} {url}")
                
                if req.response:
                    print(f"  Status: {req.response.status_code}")
                    content_type = req.response.headers.get('Content-Type', '')
                    print(f"  Content-Type: {content_type}")
                    
                    # Capturar resposta da API
                    if 'api' in url and req.response.body:
                        try:
                            body = req.response.body.decode('utf-8', errors='ignore')
                            print(f"  Body: {body[:500]}")
                            api_responses.append({'url': url, 'body': body})
                        except:
                            pass
            
            # Identificar URLs de vídeo
            if any(ext in url.lower() for ext in ['.m3u8', '.mp4', 'master.txt', '/hls/', '/stream/']):
                if '.js' not in url.lower():
                    video_urls.append(url)
        
        print("\n" + "=" * 80)
        
        # Analisar JavaScript da página
        print("\n[*] Analisando JavaScript...")
        js_vars = driver.execute_script("""
            var result = {};
            // Variáveis globais
            if (window.source) result.source = window.source;
            if (window.file) result.file = window.file;
            if (window.videoUrl) result.videoUrl = window.videoUrl;
            if (window.hls) result.hls = window.hls.url || 'HLS object exists';
            if (window.player) result.player = 'Player exists';
            
            // Elemento video
            var video = document.querySelector('video');
            if (video) {
                result.videoSrc = video.src;
                result.videoCurrentSrc = video.currentSrc;
            }
            
            return result;
        """)
        print(f"[*] Variáveis JS: {json.dumps(js_vars, indent=2)}")
        
        if video_urls:
            print(f"\n[+] URLs de vídeo encontradas:")
            for u in video_urls:
                print(f"  - {u}")
        else:
            print("\n[!] Nenhuma URL de vídeo direta encontrada")
            print("[!] O MegaEmbed descriptografa a URL via JavaScript AES")
            
            # Mostrar respostas da API
            if api_responses:
                print("\n[*] Respostas da API (podem conter dados criptografados):")
                for resp in api_responses:
                    print(f"\n  URL: {resp['url']}")
                    print(f"  Body: {resp['body'][:200]}...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_megaembed()
