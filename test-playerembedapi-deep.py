#!/usr/bin/env python3
"""
Análise profunda do PlayerEmbedAPI para encontrar o link do vídeo
"""

import requests
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def main():
    url = "https://playerembedapi.link/?v=4PHWs34H0"
    referer = "https://playerthree.online"
    
    print(f"🔍 Analisando: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": referer
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    print(f"Status: {response.status_code}")
    print(f"Tamanho: {len(html)} chars")
    
    # Salvar HTML completo
    with open("playerembedapi_response_new.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ HTML salvo em playerembedapi_response_new.html")
    
    # Procurar padrões de URL de vídeo
    print("\n🔍 Procurando URLs de vídeo...")
    
    patterns = [
        (r'src\s*=\s*["\']([^"\']*storage\.googleapis\.com[^"\']+)["\']', "storage.googleapis.com"),
        (r'src\s*=\s*["\']([^"\']+\.mp4[^"\']*)["\']', ".mp4"),
        (r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']', ".m3u8"),
        (r'"file"\s*:\s*"([^"]+)"', "file JSON"),
        (r"'file'\s*:\s*'([^']+)'", "file JS"),
        (r'source\s*:\s*["\']([^"\']+)["\']', "source"),
        (r'video\.src\s*=\s*["\']([^"\']+)["\']', "video.src"),
        (r'videoUrl\s*=\s*["\']([^"\']+)["\']', "videoUrl"),
        (r'playbackUrl\s*=\s*["\']([^"\']+)["\']', "playbackUrl"),
        (r'https://[^"\'<>\s]+\.mp4', "URL direta mp4"),
        (r'https://[^"\'<>\s]+\.m3u8', "URL direta m3u8"),
        (r'https://storage\.googleapis\.com/[^"\'<>\s]+', "GCS URL"),
    ]
    
    found = []
    for pattern, name in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"\n✅ {name}:")
            for m in matches[:5]:
                print(f"   {m[:100]}...")
                if m not in found:
                    found.append(m)
    
    # Procurar scripts
    print("\n🔍 Analisando scripts...")
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    print(f"Encontrados {len(scripts)} scripts")
    
    for i, script in enumerate(scripts):
        if len(script) > 100:
            print(f"\n📜 Script {i+1} ({len(script)} chars):")
            # Procurar variáveis interessantes
            if "src" in script.lower() or "url" in script.lower() or "file" in script.lower():
                print(script[:500])
                print("...")
    
    # Procurar elementos video
    print("\n🔍 Procurando elementos <video>...")
    videos = re.findall(r'<video[^>]*>.*?</video>', html, re.DOTALL | re.IGNORECASE)
    print(f"Encontrados {len(videos)} elementos video")
    for v in videos:
        print(v[:300])
    
    # Procurar elementos source
    print("\n🔍 Procurando elementos <source>...")
    sources = re.findall(r'<source[^>]+>', html, re.IGNORECASE)
    print(f"Encontrados {len(sources)} elementos source")
    for s in sources:
        print(s)

if __name__ == "__main__":
    main()
