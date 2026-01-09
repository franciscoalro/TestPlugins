#!/usr/bin/env python3
"""
Análise profunda do PlayerEmbedAPI
"""

import requests
import re
import json
import base64

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://playerembedapi.link/',
}

def analyze_playerembedapi():
    """Análise completa do PlayerEmbedAPI"""
    print('='*70)
    print('🔬 PLAYEREMBEDAPI - Análise Completa')
    print('='*70)
    
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    r = requests.get(url, headers=HEADERS)
    html = r.text
    
    # Salvar HTML completo
    with open('playerembedapi_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 1. Extrair datas
    print('\n📦 Extraindo variável datas...')
    datas_match = re.search(r'const\s+datas\s*=\s*["\']([^"\']+)["\']', html)
    if datas_match:
        datas_b64 = datas_match.group(1)
        decoded = base64.b64decode(datas_b64)
        
        # Tentar parsear como JSON parcial
        try:
            # O JSON tem caracteres binários no campo media
            # Vamos extrair os campos que conseguimos
            text = decoded.decode('utf-8', errors='replace')
            
            # Extrair slug
            slug_match = re.search(r'"slug":"([^"]+)"', text)
            md5_match = re.search(r'"md5_id":(\d+)', text)
            user_match = re.search(r'"user_id":(\d+)', text)
            
            print(f'   slug: {slug_match.group(1) if slug_match else "N/A"}')
            print(f'   md5_id: {md5_match.group(1) if md5_match else "N/A"}')
            print(f'   user_id: {user_match.group(1) if user_match else "N/A"}')
            
            # O campo media parece estar criptografado
            media_start = text.find('"media":"') + 9
            if media_start > 8:
                # Extrair bytes do media
                media_raw = decoded[media_start:]
                print(f'\n   📼 Campo media (raw bytes): {media_raw[:50]}...')
                print(f'   Hex: {media_raw[:30].hex()}')
                
        except Exception as e:
            print(f'   Erro: {e}')
    
    # 2. Buscar script principal
    print('\n📜 Analisando script principal...')
    
    # Buscar o script que processa os dados
    script_match = re.search(r'https://iamcdn\.net/player-v2/core\.bundle\.js', html)
    if script_match:
        print('   Encontrado: core.bundle.js')
        
        r2 = requests.get('https://iamcdn.net/player-v2/core.bundle.js', headers=HEADERS)
        js = r2.text
        
        with open('core_bundle.js', 'w', encoding='utf-8') as f:
            f.write(js)
        print(f'   Salvo ({len(js)} chars)')
        
        # Procurar funções de decrypt
        print('\n   🔍 Procurando funções de decrypt...')
        
        # Procurar por AES, decrypt, etc
        patterns = [
            r'decrypt\s*[:(]',
            r'AES',
            r'CryptoJS',
            r'atob',
            r'fromCharCode',
            r'\.media',
            r'sources',
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, js, re.IGNORECASE))
            if matches:
                print(f'   ✅ "{pattern}": {len(matches)} ocorrências')
                # Mostrar contexto da primeira
                if matches:
                    pos = matches[0].start()
                    context = js[max(0, pos-50):pos+100]
                    print(f'      Contexto: ...{context}...')
    
    # 3. Procurar por API de sources
    print('\n📡 Procurando APIs de sources...')
    
    # Procurar fetch/axios calls no HTML
    api_patterns = [
        r"fetch\(['\"]([^'\"]+)['\"]",
        r"axios\.\w+\(['\"]([^'\"]+)['\"]",
        r"\$\.(get|post)\(['\"]([^'\"]+)['\"]",
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f'   {pattern}: {matches}')
    
    # 4. Tentar endpoint de API direto
    print('\n🌐 Testando endpoints de API...')
    
    video_id = 'izD1HrKWL'
    endpoints = [
        f'https://playerembedapi.link/api/source/{video_id}',
        f'https://playerembedapi.link/api/v1/source/{video_id}',
        f'https://playerembedapi.link/source/{video_id}',
        f'https://playerembedapi.link/embed/source/{video_id}',
        'https://iamcdn.net/api/source',
    ]
    
    for endpoint in endpoints:
        try:
            r3 = requests.get(endpoint, headers=HEADERS, timeout=10)
            print(f'   {endpoint}: {r3.status_code}')
            if r3.status_code == 200 and r3.text:
                print(f'      {r3.text[:100]}')
        except Exception as e:
            print(f'   {endpoint}: {e}')
    
    # 5. Analisar JWPlayer setup
    print('\n🎬 Analisando JWPlayer...')
    
    # Procurar por jwplayer setup
    jwsetup = re.search(r'jwplayer\([^)]+\)\.setup\((\{[\s\S]*?\})\s*\)', html)
    if jwsetup:
        setup_str = jwsetup.group(1)
        print(f'   Setup encontrado: {setup_str[:200]}...')
        
        # Procurar sources dentro do setup
        sources = re.search(r'sources\s*:\s*(\[[\s\S]*?\])', setup_str)
        if sources:
            print(f'   Sources: {sources.group(1)}')
    
    # 6. Procurar por variáveis globais
    print('\n🔍 Variáveis globais importantes...')
    
    global_vars = re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*([^;]{10,100});', html)
    for name, value in global_vars[:20]:
        if any(x in name.lower() for x in ['source', 'video', 'url', 'file', 'media', 'stream']):
            print(f'   {name} = {value[:80]}...')


def try_alternative_approach():
    """Tenta abordagem alternativa - simular o que o JS faz"""
    print('\n' + '='*70)
    print('🔄 Abordagem Alternativa')
    print('='*70)
    
    # Às vezes o player carrega sources via POST
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    
    # Tentar POST com dados
    print('\n📡 Tentando POST...')
    
    post_data = {
        'v': 'izD1HrKWL',
        'r': '',
    }
    
    try:
        r = requests.post(url, data=post_data, headers=HEADERS)
        print(f'   Status: {r.status_code}')
        print(f'   Response: {r.text[:200]}...')
    except Exception as e:
        print(f'   Erro: {e}')
    
    # Tentar com headers específicos
    print('\n📡 Tentando com X-Requested-With...')
    
    ajax_headers = {
        **HEADERS,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        r = requests.post(url, data=post_data, headers=ajax_headers)
        print(f'   Status: {r.status_code}')
        if r.text != html:
            print(f'   Response diferente! {r.text[:200]}...')
    except Exception as e:
        print(f'   Erro: {e}')


if __name__ == '__main__':
    analyze_playerembedapi()
    try_alternative_approach()
