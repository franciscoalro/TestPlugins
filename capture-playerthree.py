#!/usr/bin/env python3
"""
Acessa diretamente o playerthree.online para analisar estrutura
"""

import json
import time
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def analyze_playerthree():
    print("="*60)
    print("ANÁLISE PLAYERTHREE.ONLINE")
    print("="*60)
    
    # Primeiro, tentar via requests
    print("\n1. Tentando via requests...")
    
    url = "https://playerthree.online/embed/synden/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.maxseries.one/',
        'Accept': 'text/html,application/xhtml+xml',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f"   Status: {resp.status_code}")
        print(f"   Tamanho: {len(resp.text)} chars")
        
        # Salvar HTML
        with open('playerthree_html.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("   HTML salvo em playerthree_html.html")
        
        # Procurar data-source
        import re
        sources = re.findall(r'data-source="([^"]+)"', resp.text)
        print(f"\n   Sources encontrados: {len(sources)}")
        for s in sources[:10]:
            print(f"     - {s[:60]}...")
        
        # Procurar episódios
        episodes = re.findall(r'data-id="(\d+)"', resp.text)
        print(f"\n   Episódios (data-id): {len(episodes)}")
        
        # Procurar botões
        buttons = re.findall(r'<button[^>]*data-source="([^"]+)"[^>]*>([^<]*)</button>', resp.text)
        print(f"\n   Botões com source: {len(buttons)}")
        for url, text in buttons[:10]:
            print(f"     - {text.strip()}: {url[:50]}...")
        
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Agora via Selenium
    print("\n\n2. Tentando via Selenium...")
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    
    driver = uc.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        print(f"   URL: {driver.current_url}")
        print(f"   Título: {driver.title}")
        
        # Salvar HTML renderizado
        html = driver.page_source
        with open('playerthree_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   HTML renderizado salvo ({len(html)} chars)")
        
        # Procurar elementos
        buttons = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
        print(f"\n   Elementos com data-source: {len(buttons)}")
        
        for btn in buttons[:10]:
            src = btn.get_attribute('data-source')
            text = btn.text.strip()
            print(f"     - {text}: {src[:50]}...")
        
        # Procurar lista de episódios
        episodes = driver.find_elements(By.CSS_SELECTOR, '[data-id]')
        print(f"\n   Elementos com data-id: {len(episodes)}")
        
        # Verificar se precisa selecionar episódio primeiro
        ep_items = driver.find_elements(By.CSS_SELECTOR, '.episode-item, .ep-item, [class*="episode"]')
        print(f"\n   Items de episódio: {len(ep_items)}")
        
        for ep in ep_items[:5]:
            text = ep.text.strip()[:50]
            print(f"     - {text}")
        
        # Screenshot
        driver.save_screenshot('playerthree_screenshot.png')
        print("\n   Screenshot salvo")
        
        # Se houver episódios, clicar no primeiro
        if ep_items:
            print("\n3. Clicando no primeiro episódio...")
            try:
                ep_items[0].click()
                time.sleep(3)
                
                # Verificar botões agora
                buttons = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
                print(f"   Botões após clique: {len(buttons)}")
                
                for btn in buttons[:10]:
                    src = btn.get_attribute('data-source')
                    text = btn.text.strip()
                    print(f"     - {text}: {src[:50]}...")
                
            except Exception as e:
                print(f"   Erro ao clicar: {e}")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_playerthree()
