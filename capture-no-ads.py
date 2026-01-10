#!/usr/bin/env python3
"""
Captura de vídeo com bloqueio de popups e ads
"""

import json
import time
import random

try:
    import undetected_chromedriver as uc
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'undetected-chromedriver'], check=True)
    import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def create_driver_no_ads():
    """Driver com bloqueio de popups e ads"""
    
    options = uc.ChromeOptions()
    
    # Anti-detecção
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # BLOQUEIO DE POPUPS E ADS
    options.add_argument('--disable-popup-blocking')  # Desabilita bloqueio nativo para controlar manualmente
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    
    # Bloquear popups via preferências
    prefs = {
        'profile.default_content_setting_values.popups': 2,  # Bloquear popups
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 2,
        'profile.default_content_setting_values.ads': 2,  # Bloquear ads
        'profile.managed_default_content_settings.popups': 2,
        'profile.managed_default_content_settings.notifications': 2,
        'safebrowsing.enabled': False,
    }
    options.add_experimental_option('prefs', prefs)
    
    # Logs de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    
    # Injetar script para bloquear popups e ads
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Bloquear window.open (popups)
            window._originalOpen = window.open;
            window.open = function(url, name, features) {
                console.log('[BLOCKED POPUP]:', url);
                return null;
            };
            
            // Bloquear popunders
            Object.defineProperty(window, 'open', {
                configurable: false,
                writable: false,
                value: function() { return null; }
            });
            
            // Bloquear alert/confirm/prompt
            window.alert = function() {};
            window.confirm = function() { return true; };
            window.prompt = function() { return null; };
            
            // Remover event listeners de click que abrem popups
            document.addEventListener('click', function(e) {
                // Verificar se o clique vai abrir popup
                var target = e.target;
                while (target) {
                    if (target.tagName === 'A') {
                        var href = target.getAttribute('href');
                        var targetAttr = target.getAttribute('target');
                        // Bloquear links externos suspeitos
                        if (targetAttr === '_blank' && href && !href.includes('maxseries')) {
                            console.log('[BLOCKED LINK]:', href);
                            e.preventDefault();
                            e.stopPropagation();
                            return false;
                        }
                    }
                    target = target.parentElement;
                }
            }, true);
            
            // Remover iframes de ads
            setInterval(function() {
                var iframes = document.querySelectorAll('iframe');
                iframes.forEach(function(iframe) {
                    var src = iframe.src || '';
                    if (src.includes('ads') || src.includes('doubleclick') || 
                        src.includes('googlesyndication') || src.includes('adservice') ||
                        src.includes('popads') || src.includes('popcash')) {
                        iframe.remove();
                        console.log('[REMOVED AD IFRAME]:', src);
                    }
                });
                
                // Remover divs de overlay/ads
                var overlays = document.querySelectorAll('[class*="overlay"], [class*="popup"], [class*="modal"], [id*="overlay"], [id*="popup"]');
                overlays.forEach(function(el) {
                    if (el.style.position === 'fixed' || el.style.position === 'absolute') {
                        var zIndex = parseInt(window.getComputedStyle(el).zIndex) || 0;
                        if (zIndex > 1000) {
                            el.remove();
                            console.log('[REMOVED OVERLAY]');
                        }
                    }
                });
            }, 1000);
            
            // Bloquear beforeunload
            window.onbeforeunload = null;
            window.addEventListener('beforeunload', function(e) {
                e.stopPropagation();
            }, true);
            
            // Remover webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        '''
    })
    
    return driver

def close_extra_tabs(driver):
    """Fecha todas as abas extras (popups)"""
    main_window = driver.window_handles[0]
    for handle in driver.window_handles[1:]:
        try:
            driver.switch_to.window(handle)
            driver.close()
        except:
            pass
    driver.switch_to.window(main_window)

def safe_click(driver, element):
    """Clique seguro que fecha popups após"""
    initial_handles = len(driver.window_handles)
    
    try:
        # Scroll para o elemento
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.5)
        
        # Clicar
        element.click()
        time.sleep(1)
        
        # Fechar popups que abriram
        if len(driver.window_handles) > initial_handles:
            print(f"   [!] {len(driver.window_handles) - initial_handles} popup(s) bloqueado(s)")
            close_extra_tabs(driver)
        
        return True
    except Exception as e:
        print(f"   Erro no clique: {e}")
        return False

def capture_video():
    """Captura URL do vídeo"""
    
    print("="*60)
    print("CAPTURA COM BLOQUEIO DE ADS")
    print("="*60)
    
    driver = create_driver_no_ads()
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Acessar episódio
        url = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(4)
        
        # Fechar popups iniciais
        close_extra_tabs(driver)
        
        # 2. Encontrar players
        print("\n2. Procurando players...")
        
        # Remover overlays de ads primeiro
        driver.execute_script("""
            // Remover overlays
            document.querySelectorAll('[class*="ad"], [id*="ad"], [class*="overlay"]').forEach(el => el.remove());
            // Remover scripts de ads
            document.querySelectorAll('script[src*="ads"], script[src*="pop"]').forEach(el => el.remove());
        """)
        
        time.sleep(1)
        
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
        print(f"   Botões encontrados: {len(buttons)}")
        
        for btn in buttons:
            try:
                source = btn.get_attribute('data-source')
                text = btn.text.strip() or "Player"
                if source:
                    results['players'].append({'name': text, 'url': source})
                    print(f"   ✓ {text}: {source[:50]}...")
            except:
                pass
        
        # 3. Testar primeiro player
        if results['players']:
            player = results['players'][0]
            print(f"\n3. Testando: {player['name']}")
            print(f"   URL: {player['url']}")
            
            # Encontrar e clicar no botão
            btn = driver.find_element(By.CSS_SELECTOR, f'button[data-source="{player["url"]}"]')
            safe_click(driver, btn)
            time.sleep(3)
            
            # Fechar popups
            close_extra_tabs(driver)
            
            # Verificar iframe do player
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes: {len(iframes)}")
            
            player_iframe = None
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if any(x in src for x in ['playerembed', 'megaembed', 'playerthree', 'abyss', 'short.icu', 'dood']):
                    player_iframe = iframe
                    print(f"   → Player iframe: {src[:60]}...")
                    break
            
            if player_iframe:
                # Entrar no iframe
                driver.switch_to.frame(player_iframe)
                time.sleep(3)
                
                # Verificar iframes aninhados
                nested = driver.find_elements(By.TAG_NAME, 'iframe')
                for n in nested:
                    src = n.get_attribute('src') or ''
                    print(f"   → Nested: {src[:60]}...")
                    if any(x in src for x in ['abyss', 'short.icu', 'abysscdn']):
                        driver.switch_to.frame(n)
                        time.sleep(3)
                        break
                
                # Aguardar player carregar
                print("\n4. Aguardando player (20s)...")
                time.sleep(20)
                
                # Capturar logs de rede
                print("\n5. Analisando requisições...")
                logs = driver.get_log('performance')
                
                for log in logs:
                    try:
                        msg = json.loads(log['message'])['message']
                        method = msg.get('method', '')
                        
                        if method == 'Network.requestWillBeSent':
                            req = msg.get('params', {}).get('request', {})
                            url = req.get('url', '')
                            headers = req.get('headers', {})
                            
                            # Verificar se é vídeo
                            if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master', '/video/', '.ts']):
                                video = {
                                    'url': url,
                                    'headers': headers,
                                    'player': player['name']
                                }
                                if url not in [v['url'] for v in results['videos']]:
                                    results['videos'].append(video)
                                    print(f"\n   🎬 VÍDEO: {url[:80]}...")
                                    print(f"      Referer: {headers.get('Referer', 'N/A')[:50]}")
                    except:
                        pass
                
                # Verificar elemento video
                videos = driver.find_elements(By.TAG_NAME, 'video')
                for v in videos:
                    src = v.get_attribute('src')
                    if src and src.startswith('http'):
                        print(f"   📹 <video>: {src[:60]}...")
                        if src not in [x['url'] for x in results['videos']]:
                            results['videos'].append({'url': src, 'type': 'element'})
                
                driver.switch_to.default_content()
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for v in results['videos']:
            print(f"\n🎬 {v['url']}")
            if 'headers' in v:
                print(f"   Referer: {v['headers'].get('Referer', 'N/A')}")
        
        # Salvar
        with open('capture_results.json', 'w', encoding='utf-8') as f:
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
    capture_video()
