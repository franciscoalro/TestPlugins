"""
Playwright Video Link Extractor - Python Version
Captura links de vídeo, tokens e cookies de players embarcados

Uso: python playwright_video_extractor.py <URL>
"""

import asyncio
import json
import sys
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright

# Configurações
CONFIG = {
    'headless': False,  # Mostra o navegador para debug
    'timeout': 60000,  # 60 segundos
    'wait_for_video': 30000,  # Espera até 30s pelo vídeo
}

# Padrões de URLs de vídeo conhecidos
VIDEO_PATTERNS = [
    r'\.m3u8',
    r'\.mp4',
    r'\.mkv',
    r'\.avi',
    r'/playlist\.m3u8',
    r'/master\.m3u8',
    r'abyss\.to',
    r'filemoon',
    r'streamtape',
    r'doodstream',
    r'mixdrop',
]

# Armazena requisições capturadas
captured_requests = []
captured_cookies = {}


def is_video_url(url: str) -> bool:
    """Verifica se a URL é um link de vídeo"""
    import re
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in VIDEO_PATTERNS)


def extract_tokens(url: str) -> dict:
    """Extrai tokens da URL"""
    tokens = {}
    
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Parâmetros comuns de token
        token_keys = ['token', 'auth', 'key', 'signature', 'sig', 'hash', 'id', 'v']
        
        for key in token_keys:
            if key in params:
                tokens[key] = params[key][0] if len(params[key]) == 1 else params[key]
        
        # Extrai todos os parâmetros
        for key, values in params.items():
            if key not in tokens:
                tokens[key] = values[0] if len(values) == 1 else values
                
    except Exception as e:
        print(f'Erro ao extrair tokens: {e}')
    
    return tokens


async def try_click_play(page):
    """Tenta clicar no botão de play"""
    play_selectors = [
        'button[aria-label*="play" i]',
        'button[title*="play" i]',
        'button.play-button',
        'button.vjs-big-play-button',
        'div.play-button',
        '[class*="play"]',
        '[id*="play"]',
        'video',
    ]
    
    for selector in play_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                print(f'🎬 Tentando clicar em: {selector}')
                await element.click(timeout=2000)
                await page.wait_for_timeout(2000)
                return True
        except Exception:
            # Continua tentando outros seletores
            pass
    
    return False


async def capture_video_links(page, context, target_url):
    """Aguarda e captura links de vídeo"""
    print(f'\n🔍 Navegando para: {target_url}\n')
    
    # Intercepta todas as requisições
    async def handle_request(request):
        url = request.url
        
        if is_video_url(url):
            info = {
                'url': url,
                'method': request.method,
                'headers': request.headers,
                'timestamp': datetime.now().isoformat(),
            }
            captured_requests.append(info)
            print(f'\n✅ VÍDEO CAPTURADO!')
            print(f'📹 URL: {url}')
            print(f'🔧 Method: {info["method"]}')
    
    # Intercepta respostas
    async def handle_response(response):
        url = response.url
        
        if is_video_url(url):
            print(f'\n📥 RESPOSTA DE VÍDEO:')
            print(f'📹 URL: {url}')
            print(f'📊 Status: {response.status}')
            headers = await response.all_headers()
            print(f'📦 Content-Type: {headers.get("content-type", "N/A")}')
    
    page.on('request', handle_request)
    page.on('response', handle_response)
    
    # Navega para a página
    try:
        await page.goto(target_url, wait_until='domcontentloaded', timeout=CONFIG['timeout'])
        print('✅ Página carregada')
        
        # Aguarda um pouco para JavaScript carregar
        await page.wait_for_timeout(3000)
        
        # Tenta clicar no play
        print('\n🎬 Procurando botão de play...')
        await try_click_play(page)
        
        # Aguarda links de vídeo
        print(f'\n⏳ Aguardando links de vídeo ({CONFIG["wait_for_video"] / 1000}s)...')
        await page.wait_for_timeout(CONFIG['wait_for_video'])
        
        # Captura cookies finais
        cookies = await context.cookies(target_url)
        for cookie in cookies:
            key = f"{cookie['domain']}:{cookie['name']}"
            captured_cookies[key] = cookie
        
    except Exception as e:
        print(f'❌ Erro ao navegar: {e}')


def display_results():
    """Formata e exibe resultados"""
    print('\n\n' + '=' * 80)
    print('📊 RESULTADOS DA CAPTURA')
    print('=' * 80)
    
    if not captured_requests:
        print('\n❌ Nenhum link de vídeo capturado')
        return
    
    print(f'\n✅ {len(captured_requests)} link(s) de vídeo capturado(s)\n')
    
    for index, req in enumerate(captured_requests):
        print(f'\n{"─" * 80}')
        print(f'📹 VÍDEO #{index + 1}')
        print(f'{"─" * 80}')
        
        print(f'\n🔗 URL:')
        print(req['url'])
        
        tokens = extract_tokens(req['url'])
        if tokens:
            print(f'\n🎫 TOKENS EXTRAÍDOS:')
            for key, value in tokens.items():
                print(f'  {key}: {value}')
        
        print(f'\n📋 HEADERS:')
        for key, value in req['headers'].items():
            print(f'  {key}: {value}')
    
    if captured_cookies:
        print(f'\n\n{"─" * 80}')
        print(f'🍪 COOKIES CAPTURADOS ({len(captured_cookies)})')
        print(f'{"─" * 80}\n')
        
        for cookie in captured_cookies.values():
            print(f'📌 {cookie["name"]}')
            print(f'   Domain: {cookie["domain"]}')
            print(f'   Value: {cookie["value"]}')
            print(f'   Path: {cookie["path"]}')
            print(f'   Secure: {cookie.get("secure", False)}')
            print(f'   HttpOnly: {cookie.get("httpOnly", False)}')
            print()
    
    # Salva em arquivo JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'totalVideos': len(captured_requests),
        'videos': [
            {
                'url': req['url'],
                'tokens': extract_tokens(req['url']),
                'headers': req['headers'],
                'method': req['method'],
            }
            for req in captured_requests
        ],
        'cookies': list(captured_cookies.values()),
    }
    
    filename = f'video-capture-{int(datetime.now().timestamp())}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f'\n💾 Resultados salvos em: {filename}')
    print('=' * 80 + '\n')


async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print('❌ Uso: python playwright_video_extractor.py <URL>')
        print('📝 Exemplo: python playwright_video_extractor.py https://playerthree.online/...')
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    print('🚀 Playwright Video Extractor (Python)')
    print('=' * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=CONFIG['headless'],
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ],
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
        )
        
        page = await context.new_page()
        
        try:
            await capture_video_links(page, context, target_url)
            display_results()
        except Exception as e:
            print(f'❌ Erro fatal: {e}')
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
