#!/usr/bin/env python3
"""
Teste MegaEmbed -> VLC
Captura URL de vídeo do MegaEmbed e abre no VLC
"""

import subprocess
import time
import json
import re
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Instalando selenium...")
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

# URL de teste do MegaEmbed
MEGAEMBED_URL = "https://megaembed.link/#Yzg0NjI0NjI="
VLC_PATH = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

def capture_video_url(url):
    """Captura URL de vídeo usando Selenium com interceptação de rede"""
    print(f"\n[*] Abrindo: {url}")
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    video_urls = []
    
    try:
        driver.get(url)
        print("[*] Aguardando página carregar...")
        time.sleep(3)
        
        # Tentar clicar no play
        try:
            play_btn = driver.find_element(By.CSS_SELECTOR, "#play, .play-button, [class*='play']")
            play_btn.click()
            print("[*] Clicou no play")
            time.sleep(2)
        except:
            pass
        
        # Capturar logs de rede
        print("[*] Analisando requisições de rede...")
        logs = driver.get_log("performance")
        
        for log in logs:
            try:
                msg = json.loads(log["message"])["message"]
                if msg["method"] == "Network.requestWillBeSent":
                    req_url = msg["params"]["request"]["url"]
                    # Filtrar URLs de vídeo
                    if any(ext in req_url.lower() for ext in ['.m3u8', '.mp4', 'master.txt', '/hls/', '/stream/']):
                        if '.js' not in req_url.lower() and 'client' not in req_url.lower():
                            video_urls.append(req_url)
                            print(f"[+] Video URL: {req_url}")
            except:
                pass
        
        # Tentar capturar do elemento video
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            src = video.get_attribute("src") or video.get_attribute("currentSrc")
            if src and src.startswith("http"):
                video_urls.append(src)
                print(f"[+] Video element src: {src}")
        except:
            pass
        
        # Executar JavaScript para capturar
        js_result = driver.execute_script("""
            var urls = [];
            // Video element
            var video = document.querySelector('video');
            if (video) {
                if (video.src) urls.push(video.src);
                if (video.currentSrc) urls.push(video.currentSrc);
            }
            // HLS.js
            if (window.hls && window.hls.url) urls.push(window.hls.url);
            // Player global
            if (window.player && window.player.src) urls.push(window.player.src);
            return urls;
        """)
        
        if js_result:
            for u in js_result:
                if u and u.startswith("http") and '.js' not in u:
                    video_urls.append(u)
                    print(f"[+] JS capturou: {u}")
        
        # Aguardar mais um pouco se não encontrou
        if not video_urls:
            print("[*] Aguardando mais 10s...")
            time.sleep(10)
            
            logs = driver.get_log("performance")
            for log in logs:
                try:
                    msg = json.loads(log["message"])["message"]
                    if msg["method"] == "Network.requestWillBeSent":
                        req_url = msg["params"]["request"]["url"]
                        if any(ext in req_url.lower() for ext in ['.m3u8', '.mp4', 'master.txt']):
                            if '.js' not in req_url.lower():
                                video_urls.append(req_url)
                                print(f"[+] Video URL (delayed): {req_url}")
                except:
                    pass
                    
    finally:
        driver.quit()
    
    return list(set(video_urls))  # Remove duplicatas

def open_in_vlc(url):
    """Abre URL no VLC"""
    print(f"\n[*] Abrindo no VLC: {url}")
    try:
        subprocess.Popen([VLC_PATH, url])
        return True
    except Exception as e:
        print(f"[!] Erro ao abrir VLC: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE MEGAEMBED -> VLC")
    print("=" * 60)
    
    urls = capture_video_url(MEGAEMBED_URL)
    
    if urls:
        print(f"\n[+] Encontradas {len(urls)} URLs de vídeo:")
        for i, u in enumerate(urls, 1):
            print(f"  {i}. {u}")
        
        # Abrir a primeira no VLC
        best_url = urls[0]
        for u in urls:
            if '.m3u8' in u or 'master' in u:
                best_url = u
                break
        
        open_in_vlc(best_url)
        print(f"\n[+] URL para copiar:\n{best_url}")
    else:
        print("\n[!] Nenhuma URL de vídeo encontrada")
        print("[!] O MegaEmbed pode estar usando criptografia AES no JavaScript")
