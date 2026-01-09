#!/usr/bin/env python3
"""
Captura todas as fontes de vídeo do PlayerthreeOnline
Extrai data-source dos botões de player
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
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    return driver

def get_network_logs(driver):
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
    urls = []
    for event in events:
        if event.get('method') == 'Network.requestWillBeSent':
            url = event.get('params', {}).get('request', {}).get('url', '')
            headers = event.get('params', {}).get('request', {}).get('headers', {})
            
            if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                urls.append({'url': url, 'headers': headers})
    return urls

def main():
    print("="*60)
    print("CAPTURA DE FONTES - Terra de Pecados")
    print("="*60)
    
    driver = setup_driver()
    results = {'episodes': []}
    
    try:
        # 1. Carregar página
        url = "https://playerthree.online/embed/synden/"
        print(f"\n1. Carregando: {url}")
        driver.get(url)
        time.sleep(4)
        
        # 2. Pegar lista de episódios
        episodes = driver.find_elements(By.CSS_SELECTOR, '[data-episode-id]')
        print(f"\n2. Episódios encontrados: {len(episodes)}")
        
        # Testar primeiro episódio
        if episodes:
            ep = episodes[0]
            ep_id = ep.get_attribute('data-episode-id')
            ep_text = ep.text.strip()
            print(f"\n3. Clicando no episódio: {ep_text} (ID: {ep_id})")
            
            link = ep.find_element(By.TAG_NAME, 'a')
            driver.execute_script("arguments[0].click();", link)
            time.sleep(3)
            
            # 3. Capturar botões de player com data-source
            print("\n4. Capturando fontes dos players...")
            player_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
            
            sources = []
            for btn in player_buttons:
                source = btn.get_attribute('data-source')
                data_type = btn.get_attribute('data-type')
                data_id = btn.get_attribute('data-id')
                subtitles = btn.get_attribute('data-subtitles')
                text = btn.text.strip()
                
                source_info = {
                    'name': text,
                    'url': source,
                    'type': data_type,
                    'id': data_id,
                    'subtitles': subtitles,
                    'host': identify_host(source)
                }
                sources.append(source_info)
                
                print(f"\n   {text}:")
                print(f"      URL: {source}")
                print(f"      Type: {data_type}")
                print(f"      Host: {source_info['host']}")
            
            results['episodes'].append({
                'id': ep_id,
                'title': ep_text,
                'sources': sources
            })
            
            # 4. Testar cada fonte
            print("\n" + "="*60)
            print("5. TESTANDO CADA FONTE")
            print("="*60)
            
            for source in sources:
                print(f"\n>>> Testando: {source['name']} ({source['host']})")
                print(f"    URL: {source['url']}")
                
                # Limpar logs
                get_network_logs(driver)
                
                # Navegar para a fonte
                driver.get(source['url'])
                time.sleep(5)
                
                # Verificar iframes
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                print(f"    Iframes: {len(iframes)}")
                
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if src:
                        print(f"      -> {src[:80]}...")
                        
                        # Seguir iframe se for de interesse
                        if any(x in src.lower() for x in ['abyss', 'short.icu', 'player']):
                            print(f"    Seguindo iframe...")
                            driver.get(src)
                            time.sleep(10)
                
                # Capturar URLs de vídeo
                events = get_network_logs(driver)
                video_urls = find_video_urls(events)
                
                if video_urls:
                    print(f"\n    ✓ VÍDEOS ENCONTRADOS:")
                    for v in video_urls:
                        print(f"      {v['url']}")
                        source['video_url'] = v['url']
                        source['video_headers'] = v['headers']
                else:
                    print(f"    ✗ Nenhum vídeo capturado diretamente")
                    
                    # Verificar elemento video
                    try:
                        video = driver.find_element(By.TAG_NAME, 'video')
                        video_src = video.get_attribute('src')
                        if video_src:
                            print(f"    Video element src: {video_src}")
                            source['video_url'] = video_src
                    except:
                        pass
        
        # Salvar resultados
        with open('sources_capture.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print("RESUMO")
        print("="*60)
        
        for ep in results['episodes']:
            print(f"\nEpisódio: {ep['title']}")
            for s in ep['sources']:
                status = "✓" if s.get('video_url') else "✗"
                print(f"  {status} {s['name']} ({s['host']})")
                if s.get('video_url'):
                    print(f"      -> {s['video_url'][:60]}...")
        
        print(f"\nResultados salvos em: sources_capture.json")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

def identify_host(url):
    """Identifica o host da URL"""
    url_lower = url.lower()
    if 'playerembedapi' in url_lower:
        return 'PlayerEmbedAPI'
    elif 'megaembed' in url_lower:
        return 'MegaEmbed'
    elif 'myvidplay' in url_lower or 'dood' in url_lower:
        return 'DoodStream'
    elif 'filemoon' in url_lower:
        return 'Filemoon'
    elif 'streamtape' in url_lower:
        return 'Streamtape'
    elif 'abyss' in url_lower:
        return 'Abyss'
    else:
        # Extrair domínio
        match = re.search(r'https?://([^/]+)', url)
        return match.group(1) if match else 'Unknown'

if __name__ == "__main__":
    main()
