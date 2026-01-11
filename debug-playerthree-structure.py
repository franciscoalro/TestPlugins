#!/usr/bin/env python3
"""
Debug PlayterThree Structure - Investigar como funciona
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def debug_playerthree():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Testar uma URL específica do PlayterThree
    playerthree_url = "https://playerthree.online/embed/breakingbad/"
    
    print(f"🔍 Analisando PlayterThree: {playerthree_url}")
    
    try:
        response = session.get(playerthree_url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"📄 Status: {response.status_code}")
        print(f"📏 Tamanho HTML: {len(html)} chars")
        
        # 1. Procurar todos os botões
        print(f"\n🔘 TODOS OS BOTÕES:")
        buttons = soup.find_all('button')
        for i, btn in enumerate(buttons):
            attrs = dict(btn.attrs) if btn.attrs else {}
            text = btn.get_text(strip=True)
            print(f"   {i+1}. '{text}' - Attrs: {attrs}")
        
        # 2. Procurar elementos com data-*
        print(f"\n📊 ELEMENTOS COM DATA-*:")
        data_elements = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        for elem in data_elements:
            attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            print(f"   {elem.name}: {attrs}")
        
        # 3. Procurar JavaScript relevante
        print(f"\n📜 JAVASCRIPT RELEVANTE:")
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string.strip()
                if len(script_content) > 100:  # Scripts grandes
                    # Procurar por padrões interessantes
                    if any(keyword in script_content.lower() for keyword in ['episode', 'source', 'player', 'video', 'embed']):
                        print(f"   Script {i+1} ({len(script_content)} chars):")
                        # Mostrar primeiras linhas
                        lines = script_content.split('\n')[:5]
                        for line in lines:
                            if line.strip():
                                print(f"      {line.strip()[:100]}...")
                        print()
        
        # 4. Procurar URLs específicas no HTML
        print(f"\n🔗 URLS ENCONTRADAS NO HTML:")
        url_patterns = [
            r'https?://[^"\s\']+megaembed[^"\s\']*',
            r'https?://[^"\s\']+playerembedapi[^"\s\']*',
            r'https?://[^"\s\']+myvidplay[^"\s\']*',
            r'https?://[^"\s\']+episodio/\d+',
            r'/episodio/\d+',
            r'data-episode-id["\s]*=["\s]*["\']?(\d+)'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"   Padrão '{pattern}': {len(matches)} matches")
                for match in matches[:3]:
                    print(f"      - {match}")
        
        # 5. Verificar se há AJAX/API calls
        print(f"\n🌐 POSSÍVEIS ENDPOINTS API:")
        api_patterns = [
            r'/api/[^"\s\']+',
            r'/ajax/[^"\s\']+',
            r'/episodio/\d+[^"\s\']*',
            r'\.php[^"\s\']*'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"   API Pattern '{pattern}': {matches[:3]}")
        
        # 6. Procurar por IDs de episódio
        print(f"\n🆔 IDs DE EPISÓDIO:")
        id_patterns = [
            r'episode["\s]*:["\s]*["\']?(\d+)',
            r'episodeId["\s]*:["\s]*["\']?(\d+)',
            r'data-episode[^>]*["\'](\d+)',
            r'ep_id["\s]*=["\s]*["\']?(\d+)'
        ]
        
        for pattern in id_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"   ID Pattern '{pattern}': {matches}")
        
        # 7. Salvar HTML para análise manual
        with open('playerthree_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n💾 HTML salvo em: playerthree_debug.html")
        
        return html
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def test_ajax_endpoint():
    """Testa se há endpoint AJAX para obter fontes"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    })
    
    # Possíveis endpoints baseados em análise de outros sites similares
    test_endpoints = [
        "https://playerthree.online/episodio/1",
        "https://playerthree.online/api/episode/1",
        "https://playerthree.online/ajax/episode/1",
        "https://playerthree.online/sources/1"
    ]
    
    print(f"\n🧪 TESTANDO ENDPOINTS AJAX:")
    
    for endpoint in test_endpoints:
        try:
            response = session.get(endpoint)
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 200:
                content = response.text[:200]
                print(f"      Content: {content}...")
        except Exception as e:
            print(f"   {endpoint}: Erro - {e}")

if __name__ == "__main__":
    print("🔬 DEBUG PLAYERTHREE STRUCTURE")
    print("=" * 60)
    
    html = debug_playerthree()
    test_ajax_endpoint()
    
    print(f"\n📋 CONCLUSÕES:")
    print("1. Verificar se PlayterThree usa JavaScript para carregar fontes")
    print("2. Pode precisar de AJAX call para obter lista de episódios")
    print("3. Verificar se estrutura mudou recentemente")
    print("4. Analisar HTML salvo para mais detalhes")