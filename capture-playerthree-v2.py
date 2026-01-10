#!/usr/bin/env python3
"""
Captura playerthree - clica no episódio para carregar players
"""

import json
import time
import requests
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def block_popups(driver):
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            window.open = function() { return null; };
            window.alert = function() {};
        '''
    })

def close_popups(driver):
    main = driver.window_handles[0]
    for h in driver.window_handles[1:]:
        try:
            driver.switch_to.window(h)
            driver.close()
        except:
            pass
    driver.switch_to.window(main)

def capture():
    print("="*60)
    print("CAPTURA PLAYERTHREE V2")
    print("="*60)
    
    # Primeiro, analisar via requests para entender a API
    print("\n1. Analisando estrutura via requests...")
    
    base_url = "https://playerthree.online"
    embed_url = f"{base_url}/embed/synden/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.maxseries.one/',
    }
    
    resp = requests.get(embed_url, headers=headers)
    html = resp.text
    
    # Extrair episódios
    episodes = re.findall(r'data-episode-id="(\d+)"', html)
    print(f"   Episódios encontrados: {len(episodes)}")
    for ep in episodes[:5]:
        print(f"     - {ep}")
    
    # Agora via Selenium para clicar e capturar
    print("\n2. Abrindo Selenium...")
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    prefs = {
        'profile.default_content_setting_values.popups': 2,
        'profile.default_content_setting_values.notifications': 2,
    }
    options.add_experimental_option('prefs', prefs)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    block_popups(driver)
    
    results = {'episodes': [], 'players': [], 'videos': []}
    
    try:
        driver.get(embed_url)
        time.sleep(5)
        close_popups(driver)
        
        print(f"   URL: {driver.current_url}")
        
        # 3. Encontrar e clicar no primeiro episódio
        print("\n3. Procurando episódios...")
        
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'li[data-episode-id] a')
        print(f"   Links de episódio: {len(ep_links)}")
        
        if ep_links:
            first_ep = ep_links[0]
            ep_text = first_ep.text.strip()
            ep_href = first_ep.get_attribute('href')
            print(f"   Clicando em: {ep_text} ({ep_href})")
            
            # Clicar no episódio
            driver.execute_script("arguments[0].click();", first_ep)
            time.sleep(3)
            close_popups(driver)
            
            # 4. Verificar se apareceram botões de player
            print("\n4. Procurando players após clique...")
            
            # Aguardar elementos aparecerem
            time.sleep(3)
            
            # Verificar HTML atualizado
            html = driver.page_source
            
            # Procurar botões de player
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source], [data-source]')
            print(f"   Botões com data-source: {len(buttons)}")
            
            for btn in buttons:
                src = btn.get_attribute('data-source')
                text = btn.text.strip()
                if src:
                    results['players'].append({'name': text, 'url': src})
                    print(f"     ✓ {text}: {src[:50]}...")
            
            # Se não encontrou, procurar no HTML
            if not results['players']:
                sources = re.findall(r'data-source="([^"]+)"', html)
                print(f"\n   Sources no HTML: {len(sources)}")
                for s in sources:
                    results['players'].append({'name': 'Player', 'url': s})
                    print(f"     - {s[:60]}...")
            
            # Verificar se há div de player visível
            play_div = driver.find_elements(By.ID, 'play')
            if play_div:
                style = play_div[0].get_attribute('style')
                print(f"\n   Div #play style: {style}")
            
            # Capturar logs de rede para ver requisições AJAX
            print("\n5. Analisando requisições de rede...")
            logs = driver.get_log('performance')
            
            ajax_calls = []
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    if msg.get('method') == 'Network.requestWillBeSent':
                        url = msg.get('params', {}).get('request', {}).get('url', '')
                        if 'playerthree' in url and ('api' in url or 'episode' in url or 'player' in url):
                            ajax_calls.append(url)
                            print(f"     AJAX: {url[:80]}...")
                except:
                    pass
            
            # 6. Se encontrou players, testar o primeiro
            if results['players']:
                player = results['players'][0]
                print(f"\n6. Testando player: {player['url'][:50]}...")
                
                # Abrir URL do player diretamente
                driver.execute_script(f"window.open('{player['url']}', '_blank');")
                time.sleep(2)
                
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5)
                    
                    print(f"   URL do player: {driver.current_url}")
                    
                    # Verificar iframes
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    print(f"   Iframes: {len(iframes)}")
                    
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if src:
                            print(f"     - {src[:60]}...")
                    
                    # Aguardar e capturar vídeo
                    time.sleep(10)
                    
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            msg = json.loads(log['message'])['message']
                            if msg.get('method') == 'Network.requestWillBeSent':
                                url = msg.get('params', {}).get('request', {}).get('url', '')
                                headers = msg.get('params', {}).get('request', {}).get('headers', {})
                                
                                if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                                    results['videos'].append({
                                        'url': url,
                                        'headers': headers
                                    })
                                    print(f"\n   🎬 VÍDEO: {url[:80]}...")
                        except:
                            pass
                    
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for p in results['players']:
            print(f"\n📺 {p['name']}: {p['url']}")
        
        for v in results['videos']:
            print(f"\n🎬 {v['url']}")
        
        # Salvar
        with open('playerthree_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture()
