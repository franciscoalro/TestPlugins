#!/usr/bin/env python3
import requests
import re

def test_maxseries():
    print("🚀 TESTE RÁPIDO - MAXSERIES")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Teste 1: Homepage
    print("🔍 Teste 1: Homepage...")
    try:
        response = session.get("https://www.maxseries.one", timeout=10)
        if response.status_code == 200:
            items = len(re.findall(r'<article class="item"', response.text))
            print(f"✅ Homepage OK - {items} itens encontrados")
        else:
            print(f"❌ Homepage erro: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Homepage erro: {e}")
        return
    
    # Teste 2: Busca
    print("\n🔍 Teste 2: Busca...")
    try:
        search_response = session.get("https://www.maxseries.one/?s=breaking", timeout=10)
        if search_response.status_code == 200:
            results = len(re.findall(r'<div class="result-item"', search_response.text))
            print(f"✅ Busca OK - {results} resultados")
        else:
            print(f"❌ Busca erro: {search_response.status_code}")
    except Exception as e:
        print(f"❌ Busca erro: {e}")
    
    # Teste 3: Primeiro item
    print("\n🔍 Teste 3: Primeiro item...")
    try:
        item_match = re.search(r'<article class="item">.*?<a href="([^"]+)"', response.text, re.DOTALL)
        if item_match:
            item_url = item_match.group(1)
            print(f"🔗 URL: {item_url}")
            
            item_response = session.get(item_url, timeout=10)
            if item_response.status_code == 200:
                iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', item_response.text)
                if iframe_match:
                    iframe_url = iframe_match.group(1)
                    if iframe_url.startswith('//'):
                        iframe_url = 'https:' + iframe_url
                    print(f"✅ Player encontrado: {iframe_url}")
                    
                    # Identificar tipo
                    if "megaembed" in iframe_url:
                        print("🎯 Tipo: MegaEmbed")
                    elif "playerembedapi" in iframe_url:
                        print("🎯 Tipo: PlayerEmbedAPI")
                    elif any(d in iframe_url for d in ["myvidplay", "bysebuho", "g9r6"]):
                        print("🎯 Tipo: DoodStream Clone")
                    else:
                        print("🎯 Tipo: Outro")
                else:
                    print("⚠️ Nenhum player encontrado")
            else:
                print(f"❌ Item erro: {item_response.status_code}")
        else:
            print("❌ Nenhum item encontrado")
    except Exception as e:
        print(f"❌ Item erro: {e}")
    
    print("\n✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_maxseries()