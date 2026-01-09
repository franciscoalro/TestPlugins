#!/usr/bin/env python3
"""
Captura de vídeo com técnicas anti-detecção de bot
Usa undetected-chromedriver + patches adicionais
"""

import json
import time
import random

# Instalar: pip install undetected-chromedriver
try:
    import undetected_chromedriver as uc
except ImportError:
    print("Instalando undetected-chromedriver...")
    import subprocess
    subprocess.run(['pip', 'install', 'undetected-chromedriver'], check=True)
    import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_stealth_driver():
    """Cria driver com máxima evasão de detecção"""
    
    options = uc.ChromeOptions()
    
    # Configurações para parecer humano
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-infobars')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    
    # Idioma e timezone brasileiro
    options.add_argument('--lang=pt-BR')
    prefs = {
        'intl.accept_languages': 'pt-BR,pt,en-US,en',
        'profile.default_content_setting_values.notifications': 2,
    }
    options.add_experimental_option('prefs', prefs)
    
    # Habilitar logs de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Criar driver undetected
    driver = uc.Chrome(options=options, version_main=None)
    
    # Patches adicionais via CDP
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'platform': 'Win32',
        'acceptLanguage': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    })
    
    # Remover propriedades de webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Remover webdriver
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            
            // Simular plugins reais
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                    {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                    {name: 'Native Client', filename: 'internal-nacl-plugin'}
                ]
            });
            
            // Simular languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Chrome runtime
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // WebGL vendor
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };
        '''
    })
    
    return driver

def human_delay(min_sec=0.5, max_sec=2.0):
    """Delay aleatório para simular comportamento humano"""
    time.sleep(random.uniform(min_sec, max_sec))

def human_scroll(driver):
    """Scroll suave como humano"""
    scroll_amount = random.randint(100, 300)
    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
    human_delay(0.3, 0.8)

def capture_video_stealth(episode_url):
    """Captura vídeo simulando usuário real"""
    
    print("="*60)
    print("CAPTURA STEALTH DE VÍDEO")
    print("="*60)
    
    driver = create_stealth_driver()
    results = {'players': [], 'videos': []}
    
    try:
        # 1. Acessar página do episódio
        print(f"\n1. Acessando: {episode_url}")
        driver.get(episode_url)
        human_delay(3, 5)
        
        # Scroll para parecer humano
        human_scroll(driver)
        human_delay(1, 2)
        
        # 2. Encontrar players
        print("\n2. Procurando players...")
        
        # Esperar botões carregarem
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-source]'))
            )
        except:
            print("   Timeout esperando botões")
        
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
        
        for btn in buttons:
            try:
                source = btn.get_attribute('data-source')
                text = btn.text.strip() or btn.get_attribute('innerText').strip()
                if source:
                    results['players'].append({'name': text, 'url': source})
                    print(f"   ✓ {text}: {source[:50]}...")
            except:
                pass
        
        if not results['players']:
            print("   Nenhum player encontrado via botões")
            # Tentar extrair do HTML
            html = driver.page_source
            import re
            sources = re.findall(r'data-source="([^"]+)"', html)
            for i, src in enumerate(sources):
                results['players'].append({'name': f'Player #{i+1}', 'url': src})
                print(f"   ✓ Player #{i+1}: {src[:50]}...")
        
        # 3. Testar cada player
        for i, player in enumerate(results['players'][:2]):
            print(f"\n{'='*60}")
            print(f"3.{i+1}. TESTANDO: {player['name']}")
            print(f"{'='*60}")
            
            # Clicar no botão (mais natural que abrir URL direta)
            try:
                btn = driver.find_element(By.CSS_SELECTOR, f'button[data-source="{player["url"]}"]')
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                human_delay(0.5, 1)
                btn.click()
                human_delay(2, 4)
            except Exception as e:
                print(f"   Erro ao clicar: {e}")
                # Fallback: abrir em nova aba
                driver.execute_script(f"window.open('{player['url']}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                human_delay(3, 5)
            
            # Verificar iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes: {len(iframes)}")
            
            # Entrar no iframe do player
            player_iframe = None
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if any(x in src for x in ['playerembed', 'megaembed', 'abyss', 'short.icu']):
                    player_iframe = iframe
                    print(f"   → Iframe do player: {src[:60]}...")
                    break
            
            if player_iframe:
                try:
                    driver.switch_to.frame(player_iframe)
                    human_delay(3, 5)
                    
                    # Verificar se há mais iframes aninhados
                    nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    for nested in nested_iframes:
                        nested_src = nested.get_attribute('src') or ''
                        print(f"   → Iframe aninhado: {nested_src[:60]}...")
                        if 'abyss' in nested_src or 'short' in nested_src:
                            driver.switch_to.frame(nested)
                            human_delay(2, 3)
                            break
                    
                    # Aguardar player carregar
                    print("   Aguardando player...")
                    human_delay(5, 8)
                    
                    # Capturar logs de rede
                    logs = driver.get_log('performance')
                    for log in logs:
                        try:
                            msg = json.loads(log['message'])['message']
                            if msg.get('method') == 'Network.requestWillBeSent':
                                url = msg.get('params', {}).get('request', {}).get('url', '')
                                headers = msg.get('params', {}).get('request', {}).get('headers', {})
                                
                                if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master.txt', '/video/']):
                                    video_info = {
                                        'url': url,
                                        'headers': headers,
                                        'player': player['name']
                                    }
                                    if video_info not in results['videos']:
                                        results['videos'].append(video_info)
                                        print(f"\n   🎬 VÍDEO ENCONTRADO!")
                                        print(f"      URL: {url[:80]}...")
                        except:
                            pass
                    
                    # Verificar elemento video
                    videos = driver.find_elements(By.TAG_NAME, 'video')
                    for v in videos:
                        src = v.get_attribute('src')
                        if src and src.startswith('http'):
                            print(f"   📹 Video element: {src[:60]}...")
                            results['videos'].append({
                                'url': src,
                                'player': player['name'],
                                'type': 'video_element'
                            })
                    
                    driver.switch_to.default_content()
                    
                except Exception as e:
                    print(f"   Erro no iframe: {e}")
                    driver.switch_to.default_content()
            
            # Se abriu nova aba, fechar
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            
            human_delay(1, 2)
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print(f"Players encontrados: {len(results['players'])}")
        print(f"Vídeos capturados: {len(results['videos'])}")
        
        for v in results['videos']:
            print(f"\n🎬 {v.get('player', 'Unknown')}")
            print(f"   {v['url'][:100]}...")
        
        # Salvar
        with open('stealth_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Testar com episódio real
    capture_video_stealth("https://www.maxseries.one/episodio/terra-de-pecados-1x1/")
