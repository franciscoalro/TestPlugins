#!/usr/bin/env python3
"""
Captura de vídeo do MegaEmbed
"""

import json
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def capture_megaembed():
    print("="*60)
    print("CAPTURA DO MEGAEMBED")
    print("="*60)
    
    driver = create_driver()
    results = {'videos': [], 'api_calls': [], 'network': []}
    
    try:
        # Acessar MegaEmbed diretamente
        url = "https://megaembed.link/#3wnuij"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        
        # Aguardar carregamento
        print("\n2. Aguardando player carregar...")
        time.sleep(15)
        
        # Capturar elemento video
        print("\n3. Verificando elemento video...")
        videos = driver.find_elements(By.TAG_NAME, 'video')
        print(f"   Elementos video: {len(videos)}")
        
        for v in videos:
            src = v.get_attribute('src')
            current_src = driver.execute_script("return arguments[0].currentSrc", v)
            
            if src:
                print(f"   🎬 VIDEO SRC: {src}")
                results['videos'].append({'url': src, 'type': 'src'})
            
            if current_src:
                print(f"   🎬 CURRENT SRC: {current_src}")
                results['videos'].append({'url': current_src, 'type': 'currentSrc'})
        
        # Capturar via JavaScript
        print("\n4. Capturando via JavaScript...")
        js_result = driver.execute_script("""
            var result = {};
            
            // Video element
            var video = document.querySelector('video');
            if (video) {
                result.videoSrc = video.src;
                result.currentSrc = video.currentSrc;
            }
            
            // VidStack player
            if (window.player) {
                result.playerSrc = window.player.src;
                result.playerCurrentSrc = window.player.currentSrc;
            }
            
            // HLS.js
            if (window.hls) {
                result.hlsUrl = window.hls.url;
            }
            
            // Variáveis globais
            if (window.source) result.source = window.source;
            if (window.file) result.file = window.file;
            if (window.videoUrl) result.videoUrl = window.videoUrl;
            if (window.streamUrl) result.streamUrl = window.streamUrl;
            
            return result;
        """)
        
        print(f"   JS Result: {json.dumps(js_result, indent=2)}")
        
        for key, value in js_result.items():
            if value and isinstance(value, str) and value.startswith('http'):
                results['videos'].append({'url': value, 'type': f'js_{key}'})
        
        # Capturar logs de rede
        print("\n5. Analisando logs de rede...")
        logs = driver.get_log('performance')
        
        for log in logs:
            try:
                msg = json.loads(log['message'])['message']
                method = msg.get('method', '')
                
                if method == 'Network.requestWillBeSent':
                    req = msg.get('params', {}).get('request', {})
                    url = req.get('url', '')
                    headers = req.get('headers', {})
                    
                    # API calls
                    if '/api/' in url:
                        print(f"   📡 API: {url}")
                        results['api_calls'].append({'url': url, 'headers': headers})
                    
                    # Video URLs
                    if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                        if 'vjs.zencdn' not in url and '2mdn.net' not in url and 'vidstack' not in url:
                            print(f"   🎬 VIDEO: {url[:80]}...")
                            results['videos'].append({'url': url, 'headers': headers, 'type': 'network'})
                    
                    # CDN URLs
                    if any(x in url for x in ['cdn', 'storage', 'stream', 'media']):
                        results['network'].append({'url': url, 'headers': headers})
                        
            except:
                pass
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print("="*60)
        
        unique_videos = []
        seen = set()
        for v in results['videos']:
            url = v.get('url', '')
            if url and url not in seen and url.startswith('http'):
                seen.add(url)
                unique_videos.append(v)
        
        print(f"\nVídeos únicos: {len(unique_videos)}")
        for v in unique_videos:
            print(f"\n🎬 [{v.get('type', 'unknown')}]")
            print(f"   {v.get('url', '')[:100]}")
        
        print(f"\nChamadas de API: {len(results['api_calls'])}")
        for api in results['api_calls']:
            print(f"   📡 {api['url']}")
        
        # Salvar
        with open('megaembed_capture_results.json', 'w', encoding='utf-8') as f:
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
    capture_megaembed()
