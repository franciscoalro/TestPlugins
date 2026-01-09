#!/usr/bin/env python3
"""
Captura profunda - segue toda a cadeia de iframes até encontrar o vídeo
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    return driver

def get_all_requests(driver):
    """Captura todas as requisições de rede"""
    logs = driver.get_log('performance')
    requests = []
    
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            method = log.get('method', '')
            
            if method == 'Network.requestWillBeSent':
                url = log.get('params', {}).get('request', {}).get('url', '')
                headers = log.get('params', {}).get('request', {}).get('headers', {})
                requests.append({
                    'url': url,
                    'headers': headers,
                    'type': 'request'
                })
            elif method == 'Network.responseReceived':
                url = log.get('params', {}).get('response', {}).get('url', '')
                status = log.get('params', {}).get('response', {}).get('status', 0)
                mime = log.get('params', {}).get('response', {}).get('mimeType', '')
                requests.append({
                    'url': url,
                    'status': status,
                    'mime': mime,
                    'type': 'response'
                })
        except:
            pass
    
    return requests

def test_source(driver, name, url):
    """Testa uma fonte específica seguindo toda a cadeia"""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    # Limpar logs
    driver.get("about:blank")
    time.sleep(1)
    get_all_requests(driver)
    
    # Carregar URL
    print("\n1. Carregando URL inicial...")
    driver.get(url)
    time.sleep(5)
    
    # Seguir cadeia de iframes (até 3 níveis)
    for level in range(3):
        print(f"\n2.{level+1}. Verificando iframes (nível {level+1})...")
        
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"     Iframes encontrados: {len(iframes)}")
        
        interesting_iframe = None
        for iframe in iframes:
            src = iframe.get_attribute('src') or ''
            if src and not 'google' in src.lower():
                print(f"     -> {src[:80]}...")
                
                # Priorizar iframes de interesse
                if any(x in src.lower() for x in ['abyss', 'short.icu', 'player', 'embed', 'video']):
                    interesting_iframe = src
                    break
        
        if interesting_iframe:
            print(f"\n     Seguindo: {interesting_iframe[:60]}...")
            driver.get(interesting_iframe)
            time.sleep(8)
        else:
            break
    
    # Esperar mais para JS executar
    print("\n3. Aguardando execução de JS (20s)...")
    time.sleep(20)
    
    # Capturar todas as requisições
    requests = get_all_requests(driver)
    
    # Filtrar URLs de vídeo
    video_urls = []
    all_interesting = []
    
    for req in requests:
        url = req.get('url', '').lower()
        
        # URLs de vídeo
        if any(x in url for x in ['.m3u8', '.mp4', '/hls/', 'master.txt', '/video/']):
            video_urls.append(req)
        
        # URLs de interesse
        if any(x in url for x in ['abyss', 'playerembed', 'megaembed', 'short.icu', 'iamcdn']):
            all_interesting.append(req)
    
    print(f"\n4. RESULTADOS:")
    print(f"   Total de requisições: {len(requests)}")
    print(f"   URLs de vídeo: {len(video_urls)}")
    
    if video_urls:
        print("\n   ✓ VÍDEOS ENCONTRADOS:")
        seen = set()
        for v in video_urls:
            if v['url'] not in seen:
                seen.add(v['url'])
                print(f"\n   URL: {v['url']}")
                if 'headers' in v:
                    for h in ['Referer', 'Origin', 'referer', 'origin']:
                        if h in v['headers']:
                            print(f"   {h}: {v['headers'][h]}")
    else:
        print("\n   ✗ Nenhum vídeo encontrado nas requisições")
        
        # Verificar elemento video
        try:
            video = driver.find_element(By.TAG_NAME, 'video')
            video_src = video.get_attribute('src')
            if video_src:
                print(f"\n   Video element src: {video_src}")
                video_urls.append({'url': video_src, 'source': 'element'})
        except:
            pass
        
        # Verificar source dentro de video
        try:
            sources = driver.find_elements(By.CSS_SELECTOR, 'video source')
            for s in sources:
                src = s.get_attribute('src')
                if src:
                    print(f"   Video source: {src}")
                    video_urls.append({'url': src, 'source': 'element'})
        except:
            pass
    
    print(f"\n   URLs de interesse ({len(all_interesting)}):")
    seen = set()
    for req in all_interesting[:20]:
        url = req.get('url', '')
        if url not in seen:
            seen.add(url)
            print(f"   - {url[:80]}...")
    
    return {
        'name': name,
        'source_url': url,
        'video_urls': video_urls,
        'interesting_urls': list(seen)
    }

def main():
    print("="*60)
    print("CAPTURA PROFUNDA - PlayerEmbedAPI & MegaEmbed")
    print("="*60)
    
    driver = setup_driver()
    
    # Fontes para testar (do episódio Terra de Pecados)
    sources = [
        ("PlayerEmbedAPI", "https://playerembedapi.link/?v=kBJLtxCD3"),
        ("MegaEmbed", "https://megaembed.link/#3wnuij"),
    ]
    
    results = []
    
    try:
        for name, url in sources:
            result = test_source(driver, name, url)
            results.append(result)
        
        # Salvar resultados
        with open('deep_capture.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print("\n" + "="*60)
        print("RESUMO FINAL")
        print("="*60)
        
        for r in results:
            status = "✓" if r['video_urls'] else "✗"
            print(f"\n{status} {r['name']}:")
            if r['video_urls']:
                for v in r['video_urls']:
                    print(f"   -> {v.get('url', '')[:70]}...")
            else:
                print("   Nenhum vídeo encontrado")
        
        print(f"\nResultados salvos em: deep_capture.json")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
