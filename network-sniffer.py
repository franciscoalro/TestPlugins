#!/usr/bin/env python3
"""
Network Sniffer - Captura TODAS as requisições do MegaEmbed
Monitora em tempo real e salva detalhes completos
"""

import json
import time
import subprocess
import sys
from datetime import datetime

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

# Configuração
EPISODE_URL = "https://www.maxseries.one/episodio/terra-de-pecados-1x1/"

class NetworkSniffer:
    def __init__(self):
        self.all_requests = []
        self.video_urls = []
        self.api_responses = []
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}")
    
    def capture_request(self, req):
        """Captura detalhes de uma requisição"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "method": req.method,
            "url": req.url,
            "headers": dict(req.headers) if req.headers else {}
        }
        
        # Request body (POST data)
        if req.body:
            try:
                data["request_body"] = req.body.decode('utf-8', errors='ignore')[:1000]
            except:
                pass
        
        # Response
        if req.response:
            data["status"] = req.response.status_code
            if req.response.headers:
                data["response_headers"] = dict(req.response.headers)
            
            # Response body
            if req.response.body:
                try:
                    body = req.response.body.decode('utf-8', errors='ignore')
                    data["response_body"] = body[:5000]
                    data["response_size"] = len(req.response.body)
                except:
                    data["response_size"] = len(req.response.body) if req.response.body else 0
        
        return data
    
    def is_video_url(self, url):
        """Verifica se é URL de vídeo"""
        url_lower = url.lower()
        video_patterns = ['.m3u8', '.mp4', '.ts', 'master.txt', '/hls/', '/video/', 'playlist']
        exclude_patterns = ['.js', '.css', 'yandex', 'google', 'facebook', 'analytics', 'ads']
        
        if any(p in url_lower for p in exclude_patterns):
            return False
        return any(p in url_lower for p in video_patterns)
    
    def is_api_call(self, url):
        """Verifica se é chamada de API"""
        return any(p in url for p in ['/api/', '/info', '/embed/', '/episodio/'])
    
    def run(self):
        self.log("="*70)
        self.log("NETWORK SNIFFER - MEGAEMBED")
        self.log("="*70)
        
        # Configurar selenium-wire para capturar tudo
        seleniumwire_options = {
            'disable_encoding': True,
            'ignore_http_methods': [],  # Capturar TODOS os métodos
        }
        
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        driver = webdriver.Chrome(
            seleniumwire_options=seleniumwire_options,
            options=chrome_options
        )
        
        # Anti-detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            '''
        })
        
        try:
            # FASE 1: Carregar página do episódio
            self.log("\n[FASE 1] Carregando episódio...")
            driver.get(EPISODE_URL)
            time.sleep(4)
            
            self.log(f"  Requisições: {len(driver.requests)}")
            
            # Encontrar iframe do player
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            player_url = None
            
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "player" in src or "embed" in src:
                    player_url = src
                    self.log(f"  Player: {src}")
                    break
            
            # FASE 2: Ir para o player
            if player_url:
                self.log(f"\n[FASE 2] Abrindo player...")
                del driver.requests  # Limpar requisições anteriores
                
                driver.get(player_url)
                time.sleep(3)
                
                # Capturar requisições do player
                self.log(f"\n  Requisições do player ({len(driver.requests)}):")
                for req in driver.requests:
                    if self.is_api_call(req.url) or self.is_video_url(req.url):
                        data = self.capture_request(req)
                        self.all_requests.append(data)
                        self.log(f"    [{req.method}] {req.url[:70]}")
                        
                        if self.is_api_call(req.url):
                            self.api_responses.append(data)
                        if self.is_video_url(req.url):
                            self.video_urls.append(req.url)
            
            # FASE 3: Verificar iframe interno (MegaEmbed)
            self.log(f"\n[FASE 3] Procurando MegaEmbed iframe...")
            
            inner_iframes = driver.find_elements(By.TAG_NAME, "iframe")
            megaembed_url = None
            
            for iframe in inner_iframes:
                src = iframe.get_attribute("src") or ""
                self.log(f"    iframe: {src[:60]}")
                if "megaembed" in src:
                    megaembed_url = src
                    break
            
            if megaembed_url:
                self.log(f"\n  Entrando no MegaEmbed: {megaembed_url}")
                del driver.requests
                
                driver.get(megaembed_url)
                time.sleep(3)
            
            # FASE 4: Clicar para iniciar player
            self.log(f"\n[FASE 4] Iniciando player...")
            del driver.requests
            
            # Clicar no centro
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                ActionChains(driver).move_to_element(body).click().perform()
                self.log("  Clique no body")
            except:
                pass
            
            time.sleep(2)
            
            # Tentar clicar em botões de play
            for selector in ["media-play-button", ".vds-play-button", "button", "video"]:
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    ActionChains(driver).move_to_element(elem).click().perform()
                    self.log(f"  Clique em: {selector}")
                    time.sleep(1)
                except:
                    pass
            
            # FASE 5: Monitorar em tempo real
            self.log(f"\n[FASE 5] Monitorando requisições (60s)...")
            self.log("-"*70)
            
            seen_urls = set()
            
            for i in range(60):
                time.sleep(1)
                
                # Verificar novas requisições
                for req in driver.requests:
                    if req.url in seen_urls:
                        continue
                    seen_urls.add(req.url)
                    
                    # Filtrar requisições importantes
                    url = req.url
                    
                    # Ignorar recursos estáticos comuns
                    if any(x in url for x in ['.png', '.jpg', '.gif', '.ico', '.woff', '.ttf']):
                        continue
                    
                    # Capturar APIs e vídeos
                    if self.is_api_call(url) or self.is_video_url(url) or '/api/' in url:
                        data = self.capture_request(req)
                        self.all_requests.append(data)
                        
                        status = data.get('status', '?')
                        size = data.get('response_size', 0)
                        
                        # Destacar URLs de vídeo
                        if self.is_video_url(url):
                            self.video_urls.append(url)
                            self.log(f"\n*** VIDEO *** [{req.method}] {url}")
                            if 'response_headers' in data:
                                ct = data['response_headers'].get('Content-Type', '')
                                self.log(f"    Content-Type: {ct}")
                        else:
                            self.log(f"[{req.method}] {status} {url[:60]}... ({size}b)")
                        
                        # Mostrar body de APIs
                        if '/api/' in url and 'response_body' in data:
                            self.log(f"    Response: {data['response_body'][:200]}")
                
                # Verificar elemento video
                try:
                    video_src = driver.execute_script("""
                        var v = document.querySelector('video');
                        if (v && v.src && v.src.startsWith('http')) return v.src;
                        if (v && v.currentSrc && v.currentSrc.startsWith('http')) return v.currentSrc;
                        return null;
                    """)
                    if video_src and video_src not in self.video_urls:
                        self.video_urls.append(video_src)
                        self.log(f"\n*** VIDEO ELEMENT *** {video_src}")
                except:
                    pass
                
                # Parar se encontrou vídeo válido
                valid_videos = [v for v in self.video_urls if '.m3u8' in v or '.mp4' in v]
                if valid_videos and i > 20:
                    self.log("\n[+] Vídeo encontrado!")
                    break
                
                if i % 15 == 0 and i > 0:
                    self.log(f"  ... {i}s - {len(self.all_requests)} requisições capturadas")
            
            # RESULTADO
            self.log("\n" + "="*70)
            self.log("RESULTADO DO SNIFFER")
            self.log("="*70)
            
            # APIs encontradas
            self.log(f"\n[APIs] {len(self.api_responses)} chamadas")
            for api in self.api_responses:
                self.log(f"\n  {api['method']} {api['url']}")
                if 'response_body' in api:
                    self.log(f"    Body: {api['response_body'][:300]}")
            
            # Vídeos encontrados
            valid_videos = [v for v in self.video_urls if '.m3u8' in v or '.mp4' in v]
            self.log(f"\n[Vídeos] {len(valid_videos)} URLs válidas")
            for v in valid_videos:
                self.log(f"  {v}")
            
            # Salvar resultado completo
            result = {
                "timestamp": datetime.now().isoformat(),
                "episode_url": EPISODE_URL,
                "total_requests": len(self.all_requests),
                "api_responses": self.api_responses,
                "video_urls": list(set(self.video_urls)),
                "all_requests": self.all_requests
            }
            
            with open("sniffer_results.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.log(f"\n[*] Salvo em sniffer_results.json")
            
            # Testar vídeo no VLC
            if valid_videos:
                self.log("\n[*] Abrindo no VLC...")
                try:
                    vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                    subprocess.Popen([vlc, valid_videos[0]])
                except:
                    self.log(f"  Comando: vlc \"{valid_videos[0]}\"")
            
            return result
            
        finally:
            input("\nPressione ENTER para fechar o navegador...")
            driver.quit()


if __name__ == "__main__":
    sniffer = NetworkSniffer()
    sniffer.run()
