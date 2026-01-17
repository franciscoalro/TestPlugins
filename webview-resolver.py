#!/usr/bin/env python3
"""
Python WebViewResolver - Simula o WebViewResolver do Cloudstream
Intercepta requisições HTTP que correspondem a um padrão regex
"""

from playwright.sync_api import sync_playwright
import re
import sys

CHROME_PATH = r"D:\chrome-win64(1)\chrome-win64\chrome.exe"

class WebViewResolver:
    """Simula o WebViewResolver do Cloudstream"""
    
    def __init__(self, intercept_url_pattern, timeout=30000):
        """
        Args:
            intercept_url_pattern: Regex para interceptar URLs
            timeout: Tempo máximo de espera em ms
        """
        self.pattern = re.compile(intercept_url_pattern)
        self.timeout = timeout
        self.captured_url = None
        
    def resolve(self, url, referer=None):
        """
        Navega para URL e retorna a primeira URL interceptada que match o padrão
        Similar ao app.get(url, interceptor = resolver) do Cloudstream
        """
        print(f"\n{'='*60}")
        print(f"🔧 WebViewResolver")
        print(f"{'='*60}")
        print(f"📍 URL: {url}")
        print(f"🎯 Pattern: {self.pattern.pattern}")
        print(f"⏱️ Timeout: {self.timeout}ms")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                executable_path=CHROME_PATH,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate"
                }
            )
            
            page = context.new_page()
            
            # Anti-detection
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                window.chrome = { runtime: {} };
            """)
            
            # Interceptar requisições
            def on_request(request):
                req_url = request.url
                if self.pattern.search(req_url):
                    if not self.captured_url:
                        self.captured_url = req_url
                        print(f"\n✅ INTERCEPTED: {req_url[:80]}...")
                        # Log Headers
                        headers = request.headers
                        print(f"   ├─ Referer: {headers.get('referer', 'N/A')}")
                        print(f"   ├─ Origin:  {headers.get('origin', 'N/A')}")
                        print(f"   └─ User-Agent: {headers.get('user-agent', 'N/A')[:50]}...")
            
            page.on("request", on_request)
            
            print(f"\n🌐 Navegando...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except:
                pass
            
            # Aguardar e tentar iniciar playback
            page.wait_for_timeout(3000)
            
            print(f"▶️ Iniciando playback...")
            try:
                page.evaluate("""
                    () => {
                        document.querySelectorAll('[class*="play"], button, .media-poster, [class*="icon"]').forEach(el => {
                            try { el.click(); } catch(e) {}
                        });
                        document.querySelectorAll('video').forEach(v => {
                            v.muted = true;
                            v.play().catch(e => {});
                        });
                    }
                """)
            except:
                pass
            
            # Aguardar até interceptar ou timeout
            waited = 0
            interval = 1000
            print(f"⏳ Aguardando interceptação...")
            
            while not self.captured_url and waited < self.timeout:
                page.wait_for_timeout(interval)
                waited += interval
                if waited % 5000 == 0:
                    print(f"   ... {waited//1000}s")
            
            browser.close()
        
        if self.captured_url:
            print(f"\n{'='*60}")
            print(f"✅ RESULTADO:")
            print(f"   {self.captured_url}")
            print(f"{'='*60}")
        else:
            print(f"\n❌ Nenhuma URL interceptada após {self.timeout}ms")
        
        return self.captured_url


def test_megaembed():
    """Testa MegaEmbed com WebViewResolver"""
    
    # Padrão V111 (Path-based)
    # /v4/{shard}/{id}/cf-master.txt ou index.txt
    pattern = r"/v4/[a-z0-9]+/[a-z0-9]+/(?:cf-master|index-).*?\.txt"
    
    resolver = WebViewResolver(
        intercept_url_pattern=pattern,
        timeout=60000  # 60 segundos
    )
    
    url = "https://megaembed.link/#3wnuij"
    if len(sys.argv) > 1:
        if "#" in sys.argv[1]:
            url = sys.argv[1]
        else:
            url = f"https://megaembed.link/#{sys.argv[1]}"
    
    result = resolver.resolve(url)
    
    if result:
        print(f"\n🎬 URL do vídeo capturada!")
        print(f"   Use esta URL no player ou adicione o domínio ao extractor.")
    else:
        print(f"\n⚠️ Não foi possível capturar. O MegaEmbed pode estar bloqueando automação.")


def test_playerembed():
    """Testa PlayerEmbedAPI com WebViewResolver"""
    
    # Padrão para PlayerEmbedAPI
    pattern = r"storage\.googleapis\.com|mediastorage|\.mp4|\.m3u8"
    
    resolver = WebViewResolver(
        intercept_url_pattern=pattern,
        timeout=25000
    )
    
    url = "https://playerembedapi.link/?v=kBJLtxCD3"
    if len(sys.argv) > 2:
        url = sys.argv[2]
    
    result = resolver.resolve(url)
    return result


if __name__ == "__main__":
    print("🔧 Python WebViewResolver - Simulador do Cloudstream")
    print()
    
    if len(sys.argv) > 1 and "playerembed" in sys.argv[1].lower():
        test_playerembed()
    else:
        test_megaembed()
