#!/usr/bin/env python3
"""
Analisa a API do PlayerThree v2 - Corrigido
"""

import requests
import json
import re

API_URL = "https://playerthree.online/episodio/255703"
EMBED_URL = "https://playerthree.online/embed/synden/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": EMBED_URL,
}

def analyze():
    print("="*70)
    print("ANÁLISE PLAYERTHREE v2")
    print("="*70)
    
    # 1. Chamar API do episódio
    print(f"\n[1] API: {API_URL}")
    
    resp = requests.get(API_URL, headers=headers)
    html = resp.text
    
    # Salvar
    with open("playerthree_episodio.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # 2. Extrair gleam.config
    print("\n[2] Extraindo gleam.config...")
    
    config_match = re.search(r'gleam\.config\s*=\s*(\{[^;]+\});', html)
    if config_match:
        try:
            config = json.loads(config_match.group(1))
            print(f"\n  gleam.config:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"  Erro parsing: {e}")
            print(f"  Raw: {config_match.group(1)[:500]}")
    
    # 3. Extrair gleam.episode
    print("\n[3] Extraindo gleam.episode...")
    
    episode_match = re.search(r'gleam\.episode\s*=\s*(\{[^;]+\});', html)
    if episode_match:
        try:
            episode = json.loads(episode_match.group(1))
            print(f"\n  gleam.episode:")
            print(json.dumps(episode, indent=2, ensure_ascii=False))
            
            # Procurar sources
            if 'sources' in episode:
                print(f"\n  SOURCES ENCONTRADAS:")
                for src in episode['sources']:
                    print(f"    {src}")
        except Exception as e:
            print(f"  Erro parsing: {e}")
            print(f"  Raw: {episode_match.group(1)[:1000]}")
    
    # 4. Procurar todas as variáveis gleam
    print("\n[4] Todas variáveis gleam...")
    
    gleam_matches = re.findall(r'gleam\.(\w+)\s*=\s*([^;]+);', html)
    for name, value in gleam_matches:
        print(f"\n  gleam.{name}:")
        # Tentar parsear como JSON
        try:
            data = json.loads(value)
            if isinstance(data, dict) or isinstance(data, list):
                print(f"    {json.dumps(data, indent=4, ensure_ascii=False)[:500]}")
            else:
                print(f"    {data}")
        except:
            print(f"    {value[:200]}")
    
    # 5. Procurar URLs de vídeo/embed
    print("\n[5] URLs encontradas...")
    
    # MegaEmbed
    mega_ids = re.findall(r'megaembed\.link/e/([a-zA-Z0-9]+)', html)
    if mega_ids:
        print(f"\n  MegaEmbed IDs:")
        for mid in set(mega_ids):
            print(f"    https://megaembed.link/e/{mid}")
    
    # M3U8/MP4
    video_urls = re.findall(r'(https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*)', html)
    if video_urls:
        print(f"\n  Video URLs:")
        for url in set(video_urls):
            print(f"    {url}")
    
    # Iframes
    iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
    if iframes:
        print(f"\n  Iframes:")
        for url in iframes:
            print(f"    {url}")
    
    # 6. Testar API MegaEmbed
    print("\n[6] Testando API MegaEmbed...")
    
    mega_api = "https://megaembed.link/api/v1/info?id=3wnuij"
    try:
        resp = requests.get(mega_api, headers={
            "User-Agent": headers["User-Agent"],
            "Referer": "https://megaembed.link/",
            "Origin": "https://megaembed.link"
        })
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
    except Exception as e:
        print(f"  Erro: {e}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    analyze()
