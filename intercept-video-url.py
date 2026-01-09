#!/usr/bin/env python3
"""
Intercepta a URL final do vídeo usando Selenium com DevTools Protocol
Captura requisições de rede para encontrar .m3u8 ou .mp4
"""

import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def intercept_video_urls(embed_url, timeout=60):
    """
    Abre a URL do embed e intercepta requisições de vídeo
    """
    print(f"\n{'='*60}")
    print(f"INTERCEPTANDO VÍDEO: {embed_url}")
    print(f"{'='*60}")
    
    # Configurar Chrome com DevTools
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Habilitar logging de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    video_urls = []
    api_responses = []
    
    try:
        print(f"\n1. Abrindo URL...")
        driver.get(embed_url)
        
        print(f"2. Aguardando carregamento ({timeout}s max)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Capturar logs de performance
            logs = driver.get_log('performance')
            
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    method = message.get('method', '')
                    params = message.get('params', {})
                    
                    # Capturar requisições de rede
                    if method == 'Network.requestWillBeSent':
                        url = params.get('request', {}).get('url', '')
                        
                        # Verificar se é URL de vídeo
                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '/hls/', '/video/', 'master.txt']):
                            headers = params.get('request', {}).get('headers', {})
                            video_info = {
                                'url': url,
                                'headers': headers,
                                'type': 'request'
                            }
                            if video_info not in video_urls:
                                video_urls.append(video_info)
                                print(f"\n   🎬 VÍDEO ENCONTRADO: {url[:100]}...")
                        
                        # Capturar chamadas de API
                        if '/api/' in url:
                            print(f"   📡 API: {url}")
                    
                    # Capturar respostas
                    if method == 'Network.responseReceived':
                        url = params.get('response', {}).get('url', '')
                        mime = params.get('response', {}).get('mimeType', '')
                        
                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4']):
                            video_info = {
                                'url': url,
                                'mime': mime,
                                'type': 'response'
                            }
                            if video_info not in video_urls:
                                video_urls.append(video_info)
                                print(f"\n   ✅ RESPOSTA VÍDEO: {url[:100]}...")
                
                except Exception as e:
                    pass
            
            # Verificar se encontrou vídeo
            if video_urls:
                print(f"\n3. Vídeo encontrado após {time.time() - start_time:.1f}s")
                break
            
            time.sleep(1)
        
        # Tentar extrair do DOM também
        print(f"\n4. Verificando DOM...")
        try:
            # Procurar elemento video
            videos = driver.find_elements(By.TAG_NAME, 'video')
            for video in videos:
                src = video.get_attribute('src')
                if src:
                    print(f"   <video src>: {src}")
                    video_urls.append({'url': src, 'type': 'dom_video'})
                
                # Procurar source dentro do video
                sources = video.find_elements(By.TAG_NAME, 'source')
                for source in sources:
                    src = source.get_attribute('src')
                    if src:
                        print(f"   <source src>: {src}")
                        video_urls.append({'url': src, 'type': 'dom_source'})
            
            # Executar JavaScript para capturar variáveis
            js_result = driver.execute_script("""
                var result = {};
                
                // Tentar capturar de variáveis globais
                if (window.source) result.source = window.source;
                if (window.file) result.file = window.file;
                if (window.videoUrl) result.videoUrl = window.videoUrl;
                if (window.streamUrl) result.streamUrl = window.streamUrl;
                if (window.hlsUrl) result.hlsUrl = window.hlsUrl;
                
                // Tentar capturar de HLS.js
                if (window.Hls) {
                    var videos = document.querySelectorAll('video');
                    for (var v of videos) {
                        if (v.hls && v.hls.url) result.hlsInstance = v.hls.url;
                    }
                }
                
                // Tentar capturar de VidStack
                if (window.player) {
                    if (window.player.src) result.vidstackSrc = window.player.src;
                    if (window.player.currentSrc) result.vidstackCurrentSrc = window.player.currentSrc;
                }
                
                return result;
            """)
            
            if js_result:
                print(f"   JS Variables: {json.dumps(js_result, indent=2)}")
                for key, value in js_result.items():
                    if value and isinstance(value, str) and value.startswith('http'):
                        video_urls.append({'url': value, 'type': f'js_{key}'})
        
        except Exception as e:
            print(f"   Erro no DOM: {e}")
        
        # Aguardar mais um pouco se não encontrou
        if not video_urls:
            print(f"\n5. Aguardando mais 15s...")
            time.sleep(15)
            
            # Tentar novamente
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    if message.get('method') == 'Network.requestWillBeSent':
                        url = message.get('params', {}).get('request', {}).get('url', '')
                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4']):
                            video_urls.append({'url': url, 'type': 'late_request'})
                            print(f"   🎬 VÍDEO TARDIO: {url[:100]}...")
                except:
                    pass
    
    finally:
        driver.quit()
    
    return video_urls

def test_sources():
    """Testa as fontes conhecidas"""
    
    sources = [
        {
            'name': 'MegaEmbed',
            'url': 'https://megaembed.link/#3wnuij'
        },
        {
            'name': 'PlayerEmbedAPI',
            'url': 'https://playerembedapi.link/?v=kBJLtxCD3'
        }
    ]
    
    results = {}
    
    for source in sources:
        print(f"\n\n{'#'*60}")
        print(f"# TESTANDO: {source['name']}")
        print(f"{'#'*60}")
        
        try:
            videos = intercept_video_urls(source['url'], timeout=45)
            results[source['name']] = {
                'source_url': source['url'],
                'videos': videos,
                'success': len(videos) > 0
            }
        except Exception as e:
            print(f"ERRO: {e}")
            results[source['name']] = {
                'source_url': source['url'],
                'error': str(e),
                'success': False
            }
    
    # Salvar resultados
    print(f"\n\n{'='*60}")
    print("RESULTADOS FINAIS")
    print(f"{'='*60}")
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  URL: {result.get('source_url')}")
        print(f"  Sucesso: {result.get('success')}")
        if result.get('videos'):
            print(f"  Vídeos encontrados:")
            for v in result['videos']:
                print(f"    - {v.get('url', '')[:80]}...")
        if result.get('error'):
            print(f"  Erro: {result.get('error')}")
    
    # Salvar em arquivo
    with open('video_intercept_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em video_intercept_results.json")
    
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # URL específica passada como argumento
        url = sys.argv[1]
        videos = intercept_video_urls(url)
        print(f"\n\nVídeos encontrados: {len(videos)}")
        for v in videos:
            print(f"  - {v}")
    else:
        # Testar todas as fontes
        test_sources()
