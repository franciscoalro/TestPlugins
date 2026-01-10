#!/usr/bin/env python3
"""
CAPTURA FINAL - Fluxo completo para extrair URL do vídeo
"""

import json
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def block_popups(driver):
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            window._open = window.open;
            window.open = function() { console.log('[BLOCKED]'); return null; };
            window.alert = function() {};
            window.confirm = function() { return true; };
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
    print("CAPTURA FINAL - EXTRAÇÃO DE VÍDEO")
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
        # 1. Acessar página da série
        url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(8)
        close_popups(driver)
        
        # 2. Entrar no iframe playerthree
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
            time.sleep(4)
            close_popups(driver)
        
        # 4. Encontrar botões de player
        print("\n4. Procurando botões de player...")
        
        # Aguardar botões aparecerem
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-source]'))
            )
        except:
            pass
        
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
        print(f"   Botões encontrados: {len(buttons)}")
        
        for btn in buttons:
            src = btn.get_attribute('data-source')
            text = btn.text.strip()
            data_id = btn.get_attribute('data-id')
            if src:
                results['players'].append({
                    'name': text,
                    'url': src,
                    'id': data_id
                })
                print(f"   ✓ {text}: {src[:50]}...")
        
        # 5. Testar cada player
        for i, player in enumerate(results['players']):
            print(f"\n{'='*60}")
            print(f"5.{i+1}. TESTANDO: {player['name']}")
            print(f"     URL: {player['url']}")
            print(f"{'='*60}")
            
            # Voltar para contexto principal
            driver.switch_to.default_content()
            
            # Limpar logs
            driver.get_log('performance')
            
            # Abrir player em nova aba
            driver.execute_script(f"window.open('{player['url']}', '_blank');")
            time.sleep(2)
            
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)
                close_popups(driver)
                
                current_url = driver.current_url
                print(f"     URL atual: {current_url[:60]}...")
                
                # Verificar se redirecionou para página principal (vídeo expirado)
                if 'abyss.to' in current_url and '/e/' not in current_url and '/v/' not in current_url:
                    print("     ⚠️ Vídeo expirado ou proteção anti-bot")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    # Voltar para iframe
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    for iframe in iframes:
                        src = iframe.get_attribute('src') or ''
                        if 'playerthree' in src:
                            driver.switch_to.frame(iframe)
                            break
                    continue
                
                # Verificar iframes
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                print(f"     Iframes: {len(iframes)}")
                
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if src:
                        print(f"       - {src[:60]}...")
                        
                        # Entrar em iframes de player
                        if any(x in src for x in ['abyss', 'short.icu', 'abysscdn', 'megaembed']):
                            try:
                                driver.switch_to.frame(iframe)
                                time.sleep(5)
                                
                                # Verificar iframes aninhados
                                nested = driver.find_elements(By.TAG_NAME, 'iframe')
                                for n in nested:
                                    nsrc = n.get_attribute('src') or ''
                                    if nsrc and any(x in nsrc for x in ['abyss', 'abysscdn']):
                                        print(f"       Nested: {nsrc[:60]}...")
                                        driver.switch_to.frame(n)
                                        time.sleep(5)
                                        break
                                
                                break
                            except Exception as e:
                                print(f"       Erro: {e}")
                
                # Aguardar vídeo carregar
                print("\n     Aguardando vídeo (25s)...")
                time.sleep(25)
                
                # Capturar logs de rede
                print("     Analisando requisições...")
                logs = driver.get_log('performance')
                
                for log in logs:
                    try:
                        msg = json.loads(log['message'])['message']
                        if msg.get('method') == 'Network.requestWillBeSent':
                            req = msg.get('params', {}).get('request', {})
                            req_url = req.get('url', '')
                            headers = req.get('headers', {})
                            
                            # Verificar se é vídeo
                            if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master', '.ts', '/video/']):
                                # Ignorar analytics
                                if 'google' not in req_url and 'analytics' not in req_url:
                                    if req_url not in [v['url'] for v in results['videos']]:
                                        results['videos'].append({
                                            'url': req_url,
                                            'headers': headers,
                                            'player': player['name']
                                        })
                                        print(f"\n     🎬 VÍDEO ENCONTRADO!")
                                        print(f"        URL: {req_url[:80]}...")
                                        print(f"        Referer: {headers.get('Referer', 'N/A')[:50]}")
                    except:
                        pass
                
                # Verificar elemento video
                try:
                    videos = driver.find_elements(By.TAG_NAME, 'video')
                    for v in videos:
                        vsrc = v.get_attribute('src')
                        if vsrc and vsrc.startswith('http'):
                            print(f"     📹 <video>: {vsrc[:60]}...")
                            if vsrc not in [x['url'] for x in results['videos']]:
                                results['videos'].append({
                                    'url': vsrc,
                                    'player': player['name'],
                                    'type': 'video_element'
                                })
                except:
                    pass
                
                # Fechar aba
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
                # Voltar para iframe playerthree
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if 'playerthree' in src:
                        driver.switch_to.frame(iframe)
                        break
                
                time.sleep(2)
        
        # RESUMO FINAL
        print(f"\n\n{'='*60}")
        print("RESULTADOS FINAIS")
        print(f"{'='*60}")
        print(f"Players encontrados: {len(results['players'])}")
        print(f"Vídeos capturados: {len(results['videos'])}")
        
        print("\n📺 PLAYERS:")
        for p in results['players']:
            print(f"   - {p['name']}: {p['url']}")
        
        print("\n🎬 VÍDEOS:")
        for v in results['videos']:
            print(f"\n   Player: {v.get('player', '?')}")
            print(f"   URL: {v['url']}")
            if 'headers' in v:
                print(f"   Referer: {v['headers'].get('Referer', 'N/A')}")
        
        # Salvar resultados
        with open('final_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Resultados salvos em final_results.json")
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture()
