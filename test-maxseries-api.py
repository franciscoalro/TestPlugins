#!/usr/bin/env python3
"""
Teste da API do MaxSeries e análise do player
"""

import requests
import json
import re
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html, */*',
    'Referer': 'https://www.maxseries.one/',
}

def test_player_api():
    """Testa a API do player"""
    print("="*60)
    print("TESTE DA API DO PLAYER")
    print("="*60)
    
    # API encontrada no HTML
    api_base = "https://www.maxseries.one/wp-json/dooplayer/v2/"
    
    # Testar endpoints comuns
    endpoints = [
        "player/",
        "video/",
        "embed/",
    ]
    
    for ep in endpoints:
        url = api_base + ep
        print(f"\nTestando: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            print(f"  Status: {resp.status_code}")
            print(f"  Response: {resp.text[:200]}...")
        except Exception as e:
            print(f"  Erro: {e}")

def test_playerthree():
    """Testa o iframe playerthree.online"""
    print("\n" + "="*60)
    print("TESTE DO PLAYERTHREE.ONLINE")
    print("="*60)
    
    url = "https://playerthree.online/embed/synden/"
    print(f"URL: {url}")
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"URL final: {resp.url}")
        print(f"Tamanho: {len(resp.text)} bytes")
        
        # Salvar HTML
        with open('playerthree_response.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("HTML salvo em: playerthree_response.html")
        
        # Procurar URLs de vídeo
        patterns = [
            r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
            r'(https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*)',
            r'file:\s*["\']([^"\']+)["\']',
            r'source:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+)["\']',
        ]
        
        print("\nURLs de vídeo encontradas:")
        for pattern in patterns:
            matches = re.findall(pattern, resp.text, re.I)
            for m in matches:
                if 'm3u8' in m.lower() or 'mp4' in m.lower() or 'video' in m.lower():
                    print(f"  -> {m[:100]}...")
        
        # Procurar iframes
        soup = BeautifulSoup(resp.text, 'html.parser')
        iframes = soup.find_all('iframe')
        print(f"\nIframes encontrados: {len(iframes)}")
        for iframe in iframes:
            src = iframe.get('src', '')
            print(f"  -> {src}")
        
        # Procurar scripts com URLs
        scripts = soup.find_all('script')
        print(f"\nScripts encontrados: {len(scripts)}")
        for script in scripts:
            text = script.string or ''
            if any(x in text.lower() for x in ['m3u8', 'mp4', 'video', 'player', 'source']):
                print(f"  Script interessante: {text[:200]}...")
                
    except Exception as e:
        print(f"Erro: {e}")

def find_episodes_ajax():
    """Tenta encontrar episódios via AJAX"""
    print("\n" + "="*60)
    print("BUSCA DE EPISÓDIOS VIA AJAX")
    print("="*60)
    
    # Primeiro, pegar o post_id da série
    series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
    
    try:
        resp = requests.get(series_url, headers=HEADERS, timeout=30)
        
        # Procurar post_id
        post_id_match = re.search(r'post-(\d+)', resp.text)
        if post_id_match:
            post_id = post_id_match.group(1)
            print(f"Post ID encontrado: {post_id}")
        else:
            print("Post ID não encontrado")
            # Tentar outro padrão
            post_id_match = re.search(r'"post_id":\s*"?(\d+)"?', resp.text)
            if post_id_match:
                post_id = post_id_match.group(1)
                print(f"Post ID (alternativo): {post_id}")
            else:
                post_id = None
        
        # Procurar nonce
        nonce_match = re.search(r'"nonce":\s*"([^"]+)"', resp.text)
        if nonce_match:
            nonce = nonce_match.group(1)
            print(f"Nonce encontrado: {nonce}")
        else:
            nonce = None
            print("Nonce não encontrado")
        
        # Tentar chamar AJAX para episódios
        if post_id:
            ajax_url = "https://www.maxseries.one/wp-admin/admin-ajax.php"
            
            # Tentar diferentes actions
            actions = [
                'doo_player_ajax',
                'get_episodes',
                'load_episodes',
                'seasons_episodes',
            ]
            
            for action in actions:
                print(f"\nTestando action: {action}")
                data = {
                    'action': action,
                    'post_id': post_id,
                    'nonce': nonce or '',
                }
                
                try:
                    ajax_resp = requests.post(ajax_url, data=data, headers=HEADERS, timeout=10)
                    print(f"  Status: {ajax_resp.status_code}")
                    if ajax_resp.text and len(ajax_resp.text) > 10:
                        print(f"  Response: {ajax_resp.text[:300]}...")
                except Exception as e:
                    print(f"  Erro: {e}")
        
    except Exception as e:
        print(f"Erro: {e}")

def test_dooplayer_api():
    """Testa a API dooplayer diretamente"""
    print("\n" + "="*60)
    print("TESTE DA API DOOPLAYER")
    print("="*60)
    
    # Formato típico: /wp-json/dooplayer/v2/{post_id}/{type}/{num}
    # type pode ser: movie, tv, embed
    
    base_url = "https://www.maxseries.one/wp-json/dooplayer/v2/"
    
    # Testar com IDs comuns
    test_ids = ['1', '100', '1000', '258444']  # 258444 é de um episódio conhecido
    
    for post_id in test_ids:
        for tipo in ['movie', 'tv', 'embed']:
            url = f"{base_url}{post_id}/{tipo}/1"
            print(f"\nTestando: {url}")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                print(f"  Status: {resp.status_code}")
                if resp.status_code == 200 and resp.text:
                    print(f"  Response: {resp.text[:300]}...")
            except Exception as e:
                print(f"  Erro: {e}")

def main():
    test_playerthree()
    test_dooplayer_api()
    find_episodes_ajax()

if __name__ == "__main__":
    main()
