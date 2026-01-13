import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright
import re

# Configuração
CONFIG = {
    'headless': True,  # SEM INTERFACE conforme solicitado
    'timeout': 60000,
    'wait_after_load': 5000,
    'wait_for_video': 20000,
}

VIDEO_PATTERNS = [
    r'\.m3u8',
    r'\.mp4',
    r'abyss\.to',
    r'playerembedapi\.link',
    r'megaembed\.link',
    r'short\.icu',
    r'storage\.googleapis\.com'
]

captured_data = {
    'video_urls': [],
    'redirects': [],
    'players': [],
    'errors': []
}

async def verify_url(url):
    print(f"🚀 Iniciando verificação HEADLESS para: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=CONFIG['headless'],
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()

        # Interceptação de Rede
        async def handle_request(request):
            req_url = request.url
            if any(re.search(p, req_url) for p in VIDEO_PATTERNS):
                if req_url not in [x['url'] for x in captured_data['video_urls']]:
                    print(f"✅ CAPTURADO: {req_url[:80]}...")
                    captured_data['video_urls'].append({
                        'url': req_url,
                        'method': request.method,
                        'type': request.resource_type
                    })

        page.on("request", handle_request)

        try:
            # 1. Carregar página inicial
            print("⏳ Carregando página...")
            await page.goto(url, wait_until="domcontentloaded", timeout=CONFIG['timeout'])
            await asyncio.sleep(CONFIG['wait_after_load'] / 1000)

            # 2. Tentar encontrar iframes de player
            iframes = await page.query_selector_all("iframe")
            print(f"📦 Iframes encontrados: {len(iframes)}")
            
            for i, iframe in enumerate(iframes):
                src = await iframe.get_attribute("src")
                if src:
                    print(f"  - Iframe {i}: {src[:80]}")
                    captured_data['players'].append(src)

            # 3. Tentar clicar em botões de Play (Simulação de interação)
            print("🎬 Tentando interagir com a página...")
            # Clicar no centro da tela (geralmente onde está o player)
            await page.mouse.click(640, 360)
            await asyncio.sleep(2)

            # Procurar botões de play comuns
            play_selectors = [".vjs-big-play-button", ".play-button", "#play-button", "button.play"]
            for sel in play_selectors:
                try:
                    btn = await page.query_selector(sel)
                    if btn:
                        await btn.click()
                        print(f"   ✓ Clicou em {sel}")
                        await asyncio.sleep(2)
                except:
                    pass

            # 4. Aguardar tráfego de vídeo
            print(f"⏳ Aguardando tráfego de vídeo ({CONFIG['wait_for_video']/1000}s)...")
            await asyncio.sleep(CONFIG['wait_for_video'] / 1000)

        except Exception as e:
            print(f"❌ Erro durante a navegação: {str(e)}")
            captured_data['errors'].append(str(e))
        
        finally:
            await browser.close()
            
    # Resultado Final
    print("\n" + "="*50)
    print("📊 RELATÓRIO DE VERIFICAÇÃO")
    print("="*50)
    print(f"Total de URLs de interesse: {len(captured_data['video_urls'])}")
    for item in captured_data['video_urls']:
        print(f"- [{item['type'].upper()}] {item['url']}")
    
    # Salvar resultado
    with open("resultado_playwright_headless.json", "w", encoding="utf-8") as f:
        json.dump(captured_data, f, indent=4)
    print(f"\n💾 Detalhes salvos em: resultado_playwright_headless.json")

if __name__ == "__main__":
    test_url = "https://www.maxseries.one/series/terra-de-pecados/"
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    # Configurar encoding para UTF-8 no Windows para evitar UnicodeEncodeError com emojis
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    asyncio.run(verify_url(test_url))
