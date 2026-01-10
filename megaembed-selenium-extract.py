#!/usr/bin/env python3
"""
MegaEmbed Extractor usando Selenium
1. Executa o JavaScript real no browser
2. Captura a URL do vídeo descriptografada
3. Mostra como replicar via HTTP puro
"""

import json
import time
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

# URL de teste
TEST_URL = "https://megaembed.link/#Yzg0NjI0NjI="

class MegaEmbedSeleniumExtractor:
    def __init__(self):
        self.video_url = None
        self.all_requests = []
        self.cookies = {}
        self.headers = {}
    
    def extract(self, url):
        print(f"\n{'='*60}")
        print("MEGAEMBED SELENIUM EXTRACTOR")
        print(f"{'='*60}")
        print(f"URL: {url}")
        
        # Configurar Selenium Wire
        seleniumwire_options = {
            'disable_encoding': True,
        }
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = webdriver.Chrome(
            seleniumwire_options=seleniumwire_options,
            options=chrome_options
        )
        
        try:
            print("\n[1] Carregando página...")
            driver.get(url)
            time.sleep(3)
            
            # Capturar cookies
            self.cookies = {c['name']: c['value'] for c in driver.get_cookies()}
            print(f"[+] Cookies: {list(self.cookies.keys())}")
            
            # Clicar no play
            print("\n[2] Clicando no play...")
            try:
                for selector in ["#play", ".play-button", "button", "#player-button-container"]:
                    try:
                        btn = driver.find_element(By.CSS_SELECTOR, selector)
                        btn.click()
                        print(f"[+] Clicou: {selector}")
                        time.sleep(2)
                        break
                    except:
                        pass
            except:
                pass
            
            print("\n[3] Aguardando vídeo carregar (30s)...")
            
            # Aguardar e monitorar requisições
            for i in range(30):
                time.sleep(1)
                
                # Verificar se vídeo carregou
                try:
                    video_src = driver.execute_script("""
                        var v = document.querySelector('video');
                        if (v && v.src && v.src.startsWith('http')) return v.src;
                        if (v && v.currentSrc && v.currentSrc.startsWith('http')) return v.currentSrc;
                        if (window.hls && window.hls.url) return window.hls.url;
                        return null;
                    """)
                    
                    if video_src and '.m3u8' in video_src or '.mp4' in video_src:
                        self.video_url = video_src
                        print(f"\n[+] VIDEO ENCONTRADO: {video_src[:80]}...")
                        break
                except:
                    pass
                
                # Verificar requisições de rede
                for req in driver.requests:
                    url_lower = req.url.lower()
                    if any(ext in url_lower for ext in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                        if '.js' not in url_lower and 'client' not in url_lower:
                            self.video_url = req.url
                            self.headers = dict(req.headers) if req.headers else {}
                            print(f"\n[+] VIDEO NA REDE: {req.url[:80]}...")
                            break
                
                if self.video_url:
                    break
                
                if i % 5 == 0:
                    print(f"  ... {i}s")
            
            # Capturar todas as requisições relevantes
            print("\n[4] Analisando requisições...")
            for req in driver.requests:
                if 'megaembed' in req.url or '/api/' in req.url:
                    req_data = {
                        "method": req.method,
                        "url": req.url,
                        "headers": dict(req.headers) if req.headers else {},
                    }
                    
                    if req.response:
                        req_data["status"] = req.response.status_code
                        req_data["response_headers"] = dict(req.response.headers) if req.response.headers else {}
                        
                        if req.response.body:
                            try:
                                body = req.response.body.decode('utf-8', errors='ignore')
                                req_data["body"] = body[:1000]
                            except:
                                pass
                    
                    self.all_requests.append(req_data)
            
            # Executar JS para capturar dados internos
            print("\n[5] Extraindo dados do JavaScript...")
            js_data = driver.execute_script("""
                var result = {};
                
                // Variáveis globais
                try { if (window.source) result.source = window.source; } catch(e) {}
                try { if (window.file) result.file = window.file; } catch(e) {}
                try { if (window.videoUrl) result.videoUrl = window.videoUrl; } catch(e) {}
                
                // HLS
                try {
                    if (window.hls) {
                        result.hlsUrl = window.hls.url;
                        if (window.hls.levels) {
                            result.hlsLevels = window.hls.levels.map(l => ({
                                url: l.url,
                                bitrate: l.bitrate,
                                width: l.width,
                                height: l.height
                            }));
                        }
                    }
                } catch(e) {}
                
                // Video element
                try {
                    var video = document.querySelector('video');
                    if (video) {
                        result.videoSrc = video.src;
                        result.videoCurrentSrc = video.currentSrc;
                    }
                } catch(e) {}
                
                // Player
                try {
                    if (window.player) {
                        result.playerSrc = window.player.src;
                    }
                } catch(e) {}
                
                return result;
            """)
            
            print(f"[+] JS Data: {json.dumps(js_data, indent=2)}")
            
            # Se não encontrou via rede, tentar do JS
            if not self.video_url:
                for key in ['source', 'file', 'videoUrl', 'hlsUrl', 'videoSrc', 'videoCurrentSrc']:
                    if key in js_data and js_data[key]:
                        val = js_data[key]
                        if isinstance(val, str) and val.startswith('http'):
                            self.video_url = val
                            break
            
            return self.video_url
            
        finally:
            driver.quit()
    
    def print_http_replication(self):
        """Mostra como replicar via HTTP"""
        print(f"\n{'='*60}")
        print("COMO REPLICAR VIA HTTP")
        print(f"{'='*60}")
        
        if self.video_url:
            print(f"\n[VIDEO URL]")
            print(f"  {self.video_url}")
            
            print(f"\n[HEADERS NECESSÁRIOS]")
            important_headers = ['User-Agent', 'Referer', 'Origin', 'Cookie']
            for h in important_headers:
                if h in self.headers:
                    print(f"  {h}: {self.headers[h]}")
            
            print(f"\n[COOKIES]")
            for name, value in self.cookies.items():
                print(f"  {name}={value}")
            
            print(f"\n[CÓDIGO PYTHON PARA REPLICAR]")
            print("""
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://megaembed.link/",
    "Origin": "https://megaembed.link",
}

# URL do vídeo (obtida via Selenium)
video_url = "%s"

# Fazer request
resp = requests.get(video_url, headers=headers, stream=True)
print(f"Status: {resp.status_code}")
print(f"Content-Type: {resp.headers.get('Content-Type')}")
""" % self.video_url)
        
        print(f"\n[REQUISIÇÕES CAPTURADAS]")
        for req in self.all_requests[:5]:
            print(f"\n  [{req['method']}] {req['url'][:70]}")
            if 'status' in req:
                print(f"      Status: {req['status']}")


def main():
    extractor = MegaEmbedSeleniumExtractor()
    video_url = extractor.extract(TEST_URL)
    
    if video_url:
        print(f"\n{'='*60}")
        print(f"[SUCESSO] URL DO VÍDEO:")
        print(f"  {video_url}")
        print(f"{'='*60}")
        
        extractor.print_http_replication()
        
        # Salvar resultado
        result = {
            "video_url": video_url,
            "cookies": extractor.cookies,
            "headers": extractor.headers,
            "requests": extractor.all_requests
        }
        
        with open("megaembed_extracted.json", "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n[*] Resultado salvo em megaembed_extracted.json")
    else:
        print(f"\n[FALHA] Não foi possível extrair URL do vídeo")
        print("[!] O vídeo pode ter sido deletado ou a página mudou")


if __name__ == "__main__":
    main()
