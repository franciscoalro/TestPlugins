#!/usr/bin/env python3
"""
Playwright PlayerEmbedAPI Analyzer
Captura URLs de vídeo via interceptação de rede (headless)
"""

from playwright.sync_api import sync_playwright
import re
import sys

def capture_playerembed(url):
    """Captura todas as requisições de rede do PlayerEmbedAPI"""
    
    print(f"\n{'='*60}")
    print(f"🎬 Analisando: {url}")
    print(f"{'='*60}\n")
    
    video_urls = []
    all_requests = []
    
    with sync_playwright() as p:
        # Usar Chrome manual (baixado pelo usuário)
        chrome_path = r"D:\chrome-win64(1)\chrome-win64\chrome.exe"
        browser = p.chromium.launch(
            headless=True,
            executable_path=chrome_path
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        # Interceptar TODAS as requisições
        def on_request(request):
            req_url = request.url
            all_requests.append(req_url)
            
            # Filtrar URLs interessantes
            if any(ext in req_url.lower() for ext in ['.m3u8', '.mp4', '.ts', '.txt']):
                if 'google' not in req_url and 'analytics' not in req_url:
                    print(f"📥 Request: {req_url[:100]}...")
        
        def on_response(response):
            resp_url = response.url
            content_type = response.headers.get('content-type', '')
            
            # Capturar vídeos por URL
            if any(ext in resp_url.lower() for ext in ['.m3u8', '.mp4', '.ts']):
                if 'google' not in resp_url:
                    video_urls.append(resp_url)
                    print(f"🎬 VIDEO: {resp_url[:100]}...")
            
            # Capturar vídeos por content-type
            if 'video' in content_type or 'mpegurl' in content_type:
                video_urls.append(resp_url)
                print(f"🎬 VIDEO (type): {resp_url[:100]}...")
            
            # Capturar CDNs conhecidos
            cdn_patterns = ['googleapis', 'cloudatacdn', 'valenium', 'iamcdn', 'sssrr']
            if any(cdn in resp_url.lower() for cdn in cdn_patterns):
                video_urls.append(resp_url)
                print(f"🎬 CDN: {resp_url[:100]}...")
        
        page.on("request", on_request)
        page.on("response", on_response)
        
        print("🌐 Navegando para a página...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Aguardando JavaScript carregar (15s)...")
        page.wait_for_timeout(15000)
        
        # Tentar extrair do HTML após JS executar
        print("\n📄 Analisando HTML após JavaScript...")
        html = page.content()
        
        # Regex para URLs de vídeo no HTML
        patterns = [
            r'"(https?://[^"]+\.m3u8[^"]*)"',
            r'"(https?://[^"]+\.mp4[^"]*)"',
            r'"(https?://storage\.googleapis\.com[^"]+)"',
            r'"(https?://[^"]*cloudatacdn[^"]+)"',
            r'"(https?://[^"]*valenium\.shop[^"]+)"',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'source\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match.startswith('http') and 'google-analytics' not in match and '.js' not in match:
                    if match not in video_urls:
                        video_urls.append(match)
                        print(f"📝 HTML: {match[:80]}...")
        
        # Tentar executar JS para pegar URLs
        print("\n🔧 Executando JavaScript para extrair URLs...")
        try:
            js_result = page.evaluate("""
                () => {
                    const urls = [];
                    // Tentar pegar do player
                    if (typeof player !== 'undefined' && player.getPlaylistItem) {
                        const item = player.getPlaylistItem();
                        if (item && item.file) urls.push(item.file);
                    }
                    // Tentar pegar do video element
                    const videos = document.querySelectorAll('video');
                    videos.forEach(v => {
                        if (v.src) urls.push(v.src);
                        const sources = v.querySelectorAll('source');
                        sources.forEach(s => { if (s.src) urls.push(s.src); });
                    });
                    return urls;
                }
            """)
            if js_result:
                for u in js_result:
                    if u not in video_urls:
                        video_urls.append(u)
                        print(f"🔧 JS: {u[:80]}...")
        except Exception as e:
            print(f"⚠️ JS eval erro: {e}")
        
        browser.close()
    
    # Resumo
    print(f"\n{'='*60}")
    print(f"📊 RESUMO")
    print(f"{'='*60}")
    print(f"Total requisições: {len(all_requests)}")
    print(f"URLs de vídeo encontradas: {len(set(video_urls))}")
    
    unique_videos = list(set(video_urls))
    for i, v in enumerate(unique_videos, 1):
        print(f"\n[{i}] {v}")
    
    return unique_videos

def main():
    # URL de teste padrão
    test_url = "https://playerembedapi.link/?v=kBJLtxCD3"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    videos = capture_playerembed(test_url)
    
    if videos:
        print(f"\n✅ Encontradas {len(videos)} URLs de vídeo!")
    else:
        print(f"\n❌ Nenhuma URL de vídeo encontrada")

if __name__ == "__main__":
    main()
