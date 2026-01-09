#!/usr/bin/env python3
"""
Captura o fluxo completo: Episódio -> Escolher Player -> Vídeo
"""

import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
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
    """Encontra URLs de vídeo e APIs chamadas"""
    results = {
        'video_urls': [],
        'api_calls': [],
        'embeds': []
    }
    
    for event in events:
        if event.get('method') == 'Network.requestWillBeSent':
            url = event.get('params', {}).get('request', {}).get('url', '')
            headers = event.get('params', {}).get('request', {}).get('headers', {})
            
            url_lower = url.lower()
            
            # URLs de vídeo
            if any(x in url_lower for x in ['.m3u8', '.mp4', '/hls/', '/video/']):
                results['video_urls'].append({
                    'url': url,
                    'headers': headers
                })
            
            # Chamadas de API
            if '/api/' in url_lower or 'episode' in url_lower or 'player' in url_lower:
                results['api_calls'].append({
                    'url': url,
                    'headers': headers
                })
            
            # Embeds (playerembed, megaembed, etc)
            if any(x in url_lower for x in ['playerembed', 'megaembed', 'abyss', 'short.icu', 'dood', 'filemoon']):
                results['embeds'].append({
                    'url': url,
                    'headers': headers
                })
    
    return results

def main():
    print("="*60)
    print("CAPTURA DO FLUXO: Episódio -> Player -> Vídeo")
    print("="*60)
    
    driver = setup_driver()
    all_results = []
    
    try:
        # 1. Carregar página do player
        url = "https://playerthree.online/embed/synden/"
        print(f"\n1. Carregando: {url}")
        driver.get(url)
        time.sleep(3)
        
        # 2. Clicar no primeiro episódio
        print("\n2. Procurando episódios...")
        episodes = driver.find_elements(By.CSS_SELECTOR, '[data-episode-id] a')
        print(f"   Episódios encontrados: {len(episodes)}")
        
        if episodes:
            ep_text = episodes[0].text
            print(f"   Clicando em: {ep_text}")
            driver.execute_script("arguments[0].click();", episodes[0])
            time.sleep(3)
        
        # 3. Esperar aparecer os botões de player
        print("\n3. Aguardando botões de player...")
        time.sleep(2)
        
        # Procurar botões de player
        player_buttons = driver.find_elements(By.CSS_SELECTOR, 'button, .btn, [class*="player"]')
        print(f"   Botões encontrados: {len(player_buttons)}")
        
        for btn in player_buttons:
            text = btn.text.strip()
            if text:
                print(f"   - {text}")
        
        # Procurar especificamente "Player #1" e "Player #2"
        for btn in player_buttons:
            if 'Player' in btn.text:
                print(f"\n4. Clicando em: {btn.text}")
                
                # Limpar logs antes de clicar
                get_network_logs(driver)
                
                driver.execute_script("arguments[0].click();", btn)
                print("   Aguardando carregamento (15s)...")
                time.sleep(15)
                
                # Capturar requisições
                events = get_network_logs(driver)
                results = find_video_urls(events)
                
                print(f"\n   === RESULTADOS PARA {btn.text} ===")
                
                print(f"\n   URLs de Vídeo ({len(results['video_urls'])}):")
                for v in results['video_urls']:
                    print(f"      {v['url'][:100]}...")
                    if 'Referer' in v['headers']:
                        print(f"      Referer: {v['headers']['Referer']}")
                
                print(f"\n   Embeds ({len(results['embeds'])}):")
                for e in results['embeds']:
                    print(f"      {e['url'][:100]}...")
                
                print(f"\n   APIs ({len(results['api_calls'])}):")
                for a in results['api_calls']:
                    print(f"      {a['url'][:100]}...")
                
                all_results.append({
                    'player': btn.text,
                    'results': results
                })
                
                # Verificar iframes carregados
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                print(f"\n   Iframes ({len(iframes)}):")
                for iframe in iframes:
                    src = iframe.get_attribute('src') or ''
                    if src:
                        print(f"      {src[:100]}...")
                        
                        # Se for um embed conhecido, navegar para ele
                        if any(x in src.lower() for x in ['playerembed', 'megaembed']):
                            print(f"\n   -> Navegando para iframe: {src}")
                            driver.get(src)
                            time.sleep(10)
                            
                            # Capturar mais requisições
                            events2 = get_network_logs(driver)
                            results2 = find_video_urls(events2)
                            
                            print(f"\n   URLs de Vídeo do iframe ({len(results2['video_urls'])}):")
                            for v in results2['video_urls']:
                                print(f"      {v['url'][:100]}...")
                            
                            # Verificar mais iframes (cadeia)
                            inner_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                            for inner in inner_iframes:
                                inner_src = inner.get_attribute('src') or ''
                                if inner_src and any(x in inner_src.lower() for x in ['abyss', 'short.icu']):
                                    print(f"\n   -> Seguindo iframe interno: {inner_src}")
                                    driver.get(inner_src)
                                    time.sleep(15)
                                    
                                    events3 = get_network_logs(driver)
                                    results3 = find_video_urls(events3)
                                    
                                    print(f"\n   URLs de Vídeo finais ({len(results3['video_urls'])}):")
                                    for v in results3['video_urls']:
                                        print(f"      {v['url']}")
                                        print(f"      Headers: {v['headers']}")
                
                # Voltar para testar próximo player
                driver.get(url)
                time.sleep(3)
                
                # Clicar no episódio novamente
                episodes = driver.find_elements(By.CSS_SELECTOR, '[data-episode-id] a')
                if episodes:
                    driver.execute_script("arguments[0].click();", episodes[0])
                    time.sleep(3)
                
                break  # Testar só o primeiro player por enquanto
        
        # Salvar resultados
        with open('player_flow_capture.json', 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResultados salvos em: player_flow_capture.json")
        
        input("\nPressione ENTER para fechar...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
