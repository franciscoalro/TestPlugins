#!/usr/bin/env python3
"""
Playwright MaxSeries Complete Analyzer
Analisa série completa: episódios, players e fontes de vídeo
"""

from playwright.sync_api import sync_playwright
import re
import sys
import json

CHROME_PATH = r"D:\chrome-win64(1)\chrome-win64\chrome.exe"

def get_episodes(page, series_url):
    """Extrai lista de episódios da página da série"""
    print(f"\n📺 Analisando série: {series_url}")
    
    page.goto(series_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    
    # Padrão para capturar links de episódios (playerthree.online)
    episode_pattern = r'data-source\s*=\s*["\']([^"\']+playerthree\.online[^"\']+)["\']'
    episodes = list(set(re.findall(episode_pattern, html)))
    
    # Fallback: procurar iframes
    if not episodes:
        iframe_pattern = r'<iframe[^>]+src\s*=\s*["\']([^"\']+playerthree\.online[^"\']+)["\']'
        episodes = list(set(re.findall(iframe_pattern, html)))
    
    # Fallback: links diretos para episódios
    if not episodes:
        links = page.query_selector_all('a[href*="episodio"], a[href*="episode"]')
        episodes = [l.get_attribute('href') for l in links if l.get_attribute('href')]
    
    print(f"📋 Encontrados {len(episodes)} episódios")
    return episodes[:5]  # Limitar a 5 para teste

def get_sources_from_episode(page, episode_url):
    """Extrai fontes de player de um episódio"""
    print(f"\n🎬 Episódio: {episode_url}")
    
    page.goto(episode_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    
    html = page.content()
    
    sources = []
    
    # Padrão 1: data-source
    data_sources = re.findall(r'data-source\s*=\s*["\']([^"\']+)["\']', html)
    for src in data_sources:
        if src.startswith('http'):
            sources.append(src)
    
    # Padrão 2: data-src
    data_srcs = re.findall(r'data-src\s*=\s*["\']([^"\']+)["\']', html)
    for src in data_srcs:
        if src.startswith('http'):
            sources.append(src)
    
    # Padrão 3: botões com onclick
    onclick_pattern = r'onclick\s*=\s*["\'][^"\']*(?:iframe|source|play)[^"\']*\(["\']([^"\']+)["\']'
    onclick_srcs = re.findall(onclick_pattern, html, re.IGNORECASE)
    for src in onclick_srcs:
        if src.startswith('http'):
            sources.append(src)
    
    unique_sources = list(set(sources))
    print(f"   📋 {len(unique_sources)} fontes encontradas:")
    for i, src in enumerate(unique_sources, 1):
        # Detectar tipo de player
        player_type = "Unknown"
        if "playerembedapi" in src.lower():
            player_type = "PlayerEmbedAPI"
        elif "megaembed" in src.lower():
            player_type = "MegaEmbed"
        elif "myvidplay" in src.lower() or "dood" in src.lower():
            player_type = "DoodStream/MyVidPlay"
        elif "streamtape" in src.lower():
            player_type = "Streamtape"
        elif "filemoon" in src.lower():
            player_type = "Filemoon"
        elif "mixdrop" in src.lower():
            player_type = "Mixdrop"
        
        print(f"   [{i}] {player_type}: {src[:70]}...")
    
    return unique_sources

def capture_video_from_source(page, source_url):
    """Tenta capturar URL de vídeo de uma fonte"""
    print(f"\n   🔍 Analisando fonte: {source_url[:50]}...")
    
    video_urls = []
    
    def on_response(response):
        url = response.url
        content_type = response.headers.get('content-type', '')
        
        if any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.ts']):
            if 'google' not in url or 'googleapis' in url:
                video_urls.append(url)
        
        if 'video' in content_type or 'mpegurl' in content_type:
            video_urls.append(url)
        
        cdn_patterns = ['googleapis', 'cloudatacdn', 'valenium', 'iamcdn']
        if any(cdn in url.lower() for cdn in cdn_patterns):
            if '.js' not in url and '.css' not in url:
                video_urls.append(url)
    
    page.on("response", on_response)
    
    try:
        page.goto(source_url, wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(10000)
    except Exception as e:
        print(f"   ⚠️ Timeout/erro: {str(e)[:50]}")
    
    page.remove_listener("response", on_response)
    
    unique_videos = list(set(video_urls))
    if unique_videos:
        print(f"   ✅ {len(unique_videos)} vídeo(s) capturado(s):")
        for v in unique_videos[:3]:
            print(f"      → {v[:80]}...")
    else:
        print(f"   ❌ Nenhum vídeo capturado")
    
    return unique_videos

def main():
    series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
    
    if len(sys.argv) > 1:
        series_url = sys.argv[1]
    
    print("="*60)
    print("🎬 MAXSERIES COMPLETE ANALYZER")
    print("="*60)
    
    results = {
        "series": series_url,
        "episodes": []
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=CHROME_PATH
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        # 1. Pegar episódios
        episodes = get_episodes(page, series_url)
        
        if not episodes:
            # Tentar pegar da própria página
            print("⚠️ Nenhum episódio encontrado, tentando fontes da página...")
            sources = get_sources_from_episode(page, series_url)
            
            for source in sources[:3]:
                videos = capture_video_from_source(page, source)
                results["episodes"].append({
                    "url": series_url,
                    "sources": [{"url": source, "videos": videos}]
                })
        else:
            # Analisar cada episódio
            for ep_url in episodes[:3]:  # Limitar a 3 episódios
                sources = get_sources_from_episode(page, ep_url)
                
                ep_data = {
                    "url": ep_url,
                    "sources": []
                }
                
                for source in sources[:2]:  # Limitar a 2 fontes por episódio
                    videos = capture_video_from_source(page, source)
                    ep_data["sources"].append({
                        "url": source,
                        "videos": videos
                    })
                
                results["episodes"].append(ep_data)
        
        browser.close()
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO FINAL")
    print("="*60)
    
    total_videos = 0
    for ep in results["episodes"]:
        for src in ep.get("sources", []):
            total_videos += len(src.get("videos", []))
    
    print(f"Episódios analisados: {len(results['episodes'])}")
    print(f"Total de vídeos capturados: {total_videos}")
    
    # Salvar resultado
    with open("maxseries_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Resultado salvo em: maxseries_analysis.json")

if __name__ == "__main__":
    main()
