#!/usr/bin/env python3
"""
Simula o fluxo real: MaxSeries -> Episódio -> Player -> Vídeo
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

def test_real_flow():
    print("="*60)
    print("TESTE DE FLUXO REAL - MAXSERIES")
    print("="*60)
    
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remover flag de webdriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        '''
    })
    
    try:
        # 1. Acessar página do episódio
        episode_url = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"
        print(f"\n1. Acessando episódio: {episode_url}")
        driver.get(episode_url)
        time.sleep(3)
        
        # 2. Encontrar botões de player
        print("\n2. Procurando botões de player...")
        buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-source]')
        
        players = []
        for btn in buttons:
            source = btn.get_attribute('data-source')
            text = btn.text.strip()
            if source:
                players.append({'name': text, 'url': source})
                print(f"   - {text}: {source[:60]}...")
        
        if not players:
            print("   Nenhum player encontrado!")
            # Tentar via JavaScript
            players_js = driver.execute_script("""
                var buttons = document.querySelectorAll('button[data-source]');
                var result = [];
                buttons.forEach(function(btn) {
                    result.push({
                        name: btn.innerText.trim(),
                        url: btn.getAttribute('data-source')
                    });
                });
                return result;
            """)
            if players_js:
                players = players_js
                print(f"   Encontrados via JS: {len(players)}")
        
        # 3. Testar cada player
        results = []
        
        for i, player in enumerate(players[:3]):  # Testar até 3 players
            print(f"\n{'='*60}")
            print(f"3.{i+1}. TESTANDO: {player['name']}")
            print(f"     URL: {player['url']}")
            print(f"{'='*60}")
            
            # Abrir nova aba
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            # Navegar para o player com referer correto
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                'headers': {'Referer': episode_url}
            })
            
            driver.get(player['url'])
            time.sleep(5)
            
            # Capturar URL atual
            current_url = driver.current_url
            print(f"     URL atual: {current_url}")
            
            # Verificar se redirecionou para página principal
            if 'abyss.to' in current_url and '/e/' not in current_url:
                print("     ⚠️ Redirecionou para página principal do Abyss")
                print("     Possível causa: vídeo expirado ou proteção anti-bot")
            
            # Procurar iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"     Iframes encontrados: {len(iframes)}")
            
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src:
                    print(f"       - {src[:80]}...")
            
            # Capturar logs de rede
            video_urls = []
            logs = driver.get_log('performance')
            
            for log in logs:
                try:
                    msg = json.loads(log['message'])['message']
                    if msg.get('method') == 'Network.requestWillBeSent':
                        url = msg.get('params', {}).get('request', {}).get('url', '')
                        if any(x in url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                            if url not in video_urls:
                                video_urls.append(url)
                                print(f"     🎬 VÍDEO: {url[:80]}...")
                except:
                    pass
            
            # Tentar entrar no iframe
            if iframes and not video_urls:
                print("\n     Tentando acessar iframe...")
                for iframe in iframes:
                    try:
                        driver.switch_to.frame(iframe)
                        time.sleep(2)
                        
                        # Verificar vídeo no iframe
                        videos = driver.find_elements(By.TAG_NAME, 'video')
                        for v in videos:
                            src = v.get_attribute('src')
                            if src:
                                print(f"     📹 Video src: {src}")
                                video_urls.append(src)
                        
                        driver.switch_to.default_content()
                    except Exception as e:
                        print(f"     Erro no iframe: {e}")
                        driver.switch_to.default_content()
            
            results.append({
                'player': player['name'],
                'source_url': player['url'],
                'final_url': current_url,
                'video_urls': video_urls,
                'success': len(video_urls) > 0
            })
            
            # Fechar aba
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESUMO DOS RESULTADOS")
        print(f"{'='*60}")
        
        for r in results:
            status = "✅" if r['success'] else "❌"
            print(f"\n{status} {r['player']}")
            print(f"   Source: {r['source_url'][:50]}...")
            print(f"   Final: {r['final_url'][:50]}...")
            if r['video_urls']:
                print(f"   Vídeos: {len(r['video_urls'])}")
                for v in r['video_urls']:
                    print(f"     - {v[:70]}...")
        
        # Salvar
        with open('real_flow_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_real_flow()
