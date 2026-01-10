#!/usr/bin/env python3
"""
Debug MegaEmbed - Verifica erros e estado do player
"""

import json
import time
import subprocess
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

VIDEO_ID = "3wnuij"
MEGAEMBED_URL = f"https://megaembed.link/e/{VIDEO_ID}"

def debug_megaembed():
    print("="*70)
    print("DEBUG MEGAEMBED")
    print("="*70)
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Habilitar logs do console
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1200, 800)
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    try:
        # 1. Carregar página
        print(f"\n[1] Carregando: {MEGAEMBED_URL}")
        driver.get(MEGAEMBED_URL)
        time.sleep(5)
        
        # 2. Verificar erros no console
        print("\n[2] Erros no console:")
        logs = driver.get_log('browser')
        for log in logs:
            level = log.get('level', '')
            message = log.get('message', '')
            if 'error' in level.lower() or 'error' in message.lower():
                print(f"  [{level}] {message[:150]}")
        
        # 3. Verificar HTML da página
        print("\n[3] Estrutura da página:")
        
        page_info = driver.execute_script("""
            return {
                title: document.title,
                url: window.location.href,
                bodyLength: document.body.innerHTML.length,
                hasVideo: !!document.querySelector('video'),
                hasMediaPlayer: !!document.querySelector('media-player'),
                hasIframe: !!document.querySelector('iframe'),
                scripts: Array.from(document.querySelectorAll('script[src]')).map(s => s.src).slice(0, 10),
                divs: Array.from(document.querySelectorAll('div[class]')).map(d => d.className).slice(0, 10)
            };
        """)
        
        print(f"  Title: {page_info['title']}")
        print(f"  URL: {page_info['url']}")
        print(f"  Body length: {page_info['bodyLength']}")
        print(f"  Has video: {page_info['hasVideo']}")
        print(f"  Has media-player: {page_info['hasMediaPlayer']}")
        print(f"  Has iframe: {page_info['hasIframe']}")
        print(f"\n  Scripts:")
        for s in page_info['scripts']:
            print(f"    {s}")
        print(f"\n  Divs:")
        for d in page_info['divs'][:5]:
            print(f"    {d}")
        
        # 4. Verificar se API foi chamada
        print("\n[4] Testando API diretamente...")
        
        api_result = driver.execute_script("""
            return fetch('/api/v1/info?id=""" + VIDEO_ID + """')
                .then(r => r.text())
                .then(data => ({success: true, data: data.substring(0, 200)}))
                .catch(e => ({success: false, error: e.toString()}));
        """)
        
        time.sleep(2)
        api_result = driver.execute_script("return window.__apiResult;") or api_result
        print(f"  API Result: {api_result}")
        
        # 5. Verificar estado do player
        print("\n[5] Estado do player:")
        
        player_state = driver.execute_script("""
            var state = {};
            
            // Verificar media-player
            var mp = document.querySelector('media-player');
            if (mp) {
                state.mediaPlayer = {
                    exists: true,
                    src: mp.getAttribute('src'),
                    state: mp.state,
                    paused: mp.paused,
                    currentTime: mp.currentTime
                };
            }
            
            // Verificar video
            var v = document.querySelector('video');
            if (v) {
                state.video = {
                    exists: true,
                    src: v.src,
                    currentSrc: v.currentSrc,
                    readyState: v.readyState,
                    paused: v.paused,
                    error: v.error ? v.error.message : null
                };
            }
            
            // Verificar erros globais
            state.errors = window.__errors || [];
            
            return state;
        """)
        
        print(f"  {json.dumps(player_state, indent=2)}")
        
        # 6. Aguardar interação manual
        print("\n[6] Navegador aberto para debug manual...")
        print("    - Verifique se o player carrega")
        print("    - Clique no play manualmente")
        print("    - Observe o Network tab no DevTools")
        
        input("\nPressione ENTER quando terminar de debugar...")
        
        # 7. Capturar estado final
        print("\n[7] Estado final:")
        
        final_state = driver.execute_script("""
            var v = document.querySelector('video');
            return {
                videoSrc: v ? (v.src || v.currentSrc) : null,
                videoDuration: v ? v.duration : null,
                videoPlaying: v ? !v.paused : null
            };
        """)
        
        print(f"  {json.dumps(final_state, indent=2)}")
        
        if final_state.get('videoSrc'):
            print(f"\n[+] VIDEO URL: {final_state['videoSrc']}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_megaembed()
