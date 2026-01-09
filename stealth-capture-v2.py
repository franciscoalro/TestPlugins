#!/usr/bin/env python3
"""
Captura de vídeo com técnicas anti-detecção - V2
"""

import json
import time
import random
import re

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_stealth_driver():
    """Cria driver com máxima evasão"""
    options = uc.ChromeOptions()
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=pt-BR')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def human_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def capture_video(episode_url):
    print("="*60)
    print("CAPTURA STEALTH V2")
    print("="*60)
    
    driver = create_stealth_driver()
    results = {'players': [], 'videos': [], 'html_snippets': []}
    
    try:
        # 1. Acessar página
        print(f"\n1. Acessando: {episode_url}")
        driver.get(episode_url)
        human_delay(5, 8)
        
        # 2. Salvar HTML para análise
        html = driver.page_source
        with open('episode_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("   HTML salvo em episode_page.html")
        
        # 3. Procurar players de várias formas
        print("\n2. Procurando players...")
        
        # Via regex no HTML
        sources = re.findall(r'data-source=["\']([^"\']+)["\']', html)
        for src in sources:
            if src.startswith('http'):
                results['players'].append({'url': src, 'method': 'regex'})
                print(f"   ✓ Regex: {src[:60]}...")
        
        # Via JavaScript
        js_sources = driver.execute_script("""
            var sources = [];
            // Botões com data-source
            document.querySelectorAll('[data-source]').forEach(function(el) {
                var src = el.getAttribute('data-source');
                if (src) sources.push({url: src, text: el.innerText || el.textContent});
            });
            // Links com embed
            document.querySelectorAll('a[href*="embed"], a[href*="player"]').forEach(function(el) {
                sources.push({url: el.href, text: el.innerText});
            });
            // Iframes
            document.querySelectorAll('iframe').forEach(function(el) {
                if (el.src) sources.push({url: el.src, text: 'iframe'});
            });
            return sources;
        """)
        
        for src in js_sources:
            if src['url'] and src['url'].startswith('http'):
                results['players'].append({'url': src['url'], 'name': src.get('text', ''), 'method': 'js'})
                print(f"   ✓ JS: {src['url'][:60]}...")
        
        # 4. Se não encontrou, verificar se precisa clicar em algo
        if not results['players']:
            print("\n   Tentando encontrar botões clicáveis...")
            
            # Procurar elementos que parecem botões de player
            clickables = driver.execute_script("""
                var elements = [];
                var selectors = [
                    'button', '.btn', '[role="button"]', 
                    '[onclick]', '.player-btn', '.source-btn',
                    '.tab', '.tab-item', '[data-toggle]'
                ];
                selectors.forEach(function(sel) {
                    document.querySelectorAll(sel).forEach(function(el) {
                        var text = (el.innerText || '').toLowerCase();
                        if (text.includes('player') || text.includes('assistir') || 
                            text.includes('play') || text.includes('fonte') ||
                            text.includes('servidor') || text.includes('option')) {
                            elements.push({
                                tag: el.tagName,
                                text: el.innerText.substring(0, 50),
                                class: el.className,
                                id: el.id
                            });
                        }
                    });
                });
                return elements;
            """)
            
            print(f"   Elementos clicáveis encontrados: {len(clickables)}")
            for el in clickables[:5]:
                print(f"     - {el}")
        
        # 5. Testar cada player encontrado
        unique_urls = list(set([p['url'] for p in results['players']]))
        print(f"\n3. Testando {len(unique_urls)} players únicos...")
        
        for i, url in enumerate(unique_urls[:3]):
            print(f"\n{'='*60}")
            print(f"PLAYER {i+1}: {url[:70]}...")
            print("="*60)
            
            # Abrir em nova aba
            driver.execute_script(f"window.open('{url}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])
            human_delay(5, 8)
            
            current = driver.current_url
            print(f"   URL atual: {current[:70]}...")
            
            # Verificar redirecionamento
            if 'abyss.to' in current and '/e/' not in current and '/v/' not in current:
                print("   ⚠️ Redirecionou para página principal - vídeo pode ter expirado")
            
            # Procurar iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            print(f"   Iframes: {len(iframes)}")
            
            for iframe in iframes:
                src = iframe.get_attribute('src') or ''
                if src:
                    print(f"     → {src[:60]}...")
                    
                    # Entrar no iframe
                    try:
                        driver.switch_to.frame(iframe)
                        human_delay(3, 5)
                        
                        # Verificar vídeos
                        videos = driver.find_elements(By.TAG_NAME, 'video')
                        for v in videos:
                            vsrc = v.get_attribute('src')
                            if vsrc:
                                print(f"   🎬 VIDEO: {vsrc[:70]}...")
                                results['videos'].append({'url': vsrc, 'player': url})
                        
                        # Verificar sources
                        sources = driver.find_elements(By.TAG_NAME, 'source')
                        for s in sources:
                            ssrc = s.get_attribute('src')
                            if ssrc:
                                print(f"   🎬 SOURCE: {ssrc[:70]}...")
                                results['videos'].append({'url': ssrc, 'player': url})
                        
                        driver.switch_to.default_content()
                    except Exception as e:
                        print(f"   Erro iframe: {e}")
                        driver.switch_to.default_content()
            
            # Capturar logs de rede
            try:
                logs = driver.get_log('performance')
                for log in logs:
                    try:
                        msg = json.loads(log['message'])['message']
                        if msg.get('method') == 'Network.requestWillBeSent':
                            req_url = msg.get('params', {}).get('request', {}).get('url', '')
                            if any(x in req_url.lower() for x in ['.m3u8', '.mp4', '/hls/', 'master']):
                                print(f"   🎬 REDE: {req_url[:70]}...")
                                results['videos'].append({'url': req_url, 'player': url, 'type': 'network'})
                    except:
                        pass
            except:
                pass
            
            # Fechar aba
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            human_delay(1, 2)
        
        # Resumo
        print(f"\n\n{'='*60}")
        print("RESULTADOS FINAIS")
        print("="*60)
        print(f"Players: {len(results['players'])}")
        print(f"Vídeos: {len(results['videos'])}")
        
        for v in results['videos']:
            print(f"\n🎬 {v['url'][:80]}...")
        
        with open('stealth_results_v2.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    capture_video("https://www.maxseries.one/episodio/terra-de-pecados-1x1/")
