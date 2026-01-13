#!/usr/bin/env python3
"""
Teste para verificar quantas sources o playerthree.online retorna
para diferentes episódios.
"""

import requests
import re
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def extract_sources(html):
    """Extrai sources do HTML usando os mesmos padrões do Kotlin v73"""
    sources = []
    
    # Padrão 1: data-source="url"
    pattern1 = re.compile(r'data-source\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for match in pattern1.findall(html):
        url = match.strip()
        if url.startswith("http") and url not in sources:
            print(f"  🔹 data-source: {url}")
            sources.append(url)
    
    # Padrão 2: data-src="url"
    pattern2 = re.compile(r'data-src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for match in pattern2.findall(html):
        url = match.strip()
        if url.startswith("http") and url not in sources:
            print(f"  🔹 data-src: {url}")
            sources.append(url)
    
    return sources

def test_episode(episode_id, referer="https://playerthree.online"):
    """Testa um episódio específico"""
    url = f"https://playerthree.online/episodio/{episode_id}"
    print(f"\n🎬 Testando: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        print(f"📄 Status: {response.status_code}")
        print(f"📄 Tamanho: {len(html)} chars")
        print(f"📄 Início: {html[:300]}...")
        
        sources = extract_sources(html)
        print(f"\n✅ Total sources: {len(sources)}")
        
        # Categorizar
        for src in sources:
            if "playerembedapi" in src.lower():
                print(f"  🟢 [PRIORIDADE 1] PlayerEmbedAPI: {src}")
            elif "myvidplay" in src.lower() or "dood" in src.lower():
                print(f"  🟡 [PRIORIDADE 2] Dood/MyVidPlay: {src}")
            elif "megaembed" in src.lower():
                print(f"  🔴 [PRIORIDADE 3] MegaEmbed: {src}")
            else:
                print(f"  ⚪ [OUTRO] {src}")
        
        return sources
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    print("=" * 60)
    print("🔍 TESTE DE SOURCES DO PLAYERTHREE.ONLINE")
    print("=" * 60)
    
    # IDs de episódios conhecidos (dos arquivos de captura)
    episode_ids = [
        "209708",  # Do ajax_response.html
        "209709",  # Do ajax_response.html
        "219179",  # Do network_analysis_results.json
        "258444",  # Do network_analysis_results.json
        "172306",  # Do network_analysis_results.json
        "212780",  # Do network_analysis_results.json
    ]
    
    all_results = {}
    
    for ep_id in episode_ids:
        sources = test_episode(ep_id)
        all_results[ep_id] = sources
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    
    for ep_id, sources in all_results.items():
        print(f"Episódio {ep_id}: {len(sources)} sources")
        for src in sources:
            domain = src.split("/")[2] if len(src.split("/")) > 2 else src
            print(f"  - {domain}")

if __name__ == "__main__":
    main()
