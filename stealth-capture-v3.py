#!/usr/bin/env python3
"""
Captura de vídeo com técnicas anti-detecção - V3
Foco em capturar o fluxo completo do playerthree.online
"""

import json
import time
import random
import re

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

def human_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def capture_playerthree():
    """Captura diretamente do playerthree.online"""
    
    print("="*60)
    print("CAPTURA DO PLAYERTHREE.ONLINE")
    print("="*60)
    
    driver = create_driver()
    results = {'players': [], 'videos': [], 'network': []}
    
    try:
        # 1. Acessar playerthree diretamente
        url = "https://playerthree.online/embed/synden/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        human_delay(5, 8)
        
        # Salvar HTML
        html = driver.page_source
        with open('playerthree_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   HTML salvo")
        
        # 2. Extrair botões de player
        print("\n2. Extraindo players...")
        
        # Via regex
        sources = re.findall(r'data-source=["\']([^"\']+)["\']', html)
        for src in sources:
            if src.startswith('http'):
                results['players'].append(src)
                print(f"   ✓ {src[:70]}...")
        
        # Via JS
        js_sources = driver.execute_script("""
            var sources = [];
            document.querySelectorAll('[data-source]').forEach(function(el) {
                var src = el.getAttribute('data-source');
                if (src && src.startsWith('http')) {
                    sources.push({
                        url: src,
                        text: el.innerText.trim(),
                        type: el.getAttribute('data-type')
                    });
                }
            });
            return sources;
        """)
        
        print(f"\n   Players encontrados via JS: {len(js_sources)}")
        for p in js_sources:
            print(f"   - {p['text']}: {p['url'][:50]}...")
        
        # 3. Testar cada player
        for i, player in enumerate(js_sources[:3]):
            print(f"\n{'='*60}")
            print(f"TESTANDO: {player['text']}")
            print(f"URL: {player['url']}")
            print("="*60)
            
            # Navegar para o player
            driver.get(player['url'])
            human_delay(5, 8)
            
            current = driver.current_url
            print(f"   URL atual: {current}")
            
            # Verificar se é página de erro
            if 'abyss.to' in current and '/e/' not in current:
                print("   ⚠️ Vídeo expirado ou proteção ativa")
                continue
            
            # Aguardar e capturar
            print("   Aguardando player carregar...")
            human_delay(8, 12)
            
            # Capturar logs de rede
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    
                    if method == 'Network.requestWillBeSent':
                        req = msg.get('params', {}).get('request', {})
                        url = req.get('url', '')
                        headers = req.get('headers', {})
                        
                        # Salvar todas as requisições interessantes
                        if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master', 'video', 'stream']):
                            video_info = {
                                'url': url,
                                'headers': headers,
                                'player': player['text']
                            }
                            results['videos'].append(video_info)
                            print(f"\n   🎬 VÍDEO: {url[:80]}...")
                            print(f"      Headers: {json.dumps(headers, indent=8)[:200]}")
                        
                        # Salvar chamadas de API
                        if '/api/' in url:
                            results['network'].append({'url': url, 'headers': headers})
                            print(f"   📡 API: {url[:60]}...")
                    
                    if method == 'Network.responseReceived':
                        resp = msg.get('params', {}).get('response', {})
                        url = resp.get('url', '')
                        if any(x in url.lower() for x in ['.m3u8', '.mp4']):
                            print(f"   ✅ RESPOSTA: {url[:60]}...")
                            
                except Exception as e:
                    pass
            
            # Verificar elemento video
            try:
                videos = driver.find_elements(By.TAG_NAME, 'video')
                for v in videos:
                    src = v.get_attribute('src')
                    if src:
                        print(f"   📹 <video>: {src[:60]}...")
                        results['videos'].append({'url': src, 'type': 'element'})
                    
                    # Verificar currentSrc
                    current_src = driver.execute_script("return arguments[0].currentSrc", v)
                    if current_src and current_src != src:
                        print(f"   📹 currentSrc: {current_src[:60]}...")
                        results['videos'].append({'url': current_src, 'type': 'currentSrc'})
            except:
                pass
            
            # Verificar iframes aninhados
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                iframe_src = iframe.get_attribute('src')
                if iframe_src:
                    print(f"   📦 Iframe: {iframe_src[:60]}...")
                    
                    try:
                        driver.switch_to.frame(iframe)
                        human_delay(3, 5)
                        
                        # Verificar vídeos no iframe
                        inner_videos = driver.find_elements(By.TAG_NAME, 'video')
                        for v in inner_videos:
                            src = v.get_attribute('src')
                            if src:
                                print(f"      🎬 Video no iframe: {src[:50]}...")
                                results['videos'].append({'url': src, 'type': 'iframe_video'})
                        
                        driver.switch_to.default_content()
                    except:
                        driver.switch_to.default_content()
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print("="*60)
        
        unique_videos = list({v['url'] for v in results['videos'] if v.get('url')})
        print(f"\nVídeos únicos encontrados: {len(unique_videos)}")
        for v in unique_videos:
            print(f"  🎬 {v}")
        
        # Salvar
        with open('stealth_results_v3.json', 'w', encoding='utf-8') as f:
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
    capture_playerthree()
