#!/usr/bin/env python3
"""
Captura URL do Google Cloud Storage do PlayerEmbedAPI
"""

import json
import time
import random
import re

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def capture_gcs_video():
    print("="*60)
    print("CAPTURA DE URL DO GOOGLE CLOUD STORAGE")
    print("="*60)
    
    driver = create_driver()
    results = {'gcs_urls': [], 'all_videos': []}
    
    try:
        # Acessar playerthree
        url = "https://playerthree.online/embed/synden/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(8)
        
        # Encontrar iframe do playerembedapi
        print("\n2. Procurando iframe do PlayerEmbedAPI...")
        
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        player_iframe = None
        
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            print(f"   Iframe: {src[:60]}...")
            if 'playerembedapi' in src:
                player_iframe = iframe
                break
        
        if player_iframe:
            print(f"\n3. Entrando no iframe: {player_iframe.get_attribute('src')[:60]}...")
            driver.switch_to.frame(player_iframe)
            time.sleep(5)
            
            # Verificar iframes aninhados
            nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes aninhados: {len(nested_iframes)}")
            
            for nested in nested_iframes:
                nested_src = nested.get_attribute('src') or ''
                print(f"   → {nested_src[:60]}...")
                
                if 'short.icu' in nested_src or 'abyss' in nested_src:
                    print(f"\n4. Entrando no iframe aninhado...")
                    driver.switch_to.frame(nested)
                    time.sleep(5)
                    break
            
            # Aguardar vídeo carregar
            print("\n5. Aguardando vídeo carregar...")
            time.sleep(10)
            
            # Capturar elemento video
            videos = driver.find_elements(By.TAG_NAME, 'video')
            print(f"   Elementos video: {len(videos)}")
            
            for v in videos:
                src = v.get_attribute('src')
                current_src = driver.execute_script("return arguments[0].currentSrc", v)
                
                if src:
                    print(f"\n   🎬 VIDEO SRC: {src}")
                    results['all_videos'].append(src)
                    if 'storage.googleapis.com' in src or 'googleusercontent' in src:
                        results['gcs_urls'].append(src)
                
                if current_src and current_src != src:
                    print(f"   🎬 CURRENT SRC: {current_src}")
                    results['all_videos'].append(current_src)
                    if 'storage.googleapis.com' in current_src or 'googleusercontent' in current_src:
                        results['gcs_urls'].append(current_src)
            
            # Capturar via JavaScript
            js_src = driver.execute_script("""
                var result = {};
                var video = document.querySelector('video');
                if (video) {
                    result.src = video.src;
                    result.currentSrc = video.currentSrc;
                }
                // Tentar HLS.js
                if (window.Hls) {
                    result.hlsUrl = window.Hls.DefaultConfig ? 'HLS detected' : null;
                }
                // Variáveis globais
                if (window.source) result.source = window.source;
                if (window.file) result.file = window.file;
                if (window.videoUrl) result.videoUrl = window.videoUrl;
                return result;
            """)
            
            print(f"\n   JS Result: {json.dumps(js_src, indent=2)}")
            
            driver.switch_to.default_content()
        
        # Capturar logs de rede
        print("\n6. Analisando logs de rede...")
        logs = driver.get_log('performance')
        
        for log in logs:
            try:
                msg = json.loads(log['message'])['message']
                if msg.get('method') == 'Network.requestWillBeSent':
                    req_url = msg.get('params', {}).get('request', {}).get('url', '')
                    headers = msg.get('params', {}).get('request', {}).get('headers', {})
                    
                    # Google Cloud Storage
                    if 'storage.googleapis.com' in req_url or 'googleusercontent' in req_url:
                        print(f"\n   🎯 GCS URL: {req_url}")
                        print(f"      Headers: {json.dumps(headers, indent=8)}")
                        results['gcs_urls'].append({
                            'url': req_url,
                            'headers': headers
                        })
                    
                    # Outros vídeos
                    if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/']):
                        if 'vjs.zencdn' not in req_url and '2mdn.net' not in req_url:
                            print(f"   🎬 Video: {req_url[:80]}...")
                            results['all_videos'].append(req_url)
            except:
                pass
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print("="*60)
        
        print(f"\nURLs do Google Cloud Storage: {len(results['gcs_urls'])}")
        for url in results['gcs_urls']:
            if isinstance(url, dict):
                print(f"\n  🎯 {url['url']}")
            else:
                print(f"\n  🎯 {url}")
        
        # Salvar
        with open('gcs_capture_results.json', 'w', encoding='utf-8') as f:
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
    capture_gcs_video()
