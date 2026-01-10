#!/usr/bin/env python3
"""
Captura de vídeo do MegaEmbed - V2
Aguarda mais tempo para decriptação JS
"""

import json
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.add_argument('--autoplay-policy=no-user-gesture-required')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def capture_megaembed():
    print("="*60)
    print("CAPTURA DO MEGAEMBED V2")
    print("="*60)
    
    driver = create_driver()
    results = {'videos': [], 'api_responses': []}
    
    try:
        url = "https://megaembed.link/#3wnuij"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        
        # Aguardar mais tempo
        print("\n2. Aguardando decriptação (30s)...")
        time.sleep(30)
        
        # Tentar clicar no play se houver
        print("\n3. Tentando iniciar reprodução...")
        try:
            play_btn = driver.find_element(By.CSS_SELECTOR, '[data-part="play-button"], .play-button, button[aria-label*="play"]')
            play_btn.click()
            print("   Clicou no play")
            time.sleep(10)
        except:
            print("   Nenhum botão de play encontrado")
            # Tentar via JS
            driver.execute_script("""
                var video = document.querySelector('video');
                if (video) {
                    video.play().catch(function(e) { console.log('Play error:', e); });
                }
            """)
            time.sleep(10)
        
        # Verificar vídeos
        print("\n4. Verificando elementos video...")
        
        for attempt in range(5):
            videos = driver.find_elements(By.TAG_NAME, 'video')
            print(f"   Tentativa {attempt+1}: {len(videos)} elementos video")
            
            for v in videos:
                src = v.get_attribute('src')
                current_src = driver.execute_script("return arguments[0].currentSrc", v)
                ready_state = driver.execute_script("return arguments[0].readyState", v)
                
                print(f"     readyState: {ready_state}")
                
                if src:
                    print(f"     🎬 src: {src[:80]}...")
                    results['videos'].append({'url': src, 'type': 'src'})
                
                if current_src:
                    print(f"     🎬 currentSrc: {current_src[:80]}...")
                    results['videos'].append({'url': current_src, 'type': 'currentSrc'})
            
            if results['videos']:
                break
            
            time.sleep(5)
        
        # Capturar logs de rede
        print("\n5. Analisando logs de rede...")
        logs = driver.get_log('performance')
        
        hls_urls = []
        mp4_urls = []
        
        for log in logs:
            try:
                msg = json.loads(log['message'])['message']
                method = msg.get('method', '')
                
                if method == 'Network.requestWillBeSent':
                    req = msg.get('params', {}).get('request', {})
                    url = req.get('url', '')
                    headers = req.get('headers', {})
                    
                    if '.m3u8' in url.lower():
                        print(f"   🎬 HLS: {url[:80]}...")
                        hls_urls.append({'url': url, 'headers': headers})
                    
                    if '.mp4' in url.lower() and 'vidstack' not in url:
                        print(f"   🎬 MP4: {url[:80]}...")
                        mp4_urls.append({'url': url, 'headers': headers})
                    
                    if '/api/' in url:
                        print(f"   📡 API: {url}")
                        
            except:
                pass
        
        results['hls_urls'] = hls_urls
        results['mp4_urls'] = mp4_urls
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS")
        print("="*60)
        print(f"Vídeos do elemento: {len(results['videos'])}")
        print(f"URLs HLS: {len(hls_urls)}")
        print(f"URLs MP4: {len(mp4_urls)}")
        
        all_videos = results['videos'] + hls_urls + mp4_urls
        for v in all_videos:
            print(f"\n🎬 {v.get('url', '')[:100]}")
        
        with open('megaembed_v2_results.json', 'w', encoding='utf-8') as f:
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
