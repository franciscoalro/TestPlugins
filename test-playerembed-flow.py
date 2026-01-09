#!/usr/bin/env python3
"""
Teste de engenharia reversa do PlayerEmbedAPI usando Selenium + CDP
Captura todas as requisições HTTP para descobrir o endpoint final do vídeo
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# URLs reais de teste (extraídas de all_sources_analysis.json)
TEST_URLS = {
    'playerembed': [
        "https://playerembedapi.link/?v=deixAL6zP",
        "https://playerembedapi.link/?v=tx3jQLbTT",
        "https://playerembedapi.link/?v=4PHWs34H0",
    ],
    'megaembed': [
        "https://megaembed.link/#85n51n",
        "https://megaembed.link/#dqd1uk",
        "https://megaembed.link/#xef8u6",
    ],
    'myvidplay': [
        "https://myvidplay.com/e/tilgznkxayrx",  # DoodStream - funciona!
    ]
}

# Armazenar requisições capturadas
captured_requests = []
captured_responses = []

def setup_driver():
    """Configura o Chrome com DevTools Protocol para interceptar requisições"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Comentado para ver o navegador
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Habilitar Network domain via CDP
    driver.execute_cdp_cmd('Network.enable', {})
    
    return driver

def get_network_logs(driver):
    """Extrai logs de rede do Chrome DevTools"""
    logs = driver.get_log('performance')
    network_events = []
    
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            if 'Network' in log['method']:
                network_events.append(log)
        except:
            pass
    
    return network_events

def analyze_network_events(events):
    """Analisa eventos de rede para encontrar URLs de vídeo"""
    results = {
        'video_urls': [],
        'iframe_urls': [],
        'api_calls': [],
        'redirects': [],
        'all_urls': []
    }
    
    video_patterns = [r'\.m3u8', r'\.mp4', r'\.ts(\?|$)', r'/hls/', r'/video/', r'/stream/']
    interest_domains = ['abyss', 'abysscdn', 'short.icu', 'playerembed', 'megaembed', 'iamcdn']
    
    for event in events:
        method = event.get('method', '')
        params = event.get('params', {})
        
        # Capturar requisições
        if method == 'Network.requestWillBeSent':
            url = params.get('request', {}).get('url', '')
            req_type = params.get('type', '')
            headers = params.get('request', {}).get('headers', {})
            
            req_info = {
                'url': url,
                'type': req_type,
                'headers': headers,
                'redirectUrl': params.get('redirectResponse', {}).get('url', '')
            }
            
            results['all_urls'].append(req_info)
            
            # Classificar
            url_lower = url.lower()
            
            # URLs de vídeo
            for pattern in video_patterns:
                if re.search(pattern, url_lower):
                    results['video_urls'].append(req_info)
                    break
            
            # Domínios de interesse
            for domain in interest_domains:
                if domain in url_lower:
                    if '/api/' in url_lower:
                        results['api_calls'].append(req_info)
                    elif 'iframe' in url_lower or 'embed' in url_lower or req_type == 'Document':
                        results['iframe_urls'].append(req_info)
                    break
            
            # Redirects
            if params.get('redirectResponse'):
                results['redirects'].append({
                    'from': params.get('redirectResponse', {}).get('url', ''),
                    'to': url,
                    'status': params.get('redirectResponse', {}).get('status', '')
                })
        
        # Capturar respostas
        elif method == 'Network.responseReceived':
            url = params.get('response', {}).get('url', '')
            status = params.get('response', {}).get('status', '')
            mime = params.get('response', {}).get('mimeType', '')
            
            # Se for resposta de vídeo
            if any(re.search(p, url.lower()) for p in video_patterns):
                results['video_urls'].append({
                    'url': url,
                    'status': status,
                    'mimeType': mime,
                    'headers': params.get('response', {}).get('headers', {})
                })
    
    return results

def test_direct_embed(driver, url, name):
    """Testa uma URL de embed diretamente"""
    print("\n" + "="*60)
    print(f"TESTE: {name}")
    print(f"URL: {url}")
    print("="*60)
    
    try:
        driver.get(url)
        print("Aguardando carregamento e execução de JS...")
        time.sleep(15)  # Tempo para JS executar
        
        # Verificar se há video element
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            video_src = video.get_attribute('src')
            print(f"Video element src: {video_src}")
            
            # Verificar sources dentro do video
            sources = video.find_elements(By.TAG_NAME, "source")
            for s in sources:
                print(f"  Source: {s.get_attribute('src')}")
        except:
            print("Nenhum elemento video encontrado diretamente")
        
        # Verificar iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Iframes encontrados: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute('src') or ''
            if src:
                print(f"  Iframe {i+1}: {src[:80]}...")
                
                # Se for iframe de interesse, entrar nele
                if any(d in src.lower() for d in ['abyss', 'short.icu', 'player']):
                    print(f"  -> Entrando no iframe...")
                    driver.get(src)
                    time.sleep(10)
                    break
        
        # Capturar todos os eventos de rede
        all_events = get_network_logs(driver)
        print(f"Eventos de rede capturados: {len(all_events)}")
        
        # Analisar eventos
        results = analyze_network_events(all_events)
        return results
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_maxseries_episode(driver):
    """Testa um episódio real do MaxSeries para capturar o fluxo"""
    print("\n" + "="*60)
    print("TESTE: Episódio MaxSeries")
    print("="*60)
    
    try:
        driver.get(MAXSERIES_EPISODE)
        print(f"Carregando: {MAXSERIES_EPISODE}")
        
        # Esperar a página carregar
        time.sleep(5)
        
        # Capturar logs iniciais
        initial_events = get_network_logs(driver)
        print(f"Eventos de rede capturados: {len(initial_events)}")
        
        # Procurar botões de player/fonte
        try:
            # Tentar encontrar e clicar em botões de player
            player_buttons = driver.find_elements(By.CSS_SELECTOR, 
                "[data-player], .player-option, .source-btn, [onclick*='player'], .btn-player, [data-embed]")
            print(f"Encontrados {len(player_buttons)} botões de player")
            
            for i, btn in enumerate(player_buttons[:5]):  # Testar até 5 fontes
                try:
                    btn_text = btn.text or btn.get_attribute('data-player') or btn.get_attribute('title') or f"Botão {i+1}"
                    if btn_text.strip():
                        print(f"\nClicando em: {btn_text}")
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(8)  # Esperar carregar o player
                except Exception as e:
                    print(f"Erro ao clicar: {e}")
                    
        except Exception as e:
            print(f"Erro ao procurar botões: {e}")
        
        # Procurar iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"\nEncontrados {len(iframes)} iframes")
        
        interesting_iframe = None
        for i, iframe in enumerate(iframes):
            src = iframe.get_attribute('src') or iframe.get_attribute('data-src') or ''
            if src:
                print(f"  Iframe {i+1}: {src[:100]}...")
                
                # Se for playerembedapi ou similar
                if any(domain in src.lower() for domain in ['playerembed', 'megaembed', 'abyss', 'short.icu']):
                    print(f"  -> Iframe de interesse detectado!")
                    interesting_iframe = src
        
        # Se encontrou iframe interessante, navegar para ele
        if interesting_iframe:
            print(f"\nNavegando para iframe: {interesting_iframe}")
            driver.get(interesting_iframe)
            time.sleep(15)  # Tempo para JS executar
        
        # Capturar todos os eventos de rede
        all_events = get_network_logs(driver)
        print(f"\nTotal de eventos de rede: {len(all_events)}")
        
        # Analisar eventos
        results = analyze_network_events(all_events)
        return results
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_results(results):
    """Imprime os resultados de forma organizada"""
    if not results:
        print("Nenhum resultado")
        return
    
    print("\n" + "="*60)
    print("URLS DE VÍDEO ENCONTRADAS:")
    print("="*60)
    
    if results['video_urls']:
        seen = set()
        for req in results['video_urls']:
            url = req.get('url', '')
            if url and url not in seen:
                seen.add(url)
                print(f"\n  URL: {url}")
                if 'status' in req:
                    print(f"  Status: {req['status']}")
                if 'mimeType' in req:
                    print(f"  MIME: {req['mimeType']}")
                if 'headers' in req:
                    headers = req['headers']
                    for h in ['Referer', 'Origin', 'referer', 'origin']:
                        if h in headers:
                            print(f"  {h}: {headers[h]}")
    else:
        print("  Nenhuma URL de vídeo capturada diretamente")
    
    print("\n" + "="*60)
    print("IFRAMES/EMBEDS DETECTADOS:")
    print("="*60)
    
    if results['iframe_urls']:
        seen = set()
        for req in results['iframe_urls']:
            url = req.get('url', '')
            if url and url not in seen:
                seen.add(url)
                print(f"  {url[:100]}...")
    else:
        print("  Nenhum iframe de interesse")
    
    print("\n" + "="*60)
    print("REDIRECTS:")
    print("="*60)
    
    if results['redirects']:
        for r in results['redirects'][:10]:
            print(f"  {r.get('status', '?')} {r.get('from', '')[:60]}...")
            print(f"    -> {r.get('to', '')[:60]}...")
    else:
        print("  Nenhum redirect capturado")
    
    print("\n" + "="*60)
    print("CHAMADAS DE API:")
    print("="*60)
    
    if results['api_calls']:
        for req in results['api_calls']:
            print(f"  {req.get('url', '')}")
    else:
        print("  Nenhuma chamada de API")
    
    # Mostrar domínios únicos de interesse
    print("\n" + "="*60)
    print("DOMÍNIOS DE INTERESSE ACESSADOS:")
    print("="*60)
    
    interest_domains = ['abyss', 'abysscdn', 'short.icu', 'playerembed', 'megaembed', 'iamcdn', 'm3u8', 'hls']
    domains_found = set()
    
    for req in results['all_urls']:
        url = req.get('url', '').lower()
        for domain in interest_domains:
            if domain in url:
                try:
                    match = re.search(r'https?://([^/]+)', req.get('url', ''))
                    if match:
                        domains_found.add(match.group(1))
                except:
                    pass
    
    for d in sorted(domains_found):
        print(f"  - {d}")
    
    print(f"\nTotal de URLs capturadas: {len(results['all_urls'])}")

def save_results(results, filename):
    """Salva resultados em JSON"""
    # Filtrar apenas dados relevantes para não ficar muito grande
    filtered = {
        'video_urls': results['video_urls'],
        'iframe_urls': results['iframe_urls'],
        'api_calls': results['api_calls'],
        'redirects': results['redirects'],
        'interesting_urls': [
            r for r in results['all_urls'] 
            if any(d in r.get('url', '').lower() for d in ['abyss', 'playerembed', 'megaembed', 'short.icu', 'm3u8', 'mp4', 'hls'])
        ]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nResultados salvos em: {filename}")

def main():
    print("="*60)
    print("TESTE DE ENGENHARIA REVERSA - PlayerEmbedAPI & MegaEmbed")
    print("Usando Selenium + Chrome DevTools Protocol")
    print("="*60)
    
    driver = setup_driver()
    all_results = {}
    
    try:
        # Testar PlayerEmbedAPI
        print("\n\n>>> TESTANDO PLAYEREMBEDAPI <<<")
        for i, url in enumerate(TEST_URLS['playerembed'][:1]):  # Testar 1 URL
            results = test_direct_embed(driver, url, f"PlayerEmbedAPI #{i+1}")
            if results:
                print_results(results)
                all_results[f'playerembed_{i+1}'] = results
        
        # Testar MegaEmbed
        print("\n\n>>> TESTANDO MEGAEMBED <<<")
        for i, url in enumerate(TEST_URLS['megaembed'][:1]):  # Testar 1 URL
            results = test_direct_embed(driver, url, f"MegaEmbed #{i+1}")
            if results:
                print_results(results)
                all_results[f'megaembed_{i+1}'] = results
        
        # Testar MyVidPlay (DoodStream) - referência que funciona
        print("\n\n>>> TESTANDO MYVIDPLAY (REFERÊNCIA) <<<")
        for i, url in enumerate(TEST_URLS['myvidplay'][:1]):
            results = test_direct_embed(driver, url, f"MyVidPlay #{i+1}")
            if results:
                print_results(results)
                all_results[f'myvidplay_{i+1}'] = results
        
        # Salvar todos os resultados
        save_results(all_results, 'playerembed_capture.json')
        
        input("\nPressione ENTER para fechar o navegador...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
