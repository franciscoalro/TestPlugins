#!/usr/bin/env python3
"""
Captura via parsing de HTML - mais confiável
"""

import json
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

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
    print("CAPTURA VIA HTML PARSE")
    print("="*60)
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    prefs = {'profile.default_content_setting_values.popups': 2}
    options.add_experimental_option('prefs', prefs)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    block_popups(driver)
    
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Acessar série
        url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(8)
        close_popups(driver)
        
        # 2. Entrar no iframe
        print("\n2. Entrando no iframe playerthree...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if 'playerthree' in src:
                driver.switch_to.frame(iframe)
                print(f"   ✓ {src[:50]}...")
                break
        
        time.sleep(3)
        
        # 3. Clicar no episódio
        print("\n3. Clicando no episódio...")
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'li[data-episode-id] a')
        if ep_links:
            driver.execute_script("arguments[0].click();", ep_links[0])
            print("   Clicado! Aguardando 5s...")
            time.sleep(5)
            close_popups(driver)
        
        # 4. Extrair players do HTML
        print("\n4. Extraindo players do HTML...")
        html = driver.page_source
        
        # Regex para encontrar botões com data-source
        pattern = r'data-source="([^"]+)"[^>]*data-type="([^"]*)"[^>]*data-id="([^"]*)"[^>]*>([^<]*)<'
        matches = re.findall(pattern, html)
        
        print(f"   Matches encontrados: {len(matches)}")
        
        for source, dtype, did, text in matches:
            results['players'].append({
                'name': text.strip(),
                'url': source,
                'type': dtype,
                'id': did
            })
            print(f"   ✓ {text.strip()}: {source[:50]}...")
        
        # Se não encontrou, tentar outro padrão
        if not results['players']:
            pattern2 = r'data-source="([^"]+)"'
            sources = re.findall(pattern2, html)
            print(f"   Sources via regex simples: {len(sources)}")
            for src in sources:
                results['players'].append({'url': src, 'name': 'Player'})
                print(f"   ✓ {src[:50]}...")
        
        # 5. Testar players
        if results['players']:
            for i, player in enumerate(results['players']):
                print(f"\n{'='*60}")
                print(f"5.{i+1}. TESTANDO: {player.get('name', 'Player')}")
                print(f"     URL: {player['url']}")
                print(f"{'='*60}")
                
                # Voltar para contexto principal
                driver.switch_to.default_content()
                
                # Limpar logs
                driver.get_log('performance')
                
                # Abrir em nova aba
                driver.execute_script(f"window.open('{player['url']}', '_blank');")
                time.sleep(2)
                
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5)
                    close_popups(driver)
                    
                    current = driver.current_url
                    print(f"     URL atual: {current[:60]}...")
                    
                    # Verificar redirecionamento
                    if 'abyss.to' in current and '/e/' not in current:
                        print("     ⚠️ Redirecionou para página principal")
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        continue
                    
                    # Entrar em iframes
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    print(f"     Iframes: {len(iframes)}")
                    
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if src:
                            print(f"       - {src[:60]}...")
                            if any(x in src for x in ['abyss', 'short.icu', 'abysscdn']):
                                try:
                                    driver.switch_to.frame(iframe)
                                    time.sleep(5)
                                    
                                    # Nested
                                    nested = driver.find_elements(By.TAG_NAME, 'iframe')
                                    for n in nested:
                                        nsrc = n.get_attribute('src') or ''
                                        if nsrc:
                                            print(f"       Nested: {nsrc[:60]}...")
                                            if 'abyss' in nsrc:
                                                driver.switch_to.frame(n)
                                                time.sleep(5)
                                except:
                                    pass
                                break
                    
                    # Aguardar
                    print("\n     Aguardando vídeo (30s)...")
                    time.sleep(30)
                    
                    # Capturar logs
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            msg = json.loads(log['message'])['message']
                            if msg.get('method') == 'Network.requestWillBeSent':
                                req = msg.get('params', {}).get('request', {})
                                req_url = req.get('url', '')
                                headers = req.get('headers', {})
                                
                                if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                                    if 'google' not in req_url:
                                        if req_url not in [v['url'] for v in results['videos']]:
                                            results['videos'].append({
                                                'url': req_url,
                                                'headers': headers,
                                                'player': player.get('name', 'Player')
                                            })
                                            print(f"\n     🎬 VÍDEO: {req_url[:80]}...")
                        except:
                            pass
                    
                    # Fechar
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for p in results['players']:
            print(f"\n📺 {p.get('name', 'Player')}: {p['url']}")
        
        for v in results['videos']:
            print(f"\n🎬 {v.get('player', '?')}: {v['url']}")
        
        with open('html_parse_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture()
