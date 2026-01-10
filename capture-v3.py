#!/usr/bin/env python3
"""
Captura v3 - Entra no iframe do playerthree para encontrar os players
"""

import json
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def block_popups(driver):
    """Injeta script para bloquear popups"""
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            window.open = function() { return null; };
            window.alert = function() {};
            window.confirm = function() { return true; };
        '''
    })

def close_popups(driver):
    """Fecha abas extras"""
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
    print("CAPTURA V3 - PLAYERTHREE IFRAME")
    print("="*60)
    
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-popup-blocking')
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
        # 1. Acessar série (que tem o iframe do playerthree)
        url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(5)
        close_popups(driver)
        
        # 2. Encontrar iframe do playerthree
        print("\n2. Procurando iframe playerthree...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        
        playerthree_iframe = None
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if 'playerthree' in src:
                playerthree_iframe = iframe
                print(f"   ✓ Encontrado: {src[:60]}...")
                break
        
        if not playerthree_iframe:
            print("   ✗ Iframe playerthree não encontrado!")
            return results
        
        # 3. Entrar no iframe
        print("\n3. Entrando no iframe...")
        driver.switch_to.frame(playerthree_iframe)
        time.sleep(3)
        
        # 4. Encontrar botões de player
        print("\n4. Procurando botões de player...")
        
        # Aguardar botões carregarem
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-source]'))
            )
        except:
            print("   Timeout esperando botões")
        
        buttons = driver.find_elements(By.CSS_SELECTOR, '[data-source]')
        print(f"   Botões encontrados: {len(buttons)}")
        
        for btn in buttons:
            try:
                source = btn.get_attribute('data-source')
                text = btn.text.strip() or btn.get_attribute('innerText').strip() or "Player"
                data_type = btn.get_attribute('data-type')
                if source:
                    results['players'].append({
                        'name': text,
                        'url': source,
                        'type': data_type
                    })
                    print(f"   ✓ {text}: {source[:50]}...")
            except Exception as e:
                print(f"   Erro: {e}")
        
        # 5. Testar cada player
        for i, player in enumerate(results['players'][:3]):
            print(f"\n{'='*60}")
            print(f"5.{i+1}. TESTANDO: {player['name']}")
            print(f"     URL: {player['url']}")
            print(f"{'='*60}")
            
            # Clicar no botão
            try:
                btn = driver.find_element(By.CSS_SELECTOR, f'[data-source="{player["url"]}"]')
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                close_popups(driver)
            except Exception as e:
                print(f"     Erro ao clicar: {e}")
                continue
            
            # Verificar se carregou iframe do player
            time.sleep(3)
            
            player_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"     Iframes após clique: {len(player_iframes)}")
            
            for pf in player_iframes:
                src = pf.get_attribute('src') or ''
                if src and any(x in src for x in ['playerembed', 'megaembed', 'abyss', 'dood', 'short.icu']):
                    print(f"     → Player: {src[:60]}...")
                    
                    # Entrar no iframe do player
                    try:
                        driver.switch_to.frame(pf)
                        time.sleep(5)
                        
                        # Verificar iframes aninhados
                        nested = driver.find_elements(By.TAG_NAME, 'iframe')
                        for n in nested:
                            nsrc = n.get_attribute('src') or ''
                            if nsrc:
                                print(f"     → Nested: {nsrc[:60]}...")
                                if any(x in nsrc for x in ['abyss', 'short.icu', 'abysscdn']):
                                    driver.switch_to.frame(n)
                                    time.sleep(5)
                                    break
                        
                        # Aguardar vídeo carregar
                        print("     Aguardando vídeo (15s)...")
                        time.sleep(15)
                        
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
                                                'headers': headers,
                                                'player': player['name']
                                            })
                                            print(f"\n     🎬 VÍDEO: {req_url[:80]}...")
                            except:
                                pass
                        
                        # Verificar elemento video
                        videos = driver.find_elements(By.TAG_NAME, 'video')
                        for v in videos:
                            vsrc = v.get_attribute('src')
                            if vsrc and vsrc.startswith('http'):
                                print(f"     📹 <video>: {vsrc[:60]}...")
                                if vsrc not in [x['url'] for x in results['videos']]:
                                    results['videos'].append({'url': vsrc, 'player': player['name']})
                        
                        # Voltar para iframe do playerthree
                        driver.switch_to.default_content()
                        driver.switch_to.frame(playerthree_iframe)
                        
                    except Exception as e:
                        print(f"     Erro no iframe: {e}")
                        driver.switch_to.default_content()
                        driver.switch_to.frame(playerthree_iframe)
                    
                    break
            
            time.sleep(2)
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS FINAIS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for p in results['players']:
            print(f"\n📺 {p['name']}: {p['url'][:50]}...")
        
        for v in results['videos']:
            print(f"\n🎬 {v.get('player', '?')}: {v['url'][:80]}...")
            if 'headers' in v:
                print(f"   Referer: {v['headers'].get('Referer', 'N/A')[:50]}")
        
        # Salvar
        with open('capture_v3_results.json', 'w', encoding='utf-8') as f:
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
