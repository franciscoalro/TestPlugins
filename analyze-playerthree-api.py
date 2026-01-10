#!/usr/bin/env python3
"""
Analisa a API do playerthree.online
"""

import json
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def capture():
    print("="*60)
    print("ANÁLISE API PLAYERTHREE")
    print("="*60)
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    
    try:
        # Acessar página
        url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(8)
        
        # Entrar no iframe
        print("\n2. Entrando no iframe playerthree...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if 'playerthree' in src:
                driver.switch_to.frame(iframe)
                break
        
        time.sleep(3)
        
        # Limpar logs anteriores
        driver.get_log('performance')
        
        # Clicar no episódio
        print("\n3. Clicando no episódio...")
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'li[data-episode-id] a')
        
        if ep_links:
            # Pegar info do episódio
            parent = ep_links[0].find_element(By.XPATH, '..')
            season_id = parent.get_attribute('data-season-id')
            episode_id = parent.get_attribute('data-episode-id')
            print(f"   Season ID: {season_id}")
            print(f"   Episode ID: {episode_id}")
            
            # Clicar
            driver.execute_script("arguments[0].click();", ep_links[0])
            time.sleep(5)
            
            # Capturar requisições AJAX
            print("\n4. Analisando requisições de rede...")
            logs = driver.get_log('performance')
            
            api_calls = []
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    
                    if method == 'Network.requestWillBeSent':
                        req = msg.get('params', {}).get('request', {})
                        req_url = req.get('url', '')
                        req_method = req.get('method', '')
                        
                        # Filtrar requisições interessantes
                        if any(x in req_url for x in ['api', 'episode', 'player', 'source', 'embed']):
                            api_calls.append({
                                'url': req_url,
                                'method': req_method,
                                'headers': req.get('headers', {})
                            })
                            print(f"   {req_method} {req_url[:80]}...")
                    
                    if method == 'Network.responseReceived':
                        resp = msg.get('params', {}).get('response', {})
                        resp_url = resp.get('url', '')
                        
                        if any(x in resp_url for x in ['api', 'episode', 'player', 'source']):
                            print(f"   RESPONSE: {resp_url[:80]}...")
                            
                except:
                    pass
            
            # Verificar HTML após clique
            print("\n5. Verificando HTML após clique...")
            html = driver.page_source
            
            # Salvar HTML
            with open('playerthree_after_click.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   HTML salvo ({len(html)} chars)")
            
            # Procurar elementos de player
            play_div = driver.find_elements(By.ID, 'play')
            if play_div:
                style = play_div[0].get_attribute('style')
                inner = play_div[0].get_attribute('innerHTML')[:500]
                print(f"   #play style: {style}")
                print(f"   #play inner: {inner[:200]}...")
            
            # Procurar iframes de player
            player_iframes = driver.find_elements(By.CSS_SELECTOR, 'iframe')
            print(f"\n   Iframes: {len(player_iframes)}")
            for pf in player_iframes:
                src = pf.get_attribute('src') or ''
                if src:
                    print(f"     - {src[:60]}...")
            
            # Executar JavaScript para ver variáveis
            print("\n6. Verificando variáveis JavaScript...")
            
            js_vars = driver.execute_script("""
                var result = {};
                if (window.gleam) result.gleam = window.gleam;
                if (window.player) result.player = window.player;
                if (window.sources) result.sources = window.sources;
                if (window.episode) result.episode = window.episode;
                return JSON.stringify(result, null, 2);
            """)
            
            print(f"   JS vars: {js_vars[:500]}...")
            
            # Salvar
            with open('playerthree_api_analysis.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'season_id': season_id,
                    'episode_id': episode_id,
                    'api_calls': api_calls,
                    'js_vars': js_vars
                }, f, indent=2)
        
        print("\n\nAnálise completa!")
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture()
