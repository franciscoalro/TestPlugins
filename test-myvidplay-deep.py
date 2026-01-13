#!/usr/bin/env python3
"""
Análise profunda do MyVidPlay para encontrar o link do vídeo
"""

import requests
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def main():
    url = "https://myvidplay.com/e/tilgznkxayrx"
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
    print(f"URL final: {response.url}")
    
    # Salvar HTML completo
    with open("myvidplay_response_new.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ HTML salvo em myvidplay_response_new.html")
    
    # Verificar se é DoodStream
    if "dood" in html.lower() or "doodstream" in html.lower():
        print("\n🔍 É um player DoodStream!")
    
    # Procurar padrões de URL de vídeo
    print("\n🔍 Procurando URLs de vídeo...")
    
    patterns = [
        (r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*', "m3u8"),
        (r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*', "mp4"),
        (r'https?://[a-z0-9]+\.dood[a-z]*\.[a-z]+/[^"\'<>\s]+', "dood URL"),
        (r'https?://[a-z0-9]+\.doodcdn\.[a-z]+/[^"\'<>\s]+', "doodcdn URL"),
        (r'/pass_md5/[^"\'<>\s]+', "pass_md5"),
        (r'token=[^"\'<>\s&]+', "token"),
    ]
    
    for pattern, name in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"\n✅ {name}:")
            for m in list(set(matches))[:5]:
                print(f"   {m[:100]}...")
    
    # Procurar scripts
    print("\n🔍 Analisando scripts inline...")
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    
    for i, script in enumerate(scripts):
        if len(script) > 50 and ("pass_md5" in script or "token" in script or "dood" in script.lower()):
            print(f"\n📜 Script {i+1} relevante ({len(script)} chars):")
            print(script[:800])
            print("...")
    
    # Procurar a função de geração de URL do Dood
    print("\n🔍 Procurando função de geração de URL...")
    
    # Padrão típico do DoodStream
    dood_patterns = [
        r"(https?://[^'\"]+/pass_md5/[^'\"]+)",
        r"makePlay\.setAttribute\('src',\s*'([^']+)'",
        r"dsplayer\.src\s*=\s*['\"]([^'\"]+)['\"]",
    ]
    
    for pattern in dood_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f"\n✅ Padrão encontrado:")
            for m in matches[:3]:
                print(f"   {m}")

if __name__ == "__main__":
    main()
