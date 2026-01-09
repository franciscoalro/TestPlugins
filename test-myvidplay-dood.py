#!/usr/bin/env python3
"""
Extração do MyVidPlay usando padrão DoodStream
"""

import requests
import re
import time
import random
import string

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def make_play():
    """Gera token aleatório como o JavaScript faz"""
    chars = string.ascii_letters + string.digits
    token = ''.join(random.choice(chars) for _ in range(10))
    return token

def extract_doodstream(url):
    """Extrai vídeo do DoodStream/MyVidPlay"""
    print(f'\n{"="*60}')
    print(f'🔍 Extraindo DoodStream: {url}')
    print('='*60)
    
    try:
        # 1. Obter página do player
        r = requests.get(url, headers=HEADERS, timeout=30)
        print(f'Status: {r.status_code}')
        
        html = r.text
        
        # 2. Extrair URL do pass_md5
        # Padrão: $.get('/pass_md5/...'
        pass_md5_match = re.search(r"\$\.get\(['\"](/pass_md5/[^'\"]+)['\"]", html)
        
        if not pass_md5_match:
            print('❌ Não encontrou pass_md5')
            # Tentar padrão alternativo
            pass_md5_match = re.search(r"pass_md5/([^'\"]+)", html)
            if pass_md5_match:
                pass_md5_path = '/pass_md5/' + pass_md5_match.group(1)
            else:
                return None
        else:
            pass_md5_path = pass_md5_match.group(1)
        
        print(f'✅ pass_md5 encontrado: {pass_md5_path}')
        
        # 3. Extrair token do makePlay
        token_match = re.search(r"token=([a-zA-Z0-9]+)", html)
        token = token_match.group(1) if token_match else make_play()
        print(f'✅ Token: {token}')
        
        # 4. Determinar domínio base
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # 5. Fazer request para pass_md5
        pass_url = base_url + pass_md5_path
        print(f'\n📡 Requisitando: {pass_url}')
        
        pass_headers = {
            **HEADERS,
            'Referer': url,
        }
        
        r2 = requests.get(pass_url, headers=pass_headers, timeout=30)
        print(f'Status: {r2.status_code}')
        print(f'Resposta: {r2.text[:200]}...')
        
        if r2.status_code != 200:
            print('❌ Erro ao obter pass_md5')
            return None
        
        # 6. Construir URL final do vídeo
        video_base = r2.text.strip()
        
        # Gerar token aleatório como makePlay() faz
        random_token = make_play()
        expiry = int(time.time() * 1000)
        
        video_url = f"{video_base}{random_token}?token={token}&expiry={expiry}"
        
        print(f'\n🎬 URL do vídeo:')
        print(f'   {video_url}')
        
        # 7. Testar se o vídeo é acessível
        print(f'\n🔍 Testando acesso ao vídeo...')
        
        video_headers = {
            **HEADERS,
            'Referer': url,
            'Range': 'bytes=0-1024',
        }
        
        r3 = requests.get(video_url, headers=video_headers, timeout=30, stream=True)
        print(f'Status: {r3.status_code}')
        print(f'Content-Type: {r3.headers.get("Content-Type", "N/A")}')
        print(f'Content-Length: {r3.headers.get("Content-Length", "N/A")}')
        
        if r3.status_code in [200, 206]:
            print('\n✅ SUCESSO! Vídeo acessível!')
            return video_url
        else:
            print('\n❌ Vídeo não acessível')
            return None
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return None


def main():
    urls = [
        'https://myvidplay.com/e/kieb85xhpkf3',
        'https://myvidplay.com/e/lsp5ozsw6zc9',
    ]
    
    results = []
    for url in urls:
        video_url = extract_doodstream(url)
        results.append({
            'source': url,
            'video': video_url,
            'success': video_url is not None
        })
    
    print('\n' + '='*60)
    print('📊 RESUMO')
    print('='*60)
    for r in results:
        status = '✅' if r['success'] else '❌'
        print(f"{status} {r['source']}")
        if r['video']:
            print(f"   → {r['video'][:80]}...")


if __name__ == '__main__':
    main()
