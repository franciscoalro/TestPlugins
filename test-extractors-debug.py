#!/usr/bin/env python3
"""
Teste para verificar se os extractors estão funcionando corretamente.
Simula o que o CloudStream faz.
"""

import requests
import re
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def test_playerembedapi(url, referer):
    """Testa o PlayerEmbedAPI extractor"""
    print(f"\n🟢 Testando PlayerEmbedAPI: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Referer": referer
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        text = response.text
        
        print(f"  Status: {response.status_code}")
        print(f"  Tamanho: {len(text)} chars")
        print(f"  Resposta: {text[:500]}...")
        
        # Tentar parsear JSON
        try:
            data = json.loads(text)
            if "sources" in data:
                print(f"  ✅ JSON válido com {len(data['sources'])} sources:")
                for src in data["sources"]:
                    print(f"    - {src.get('label', 'Auto')}: {src.get('file', 'N/A')[:80]}...")
                return True
        except:
            pass
        
        # Fallback regex
        files = re.findall(r'"file"\s*:\s*"([^"]+)"', text)
        if files:
            print(f"  ✅ Regex encontrou {len(files)} files:")
            for f in files:
                print(f"    - {f[:80]}...")
            return True
        
        print("  ❌ Nenhum link encontrado")
        return False
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_megaembed(url, referer):
    """Testa o MegaEmbed - só verifica se a URL é válida"""
    print(f"\n🔴 Testando MegaEmbed: {url}")
    
    # MegaEmbed precisa de WebView, então só verificamos se a URL está correta
    if "megaembed.link" in url and "#" in url:
        hash_id = url.split("#")[-1]
        print(f"  Hash ID: {hash_id}")
        print(f"  ✅ URL válida para WebView")
        return True
    else:
        print(f"  ❌ URL inválida")
        return False

def test_myvidplay(url, referer):
    """Testa o MyVidPlay extractor"""
    print(f"\n🟡 Testando MyVidPlay: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": referer
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        text = response.text
        
        print(f"  Status: {response.status_code}")
        print(f"  Tamanho: {len(text)} chars")
        
        # Procurar links de vídeo
        patterns = [
            r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'"file"\s*:\s*"([^"]+\.mp4[^"]*)"',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"  ✅ Encontrado {len(matches)} links:")
                for m in matches[:3]:
                    print(f"    - {m[:80]}...")
                return True
        
        print(f"  ⚠️ Nenhum link direto encontrado (pode precisar de JS)")
        print(f"  Início HTML: {text[:300]}...")
        return False
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 TESTE DOS EXTRACTORS")
    print("=" * 60)
    
    # Episódio com 3 sources
    episode_id = "258444"
    referer = "https://playerthree.online"
    
    # Buscar sources do episódio
    url = f"https://playerthree.online/episodio/{episode_id}"
    print(f"\n📺 Buscando sources de: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    # Extrair sources
    sources = []
    pattern = re.compile(r'data-source\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
    for match in pattern.findall(html):
        if match.startswith("http"):
            sources.append(match)
    
    print(f"✅ {len(sources)} sources encontradas")
    
    # Testar cada extractor
    results = {}
    
    for source in sources:
        if "playerembedapi" in source.lower():
            results["PlayerEmbedAPI"] = test_playerembedapi(source, referer)
        elif "megaembed" in source.lower():
            results["MegaEmbed"] = test_megaembed(source, referer)
        elif "myvidplay" in source.lower():
            results["MyVidPlay"] = test_myvidplay(source, referer)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO DOS EXTRACTORS")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FALHOU"
        print(f"  {name}: {status}")

if __name__ == "__main__":
    main()
