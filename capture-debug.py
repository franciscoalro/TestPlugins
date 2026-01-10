#!/usr/bin/env python3
"""
Debug - verificar o que está carregando na página
"""

import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def debug_page():
    print("="*60)
    print("DEBUG - VERIFICANDO PÁGINA")
    print("="*60)
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    
    try:
        url = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        
        print("\n2. Aguardando 10 segundos...")
        time.sleep(10)
        
        print(f"\n3. URL atual: {driver.current_url}")
        print(f"   Título: {driver.title}")
        
        # Salvar HTML
        html = driver.page_source
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n4. HTML salvo em debug_page.html ({len(html)} chars)")
        
        # Verificar elementos
        print("\n5. Elementos encontrados:")
        
        # Botões
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        print(f"   - Botões: {len(buttons)}")
        for btn in buttons[:10]:
            text = btn.text.strip()[:30] if btn.text else ""
            attrs = btn.get_attribute('outerHTML')[:100]
            print(f"     {text} | {attrs}...")
        
        # Botões com data-source
        data_btns = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
        print(f"\n   - Elementos com data-source: {len(data_btns)}")
        for el in data_btns:
            src = el.get_attribute('data-source')
            print(f"     {src[:60]}...")
        
        # Iframes
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"\n   - Iframes: {len(iframes)}")
        for iframe in iframes:
            src = iframe.get_attribute('src') or 'no-src'
            print(f"     {src[:80]}...")
        
        # Links de player
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="player"], a[href*="embed"]')
        print(f"\n   - Links de player: {len(links)}")
        for link in links[:5]:
            href = link.get_attribute('href')
            print(f"     {href[:60]}...")
        
        # Verificar se há player já carregado
        print("\n6. Procurando player no HTML...")
        if 'playerembedapi' in html.lower():
            print("   ✓ Encontrado: playerembedapi")
        if 'megaembed' in html.lower():
            print("   ✓ Encontrado: megaembed")
        if 'playerthree' in html.lower():
            print("   ✓ Encontrado: playerthree")
        if 'data-source' in html:
            print("   ✓ Encontrado: data-source")
            # Extrair via regex
            import re
            sources = re.findall(r'data-source="([^"]+)"', html)
            print(f"   Sources encontrados: {len(sources)}")
            for s in sources[:5]:
                print(f"     - {s[:60]}...")
        
        # Screenshot
        driver.save_screenshot('debug_screenshot.png')
        print("\n7. Screenshot salvo em debug_screenshot.png")
        
        input("\nPressione ENTER para fechar o browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_page()
