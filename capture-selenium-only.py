#!/usr/bin/env python3
"""
Captura usando apenas Selenium - sem requests
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
    print("CAPTURA SELENIUM ONLY")
    print("="*60)
    
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
    
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Acessar página da série no MaxSeries
        url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(8)
        close_popups(driver)
        
        print(f"   URL atual: {driver.current_url}")
        
        # 2. Encontrar iframe do playerthree
        print("\n2. Procurando iframe playerthree...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        
        playerthree_src = None
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if 'playerthree' in src:
                playerthree_src = src
                print(f"   ✓ Encontrado: {src[:60]}...")
                driver.switch_to.frame(iframe)
                break
        
        if not playerthree_src:
            print("   ✗ Iframe não encontrado!")
            return results
        
        time.sleep(3)
        
        # 3. Clicar no primeiro episódio
        print("\n3. Procurando episódios...")
        
        ep_links = driver.find_elements(By.CSS_SELECTOR, 'li[data-episode-id] a')
        print(f"   Episódios: {len(ep_links)}")
        
        if ep_links:
            first_ep = ep_links[0]
            ep_text = first_ep.text.strip()
            print(f"   Clicando em: {ep_text}")
            
            driver.execute_script("arguments[0].click();", first_ep)
            time.sleep(4)
            close_popups(driver)
            
            # 4. Procurar botões de player
            print("\n4. Procurando players...")
            
            # Verificar HTML
            html = driver.page_source
            
            # Procurar data-source no HTML
            sources = re.findall(r'data-source="([^"]+)"', html)
            print(f"   Sources no HTML: {len(sources)}")
            
            for src in sources:
                results['players'].append({'url': src})
                print(f"     - {src[:60]}...")
            
            # Procurar botões visíveis
            buttons = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
            print(f"   Botões visíveis: {len(buttons)}")
            
            for btn in buttons:
                src = btn.get_attribute('data-source')
                text = btn.text.strip()
                if src and src not in [p['url'] for p in results['players']]:
                    results['players'].append({'name': text, 'url': src})
                    print(f"     ✓ {text}: {src[:50]}...")
            
            # 5. Se encontrou players, testar
            if results['players']:
                player = results['players'][0]
                print(f"\n5. Testando: {player['url'][:50]}...")
                
                # Voltar para contexto principal
                driver.switch_to.default_content()
                
                # Abrir player em nova aba
                driver.execute_script(f"window.open('{player['url']}', '_blank');")
                time.sleep(2)
                
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(5)
                    close_popups(driver)
                    
                    print(f"   URL: {driver.current_url}")
                    
                    # Verificar iframes aninhados
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    print(f"   Iframes: {len(iframes)}")
                    
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if src:
                            print(f"     - {src[:60]}...")
                            
                            # Se for abyss/short.icu, entrar
                            if any(x in src for x in ['abyss', 'short.icu', 'abysscdn']):
                                print(f"   Entrando no iframe...")
                                driver.switch_to.frame(iframe)
                                time.sleep(5)
                                
                                # Verificar mais iframes
                                nested = driver.find_elements(By.TAG_NAME, 'iframe')
                                for n in nested:
                                    nsrc = n.get_attribute('src') or ''
                                    if nsrc:
                                        print(f"     Nested: {nsrc[:60]}...")
                                
                                break
                    
                    # Aguardar vídeo
                    print("\n6. Aguardando vídeo (20s)...")
                    time.sleep(20)
                    
                    # Capturar logs
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            msg = json.loads(log['message'])['message']
                            if msg.get('method') == 'Network.requestWillBeSent':
                                req_url = msg.get('params', {}).get('request', {}).get('url', '')
                                headers = msg.get('params', {}).get('request', {}).get('headers', {})
                                
                                if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master', '.ts']):
                                    if req_url not in [v['url'] for v in results['videos']]:
                                        results['videos'].append({
                                            'url': req_url,
                                            'headers': headers
                                        })
                                        print(f"\n   🎬 VÍDEO: {req_url[:80]}...")
                                        print(f"      Referer: {headers.get('Referer', 'N/A')[:50]}")
                        except:
                            pass
                    
                    # Verificar elemento video
                    videos = driver.find_elements(By.TAG_NAME, 'video')
                    for v in videos:
                        vsrc = v.get_attribute('src')
                        if vsrc and vsrc.startswith('http'):
                            print(f"   📹 <video>: {vsrc[:60]}...")
                            if vsrc not in [x['url'] for x in results['videos']]:
                                results['videos'].append({'url': vsrc})
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for p in results['players']:
            print(f"\n📺 {p.get('name', 'Player')}: {p['url']}")
        
        for v in results['videos']:
            print(f"\n🎬 {v['url']}")
            if 'headers' in v:
                print(f"   Referer: {v['headers'].get('Referer', 'N/A')}")
        
        # Salvar
        with open('selenium_results.json', 'w', encoding='utf-8') as f:
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
