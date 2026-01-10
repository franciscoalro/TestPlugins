#!/usr/bin/env python3
"""
Analisa a API do PlayerThree - /episodio/255703
Captura a resposta e identifica o fluxo para o vídeo
"""

import requests
import json
import re

# API descoberta
API_URL = "https://playerthree.online/episodio/255703"
EMBED_URL = "https://playerthree.online/embed/synden/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": EMBED_URL,
    "Origin": "https://playerthree.online",
}

def analyze_api():
    print("="*70)
    print("ANÁLISE API PLAYERTHREE")
    print("="*70)
    
    # 1. Primeiro, pegar a página embed para ver a estrutura
    print("\n[1] Analisando página embed...")
    
    resp = requests.get(EMBED_URL, headers=headers)
    print(f"  Status: {resp.status_code}")
    
    # Procurar scripts e dados
    html = resp.text
    
    # Salvar HTML
    with open("playerthree_embed.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  Salvo em playerthree_embed.html")
    
    # Procurar IDs e configurações
    print("\n  Procurando dados no HTML...")
    
    # Procurar data attributes
    data_matches = re.findall(r'data-(\w+)=["\']([^"\']+)["\']', html)
    for name, value in data_matches[:20]:
        print(f"    data-{name}: {value}")
    
    # Procurar URLs de iframe
    iframe_matches = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
    for url in iframe_matches:
        print(f"    iframe: {url}")
    
    # Procurar megaembed
    mega_matches = re.findall(r'megaembed[^"\'>\s]+', html)
    for m in set(mega_matches):
        print(f"    megaembed: {m}")
    
    # 2. Chamar API do episódio
    print(f"\n[2] Chamando API: {API_URL}")
    
    resp = requests.get(API_URL, headers=headers)
    print(f"  Status: {resp.status_code}")
    print(f"  Content-Type: {resp.headers.get('Content-Type')}")
    
    # Salvar resposta
    with open("playerthree_api_response.txt", "w", encoding="utf-8") as f:
        f.write(resp.text)
    
    print(f"\n  Resposta ({len(resp.text)} chars):")
    print(f"  {resp.text[:500]}")
    
    # Tentar parsear como JSON
    try:
        data = resp.json()
        print(f"\n  JSON parseado:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
        
        # Procurar URLs de vídeo no JSON
        def find_urls(obj, path=""):
            urls = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    urls.extend(find_urls(v, f"{path}.{k}"))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    urls.extend(find_urls(v, f"{path}[{i}]"))
            elif isinstance(obj, str):
                if any(x in obj for x in ['.m3u8', '.mp4', 'http', 'megaembed']):
                    urls.append((path, obj))
            return urls
        
        urls = find_urls(data)
        if urls:
            print(f"\n  URLs encontradas:")
            for path, url in urls:
                print(f"    {path}: {url}")
                
    except:
        print("  Não é JSON, analisando como HTML/texto...")
        
        # Procurar URLs no texto
        url_matches = re.findall(r'https?://[^\s"\'<>]+', resp.text)
        if url_matches:
            print(f"\n  URLs encontradas:")
            for url in set(url_matches)[:20]:
                print(f"    {url}")
        
        # Procurar megaembed
        mega_matches = re.findall(r'megaembed\.link/e/([a-zA-Z0-9]+)', resp.text)
        if mega_matches:
            print(f"\n  MegaEmbed IDs:")
            for mid in set(mega_matches):
                print(f"    {mid} -> https://megaembed.link/e/{mid}")
    
    # 3. Testar outras variações da API
    print("\n[3] Testando outras APIs...")
    
    test_urls = [
        "https://playerthree.online/api/episodio/255703",
        "https://playerthree.online/api/v1/episodio/255703",
        "https://playerthree.online/embed/synden/255703",
        "https://megaembed.link/api/v1/info?id=3wnuij",
    ]
    
    for url in test_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"\n  {url}")
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"    Response: {resp.text[:200]}")
        except Exception as e:
            print(f"\n  {url}")
            print(f"    Erro: {e}")
    
    print("\n" + "="*70)
    print("ANÁLISE COMPLETA")
    print("="*70)


if __name__ == "__main__":
    analyze_api()
