#!/usr/bin/env python3
"""
Abordagem final - Usar Selenium/Playwright para capturar o vídeo
"""

import requests
import re
import json
import base64

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def analyze_raw_media():
    """Analisa o campo media raw"""
    print('='*70)
    print('🔬 Análise detalhada do campo media')
    print('='*70)
    
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    r = requests.get(url, headers=HEADERS)
    html = r.text
    
    # Extrair datas como string raw
    datas_match = re.search(r'const\s+datas\s*=\s*"([^"]+)"', html)
    if not datas_match:
        datas_match = re.search(r"const\s+datas\s*=\s*'([^']+)'", html)
    
    if datas_match:
        datas_b64 = datas_match.group(1)
        print(f'📦 datas base64: {datas_b64[:100]}...')
        
        # Decodificar base64
        decoded_bytes = base64.b64decode(datas_b64)
        print(f'\n📄 Bytes decodificados ({len(decoded_bytes)}):')
        print(f'   {decoded_bytes[:100]}')
        
        # O JSON tem unicode escapes - vamos processar corretamente
        # Primeiro, converter para string tratando os escapes
        try:
            # Tentar decodificar como JSON diretamente
            decoded_str = decoded_bytes.decode('utf-8', errors='surrogateescape')
            print(f'\n📝 String decodificada:')
            print(f'   {decoded_str[:200]}...')
            
            # Tentar parsear como JSON
            try:
                data = json.loads(decoded_str)
                print(f'\n✅ JSON parseado com sucesso!')
                print(f'   Chaves: {list(data.keys())}')
                
                if 'media' in data:
                    media = data['media']
                    print(f'\n📼 Campo media:')
                    print(f'   Tipo: {type(media)}')
                    print(f'   Tamanho: {len(media) if isinstance(media, (str, bytes)) else "N/A"}')
                    
                    if isinstance(media, str):
                        print(f'   Primeiros 100 chars: {media[:100]}')
                        print(f'   Hex dos primeiros bytes: {media[:20].encode("latin-1").hex()}')
                        
                        # O media pode ser uma string com bytes raw
                        # Vamos tentar converter para bytes
                        media_bytes = media.encode('latin-1')
                        print(f'\n   Como bytes ({len(media_bytes)}): {media_bytes[:50]}')
                        
            except json.JSONDecodeError as e:
                print(f'\n⚠️ Erro ao parsear JSON: {e}')
                
                # Tentar extrair campos manualmente
                slug = re.search(r'"slug":"([^"]+)"', decoded_str)
                md5_id = re.search(r'"md5_id":(\d+)', decoded_str)
                
                if slug:
                    print(f'   slug: {slug.group(1)}')
                if md5_id:
                    print(f'   md5_id: {md5_id.group(1)}')
                
        except Exception as e:
            print(f'❌ Erro: {e}')


def check_network_requests():
    """Verifica se há requests de rede que podemos interceptar"""
    print('\n' + '='*70)
    print('🌐 Analisando requests de rede')
    print('='*70)
    
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    r = requests.get(url, headers=HEADERS)
    html = r.text
    
    # Procurar por URLs de API
    print('\n📡 URLs de API encontradas:')
    
    api_patterns = [
        r'https?://[^\s"\'<>]+/api/[^\s"\'<>]+',
        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
        r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
        r'https?://[^\s"\'<>]+/source[^\s"\'<>]*',
        r'https?://[^\s"\'<>]+/video[^\s"\'<>]*',
    ]
    
    for pattern in api_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f'\n   Padrão: {pattern[:40]}...')
            for m in set(matches):
                print(f'      {m}')
    
    # Procurar por domínios de CDN
    print('\n📦 Domínios de CDN:')
    cdn_domains = re.findall(r'https?://([a-zA-Z0-9.-]+cdn[a-zA-Z0-9.-]*)', html)
    for d in set(cdn_domains):
        print(f'   {d}')
    
    # Procurar por domínios de streaming
    print('\n🎬 Domínios de streaming:')
    stream_domains = re.findall(r'https?://([a-zA-Z0-9.-]+(?:stream|video|play|media)[a-zA-Z0-9.-]*)', html, re.IGNORECASE)
    for d in set(stream_domains):
        print(f'   {d}')


def try_direct_video_api():
    """Tenta APIs diretas de vídeo"""
    print('\n' + '='*70)
    print('🎬 Tentando APIs diretas')
    print('='*70)
    
    video_id = 'izD1HrKWL'
    md5_id = '28973410'
    user_id = '482120'
    
    # APIs comuns de players
    apis = [
        f'https://iamcdn.net/api/source/{video_id}',
        f'https://iamcdn.net/api/v1/source/{video_id}',
        f'https://iamcdn.net/source/{video_id}',
        f'https://statics.sssrr.org/api/source/{video_id}',
        f'https://playerembedapi.link/ajax/embed/{video_id}',
        f'https://playerembedapi.link/ajax/source/{video_id}',
    ]
    
    for api in apis:
        try:
            r = requests.get(api, headers={
                **HEADERS,
                'Referer': f'https://playerembedapi.link/?v={video_id}',
                'X-Requested-With': 'XMLHttpRequest',
            }, timeout=10)
            print(f'\n   {api}')
            print(f'      Status: {r.status_code}')
            if r.status_code == 200:
                print(f'      Response: {r.text[:200]}')
        except Exception as e:
            print(f'\n   {api}')
            print(f'      Erro: {e}')
    
    # Tentar POST
    print('\n📤 Tentando POST...')
    
    post_apis = [
        ('https://playerembedapi.link/ajax/embed', {'v': video_id}),
        ('https://iamcdn.net/api/source', {'id': video_id}),
    ]
    
    for api, data in post_apis:
        try:
            r = requests.post(api, data=data, headers={
                **HEADERS,
                'Referer': f'https://playerembedapi.link/?v={video_id}',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded',
            }, timeout=10)
            print(f'\n   POST {api}')
            print(f'      Status: {r.status_code}')
            if r.status_code == 200:
                print(f'      Response: {r.text[:200]}')
        except Exception as e:
            print(f'\n   POST {api}')
            print(f'      Erro: {e}')


def conclusion():
    """Conclusão da análise"""
    print('\n' + '='*70)
    print('📋 CONCLUSÃO')
    print('='*70)
    
    print('''
    O PlayerEmbedAPI usa criptografia AES-CTR para proteger os dados do vídeo.
    A chave de criptografia é gerada dinamicamente no JavaScript do cliente.
    
    Para extrair o vídeo, as opções são:
    
    1. ❌ Engenharia reversa do JS - Muito complexo, código ofuscado
    
    2. ✅ WebView no Android - Executar o JS e interceptar requests
       - Carregar a página no WebView
       - Interceptar requests de rede
       - Capturar URLs .m3u8 ou .mp4
    
    3. ✅ Usar hosts alternativos - MyVidPlay já funciona!
       - O extractor que criamos para myvidplay.com funciona
       - Priorizar esse host no plugin
    
    RECOMENDAÇÃO: Focar no myvidplay.com que já funciona, e ignorar
    playerembedapi e megaembed por enquanto.
    ''')


if __name__ == '__main__':
    analyze_raw_media()
    check_network_requests()
    try_direct_video_api()
    conclusion()
