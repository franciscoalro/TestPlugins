#!/usr/bin/env python3
"""
Captura vídeo de ambos os players encontrados:
- Player #1: playerembedapi.link
- Player #2: megaembed.link
"""

import json
import time
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains

# Players descobertos
PLAYERS = {
    "playerembedapi": "https://playerembedapi.link/?v=kBJLtxCD3",
    "megaembed": "https://megaembed.link/#3wnuij"
}

def capture_player(driver, name, url):
    """Captura vídeo de um player específico"""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {name}")
    print(f"URL: {url}")
    print("="*60)
    
    video_urls = []
    
    # Limpar requisições
    del driver.requests
    
    # Carregar player
    driver.get(url)
    time.sleep(5)
    
    # Clicar para iniciar
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        ActionChains(driver).move_to_element(body).click().perform()
        print("[+] Clique no body")
    except:
        pass
    
    time.sleep(2)
    
    # Tentar clicar em play
    for sel in ["media-play-button", ".vds-play-button", "button", ".play-btn", "video"]:
        try:
            elem = driver.find_element(By.CSS_SELECTOR, sel)
            ActionChains(driver).move_to_element(elem).click().perform()
            print(f"[+] Clique em: {sel}")
            time.sleep(1)
        except:
            pass
    
    # Monitorar por 30 segundos
    print("\n[*] Monitorando requisições...")
    
    for i in range(30):
        time.sleep(1)
        
        # Verificar video element
        try:
            src = driver.execute_script("""
                var v = document.querySelector('video');
                return v ? (v.src || v.currentSrc) : null;
            """)
            if src and src.startswith('http') and src not in video_urls:
                if '.m3u8' in src or '.mp4' in src:
                    video_urls.append(src)
                    print(f"\n[VIDEO ELEMENT] {src}")
        except:
            pass
        
        # Verificar requisições
        for req in driver.requests:
            url_lower = req.url.lower()
            if any(x in url_lower for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                if '.js' not in url_lower and req.url not in video_urls:
                    video_urls.append(req.url)
                    print(f"\n[NET] {req.url}")
        
        if video_urls and i > 10:
            break
        
        if i % 10 == 0:
            print(f"  ... {i}s")
    
    return video_urls


def main():
    print("="*70)
    print("CAPTURA DE AMBOS OS PLAYERS")
    print("="*70)
    
    seleniumwire_options = {'disable_encoding': True}
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    driver = webdriver.Chrome(
        seleniumwire_options=seleniumwire_options,
        options=chrome_options
    )
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
    })
    
    results = {}
    
    try:
        for name, url in PLAYERS.items():
            videos = capture_player(driver, name, url)
            results[name] = videos
            
            if videos:
                print(f"\n[+] {name}: {len(videos)} vídeos encontrados")
                for v in videos:
                    print(f"    {v}")
        
        # Resultado final
        print("\n" + "="*70)
        print("RESULTADO FINAL")
        print("="*70)
        
        all_videos = []
        for name, videos in results.items():
            print(f"\n{name}:")
            for v in videos:
                print(f"  {v}")
                all_videos.append(v)
        
        # Salvar
        with open("both_players_capture.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        # Testar no VLC
        if all_videos:
            print("\n[*] Abrindo no VLC...")
            try:
                vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                subprocess.Popen([vlc, all_videos[0]])
            except:
                print(f"  vlc \"{all_videos[0]}\"")
        
        return results
        
    finally:
        input("\nPressione ENTER para fechar...")
        driver.quit()


if __name__ == "__main__":
    main()
