#!/usr/bin/env python3
"""
Teste rapido do PlayerEmbedAPI para verificar o que esta acontecendo
"""

import requests
import re
import sys

# Headers simulando navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://playerembedapi.link/',
    'Origin': 'https://playerembedapi.link'
}

def test_playerembedapi(url):
    print(f"\n{'='*60}")
    print(f"Testando: {url}")
    print(f"{'='*60}\n")
    
    try:
        # Fazer requisicao
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"URL final: {response.url}")
        print(f"Tamanho: {len(response.text)} bytes\n")
        
        html = response.text
        
        # Procurar por JWPlayer setup
        print("--- Procurando JWPlayer setup ---")
        jwplayer_match = re.search(r"jwplayer\s*\(\s*['\"]?[\w_-]+['\"]?\s*\)\s*\.setup\s*\(\s*(\{[\s\S]*?\})\s*\)", html, re.DOTALL | re.IGNORECASE)
        if jwplayer_match:
            print("[OK] JWPlayer setup encontrado!")
            setup_json = jwplayer_match.group(1)[:500]
            print(f"Preview: {setup_json}...")
        else:
            print("[ERRO] JWPlayer setup NAO encontrado")
        
        # Procurar por URLs de video
        print("\n--- Procurando URLs de video ---")
        patterns = [
            (r'https?://[^"\s]+\.m3u8[^"\s]*', "M3U8"),
            (r'https?://[^"\s]*cloudatacdn[^"\s]+', "CloudAtaCDN"),
            (r'https?://[^"\s]*googleapis[^"\s]+\.mp4[^"\s]*', "Google APIs"),
            (r'https?://[^"\s]*sssrr[^"\s]+', "SSSRR"),
            (r'https?://[^"\s]+\.mp4[^"\s]*', "MP4"),
        ]
        
        found = False
        for pattern, name in patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f"[OK] {name}: {len(matches)} encontrado(s)")
                for i, match in enumerate(matches[:3]):  # Mostrar primeiros 3
                    print(f"  {i+1}. {match[:80]}...")
                found = True
        
        if not found:
            print("[ERRO] Nenhuma URL de video encontrada no HTML")
        
        # Procurar por chamadas de API
        print("\n--- Procurando chamadas de API ---")
        api_patterns = [
            (r'fetch\s*\(\s*["\']([^"\']+)["\']', "fetch"),
            (r'\.get\s*\(\s*["\']([^"\']+)["\']', "GET"),
            (r'url\s*:\s*["\']([^"\']*(?:api|playlist|source|video)[^"\']*)["\']', "API URL"),
        ]
        
        for pattern, name in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"[OK] {name}: {len(matches)} encontrado(s)")
                for i, match in enumerate(matches[:3]):
                    print(f"  {i+1}. {match[:80]}...")
        
        # Salvar HTML para analise
        print(f"\n--- Salvando HTML para analise ---")
        filename = "playerembedapi_debug.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] HTML salvo em: {filename}")
        
        return True
        
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

if __name__ == "__main__":
    # URL de teste - usar um exemplo real do MaxSeries
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://playerembedapi.link/?v=QvXFt2de3"
    test_playerembedapi(test_url)
