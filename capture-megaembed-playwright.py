#!/usr/bin/env python3
"""
Playwright MegaEmbed Deep Analyzer
Captura TODOS os domínios CDN automaticamente (sem dicionário)
"""

from playwright.sync_api import sync_playwright
import re
import json
import sys

CHROME_PATH = r"D:\chrome-win64(1)\chrome-win64\chrome.exe"

def analyze_megaembed(megaembed_url):
    """Captura todas as requisições do MegaEmbed automaticamente"""
    
    print(f"\n{'='*60}")
    print(f"🎬 MegaEmbed Deep Analyzer")
    print(f"{'='*60}")
    print(f"📍 URL: {megaembed_url}\n")
    
    # Armazenar todas as requisições
    all_requests = []
    api_responses = []
    video_playlists = []
    video_segments = []
    cdn_domains = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        # Contexto mais humano - simula navegador real
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
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
        )
        
        # Remover detecção de automação
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)
        
        def on_request(request):
            url = request.url
            all_requests.append(url)
            
            # Detectar APIs do MegaEmbed
            if "megaembed.link/api/" in url:
                print(f"📡 API: {url[:80]}...")
            
            # Detectar playlists (.txt)
            if url.endswith(".txt") and "megaembed" not in url:
                print(f"📋 Playlist: {url}")
                video_playlists.append(url)
                # Extrair domínio CDN
                domain = re.search(r"https?://([^/]+)", url)
                if domain:
                    cdn_domains.add(domain.group(1))
            
            # Detectar segmentos (.woff, .woff2) e playlists (.txt)
            if any(ext in url for ext in ['.woff', '.woff2', '.txt']):
                if "megaembed" not in url:
                    if url not in video_segments:
                        video_segments.append(url)
                        print(f"🎬 Request: {url[:80]}...")
                        
                        # Se for .txt, tentar ler o conteudo para ver se eh M3U8
                        if ".txt" in url:
                            print(f"   📄 Playlist TXT encontrada! Verificando conteúdo...")
                            try:
                                # Fazer request separado para ver o conteudo
                                import requests
                                r = requests.get(url, headers={"Referer": "https://megaembed.link/", "User-Agent": request.headers.get('user-agent')})
                                if r.status_code == 200:
                                    content = r.text[:100]
                                    print(f"   📝 Conteúdo (First 100 chars):")
                                    print(f"   {content}")
                                    if "#EXTM3U" in content:
                                        print(f"   ✅ CONFIRMADO: É um arquivo M3U8 disfarçado!")
                                    else:
                                        print(f"   ⚠️ AVISO: Não parece um M3U8 padrão.")
                            except Exception as e:
                                print(f"   ❌ Erro ao ler .txt: {e}")

                        # Imprimir headers importantes
                        headers = request.headers
                        print(f"   ├─ Referer: {headers.get('referer', 'N/A')}")
                        print(f"   ├─ Origin:  {headers.get('origin', 'N/A')}")
                        print(f"   └─ Host:    {headers.get('host', 'N/A')}")
                        
                        # Extrair domínio CDN
                        domain = re.search(r"https?://([^/]+)", url)
                        if domain:
                            cdn_domains.add(domain.group(1))
        
        def on_response(response):
            url = response.url
            
            # Capturar respostas da API
            if "megaembed.link/api/" in url:
                try:
                    body = response.text()
                    api_responses.append({
                        "url": url,
                        "body": body[:500] if len(body) > 500 else body
                    })
                except:
                    pass
        
        page.on("request", on_request)
        page.on("response", on_response)
        
        print("🌐 Navegando para MegaEmbed...")
        page.goto(megaembed_url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Aguardando player carregar (5s)...")
        page.wait_for_timeout(5000)
        
        # Tentar clicar no player para iniciar
        print("▶️ Tentando iniciar playback...")
        try:
            # Clicar em qualquer overlay/botão de play
            page.evaluate("""
                () => {
                    // Clicar em elementos play
                    document.querySelectorAll('[class*="play"], [class*="icon"], button, .media-poster').forEach(el => {
                        try { el.click(); } catch(e) {}
                    });
                    // Forçar play em videos
                    document.querySelectorAll('video').forEach(v => {
                        v.muted = true;
                        v.play().catch(e => {});
                    });
                }
            """)
        except Exception as e:
            print(f"   ⚠️ Click erro: {e}")
        
        print("⏳ Aguardando segmentos carregarem (25s)...")
        page.wait_for_timeout(25000)
        
        browser.close()
    
    # Análise final
    print(f"\n{'='*60}")
    print(f"📊 ANÁLISE COMPLETA")
    print(f"{'='*60}")
    
    print(f"\n📡 Total requisições: {len(all_requests)}")
    print(f"📋 Playlists (.txt): {len(video_playlists)}")
    print(f"🎬 Segmentos (.woff/.woff2): {len(video_segments)}")
    
    print(f"\n🌐 DOMÍNIOS CDN DETECTADOS (dinâmicos):")
    for domain in sorted(cdn_domains):
        print(f"   → {domain}")
    
    if video_playlists:
        print(f"\n📋 PLAYLISTS CAPTURADAS:")
        for pl in video_playlists:
            print(f"   → {pl}")
    
    if api_responses:
        print(f"\n📡 RESPOSTAS API:")
        for api in api_responses[:3]:
            print(f"   → {api['url'][:60]}...")
            # Tentar encontrar URLs no corpo da resposta
            urls_in_body = re.findall(r"https?://[^\s\"']+", api['body'])
            for u in urls_in_body[:3]:
                if "megaembed" not in u:
                    print(f"      📍 {u[:60]}...")
    
    # Salvar resultado
    result = {
        "megaembed_url": megaembed_url,
        "cdn_domains": list(cdn_domains),
        "playlists": video_playlists,
        "segments_count": len(video_segments),
        "api_responses": api_responses
    }
    
    with open("megaembed_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Salvo em: megaembed_analysis.json")
    
    return result

def main():
    # URL padrão do MegaEmbed
    url = "https://megaembed.link/#3wnuij"
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    analyze_megaembed(url)

if __name__ == "__main__":
    main()
