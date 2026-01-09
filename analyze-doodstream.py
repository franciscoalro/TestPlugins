#!/usr/bin/env python3
"""
Analisar como Bysebuho/Doodstream gera o link m3u8
"""
import requests
import re
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': '*/*',
}

def analyze_doodstream(video_id):
    """Analisa o fluxo do Doodstream"""
    print(f'🔍 Analisando Bysebuho: {video_id}')
    
    # 1. Página principal
    url = f'https://bysebuho.com/e/{video_id}'
    print(f'\n1. Carregando: {url}')
    
    r = requests.get(url, headers={**HEADERS, 'Referer': url}, timeout=30)
    print(f'   Status: {r.status_code}')
    
    # Procurar padrões importantes
    print('\n2. Procurando padrões no HTML...')
    
    # pass_md5
    pass_match = re.search(r"'/pass_md5/([^']+)'", r.text)
    if pass_match:
        print(f'   ✅ pass_md5: /pass_md5/{pass_match.group(1)}')
    
    # Token
    token_match = re.search(r"token=([a-zA-Z0-9]+)", r.text)
    if token_match:
        print(f'   ✅ token: {token_match.group(1)}')
    
    # makePlay function
    makeplay = re.search(r'function\s+makePlay\s*\([^)]*\)\s*\{([^}]+)\}', r.text)
    if makeplay:
        print(f'   ✅ makePlay encontrado')
    
    # Procurar $.get ou fetch
    ajax_calls = re.findall(r"\$\.get\s*\(\s*['\"]([^'\"]+)['\"]", r.text)
    print(f'   Ajax calls: {ajax_calls}')
    
    # 3. Tentar API de detalhes
    print('\n3. API de detalhes...')
    api_url = f'https://bysebuho.com/api/videos/{video_id}/embed/details'
    r2 = requests.get(api_url, headers=HEADERS, timeout=30)
    if r2.status_code == 200:
        data = r2.json()
        print(f'   ✅ embed_frame_url: {data.get("embed_frame_url")}')
        embed_url = data.get('embed_frame_url')
        
        if embed_url:
            # 4. Carregar embed frame
            print(f'\n4. Carregando embed frame: {embed_url}')
            r3 = requests.get(embed_url, headers={**HEADERS, 'Referer': url}, timeout=30)
            print(f'   Status: {r3.status_code}')
            
            # Procurar pass_md5 no embed
            pass_match2 = re.search(r"'/pass_md5/([^']+)'", r3.text)
            if pass_match2:
                pass_path = f'/pass_md5/{pass_match2.group(1)}'
                print(f'   ✅ pass_md5: {pass_path}')
                
                # Extrair domínio
                domain = re.match(r'(https?://[^/]+)', embed_url).group(1)
                pass_url = domain + pass_path
                
                print(f'\n5. Chamando pass_md5: {pass_url}')
                r4 = requests.get(pass_url, headers={**HEADERS, 'Referer': embed_url}, timeout=30)
                print(f'   Status: {r4.status_code}')
                print(f'   Response: {r4.text[:200]}')
                
                if r4.text.startswith('http'):
                    # Procurar token
                    token_match2 = re.search(r"'([a-zA-Z0-9]{10,})'", r3.text)
                    if token_match2:
                        token = token_match2.group(1)
                        expiry = int(time.time() * 1000)
                        video_url = f'{r4.text.strip()}?token={token}&expiry={expiry}'
                        print(f'\n✅ VIDEO URL: {video_url}')
                        return video_url

    return None

if __name__ == '__main__':
    result = analyze_doodstream('cnox47bzdraa')
    
    if result:
        print(f'\n{"="*60}')
        print('SUCESSO!')
        print(f'URL: {result}')
    else:
        print('\nNão foi possível extrair via requests simples')
        print('O site requer JavaScript para gerar o token')
