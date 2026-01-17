#!/usr/bin/env python3
"""
MegaEmbed Complete Extractor - Simula o comportamento do Cloudstream
Combina: Playwright (WebView) + Requests (OkHttp) + JSON parsing
"""

from playwright.sync_api import sync_playwright
import requests
import re
import json
import sys
from urllib.parse import urljoin, urlparse

CHROME_PATH = r"D:\chrome-win64(1)\chrome-win64\chrome.exe"

# Headers similares ao Cloudstream
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://megaembed.link",
    "Referer": "https://megaembed.link/",
}

class MegaEmbedExtractor:
    """Simula o extrator do Cloudstream"""
    
    def __init__(self, video_id):
        self.video_id = video_id
        self.base_url = "https://megaembed.link"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        # Dados capturados
        self.info_data = None
        self.video_data = None
        self.player_data = None
        self.cdn_url = None
        self.playlist_url = None
        
    def extract_with_requests(self):
        """Método 1: Usar APIs diretas (como app.get no Cloudstream)"""
        print(f"\n{'='*60}")
        print(f"🔧 MÉTODO 1: Requests (OkHttp-like)")
        print(f"{'='*60}")
        
        # 1. API Info
        print(f"\n📡 [1/3] Chamando /api/v1/info...")
        try:
            info_url = f"{self.base_url}/api/v1/info?id={self.video_id}"
            resp = self.session.get(info_url)
            self.info_data = resp.text
            print(f"   ✅ Resposta: {len(self.info_data)} chars")
            print(f"   📄 Preview: {self.info_data[:100]}...")
            
            # Tentar parsear como JSON
            try:
                info_json = resp.json()
                print(f"   📋 JSON Keys: {list(info_json.keys()) if isinstance(info_json, dict) else 'array'}")
            except:
                print(f"   ⚠️ Resposta não é JSON (provavelmente criptografada)")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 2. API Video
        print(f"\n📡 [2/3] Chamando /api/v1/video...")
        try:
            video_url = f"{self.base_url}/api/v1/video?id={self.video_id}&w=1920&h=1080&r=playerthree.online"
            resp = self.session.get(video_url)
            self.video_data = resp.text
            print(f"   ✅ Resposta: {len(self.video_data)} chars")
            
            # Tentar parsear e extrair URLs
            try:
                video_json = resp.json()
                print(f"   📋 JSON Keys: {list(video_json.keys()) if isinstance(video_json, dict) else 'array'}")
                
                # Procurar URLs nos dados
                json_str = json.dumps(video_json)
                urls = re.findall(r'https?://[^\s"\']+', json_str)
                for url in urls[:5]:
                    if 'megaembed' not in url:
                        print(f"   🔗 URL: {url[:70]}...")
            except:
                print(f"   ⚠️ Resposta não é JSON")
                # Procurar URLs na resposta raw
                urls = re.findall(r'https?://[^\s"\']+', self.video_data)
                for url in urls[:5]:
                    if 'megaembed' not in url:
                        print(f"   🔗 URL: {url[:70]}...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 3. API Player (se tiver token)
        print(f"\n📡 [3/3] Testando /api/v1/player...")
        # O token é gerado dinamicamente, então não podemos chamar diretamente
        print(f"   ⚠️ Requer token dinâmico (precisa de Playwright)")
        
    def extract_with_playwright(self):
        """Método 2: WebView com interceptação (como WebViewResolver)"""
        print(f"\n{'='*60}")
        print(f"🌐 MÉTODO 2: Playwright (WebView Interception)")
        print(f"{'='*60}")
        
        captured_urls = []
        api_responses = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                executable_path=CHROME_PATH
            )
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"]
            )
            page = context.new_page()
            
            def on_response(response):
                url = response.url
                
                # Capturar respostas da API
                if "megaembed.link/api/" in url:
                    try:
                        body = response.text()
                        api_responses[url] = body
                        print(f"   📡 API: {url.split('?')[0].split('/')[-1]}")
                        
                        # Procurar URLs na resposta
                        urls_in_body = re.findall(r'https?://[^\s"\'\\]+', body)
                        for u in urls_in_body:
                            if 'megaembed' not in u and u not in captured_urls:
                                captured_urls.append(u)
                                print(f"      🔗 {u[:60]}...")
                    except:
                        pass
                
                # Capturar playlists e segmentos
                if any(ext in url for ext in ['.txt', '.woff', '.woff2', '.m3u8', '.mp4']):
                    if 'megaembed' not in url and url not in captured_urls:
                        captured_urls.append(url)
                        content_type = response.headers.get('content-type', '')
                        print(f"   🎬 Media: {url[:60]}... ({content_type[:20]})")
            
            page.on("response", on_response)
            
            print(f"\n🌐 Navegando para MegaEmbed...")
            megaembed_url = f"{self.base_url}/#{self.video_id}"
            page.goto(megaembed_url, wait_until="domcontentloaded", timeout=60000)
            
            print(f"⏳ Aguardando player (5s)...")
            page.wait_for_timeout(5000)
            
            # Forçar play
            print(f"▶️ Iniciando playback...")
            page.evaluate("""
                () => {
                    document.querySelectorAll('[class*="play"], button, .media-poster').forEach(el => {
                        try { el.click(); } catch(e) {}
                    });
                    document.querySelectorAll('video').forEach(v => {
                        v.muted = true;
                        v.play().catch(e => {});
                    });
                }
            """)
            
            print(f"⏳ Capturando tráfego (30s)...")
            page.wait_for_timeout(30000)
            
            browser.close()
        
        # Analisar resultados
        print(f"\n📊 Resultados Playwright:")
        print(f"   APIs capturadas: {len(api_responses)}")
        print(f"   URLs capturadas: {len(captured_urls)}")
        
        # Extrair domínios CDN únicos
        cdn_domains = set()
        playlist_urls = []
        for url in captured_urls:
            domain = urlparse(url).netloc
            if domain and 'megaembed' not in domain:
                cdn_domains.add(domain)
            if '.txt' in url:
                playlist_urls.append(url)
        
        if cdn_domains:
            print(f"\n🌐 DOMÍNIOS CDN DINÂMICOS:")
            for domain in sorted(cdn_domains):
                print(f"   → {domain}")
        
        if playlist_urls:
            print(f"\n📋 PLAYLISTS CAPTURADAS:")
            for pl in playlist_urls:
                print(f"   → {pl}")
                self.playlist_url = pl  # Salvar última playlist
        
        # Salvar respostas da API para análise
        if api_responses:
            with open("megaembed_api_responses.json", "w", encoding="utf-8") as f:
                json.dump(api_responses, f, indent=2, ensure_ascii=False)
            print(f"\n💾 APIs salvas em: megaembed_api_responses.json")
        
        return captured_urls, cdn_domains, api_responses
    
    def analyze_api_response(self, api_responses):
        """Analisar respostas da API (como o Cloudstream faz)"""
        print(f"\n{'='*60}")
        print(f"🔍 ANÁLISE DAS RESPOSTAS API")
        print(f"{'='*60}")
        
        for url, body in api_responses.items():
            api_name = url.split('?')[0].split('/')[-1]
            print(f"\n📡 {api_name}:")
            print(f"   Tamanho: {len(body)} chars")
            
            # Tentar parsear como JSON
            try:
                data = json.loads(body)
                print(f"   Tipo: JSON")
                
                if isinstance(data, dict):
                    for key, value in list(data.items())[:5]:
                        if isinstance(value, str) and len(value) > 100:
                            print(f"   {key}: {value[:50]}...")
                        else:
                            print(f"   {key}: {value}")
            except:
                # Verificar se é hex/criptografado
                if re.match(r'^[0-9a-f]+$', body.strip()):
                    print(f"   Tipo: Hex/Criptografado")
                else:
                    print(f"   Tipo: Texto")
                    # Procurar URLs
                    urls = re.findall(r'https?://[^\s"\']+', body)
                    if urls:
                        print(f"   URLs encontradas:")
                        for u in urls[:3]:
                            print(f"      → {u[:60]}...")

def main():
    video_id = "3wnuij"
    
    if len(sys.argv) > 1:
        # Aceitar tanto ID quanto URL completa
        arg = sys.argv[1]
        if "#" in arg:
            video_id = arg.split("#")[-1]
        elif "id=" in arg:
            video_id = re.search(r'id=([^&]+)', arg).group(1)
        else:
            video_id = arg
    
    print(f"{'='*60}")
    print(f"🎬 MEGAEMBED COMPLETE EXTRACTOR")
    print(f"{'='*60}")
    print(f"Video ID: {video_id}")
    
    extractor = MegaEmbedExtractor(video_id)
    
    # Método 1: Requests diretos (OkHttp-like)
    extractor.extract_with_requests()
    
    # Método 2: Playwright (WebView)
    captured_urls, cdn_domains, api_responses = extractor.extract_with_playwright()
    
    # Analisar APIs
    if api_responses:
        extractor.analyze_api_response(api_responses)
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*60}")
    
    if cdn_domains:
        print(f"\n✅ Domínios CDN para adicionar ao extractor:")
        for domain in sorted(cdn_domains):
            print(f'   "{domain}",')
    
    if extractor.playlist_url:
        print(f"\n✅ Playlist capturada:")
        print(f"   {extractor.playlist_url}")

if __name__ == "__main__":
    main()
