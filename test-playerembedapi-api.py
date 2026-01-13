#!/usr/bin/env python3
"""
Teste para encontrar a API real do PlayerEmbedAPI
"""

import requests
import re
import json
import base64

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def test_api_endpoints():
    """Testa diferentes endpoints da API"""
    video_id = "4PHWs34H0"
    base_url = "https://playerembedapi.link"
    
    endpoints = [
        f"{base_url}/?v={video_id}",
        f"{base_url}/api/source/{video_id}",
        f"{base_url}/api/video/{video_id}",
        f"{base_url}/embed/{video_id}",
        f"{base_url}/v/{video_id}",
        f"{base_url}/source/{video_id}",
    ]
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://playerthree.online"
    }
    
    for url in endpoints:
        print(f"\n🔍 Testando: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            print(f"  Status: {response.status_code}")
            print(f"  URL final: {response.url}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            text = response.text[:500]
            if "sources" in text.lower() or "file" in text.lower():
                print(f"  ✅ Possível resposta com vídeo!")
                print(f"  Conteúdo: {text}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")

def test_iamcdn_api():
    """Testa a API do iamcdn.net (player real)"""
    print("\n" + "=" * 60)
    print("🔍 Testando API do iamcdn.net")
    print("=" * 60)
    
    # Dados do base64 decodificado
    slug = "4PHWs34H0"
    md5_id = 28975276
    user_id = 482120
    
    endpoints = [
        f"https://iamcdn.net/player-v2/api/source/{slug}",
        f"https://iamcdn.net/api/source/{slug}",
        f"https://iamcdn.net/v/{slug}",
        f"https://abyss.to/api/source/{slug}",
        f"https://abyss.to/embed/{slug}",
    ]
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://playerembedapi.link",
        "Origin": "https://playerembedapi.link"
    }
    
    for url in endpoints:
        print(f"\n🔍 Testando: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            print(f"  Status: {response.status_code}")
            print(f"  URL final: {response.url}")
            
            text = response.text[:500]
            print(f"  Conteúdo: {text}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")

def test_direct_video_search():
    """Busca direta por URLs de vídeo no HTML"""
    print("\n" + "=" * 60)
    print("🔍 Buscando URLs de vídeo no HTML")
    print("=" * 60)
    
    url = "https://playerembedapi.link/?v=4PHWs34H0"
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://playerthree.online"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    # Buscar todos os scripts externos
    print("\n📜 Scripts externos:")
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
    for s in scripts:
        print(f"  - {s}")
    
    # Buscar o bundle do player
    print("\n🔍 Analisando core.bundle.js...")
    bundle_url = "https://iamcdn.net/player-v2/core.bundle.js"
    try:
        bundle_response = requests.get(bundle_url, headers=headers, timeout=15)
        bundle = bundle_response.text
        print(f"  Tamanho: {len(bundle)} chars")
        
        # Procurar padrões de API
        api_patterns = [
            r'https?://[^"\']+/api/[^"\']+',
            r'https?://[^"\']+/source[^"\']*',
            r'https?://[^"\']+/video[^"\']*',
            r'\.m3u8',
            r'\.mp4',
            r'storage\.googleapis\.com',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, bundle)
            if matches:
                print(f"\n  Padrão '{pattern}':")
                for m in set(matches)[:5]:
                    print(f"    - {m[:80]}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_iamcdn_api()
    test_direct_video_search()
