#!/usr/bin/env python3
"""
MaxSeries Video Extractor Tester
Usa requests (equivalente ao OkHttp) para fazer parse HTML e buscar vídeos

Testa: Streamtape, Filemoon, DoodStream, Mixdrop, PlayerEmbedAPI, MegaEmbed
"""

import requests
import re
import sys
from urllib.parse import urljoin, urlparse
import base64

# Headers padrão (simula Firefox)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Prioridade de servidores (do BRExtractorUtils)
SERVER_PRIORITY = {
    "streamtape": 1, "strtape": 1,
    "filemoon": 2, "moonmov": 2,
    "doodstream": 3, "dood": 3, "myvidplay": 3, "bysebuho": 3,
    "mixdrop": 4, "mxtape": 4,
    "playerembedapi": 5,
    "megaembed": 6,
}

def detect_server(url):
    """Detecta o tipo de servidor pela URL"""
    url_lower = url.lower()
    for server, priority in sorted(SERVER_PRIORITY.items(), key=lambda x: x[1]):
        if server in url_lower:
            return server, priority
    return "unknown", 99

def extract_sources_from_html(html, base_url):
    """Extrai URLs de player do HTML (data-source, iframe src, etc)"""
    sources = []
    
    # Padrão 1: data-source="url"
    for match in re.findall(r'data-source\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
        if match.startswith("http"):
            sources.append(match)
    
    # Padrão 2: data-src="url"
    for match in re.findall(r'data-src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
        if match.startswith("http"):
            sources.append(match)
    
    # Padrão 3: iframe src (players)
    for match in re.findall(r'<iframe[^>]+src\s*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE):
        if any(s in match.lower() for s in SERVER_PRIORITY.keys()):
            full_url = urljoin(base_url, match)
            sources.append(full_url)
    
    return list(set(sources))

def extract_streamtape(url, referer=None):
    """Extrai URL do Streamtape"""
    print(f"  🔄 Streamtape: {url}")
    try:
        resp = requests.get(url, headers={**HEADERS, "Referer": referer or url})
        html = resp.text
        
        # Padrão: 'robotlink').innerHTML = 'parte1' + ('parte2')
        match = re.search(r"'robotlink'\)\.innerHTML\s*=\s*'([^']+)'\s*\+\s*\('([^']+)'\)", html)
        if match:
            video_url = f"https:{match.group(1)}{match.group(2)}"
            print(f"  ✅ Streamtape URL: {video_url}")
            return video_url
        
        # Fallback
        match = re.search(r"document\.getElementById\('norobotlink'\)\.innerHTML\s*=\s*'([^']+)'", html)
        if match:
            video_url = f"https:{match.group(1)}"
            print(f"  ✅ Streamtape URL: {video_url}")
            return video_url
            
        print("  ❌ Streamtape: padrão não encontrado")
    except Exception as e:
        print(f"  ❌ Streamtape erro: {e}")
    return None

def extract_filemoon(url, referer=None):
    """Extrai URL do Filemoon (com JsUnpacker se necessário)"""
    print(f"  🔄 Filemoon: {url}")
    try:
        resp = requests.get(url, headers={**HEADERS, "Referer": referer or url})
        html = resp.text
        
        # Tentar direto primeiro
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'sources\s*:\s*\[\s*\{\s*file\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1).replace("\\/", "/")
                print(f"  ✅ Filemoon URL: {video_url}")
                return video_url
        
        # Tentar descompactar JS packed
        packed_match = re.search(r"eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\).+?\}\s*\(.+?\)\s*\)", html, re.DOTALL)
        if packed_match:
            print("  📦 JS packed detectado (precisa JsUnpacker)")
            
        print("  ❌ Filemoon: padrão não encontrado")
    except Exception as e:
        print(f"  ❌ Filemoon erro: {e}")
    return None

def extract_doodstream(url, referer=None):
    """Extrai URL do DoodStream/MyVidPlay"""
    print(f"  🔄 DoodStream: {url}")
    try:
        domain = urlparse(url).netloc
        base_url = f"https://{domain}"
        
        resp = requests.get(url, headers={**HEADERS, "Referer": referer or url})
        html = resp.text
        
        # Extrair path do pass_md5
        match = re.search(r'(/pass_md5/[^"\'\s]+)', html)
        if match:
            pass_md5_path = match.group(1)
            pass_md5_url = f"{base_url}{pass_md5_path}"
            print(f"  🔑 pass_md5: {pass_md5_url}")
            
            # Request para pass_md5
            md5_resp = requests.get(pass_md5_url, headers={**HEADERS, "Referer": url})
            md5_text = md5_resp.text.strip()
            
            if md5_text.startswith("http"):
                import random
                import string
                token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                timestamp = int(requests.get("https://httpbin.org/get").elapsed.total_seconds() * 1000)
                video_url = f"{md5_text}{token}?token={token}&expiry={timestamp}"
                print(f"  ✅ DoodStream URL: {video_url}")
                return video_url
        
        print("  ❌ DoodStream: pass_md5 não encontrado")
    except Exception as e:
        print(f"  ❌ DoodStream erro: {e}")
    return None

def extract_mixdrop(url, referer=None):
    """Extrai URL do Mixdrop"""
    print(f"  🔄 Mixdrop: {url}")
    try:
        resp = requests.get(url, headers={**HEADERS, "Referer": referer or url})
        html = resp.text
        
        patterns = [
            r'MDCore\.vsrc\s*=\s*["\']([^"\']+)["\']',
            r'MDCore\.wurl\s*=\s*["\']([^"\']+)["\']',
            r'"(//[^"]+deliverycdn[^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1).replace("\\/", "/")
                if video_url.startswith("//"):
                    video_url = f"https:{video_url}"
                print(f"  ✅ Mixdrop URL: {video_url}")
                return video_url
        
        # Tentar descompactar JS packed
        if "eval(function(p,a,c,k,e," in html:
            print("  📦 JS packed detectado (precisa JsUnpacker)")
            
        print("  ❌ Mixdrop: padrão não encontrado")
    except Exception as e:
        print(f"  ❌ Mixdrop erro: {e}")
    return None

def extract_playerembed(url, referer=None):
    """Extrai URL do PlayerEmbedAPI"""
    print(f"  🔄 PlayerEmbedAPI: {url}")
    try:
        resp = requests.get(url, headers={**HEADERS, "Referer": referer or url})
        html = resp.text
        
        # Tentar extrair objeto 'datas' para AES-CTR
        datas_match = re.search(r'datas\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
        if datas_match:
            print("  📦 Objeto 'datas' encontrado (precisa AES-CTR decrypt)")
        
        # Tentar extrair URL direta do vídeo
        patterns = [
            r'"(https?://[^"]+\.m3u8[^"]*)"',
            r'"(https?://[^"]+\.mp4[^"]*)"',
            r'"(https?://storage\.googleapis\.com[^"]+)"',
            r'"(https?://[^"]+sssrr\.org[^"]+)"',
            r'"(https?://[^"]+iamcdn\.net[^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1)
                if "google-analytics" not in video_url:
                    print(f"  ✅ PlayerEmbedAPI URL: {video_url}")
                    return video_url
        
        print("  ⚠️ PlayerEmbedAPI: precisa WebView ou AES decrypt")
    except Exception as e:
        print(f"  ❌ PlayerEmbedAPI erro: {e}")
    return None

def test_episode_url(episode_url):
    """Testa extração de um episódio do playerthree.online"""
    print(f"\n{'='*60}")
    print(f"🎬 Testando: {episode_url}")
    print(f"{'='*60}\n")
    
    try:
        resp = requests.get(episode_url, headers=HEADERS)
        html = resp.text
        
        sources = extract_sources_from_html(html, episode_url)
        
        # Ordenar por prioridade
        sources_with_priority = [(url, *detect_server(url)) for url in sources]
        sources_with_priority.sort(key=lambda x: x[2])
        
        print(f"📋 Sources encontradas: {len(sources_with_priority)}\n")
        
        results = []
        
        for source_url, server, priority in sources_with_priority:
            print(f"\n[P{priority}] {server.upper()}")
            
            video_url = None
            if server in ["streamtape", "strtape"]:
                video_url = extract_streamtape(source_url, episode_url)
            elif server in ["filemoon", "moonmov"]:
                video_url = extract_filemoon(source_url, episode_url)
            elif server in ["doodstream", "dood", "myvidplay", "bysebuho"]:
                video_url = extract_doodstream(source_url, episode_url)
            elif server in ["mixdrop", "mxtape"]:
                video_url = extract_mixdrop(source_url, episode_url)
            elif server == "playerembedapi":
                video_url = extract_playerembed(source_url, episode_url)
            else:
                print(f"  ⚠️ Extractor não implementado para: {server}")
            
            if video_url:
                results.append((server, video_url))
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMO: {len(results)}/{len(sources_with_priority)} extractors funcionaram")
        print(f"{'='*60}")
        
        for server, video_url in results:
            print(f"  ✅ {server}: {video_url[:80]}...")
            
        return results
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    # URL de teste (playerthree.online epicodio)
    test_urls = [
        "https://playerthree.online/episodio/258444",  # Garota Sequestrada
        # Adicione mais URLs para testar
    ]
    
    if len(sys.argv) > 1:
        test_urls = sys.argv[1:]
    
    for url in test_urls:
        test_episode_url(url)

if __name__ == "__main__":
    main()
