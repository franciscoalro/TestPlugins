#!/usr/bin/env python3
"""
Captura completa: clica no episódio -> carrega players -> captura vídeo
"""

import json
import time
import random

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.add_argument('--disable-popup-blocking')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def capture_full_flow():
    print("="*60)
    print("CAPTURA COMPLETA DO FLUXO")
    print("="*60)
    
    driver = create_driver()
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Acessar playerthree
        url = "https://playerthree.online/embed/synden/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(5)
        
        # 2. Clicar no primeiro episódio
        print("\n2. Clicando no episódio 1...")
        try:
            # Esperar lista de episódios
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-episode-id]'))
            )
            
            episode = driver.find_element(By.CSS_SELECTOR, 'li[data-episode-id="255704"] a')
            episode.click()
            print("   Clicou no episódio")
            time.sleep(5)
        except Exception as e:
            print(f"   Erro ao clicar: {e}")
            # Tentar via JS
            driver.execute_script("""
                var ep = document.querySelector('li[data-episode-id] a');
                if (ep) ep.click();
            """)
            time.sleep(5)
        
        # 3. Aguardar players carregarem
        print("\n3. Aguardando players...")
        time.sleep(5)
        
        # Salvar HTML após clique
        html = driver.page_source
        with open('playerthree_after_click.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   HTML salvo")
        
        # 4. Extrair players
        print("\n4. Extraindo players...")
        
        players = driver.execute_script("""
            var result = [];
            document.querySelectorAll('[data-source]').forEach(function(el) {
                result.push({
                    url: el.getAttribute('data-source'),
                    text: el.innerText.trim(),
                    type: el.getAttribute('data-type')
                });
            });
            return result;
        """)
        
        print(f"   Players encontrados: {len(players)}")
        for p in players:
            print(f"   - {p['text']}: {p['url'][:50]}...")
            results['players'].append(p)
        
        # 5. Clicar no Player #1
        if players:
            print(f"\n5. Clicando no {players[0]['text']}...")
            
            driver.execute_script("""
                var btn = document.querySelector('[data-source]');
                if (btn) btn.click();
            """)
            time.sleep(3)
            
            # Verificar iframe carregado
            print("\n6. Verificando iframe do player...")
            
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes: {len(iframes)}")
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if src:
                    print(f"   → {src[:70]}...")
                
                if 'playerembedapi' in src or 'megaembed' in src:
                    print(f"\n7. Entrando no iframe do player...")
                    driver.switch_to.frame(iframe)
                    time.sleep(8)
                    
                    # Verificar iframes aninhados
                    nested = driver.find_elements(By.TAG_NAME, 'iframe')
                    print(f"   Iframes aninhados: {len(nested)}")
                    
                    for n in nested:
                        nsrc = n.get_attribute('src') or ''
                        print(f"   → {nsrc[:60]}...")
                        
                        if 'short.icu' in nsrc or 'abyss' in nsrc:
                            driver.switch_to.frame(n)
                            time.sleep(8)
                            break
                    
                    # Capturar vídeo
                    print("\n8. Capturando vídeo...")
                    
                    videos = driver.find_elements(By.TAG_NAME, 'video')
                    for v in videos:
                        src = v.get_attribute('src')
                        if src:
                            print(f"   🎬 VIDEO: {src}")
                            results['videos'].append({'url': src, 'type': 'element'})
                        
                        # currentSrc
                        csrc = driver.execute_script("return arguments[0].currentSrc", v)
                        if csrc:
                            print(f"   🎬 CURRENT: {csrc}")
                            results['videos'].append({'url': csrc, 'type': 'currentSrc'})
                    
                    driver.switch_to.default_content()
                    break
        
        # 9. Capturar logs de rede
        print("\n9. Analisando rede...")
        logs = driver.get_log('performance')
        
        for log in logs:
            try:
                msg = json.loads(log['message'])['message']
                if msg.get('method') == 'Network.requestWillBeSent':
                    url = msg.get('params', {}).get('request', {}).get('url', '')
                    headers = msg.get('params', {}).get('request', {}).get('headers', {})
                    
                    if 'storage.googleapis.com' in url:
                        print(f"\n   🎯 GCS: {url}")
                        results['videos'].append({'url': url, 'headers': headers, 'type': 'gcs'})
                    
                    if any(x in url.lower() for x in ['.m3u8', '.mp4']) and 'vjs' not in url:
                        print(f"   🎬 {url[:70]}...")
                        results['videos'].append({'url': url, 'type': 'network'})
            except:
                pass
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print("="*60)
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for v in results['videos']:
            print(f"\n🎬 {v.get('url', '')[:100]}")
        
        with open('full_flow_results.json', 'w', encoding='utf-8') as f:
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
    capture_full_flow()
