#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            PLAYEREMBEDAPI - NETWORK INTERCEPTION & BYPASS SUITE              ║
║                  Advanced Network Analysis & Header Manipulation             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Técnicas:
1. Interceptação de rede com Playwright/Selenium
2. Manipulação avançada de headers
3. Bypass de proteções anti-bot
4. Simulação de comportamento humano
5. WebSocket analysis
6. TLS fingerprint randomization
"""

import asyncio
import json
import random
import re
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable, Any
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Tentar importar bibliotecas opcionais
try:
    from playwright.async_api import async_playwright, Page, Request, Response
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import requests


@dataclass
class NetworkCall:
    """Representa uma chamada de rede capturada"""
    url: str
    method: str
    headers: Dict[str, str]
    post_data: Optional[str] = None
    response_status: Optional[int] = None
    response_headers: Dict[str, str] = field(default_factory=dict)
    response_body: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    resource_type: str = ""
    
    def is_video(self) -> bool:
        """Verifica se é uma requisição de vídeo"""
        video_patterns = [
            r'\.m3u8',
            r'\.mp4',
            r'\.ts\?',
            r'/hls/',
            r'/video/',
            r'sssrr\.org',
            r'googleapis\.com/mediastorage',
            r'cloudatacdn',
            r'iamcdn',
        ]
        return any(re.search(p, self.url, re.I) for p in video_patterns)
    
    def is_api(self) -> bool:
        """Verifica se é uma chamada de API"""
        api_patterns = [
            r'/api/',
            r'/sora/',
            r'/future',
            r'\.json',
        ]
        return any(re.search(p, self.url, re.I) for p in api_patterns)


@dataclass  
class InterceptedVideo:
    """Vídeo interceptado da rede"""
    url: str
    quality: str
    intercepted_from: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    timestamp: float


class StealthHeaders:
    """
    Gerador de headers stealth para bypass de detecção
    """
    
    # User agents realistas rotativos
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    ]
    
    # Accept-Language realistas
    ACCEPT_LANGUAGES = [
        'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'en-US,en;q=0.9',
        'pt-BR,pt;q=0.9',
        'en-GB,en;q=0.9,pt-BR;q=0.8',
    ]
    
    @classmethod
    def get_headers(cls, url: str = None, extra: Dict = None) -> Dict[str, str]:
        """Gera headers stealth completos"""
        
        headers = {
            'User-Agent': random.choice(cls.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': random.choice(cls.ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'max-age=0',
        }
        
        if url:
            parsed = urlparse(url)
            headers['Host'] = parsed.netloc
            headers['Origin'] = f"{parsed.scheme}://{parsed.netloc}"
            headers['Referer'] = url
        
        if extra:
            headers.update(extra)
        
        return headers


class PlaywrightInterceptor:
    """
    Interceptador de rede usando Playwright
    Mais moderno e stealth que Selenium
    """
    
    def __init__(self):
        self.network_calls: List[NetworkCall] = []
        self.intercepted_videos: List[InterceptedVideo] = []
        self.browser = None
        self.context = None
        self.page = None
    
    async def launch(self, headless: bool = True, proxy: str = None):
        """Inicia o browser com configurações stealth"""
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright não instalado. Execute: pip install playwright && playwright install")
        
        self.playwright = await async_playwright().start()
        
        # Configurações do browser
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-accelerated-2d-canvas',
            '--disable-accelerated-jpeg-decoding',
            '--disable-accelerated-mjpeg-decode',
            '--disable-accelerated-video-decode',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-update',
            '--disable-default-apps',
            '--disable-features=TranslateUI',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--mute-audio',
            '--no-first-run',
            '--safebrowsing-disable-auto-update',
        ]
        
        # Contexto com viewport realista
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': StealthHeaders.USER_AGENTS[0],
            'locale': 'pt-BR',
            'timezone_id': 'America/Sao_Paulo',
            'permissions': [],
            'color_scheme': 'dark',
            'reduced_motion': 'no-preference',
        }
        
        if proxy:
            context_options['proxy'] = {'server': proxy}
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=browser_args
        )
        
        self.context = await self.browser.new_context(**context_options)
        
        # Injetar scripts de stealth
        await self.context.add_init_script("""
            // Stealth script - hide automation
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                        description: "",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "native-client", suffixes: "", description: "", enabledPlugin: Plugin},
                        description: "",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ||
                parameters.name === 'clipboard-read' ||
                parameters.name === 'clipboard-write'
                    ? Promise.resolve({state: 'prompt'})
                    : originalQuery(parameters)
            );
            
            // WebGL fingerprint randomization
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter(parameter);
            };
        """)
        
        self.page = await self.context.new_page()
        
        # Configurar interceptação de rede
        await self._setup_network_interception()
    
    async def _setup_network_interception(self):
        """Configura interceptação de todas as requisições"""
        
        async def handle_route(route, request):
            """Manipula cada requisição"""
            
            network_call = NetworkCall(
                url=request.url,
                method=request.method,
                headers=dict(request.headers),
                resource_type=request.resource_type
            )
            
            # Verificar se é vídeo
            if network_call.is_video():
                print(f"[🎬 VÍDEO] {request.url[:100]}...")
                self.intercepted_videos.append(InterceptedVideo(
                    url=request.url,
                    quality='Unknown',
                    intercepted_from='network',
                    headers=dict(request.headers),
                    cookies={},
                    timestamp=time.time()
                ))
            
            self.network_calls.append(network_call)
            
            # Continuar a requisição
            await route.continue_()
        
        # Interceptar todos os tipos
        await self.page.route("**/*", handle_route)
        
        # Também monitorar responses
        self.page.on("response", self._handle_response)
    
    async def _handle_response(self, response: Response):
        """Manipula responses"""
        request = response.request
        
        # Atualizar call existente ou criar novo
        for call in self.network_calls:
            if call.url == request.url and call.timestamp > time.time() - 1:
                call.response_status = response.status
                call.response_headers = dict(response.headers)
                break
        
        # Se for vídeo, tentar obter body
        if any(re.search(p, request.url, re.I) for p in [r'\.m3u8', r'\.mp4', r'sssrr\.org']):
            try:
                body = await response.body()
                if body and len(body) < 1000000:  # Apenas se não for muito grande
                    try:
                        text = body.decode('utf-8')
                        # Verificar se é playlist m3u8
                        if '#EXTM3U' in text:
                            print(f"[📋 M3U8 Capturado] {request.url}")
                    except:
                        pass
            except:
                pass
    
    async def extract_video(self, url: str, wait_time: int = 10) -> List[InterceptedVideo]:
        """
        Extrai vídeo de uma URL
        """
        print(f"[*] Navegando para: {url}")
        
        # Navegar para a página
        await self.page.goto(url, wait_until='networkidle', timeout=60000)
        
        # Aguardar carregamento
        print(f"[*] Aguardando {wait_time}s para carregamento...")
        await asyncio.sleep(2)
        
        # Tentar interagir com o player (clicar em play)
        try:
            # Procurar por elementos de play
            play_selectors = [
                '.vjs-big-play-button',
                '.play-button',
                '#play-button',
                '[class*="play"]',
                'button[data-show-player]',
                '.jw-icon-playback',
                '#overlay',
                '.plyr__control--overlaid',
            ]
            
            for selector in play_selectors:
                try:
                    play_btn = await self.page.query_selector(selector)
                    if play_btn:
                        print(f"[*] Clicando em: {selector}")
                        await play_btn.click()
                        await asyncio.sleep(2)
                        break
                except:
                    continue
        except Exception as e:
            print(f"[!] Erro ao clicar play: {e}")
        
        # Executar script JavaScript para extrair do player
        print("[*] Executando scripts de extração...")
        
        video_urls = await self.page.evaluate("""
            () => {
                const results = [];
                
                // 1. JWPlayer
                if (window.jwplayer) {
                    try {
                        const jw = jwplayer();
                        if (jw) {
                            const config = jw.getConfig();
                            const playlist = jw.getPlaylist();
                            
                            if (config && config.sources) {
                                config.sources.forEach(s => {
                                    if (s.file) results.push({source: 'jwplayer-config', url: s.file, quality: s.label || 'unknown'});
                                });
                            }
                            
                            if (playlist && playlist[0]) {
                                const item = playlist[0];
                                if (item.file) results.push({source: 'jwplayer-playlist', url: item.file, quality: item.label || 'unknown'});
                                if (item.sources) {
                                    item.sources.forEach(s => {
                                        if (s.file) results.push({source: 'jwplayer-sources', url: s.file, quality: s.label || 'unknown'});
                                    });
                                }
                            }
                        }
                    } catch(e) {}
                }
                
                // 2. VideoJS
                if (window.videojs) {
                    try {
                        const players = document.querySelectorAll('.video-js');
                        players.forEach(p => {
                            if (p.player && p.player.src) {
                                results.push({source: 'videojs', url: p.player.src(), quality: 'unknown'});
                            }
                        });
                    } catch(e) {}
                }
                
                // 3. Video element
                const videos = document.querySelectorAll('video');
                videos.forEach(v => {
                    if (v.src) results.push({source: 'video-element', url: v.src, quality: 'unknown'});
                    if (v.currentSrc) results.push({source: 'video-currentSrc', url: v.currentSrc, quality: 'unknown'});
                });
                
                // 4. Source elements
                const sources = document.querySelectorAll('source[src]');
                sources.forEach(s => {
                    results.push({source: 'source-element', url: s.src, quality: s.getAttribute('label') || 'unknown'});
                });
                
                return results;
            }
        """)
        
        for v in video_urls:
            print(f"[✓] Encontrado via {v['source']}: {v['url'][:80]}...")
            self.intercepted_videos.append(InterceptedVideo(
                url=v['url'],
                quality=v['quality'],
                intercepted_from=v['source'],
                headers={},
                cookies={},
                timestamp=time.time()
            ))
        
        # Aguardar mais tempo para requisições de rede
        remaining_wait = wait_time - 4  # Já esperamos ~4s
        if remaining_wait > 0:
            print(f"[*] Aguardando mais {remaining_wait}s para requisições de rede...")
            await asyncio.sleep(remaining_wait)
        
        # Obter cookies e headers finais
        cookies = await self.context.cookies()
        cookies_dict = {c['name']: c['value'] for c in cookies}
        
        for video in self.intercepted_videos:
            if not video.cookies:
                video.cookies = cookies_dict
        
        return self.intercepted_videos
    
    async def close(self):
        """Fecha o browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def save_report(self, filename: str = 'network_intercept_report.json'):
        """Salva relatório de interceptação"""
        report = {
            'total_network_calls': len(self.network_calls),
            'total_videos': len(self.intercepted_videos),
            'videos': [
                {
                    'url': v.url,
                    'quality': v.quality,
                    'intercepted_from': v.intercepted_from,
                    'headers': v.headers,
                    'cookies': v.cookies,
                    'timestamp': v.timestamp
                }
                for v in self.intercepted_videos
            ],
            'network_calls': [
                {
                    'url': c.url,
                    'method': c.method,
                    'is_video': c.is_video(),
                    'is_api': c.is_api(),
                    'resource_type': c.resource_type,
                    'response_status': c.response_status
                }
                for c in self.network_calls[-50:]  # Últimas 50 chamadas
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[*] Relatório salvo em: {filename}")


class HTTPBypassExtractor:
    """
    Extrator HTTP puro com técnicas de bypass
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(StealthHeaders.get_headers())
    
    def extract_with_retry(self, url: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Extrai com retry e rotação de headers
        """
        for attempt in range(max_retries):
            try:
                # Rotacionar headers
                self.session.headers.update(StealthHeaders.get_headers(url))
                
                # Delay aleatório
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                return {
                    'url': response.url,
                    'status': response.status_code,
                    'headers': dict(response.headers),
                    'cookies': dict(self.session.cookies),
                    'html': response.text
                }
                
            except Exception as e:
                print(f"[!] Tentativa {attempt + 1} falhou: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                
        return None
    
    def extract_video_url_from_html(self, html: str, base_url: str) -> List[Dict]:
        """
        Extrai URLs de vídeo do HTML usando múltiplas técnicas
        """
        videos = []
        
        # Técnica 1: Regex direto
        patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*',
            r'https?://[^\s"\'<>]*googleapis\.com/mediastorage[^\s"\'<>]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                videos.append({
                    'url': match,
                    'method': 'regex',
                    'quality': 'unknown'
                })
        
        # Técnica 2: JSON parsing
        json_patterns = [
            r'var\s+config\s*=\s*(\{[^;]+\})',
            r'var\s+sources\s*=\s*(\[[^\]]+\])',
            r'"sources"\s*:\s*(\[[^\]]+\])',
            r'"file"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    if match.startswith('{'):
                        data = json.loads(match)
                        if 'sources' in data:
                            for src in data['sources']:
                                if 'file' in src:
                                    videos.append({
                                        'url': src['file'],
                                        'method': 'json_sources',
                                        'quality': src.get('label', 'unknown')
                                    })
                        elif 'file' in data:
                            videos.append({
                                'url': data['file'],
                                'method': 'json_file',
                                'quality': data.get('label', 'unknown')
                            })
                    elif match.startswith('['):
                        data = json.loads(match)
                        for item in data:
                            if isinstance(item, dict) and 'file' in item:
                                videos.append({
                                    'url': item['file'],
                                    'method': 'json_array',
                                    'quality': item.get('label', 'unknown')
                                })
                    else:
                        videos.append({
                            'url': match,
                            'method': 'json_string',
                            'quality': 'unknown'
                        })
                except json.JSONDecodeError:
                    pass
        
        # Técnica 3: Base64 decoding
        b64_pattern = r'[A-Za-z0-9+/]{100,}={0,2}'
        b64_matches = re.findall(b64_pattern, html)
        
        for b64 in b64_matches[:5]:  # Limitar tentativas
            try:
                decoded = base64.b64decode(b64)
                decoded_str = decoded.decode('utf-8', errors='ignore')
                
                # Procurar URLs no decoded
                url_pattern = r'https?://[^\s"\'<>]+'
                urls = re.findall(url_pattern, decoded_str)
                for u in urls:
                    if any(ext in u for ext in ['.m3u8', '.mp4', '.ts']):
                        videos.append({
                            'url': u,
                            'method': 'base64_decoded',
                            'quality': 'unknown'
                        })
            except:
                pass
        
        # Remover duplicatas
        seen = set()
        unique = []
        for v in videos:
            if v['url'] not in seen and v['url'].startswith('http'):
                seen.add(v['url'])
                unique.append(v)
        
        return unique


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Função principal"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║            PLAYEREMBEDAPI - NETWORK INTERCEPTION & BYPASS SUITE              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python hacker_network_interceptor.py <url> [método]")
        print("  métodos: playwright, http, all")
        print("\nExemplo:")
        print("  python hacker_network_interceptor.py https://playerembedapi.link/?v=xxx playwright")
        return
    
    url = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else 'all'
    
    all_videos = []
    
    # Método 1: Playwright
    if method in ['playwright', 'all'] and PLAYWRIGHT_AVAILABLE:
        print("\n" + "="*60)
        print("MÉTODO 1: Playwright Interception")
        print("="*60)
        
        interceptor = PlaywrightInterceptor()
        try:
            await interceptor.launch(headless=True)
            videos = await interceptor.extract_video(url, wait_time=15)
            all_videos.extend(videos)
            interceptor.save_report()
        except Exception as e:
            print(f"[!] Erro no Playwright: {e}")
        finally:
            await interceptor.close()
    
    # Método 2: HTTP Puro
    if method in ['http', 'all']:
        print("\n" + "="*60)
        print("MÉTODO 2: HTTP Pure Bypass")
        print("="*60)
        
        extractor = HTTPBypassExtractor()
        result = extractor.extract_with_retry(url)
        
        if result:
            print(f"[*] HTML obtido ({len(result['html'])} bytes)")
            videos = extractor.extract_video_url_from_html(result['html'], result['url'])
            
            for v in videos:
                all_videos.append(InterceptedVideo(
                    url=v['url'],
                    quality=v['quality'],
                    intercepted_from=f"http_{v['method']}",
                    headers=result['headers'],
                    cookies=result['cookies'],
                    timestamp=time.time()
                ))
    
    # Resultados finais
    print("\n" + "="*60)
    print("RESULTADOS FINAIS")
    print("="*60)
    
    if all_videos:
        seen = set()
        unique_videos = []
        for v in all_videos:
            if v.url not in seen:
                seen.add(v.url)
                unique_videos.append(v)
        
        print(f"\n[✓] {len(unique_videos)} vídeo(s) encontrado(s):\n")
        
        for i, v in enumerate(unique_videos, 1):
            print(f"  [{i}] {v.quality}")
            print(f"      Fonte: {v.intercepted_from}")
            print(f"      URL: {v.url}")
            print()
        
        # Salvar resultado
        result = {
            'source_url': url,
            'extraction_time': time.time(),
            'videos': [
                {
                    'url': v.url,
                    'quality': v.quality,
                    'source': v.intercepted_from,
                    'headers': v.headers,
                    'cookies': v.cookies
                }
                for v in unique_videos
            ]
        }
        
        with open('extracted_videos.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("[*] Resultados salvos em: extracted_videos.json")
    else:
        print("[!] Nenhum vídeo encontrado")


if __name__ == '__main__':
    asyncio.run(main())
