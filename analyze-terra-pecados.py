#!/usr/bin/env python3
"""
Análise da série Terra de Pecados no MaxSeries
Captura fluxo de rede para engenharia reversa dos extractors
"""

import json
import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SERIES_URL = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def setup_driver():
    """Configura Chrome com logging de rede"""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    return driver

def get_network_logs(driver):
    """Extrai logs de rede"""
    logs = driver.get_log('performance')
    events = []
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            if 'Network' in log['method']:
                events.append(log)
        except:
            pass
    return events

def find_video_urls(events):
    """Encontra URLs de vídeo nos eventos de rede"""
    video_urls = []
    patterns = [r'\.m3u8', r'\.mp4', r'/hls/', r'/video/', r'master']
    
    for event in events:
        if event.get('method') == 'Network.requestWillBeSent':
            url = event.get('params', {}).get('request', {}).get('url', '')
            headers = event.get('params', {}).get('request', {}).get('headers', {})
            
            for p in patterns:
                if re.search(p, url, re.I):
                    video_urls.append({
                        'url': url,
                        'headers': headers
                    })
                    break
    
    return video_urls

def get_episodes(series_url):
    """Busca episódios da série"""
    print(f"Buscando episódios de: {series_url}")
    
    try:
        resp = requests.get(series_url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        episodes = []
        
        # Procurar links de episódios
        ep_links = soup.select('a[href*="/episodio/"]')
        for link in ep_links[:5]:  # Pegar até 5 episódios
            href = link.get('href', '')
            title = link.get_text(strip=True) or link.get('title', '')
            if href and '/episodio/' in href:
                episodes.append({
                    'url': href if href.startswith('http') else f"https://www.maxseries.one{href}",
                    'title': title
                })
        
        # Remover duplicatas
        seen = set()
        unique = []
        for ep in episodes:
            if ep['url'] not in seen:
                seen.add(ep['url'])
                unique.append(ep)
        
        return unique
        
    except Exception as e:
        print(f"Erro ao buscar episódios: {e}")
        return []

def get_sources_from_episode(driver, episode_url):
    """Extrai fontes de um episódio"""
    print(f"\nAnalisando: {episode_url}")
    
    driver.get(episode_url)
    time.sleep(5)
    
    sources = []
    
    # Procurar botões de player
    buttons = driver.find_elements(By.CSS_SELECTOR, 
        "[data-player], [data-embed], .player-btn, [onclick*='player'], [onclick*='embed']")
    
    print(f"Botões de player encontrados: {len(buttons)}")
    
    # Procurar iframes já carregados
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        src = iframe.get_attribute('src') or iframe.get_attribute('data-src') or ''
        if src and any(d in src.lower() for d in ['playerembed', 'megaembed', 'myvidplay', 'dood', 'abyss']):
            sources.append({
                'url': src,
                'type': identify_source_type(src)
            })
    
    # Clicar em botões para revelar mais fontes
    for btn in buttons[:10]:
        try:
            data_player = btn.get_attribute('data-player') or ''
            data_embed = btn.get_attribute('data-embed') or ''
            onclick = btn.get_attribute('onclick') or ''
            
            # Extrair URL do atributo
            for attr in [data_player, data_embed]:
                if attr and ('http' in attr or attr.startswith('//')):
                    url = attr if attr.startswith('http') else f"https:{attr}"
                    sources.append({
                        'url': url,
                        'type': identify_source_type(url)
                    })
            
            # Clicar e verificar iframe
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            
            # Verificar novos iframes
            new_iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in new_iframes:
                src = iframe.get_attribute('src') or ''
                if src and src not in [s['url'] for s in sources]:
                    if any(d in src.lower() for d in ['playerembed', 'megaembed', 'myvidplay', 'dood', 'abyss', 'embed']):
                        sources.append({
                            'url': src,
                            'type': identify_source_type(src)
                        })
                        
        except Exception as e:
            pass
    
    # Procurar no HTML por URLs de embed
    html = driver.page_source
    embed_patterns = [
        r'(https?://playerembedapi\.link/[^"\'<>\s]+)',
        r'(https?://megaembed\.link/[^"\'<>\s]+)',
        r'(https?://myvidplay\.com/[^"\'<>\s]+)',
        r'(https?://[^"\'<>\s]*dood[^"\'<>\s]+)',
        r'(https?://[^"\'<>\s]*abyss[^"\'<>\s]+)',
    ]
    
    for pattern in embed_patterns:
        matches = re.findall(pattern, html, re.I)
        for url in matches:
            if url not in [s['url'] for s in sources]:
                sources.append({
                    'url': url,
                    'type': identify_source_type(url)
                })
    
    return sources

def identify_source_type(url):
    """Identifica o tipo de fonte pela URL"""
    url_lower = url.lower()
    if 'playerembed' in url_lower:
        return 'PlayerEmbedAPI'
    elif 'megaembed' in url_lower:
        return 'MegaEmbed'
    elif 'myvidplay' in url_lower or 'dood' in url_lower:
        return 'DoodStream'
    elif 'abyss' in url_lower:
        return 'Abyss'
    elif 'filemoon' in url_lower:
        return 'Filemoon'
    elif 'streamtape' in url_lower:
        return 'Streamtape'
    else:
        return 'Unknown'

def test_embed_url(driver, embed_url, source_type):
    """Testa uma URL de embed e captura o fluxo de rede"""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {source_type}")
    print(f"URL: {embed_url}")
    print('='*60)
    
    # Limpar logs anteriores
    driver.get("about:blank")
    time.sleep(1)
    get_network_logs(driver)  # Limpar
    
    driver.get(embed_url)
    print("Aguardando carregamento (20s)...")
    time.sleep(20)
    
    # Verificar iframes aninhados
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        src = iframe.get_attribute('src') or ''
        if src:
            print(f"  Iframe encontrado: {src[:80]}...")
            if any(d in src.lower() for d in ['abyss', 'short.icu']):
                print("  -> Seguindo iframe...")
                driver.get(src)
                time.sleep(15)
                break
    
    # Capturar eventos de rede
    events = get_network_logs(driver)
    video_urls = find_video_urls(events)
    
    # Verificar elemento video
    try:
        video = driver.find_element(By.TAG_NAME, "video")
        video_src = video.get_attribute('src')
        if video_src:
            print(f"  Video src: {video_src}")
            video_urls.append({'url': video_src, 'headers': {}})
    except:
        pass
    
    # Extrair domínios acessados
    domains = set()
    for event in events:
        if event.get('method') == 'Network.requestWillBeSent':
            url = event.get('params', {}).get('request', {}).get('url', '')
            match = re.search(r'https?://([^/]+)', url)
            if match:
                domain = match.group(1)
                if any(d in domain.lower() for d in ['abyss', 'playerembed', 'megaembed', 'short', 'iamcdn', 'm3u8', 'hls']):
                    domains.add(domain)
    
    return {
        'source_type': source_type,
        'embed_url': embed_url,
        'video_urls': video_urls,
        'domains': list(domains),
        'total_requests': len(events)
    }

def main():
    print("="*60)
    print("ANÁLISE: Terra de Pecados - MaxSeries")
    print("="*60)
    
    driver = setup_driver()
    results = {
        'series_url': SERIES_URL,
        'episodes': [],
        'embed_tests': []
    }
    
    try:
        # 1. Buscar episódios
        episodes = get_episodes(SERIES_URL)
        print(f"\nEpisódios encontrados: {len(episodes)}")
        
        if not episodes:
            print("Tentando acessar diretamente via Selenium...")
            driver.get(SERIES_URL)
            time.sleep(5)
            
            # Procurar episódios no DOM
            ep_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/episodio/"]')
            for link in ep_links[:5]:
                href = link.get_attribute('href')
                if href:
                    episodes.append({'url': href, 'title': link.text or 'Episódio'})
        
        # 2. Analisar primeiro episódio
        if episodes:
            ep = episodes[0]
            print(f"\nAnalisando episódio: {ep['title']}")
            
            sources = get_sources_from_episode(driver, ep['url'])
            print(f"\nFontes encontradas: {len(sources)}")
            
            for s in sources:
                print(f"  - [{s['type']}] {s['url'][:60]}...")
            
            results['episodes'].append({
                'url': ep['url'],
                'title': ep['title'],
                'sources': sources
            })
            
            # 3. Testar cada tipo de fonte
            tested_types = set()
            for source in sources:
                if source['type'] not in tested_types and source['type'] != 'Unknown':
                    tested_types.add(source['type'])
                    
                    test_result = test_embed_url(driver, source['url'], source['type'])
                    results['embed_tests'].append(test_result)
                    
                    print(f"\n  Vídeos encontrados: {len(test_result['video_urls'])}")
                    for v in test_result['video_urls']:
                        print(f"    -> {v['url'][:80]}...")
                    
                    print(f"  Domínios de interesse: {test_result['domains']}")
        
        # Salvar resultados
        with open('terra_pecados_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("RESUMO")
        print("="*60)
        print(f"Resultados salvos em: terra_pecados_analysis.json")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
