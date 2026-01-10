#!/usr/bin/env python3
"""
Captura lógica completa do MegaEmbed e replica em HTTP
Série de teste: Terra de Pecados
"""

import json
import time
import re
import requests
import subprocess
import sys

try:
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium-wire"], check=True)
    from seleniumwire import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

SERIES_URL = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"

class FullExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.captured_flow = []
        self.video_url = None
    
    def step1_get_episode_url(self):
        """Passo 1: Buscar URL de um episódio via HTTP"""
        print("\n[PASSO 1] Buscando episódio via HTTP...")
        
        resp = self.session.get(SERIES_URL)
        
        # Encontrar link de episódio
        pattern = r'href="(https://www\.maxseries\.one/episodio/[^"]+)"'
        matches = re.findall(pattern, resp.text)
        
        if matches:
            ep_url = matches[0]
            print(f"[+] Episódio: {ep_url}")
            self.captured_flow.append({
                "step": 1,
                "action": "GET series page",
                "url": SERIES_URL,
                "result": ep_url
            })
            return ep_url
        
        print("[!] Nenhum episódio encontrado")
        return None
    
    def step2_get_player_url(self, ep_url):
        """Passo 2: Buscar URL do player via HTTP"""
        print("\n[PASSO 2] Buscando player via HTTP...")
        
        resp = self.session.get(ep_url)
        
        # Procurar PlayThree ou MegaEmbed
        patterns = [
            r'href="(https://playerthree\.online/embed/[^"]+)"',
            r'src="(https://playerthree\.online/embed/[^"]+)"',
            r'(https://megaembed\.[^"\']+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resp.text)
            if matches:
                player_url = matches[0]
                print(f"[+] Player: {player_url}")
                self.captured_flow.append({
                    "step": 2,
                    "action": "GET episode page",
                    "url": ep_url,
                    "result": player_url
                })
                return player_url
        
        print("[!] Player não encontrado")
        return None

    def step3_selenium_capture(self, player_url):
        """Passo 3: Usar Selenium para capturar a lógica de decrypt"""
        print("\n[PASSO 3] Capturando com Selenium...")
        
        seleniumwire_options = {'disable_encoding': True}
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(
            seleniumwire_options=seleniumwire_options,
            options=chrome_options
        )
        
        captured_requests = []
        
        try:
            driver.get(player_url)
            print(f"[+] Página carregada")
            time.sleep(5)
            
            # Clicar em botões
            for selector in ["#play", ".play-button", "button", "[data-source]"]:
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in btns[:3]:
                        try:
                            btn.click()
                            print(f"[+] Clicou: {selector}")
                            time.sleep(2)
                        except:
                            pass
                except:
                    pass
            
            print("[*] Aguardando 20s para capturar requisições...")
            time.sleep(20)
            
            # Capturar TODAS as requisições
            for req in driver.requests:
                req_info = {
                    "method": req.method,
                    "url": req.url,
                    "headers": dict(req.headers) if req.headers else {}
                }
                
                if req.response:
                    req_info["status"] = req.response.status_code
                    req_info["resp_headers"] = dict(req.response.headers) if req.response.headers else {}
                    
                    if req.response.body:
                        try:
                            body = req.response.body.decode('utf-8', errors='ignore')
                            req_info["body"] = body[:2000]
                        except:
                            req_info["body"] = f"[binary {len(req.response.body)} bytes]"
                
                captured_requests.append(req_info)
                
                # Identificar URL de vídeo
                url_lower = req.url.lower()
                if any(x in url_lower for x in ['.m3u8', '.mp4', 'master.txt', '/hls/']):
                    if '.js' not in url_lower:
                        self.video_url = req.url
                        print(f"\n[VIDEO] {req.url}")
            
            # Capturar do elemento video
            try:
                video_src = driver.execute_script("""
                    var v = document.querySelector('video');
                    return v ? (v.currentSrc || v.src) : null;
                """)
                if video_src and video_src.startswith('http'):
                    if not self.video_url:
                        self.video_url = video_src
                    print(f"[VIDEO ELEMENT] {video_src}")
            except:
                pass
            
            # Cookies
            cookies = {c['name']: c['value'] for c in driver.get_cookies()}
            
            self.captured_flow.append({
                "step": 3,
                "action": "Selenium capture",
                "url": player_url,
                "cookies": cookies,
                "requests_count": len(captured_requests),
                "video_url": self.video_url
            })
            
            return captured_requests, cookies
            
        finally:
            driver.quit()
    
    def step4_analyze_and_replicate(self, requests_data):
        """Passo 4: Analisar requisições e criar código HTTP"""
        print("\n[PASSO 4] Analisando para replicar em HTTP...")
        
        # Filtrar requisições importantes
        important = []
        for req in requests_data:
            url = req['url']
            if any(x in url for x in ['megaembed', 'playerthree', '/api/', '.m3u8', '.mp4']):
                important.append(req)
                print(f"\n  [{req['method']}] {url[:70]}")
                if 'status' in req:
                    print(f"      Status: {req['status']}")
        
        return important
    
    def generate_http_code(self, important_requests):
        """Gera código Python para replicar via HTTP"""
        print("\n" + "="*60)
        print("CÓDIGO PARA REPLICAR VIA HTTP")
        print("="*60)
        
        code = '''
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
})

'''
        
        for i, req in enumerate(important_requests[:10]):
            code += f'''
# Request {i+1}: {req['url'][:50]}...
resp{i} = session.{req['method'].lower()}(
    "{req['url']}",
    headers={{"Referer": "{req['headers'].get('referer', '')}"}}
)
print(f"[{i+1}] Status: {{resp{i}.status_code}}")
'''
        
        if self.video_url:
            code += f'''
# URL do vídeo final
VIDEO_URL = "{self.video_url}"

# Baixar/Reproduzir
resp = session.get(VIDEO_URL, headers={{"Referer": "https://megaembed.link/"}}, stream=True)
print(f"Video Status: {{resp.status_code}}")
print(f"Content-Type: {{resp.headers.get('Content-Type')}}")
'''
        
        print(code)
        return code
    
    def run(self):
        """Executa todo o fluxo"""
        print("="*60)
        print("CAPTURA E REPLICAÇÃO - TERRA DE PECADOS")
        print("="*60)
        
        # Passo 1: HTTP
        ep_url = self.step1_get_episode_url()
        if not ep_url:
            return
        
        # Passo 2: HTTP
        player_url = self.step2_get_player_url(ep_url)
        if not player_url:
            return
        
        # Passo 3: Selenium
        requests_data, cookies = self.step3_selenium_capture(player_url)
        
        # Passo 4: Análise
        important = self.step4_analyze_and_replicate(requests_data)
        
        # Gerar código
        self.generate_http_code(important)
        
        # Salvar resultado
        result = {
            "flow": self.captured_flow,
            "video_url": self.video_url,
            "important_requests": important[:20]
        }
        
        with open("capture_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n[*] Resultado salvo em capture_result.json")
        
        if self.video_url:
            print(f"\n{'='*60}")
            print(f"[SUCESSO] VIDEO URL: {self.video_url}")
            print(f"{'='*60}")


if __name__ == "__main__":
    extractor = FullExtractor()
    extractor.run()
