#!/usr/bin/env python3
"""
Captura a URL HLS real do MegaEmbed e PlayerEmbedAPI
Usa Selenium com interceptação de rede mais precisa
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def capture_hls_url(embed_url, timeout=60):
    """
    Captura a URL HLS real do player
    """
    print(f"\n{'='*60}")
    print(f"CAPTURANDO HLS: {embed_url}")
    print(f"{'='*60}")
    
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    hls_urls = []
    api_data = {}
    
    try:
        driver.get(embed_url)
        print(f"\n1. Página carregada")
        
        # Aguardar player carregar
        time.sleep(5)
        
        # Coletar logs continuamente
        start_time = time.time()
        while time.time() - start_time < timeout:
            logs = driver.get_log('performance')
            
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    params = msg.get('params', {})
                    
                    if method == 'Network.requestWillBeSent':
                        url = params.get('request', {}).get('url', '')
                        
                        # Filtrar URLs de vídeo reais (excluir analytics)
                        if re.search(r'\.(m3u8|ts|mp4)(\?|$)', url, re.I):
                            if 'google' not in url and 'analytics' not in url:
                                headers = params.get('request', {}).get('headers', {})
                                hls_urls.append({
                                    'url': url,
                                    'headers': headers
                                })
                                print(f"\n   🎬 HLS/VIDEO: {url}")
                        
                        # Capturar API
                        if '/api/' in url:
                            api_data['api_url'] = url
                            print(f"   📡 API: {url}")
                    
                    # Capturar resposta da API
                    if method == 'Network.responseReceived':
                        url = params.get('response', {}).get('url', '')
                        if '/api/v1/info' in url:
                            request_id = params.get('requestId')
                            try:
                                body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                api_data['response'] = body.get('body', '')[:500]
                                print(f"   📦 API Response: {api_data['response'][:100]}...")
                            except:
                                pass
                
                except Exception as e:
                    pass
            
            # Verificar se encontrou HLS
            if hls_urls:
                print(f"\n2. HLS encontrado após {time.time() - start_time:.1f}s")
                break
            
            # Tentar clicar no play se existir
            try:
                play_btn = driver.find_element(By.CSS_SELECTOR, '[data-part="play-button"], .play-button, button[aria-label*="play"]')
                if play_btn.is_displayed():
                    play_btn.click()
                    print("   ▶️ Clicou no play")
                    time.sleep(3)
            except:
                pass
            
            time.sleep(2)
        
        # Tentar extrair via JavaScript
        print(f"\n3. Tentando extrair via JS...")
        
        js_urls = driver.execute_script("""
            var urls = [];
            
            // Interceptar XMLHttpRequest
            if (window._interceptedUrls) {
                urls = urls.concat(window._interceptedUrls);
            }
            
            // Procurar em elementos video
            document.querySelectorAll('video').forEach(function(v) {
                if (v.src) urls.push({type: 'video.src', url: v.src});
                if (v.currentSrc) urls.push({type: 'video.currentSrc', url: v.currentSrc});
            });
            
            // Procurar em source
            document.querySelectorAll('source').forEach(function(s) {
                if (s.src) urls.push({type: 'source.src', url: s.src});
            });
            
            // Procurar instâncias HLS
            if (window.Hls) {
                document.querySelectorAll('video').forEach(function(v) {
                    if (v._hls && v._hls.url) urls.push({type: 'hls.url', url: v._hls.url});
                });
            }
            
            // VidStack
            if (window.player) {
                if (window.player.src) urls.push({type: 'player.src', url: window.player.src});
                if (window.player.currentSrc) urls.push({type: 'player.currentSrc', url: window.player.currentSrc});
            }
            
            // Procurar em variáveis globais
            ['source', 'file', 'videoUrl', 'streamUrl', 'hlsUrl', 'src'].forEach(function(key) {
                if (window[key] && typeof window[key] === 'string') {
                    urls.push({type: 'window.' + key, url: window[key]});
                }
            });
            
            return urls;
        """)
        
        if js_urls:
            print(f"   JS URLs encontradas:")
            for item in js_urls:
                print(f"     - {item}")
                if item.get('url') and '.m3u8' in item.get('url', ''):
                    hls_urls.append(item)
        
        # Verificar iframes
        print(f"\n4. Verificando iframes...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute('src')
                print(f"   iframe[{i}]: {src}")
                
                # Entrar no iframe
                driver.switch_to.frame(iframe)
                
                # Procurar video dentro
                videos = driver.find_elements(By.TAG_NAME, 'video')
                for v in videos:
                    vsrc = v.get_attribute('src')
                    if vsrc:
                        print(f"     video src: {vsrc}")
                        hls_urls.append({'url': vsrc, 'type': 'iframe_video'})
                
                driver.switch_to.default_content()
            except Exception as e:
                driver.switch_to.default_content()
                print(f"   Erro iframe: {e}")
    
    finally:
        driver.quit()
    
    return {
        'hls_urls': hls_urls,
        'api_data': api_data
    }

def main():
    sources = [
        ('MegaEmbed', 'https://megaembed.link/#3wnuij'),
        ('PlayerEmbedAPI', 'https://playerembedapi.link/?v=kBJLtxCD3'),
    ]
    
    results = {}
    
    for name, url in sources:
        print(f"\n\n{'#'*60}")
        print(f"# {name}")
        print(f"{'#'*60}")
        
        try:
            result = capture_hls_url(url, timeout=45)
            results[name] = result
        except Exception as e:
            print(f"ERRO: {e}")
            results[name] = {'error': str(e)}
    
    # Resumo
    print(f"\n\n{'='*60}")
    print("RESUMO")
    print(f"{'='*60}")
    
    for name, result in results.items():
        print(f"\n{name}:")
        if result.get('hls_urls'):
            print(f"  ✅ HLS URLs encontradas:")
            for u in result['hls_urls']:
                print(f"     {u}")
        else:
            print(f"  ❌ Nenhuma URL HLS encontrada")
        
        if result.get('api_data'):
            print(f"  API: {result['api_data']}")
    
    # Salvar
    with open('hls_capture_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSalvo em hls_capture_results.json")

if __name__ == "__main__":
    main()
