#!/usr/bin/env python3
"""
Acessa diretamente a URL com hash do episódio
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
    print("CAPTURA DIRETA COM HASH")
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
        # Acessar diretamente o playerthree com hash do episódio
        # Hash format: #season_episode (ex: #12962_255703)
        url = "https://playerthree.online/embed/synden/#12962_255703"
        print(f"\n1. Acessando diretamente: {url}")
        driver.get(url)
        time.sleep(8)
        close_popups(driver)
        
        print(f"   URL atual: {driver.current_url}")
        
        # Salvar HTML
        html = driver.page_source
        with open('playerthree_direct.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   HTML salvo ({len(html)} chars)")
        
        # Procurar data-source
        print("\n2. Procurando players...")
        
        # Via regex
        sources = re.findall(r'data-source="([^"]+)"', html)
        print(f"   Sources no HTML: {len(sources)}")
        for src in sources:
            results['players'].append({'url': src})
            print(f"   ✓ {src[:60]}...")
        
        # Via Selenium
        buttons = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
        print(f"   Botões via Selenium: {len(buttons)}")
        for btn in buttons:
            src = btn.get_attribute('data-source')
            text = btn.text.strip()
            if src and src not in [p['url'] for p in results['players']]:
                results['players'].append({'name': text, 'url': src})
                print(f"   ✓ {text}: {src[:50]}...")
        
        # Screenshot
        driver.save_screenshot('playerthree_direct.png')
        print("\n   Screenshot salvo")
        
        # Se encontrou players, testar
        if results['players']:
            player = results['players'][0]
            print(f"\n3. Testando: {player['url'][:50]}...")
            
            # Limpar logs
            driver.get_log('performance')
            
            # Abrir player
            driver.execute_script(f"window.open('{player['url']}', '_blank');")
            time.sleep(2)
            
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)
                close_popups(driver)
                
                print(f"   URL: {driver.current_url[:60]}...")
                
                # Entrar em iframes
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if src and any(x in src for x in ['abyss', 'short']):
                        print(f"   Entrando: {src[:50]}...")
                        driver.switch_to.frame(iframe)
                        time.sleep(5)
                        break
                
                # Aguardar
                print("\n   Aguardando vídeo (30s)...")
                time.sleep(30)
                
                # Capturar
                logs = driver.get_log('performance')
                for log in logs:
                    try:
                        msg = json.loads(log['message'])['message']
                        if msg.get('method') == 'Network.requestWillBeSent':
                            req_url = msg.get('params', {}).get('request', {}).get('url', '')
                            headers = msg.get('params', {}).get('request', {}).get('headers', {})
                            
                            if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/']):
                                if 'google' not in req_url:
                                    results['videos'].append({
                                        'url': req_url,
                                        'headers': headers
                                    })
                                    print(f"\n   🎬 {req_url[:80]}...")
                    except:
                        pass
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for v in results['videos']:
            print(f"\n🎬 {v['url']}")
        
        with open('direct_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture()
