#!/usr/bin/env python3
"""
Obtém o ID correto do MegaEmbed a partir do episódio
"""

import json
import time
import re
import subprocess
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

EPISODE_URL = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"

def get_megaembed_id():
    print("="*70)
    print("OBTENDO ID DO MEGAEMBED")
    print("="*70)
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1400, 900)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    try:
        # 1. Carregar episódio
        print(f"\n[1] Carregando: {EPISODE_URL}")
        driver.get(EPISODE_URL)
        time.sleep(5)
        
        # 2. Encontrar iframes
        print("\n[2] Procurando iframes...")
        
        iframes = driver.execute_script("""
            return Array.from(document.querySelectorAll('iframe')).map(f => ({
                src: f.src,
                id: f.id,
                class: f.className
            }));
        """)
        
        print(f"  Encontrados {len(iframes)} iframes:")
        for iframe in iframes:
            print(f"    {iframe}")
        
        # 3. Encontrar player iframe
        player_url = None
        for iframe in iframes:
            src = iframe.get('src', '')
            if 'playerthree' in src or 'megaembed' in src:
                player_url = src
                break
        
        if not player_url:
            # Tentar via data attributes
            player_url = driver.execute_script("""
                var el = document.querySelector('[data-src*="player"], [data-url*="player"]');
                return el ? (el.getAttribute('data-src') || el.getAttribute('data-url')) : null;
            """)
        
        print(f"\n[3] Player URL: {player_url}")
        
        if player_url:
            # 4. Navegar para o player
            print(f"\n[4] Abrindo player...")
            driver.get(player_url)
            time.sleep(3)
            
            # 5. Procurar iframe do MegaEmbed dentro do player
            print("\n[5] Procurando MegaEmbed...")
            
            inner_iframes = driver.execute_script("""
                return Array.from(document.querySelectorAll('iframe')).map(f => f.src);
            """)
            
            print(f"  Iframes internos: {inner_iframes}")
            
            megaembed_url = None
            for src in inner_iframes:
                if 'megaembed' in src:
                    megaembed_url = src
                    break
            
            # Também verificar botões de fonte
            sources = driver.execute_script("""
                return Array.from(document.querySelectorAll('[data-source], button, .source-btn')).map(el => ({
                    text: el.innerText,
                    dataSource: el.getAttribute('data-source'),
                    onclick: el.getAttribute('onclick')
                }));
            """)
            
            print(f"\n  Fontes disponíveis:")
            for s in sources[:10]:
                print(f"    {s}")
            
            if megaembed_url:
                print(f"\n[+] MegaEmbed URL: {megaembed_url}")
                
                # Extrair ID
                match = re.search(r'/e/([a-zA-Z0-9]+)', megaembed_url)
                if match:
                    video_id = match.group(1)
                    print(f"[+] Video ID: {video_id}")
                    
                    # Navegar para MegaEmbed
                    print(f"\n[6] Abrindo MegaEmbed...")
                    driver.get(megaembed_url)
                    time.sleep(5)
                    
                    # Verificar se carregou
                    title = driver.title
                    print(f"  Title: {title}")
                    
                    if "404" not in title:
                        print("\n[+] MegaEmbed carregado com sucesso!")
                        
                        # Verificar player
                        has_player = driver.execute_script("""
                            return {
                                hasVideo: !!document.querySelector('video'),
                                hasMediaPlayer: !!document.querySelector('media-player'),
                                bodyLength: document.body.innerHTML.length
                            };
                        """)
                        print(f"  Player: {has_player}")
                    else:
                        print("\n[!] MegaEmbed retornou 404")
            else:
                print("\n[!] MegaEmbed não encontrado nos iframes")
                
                # Verificar se há link direto no HTML
                html = driver.page_source
                megaembed_matches = re.findall(r'megaembed\.link/e/([a-zA-Z0-9]+)', html)
                if megaembed_matches:
                    print(f"\n[+] IDs encontrados no HTML: {megaembed_matches}")
        
        # Manter navegador aberto para debug
        print("\n" + "="*70)
        print("Navegador aberto - verifique manualmente")
        print("="*70)
        
        input("\nENTER para fechar...")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    get_megaembed_id()
