#!/usr/bin/env python3
"""
Teste da API do PlayerThree para descobrir como carregar vídeos
"""

import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Referer': 'https://playerthree.online/',
    'Origin': 'https://playerthree.online',
}

def get_app_js():
    """Baixa e analisa o app.js"""
    print("="*60)
    print("ANALISANDO APP.JS")
    print("="*60)
    
    url = "https://playerthree.online/static/js/app.js"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Tamanho: {len(resp.text)} bytes")
        
        # Salvar
        with open('playerthree_app.js', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("Salvo em: playerthree_app.js")
        
        # Procurar endpoints de API
        api_patterns = [
            r'(\/api\/[^"\'<>\s]+)',
            r'(\/episode[^"\'<>\s]*)',
            r'(\/player[^"\'<>\s]*)',
            r'(\/video[^"\'<>\s]*)',
            r'fetch\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'url:\s*["\']([^"\']+)["\']',
        ]
        
        print("\nEndpoints encontrados:")
        found = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, resp.text)
            for m in matches:
                if m not in found and len(m) > 3:
                    found.add(m)
                    print(f"  -> {m}")
        
        # Procurar como o episódio é carregado
        print("\nProcurando lógica de carregamento de episódio...")
        
        # Procurar event handlers
        click_patterns = [
            r'click.*?function.*?\{([^}]{100,500})',
            r'data-episode-id.*?([^}]{50,300})',
            r'episode.*?([^}]{50,200})',
        ]
        
        for pattern in click_patterns:
            matches = re.findall(pattern, resp.text, re.I | re.S)
            for m in matches[:3]:
                print(f"\n  Trecho: {m[:200]}...")
        
    except Exception as e:
        print(f"Erro: {e}")

def test_episode_api():
    """Testa possíveis endpoints de episódio"""
    print("\n" + "="*60)
    print("TESTANDO ENDPOINTS DE EPISÓDIO")
    print("="*60)
    
    base_url = "https://playerthree.online"
    
    # IDs encontrados no HTML
    season_id = "12962"
    episode_ids = ["255703", "255704", "255705"]
    
    # Possíveis endpoints
    endpoints = [
        f"/api/episode/{episode_ids[0]}",
        f"/api/video/{episode_ids[0]}",
        f"/episode/{episode_ids[0]}",
        f"/video/{episode_ids[0]}",
        f"/api/season/{season_id}/episode/{episode_ids[0]}",
        f"/embed/synden/{episode_ids[0]}",
        f"/embed/synden/episode/{episode_ids[0]}",
        f"/player/{episode_ids[0]}",
    ]
    
    for ep in endpoints:
        url = base_url + ep
        print(f"\nTestando: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
            print(f"  Status: {resp.status_code}")
            print(f"  URL final: {resp.url}")
            if resp.status_code == 200:
                # Verificar se tem vídeo
                if 'm3u8' in resp.text.lower() or 'mp4' in resp.text.lower():
                    print("  -> CONTÉM REFERÊNCIA A VÍDEO!")
                    
                    # Extrair URLs
                    video_urls = re.findall(r'(https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*)', resp.text)
                    for v in video_urls[:5]:
                        print(f"     {v}")
                
                print(f"  Response: {resp.text[:300]}...")
        except Exception as e:
            print(f"  Erro: {e}")

def test_ajax_episode():
    """Testa carregamento via AJAX"""
    print("\n" + "="*60)
    print("TESTANDO AJAX PARA EPISÓDIO")
    print("="*60)
    
    base_url = "https://playerthree.online"
    episode_id = "255703"
    season_id = "12962"
    
    # Testar POST
    ajax_endpoints = [
        "/api/episode",
        "/api/video",
        "/api/player",
        "/ajax/episode",
    ]
    
    for ep in ajax_endpoints:
        url = base_url + ep
        print(f"\nPOST {url}")
        
        data = {
            'episode_id': episode_id,
            'season_id': season_id,
            'id': episode_id,
        }
        
        try:
            resp = requests.post(url, data=data, headers=HEADERS, timeout=10)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200 and resp.text:
                print(f"  Response: {resp.text[:300]}...")
        except Exception as e:
            print(f"  Erro: {e}")

def analyze_with_selenium():
    """Usa Selenium para capturar a requisição real"""
    print("\n" + "="*60)
    print("ANÁLISE COM SELENIUM")
    print("="*60)
    
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    import time
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    
    try:
        url = "https://playerthree.online/embed/synden/"
        print(f"Carregando: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Clicar no primeiro episódio
        episodes = driver.find_elements(By.CSS_SELECTOR, '[data-episode-id]')
        print(f"Episódios encontrados: {len(episodes)}")
        
        if episodes:
            print(f"Clicando no primeiro episódio...")
            driver.execute_script("arguments[0].click();", episodes[0])
            time.sleep(10)  # Esperar carregar
            
            # Capturar logs de rede
            logs = driver.get_log('performance')
            
            print(f"\nRequisições capturadas: {len(logs)}")
            
            video_requests = []
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    if log.get('method') == 'Network.requestWillBeSent':
                        url = log.get('params', {}).get('request', {}).get('url', '')
                        if any(x in url.lower() for x in ['m3u8', 'mp4', 'video', 'episode', 'api', 'player']):
                            video_requests.append({
                                'url': url,
                                'headers': log.get('params', {}).get('request', {}).get('headers', {})
                            })
                except:
                    pass
            
            print(f"\nRequisições de interesse:")
            for req in video_requests:
                print(f"  URL: {req['url']}")
                if 'Referer' in req['headers']:
                    print(f"  Referer: {req['headers']['Referer']}")
            
            # Verificar se há vídeo tocando
            try:
                video = driver.find_element(By.TAG_NAME, 'video')
                src = video.get_attribute('src')
                print(f"\nVideo src: {src}")
            except:
                print("\nNenhum elemento video encontrado")
            
            # Verificar iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"Iframes: {len(iframes)}")
            for iframe in iframes:
                src = iframe.get_attribute('src')
                print(f"  -> {src}")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

def main():
    get_app_js()
    test_episode_api()
    test_ajax_episode()
    analyze_with_selenium()

if __name__ == "__main__":
    main()
