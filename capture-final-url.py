#!/usr/bin/env python3
"""
Captura a URL final do vídeo (.m3u8/.mp4) usando undetected-chromedriver
Foco em descobrir o endpoint HTTP que pode ser replicado
"""

import json
import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def create_driver():
    """Driver stealth"""
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options)
    return driver

def capture_network_video(driver, timeout=60):
    """Captura URLs de vídeo dos logs de rede"""
    videos = []
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    method = msg.get('method', '')
                    
                    if method == 'Network.requestWillBeSent':
                        url = msg.get('params', {}).get('request', {}).get('url', '')
                        headers = msg.get('params', {}).get('request', {}).get('headers', {})
                        
                        # Filtrar URLs de vídeo
                        if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master.txt', '/video/', '.ts']):
                            # Ignorar tracking/ads
                            if not any(x in url for x in ['google', 'facebook', 'analytics', 'doubleclick', 'adsense']):
                                info = {'url': url, 'headers': headers}
                                if info not in videos:
                                    videos.append(info)
                                    print(f"\n🎬 VÍDEO: {url[:100]}...")
                                    print(f"   Headers: {json.dumps(headers, indent=2)[:200]}")
                except:
                    pass
            
            if videos:
                time.sleep(2)  # Esperar mais um pouco para pegar todas
                break
                
            time.sleep(1)
        except:
            pass
    
    return videos

def test_megaembed():
    """Testa MegaEmbed diretamente"""
    print("\n" + "="*60)
    print("TESTE: MEGAEMBED")
    print("="*60)
    
    driver = create_driver()
    results = {'source': 'megaembed', 'videos': [], 'api_data': None}
    
    try:
        # Acessar MegaEmbed
        url = "https://megaembed.link/#3wnuij"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(5)
        
        print(f"   URL atual: {driver.current_url}")
        
        # Capturar vídeos
        print("\n2. Capturando requisições de vídeo...")
        videos = capture_network_video(driver, timeout=30)
        results['videos'] = videos
        
        # Tentar extrair do DOM
        print("\n3. Verificando DOM...")
        try:
            video_els = driver.find_elements(By.TAG_NAME, 'video')
            for v in video_els:
                src = v.get_attribute('src')
                if src:
                    print(f"   <video src>: {src}")
        except:
            pass
        
        # Executar JS para capturar variáveis
        print("\n4. Capturando variáveis JS...")
        try:
            js_data = driver.execute_script("""
                var data = {};
                if (window.videoData) data.videoData = window.videoData;
                if (window.source) data.source = window.source;
                if (window.file) data.file = window.file;
                if (window.hlsUrl) data.hlsUrl = window.hlsUrl;
                
                // Tentar pegar do player
                var video = document.querySelector('video');
                if (video) {
                    data.videoSrc = video.src;
                    data.currentSrc = video.currentSrc;
                }
                
                return data;
            """)
            if js_data:
                print(f"   JS Data: {json.dumps(js_data, indent=2)}")
                results['js_data'] = js_data
        except Exception as e:
            print(f"   Erro JS: {e}")
        
    finally:
        driver.quit()
    
    return results

def test_playerembed():
    """Testa PlayerEmbedAPI com referer correto"""
    print("\n" + "="*60)
    print("TESTE: PLAYEREMBEDAPI")
    print("="*60)
    
    driver = create_driver()
    results = {'source': 'playerembedapi', 'videos': [], 'chain': []}
    
    try:
        # Primeiro acessar MaxSeries para ter cookies/referer
        print("\n1. Acessando MaxSeries primeiro...")
        driver.get("https://www.maxseries.one/")
        time.sleep(3)
        
        # Agora acessar o player
        url = "https://playerembedapi.link/?v=kBJLtxCD3"
        print(f"\n2. Acessando: {url}")
        driver.get(url)
        time.sleep(3)
        
        current = driver.current_url
        print(f"   URL atual: {current}")
        results['chain'].append(current)
        
        # Verificar iframes
        print("\n3. Verificando iframes...")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            src = iframe.get_attribute('src')
            if src:
                print(f"   Iframe: {src[:80]}...")
                results['chain'].append(src)
        
        # Entrar no iframe se existir
        if iframes:
            try:
                driver.switch_to.frame(iframes[0])
                time.sleep(3)
                
                # Verificar iframes aninhados
                nested = driver.find_elements(By.TAG_NAME, 'iframe')
                for n in nested:
                    src = n.get_attribute('src')
                    if src:
                        print(f"   Nested iframe: {src[:80]}...")
                        results['chain'].append(src)
                        
                        # Entrar no nested
                        driver.switch_to.frame(n)
                        time.sleep(5)
                        break
            except Exception as e:
                print(f"   Erro iframe: {e}")
        
        # Capturar vídeos
        print("\n4. Capturando requisições de vídeo...")
        videos = capture_network_video(driver, timeout=30)
        results['videos'] = videos
        
    finally:
        driver.quit()
    
    return results

def test_from_episode():
    """Testa a partir da página do episódio"""
    print("\n" + "="*60)
    print("TESTE: FLUXO COMPLETO DO EPISÓDIO")
    print("="*60)
    
    driver = create_driver()
    results = {'players': [], 'videos': []}
    
    try:
        # Acessar episódio
        url = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"
        print(f"\n1. Acessando: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Extrair players do HTML
        print("\n2. Extraindo players do HTML...")
        html = driver.page_source
        
        # Regex para encontrar data-source
        sources = re.findall(r'data-source="([^"]+)"', html)
        for i, src in enumerate(sources):
            print(f"   Player {i+1}: {src[:60]}...")
            results['players'].append(src)
        
        if not sources:
            print("   Nenhum player encontrado no HTML")
            # Salvar HTML para debug
            with open('episode_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("   HTML salvo em episode_debug.html")
        
        # Testar primeiro player
        if sources:
            print(f"\n3. Testando primeiro player: {sources[0][:50]}...")
            driver.get(sources[0])
            time.sleep(5)
            
            print(f"   URL atual: {driver.current_url}")
            
            # Verificar iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src:
                    print(f"   Iframe: {src[:60]}...")
            
            # Capturar vídeos
            print("\n4. Capturando vídeos...")
            videos = capture_network_video(driver, timeout=45)
            results['videos'] = videos
        
    finally:
        driver.quit()
    
    return results

def main():
    print("="*60)
    print("CAPTURA DE URLs FINAIS DE VÍDEO")
    print("="*60)
    
    all_results = {}
    
    # Teste 1: MegaEmbed direto
    try:
        all_results['megaembed'] = test_megaembed()
    except Exception as e:
        print(f"Erro MegaEmbed: {e}")
        all_results['megaembed'] = {'error': str(e)}
    
    # Teste 2: PlayerEmbedAPI
    try:
        all_results['playerembed'] = test_playerembed()
    except Exception as e:
        print(f"Erro PlayerEmbed: {e}")
        all_results['playerembed'] = {'error': str(e)}
    
    # Teste 3: Fluxo completo
    try:
        all_results['episode'] = test_from_episode()
    except Exception as e:
        print(f"Erro Episode: {e}")
        all_results['episode'] = {'error': str(e)}
    
    # Resumo
    print("\n\n" + "="*60)
    print("RESUMO FINAL")
    print("="*60)
    
    for source, data in all_results.items():
        print(f"\n{source.upper()}:")
        if 'error' in data:
            print(f"  ❌ Erro: {data['error']}")
        elif 'videos' in data and data['videos']:
            print(f"  ✅ {len(data['videos'])} vídeos encontrados:")
            for v in data['videos']:
                print(f"     - {v['url'][:80]}...")
        else:
            print(f"  ⚠️ Nenhum vídeo capturado")
    
    # Salvar
    with open('final_capture_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n\nResultados salvos em final_capture_results.json")

if __name__ == "__main__":
    main()
