#!/usr/bin/env python3
"""
Engenharia reversa do MegaEmbed e PlayerEmbedAPI
"""

import requests
import re
import json
import base64
from urllib.parse import unquote, urlparse, parse_qs

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def analyze_megaembed(url):
    """Analisa MegaEmbed"""
    print(f'\n{"="*70}')
    print(f'🔍 MEGAEMBED: {url}')
    print('='*70)
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        html = r.text
        
        # Salvar HTML
        with open('megaembed_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'📄 HTML salvo ({len(html)} chars)')
        
        # 1. Procurar scripts inline
        print('\n📜 Scripts inline:')
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(scripts):
            if len(script.strip()) > 50:
                print(f'\n  Script {i+1} ({len(script)} chars):')
                print(f'  {script[:200]}...')
        
        # 2. Procurar por eval/packed
        print('\n📦 Procurando eval/packed...')
        if 'eval(' in html:
            print('  ✅ eval() encontrado!')
            eval_match = re.search(r"eval\((.*?)\)\s*;?\s*(?:</script>|$)", html, re.DOTALL)
            if eval_match:
                print(f'  Conteúdo: {eval_match.group(1)[:100]}...')
        
        # 3. Procurar por atob (base64)
        print('\n🔐 Procurando base64/atob...')
        atob_matches = re.findall(r'atob\(["\']([^"\']+)["\']\)', html)
        for match in atob_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8')
                print(f'  ✅ atob decodificado: {decoded[:100]}...')
            except:
                print(f'  ⚠️ atob encontrado mas não decodificável: {match[:50]}...')
        
        # 4. Procurar por JSON embutido
        print('\n📊 Procurando JSON...')
        json_matches = re.findall(r'JSON\.parse\(["\']([^"\']+)["\']\)', html)
        for match in json_matches:
            try:
                data = json.loads(match.replace('\\"', '"'))
                print(f'  ✅ JSON: {data}')
            except:
                pass
        
        # 5. Procurar por URLs de vídeo
        print('\n🎬 Procurando URLs de vídeo...')
        video_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'source\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
        ]
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f'  Padrão {pattern[:30]}...: {matches[:3]}')
        
        # 6. Procurar por API endpoints
        print('\n🌐 Procurando API endpoints...')
        api_patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'\$\.get\(["\']([^"\']+)["\']',
            r'\$\.post\(["\']([^"\']+)["\']',
            r'axios\.[a-z]+\(["\']([^"\']+)["\']',
            r'XMLHttpRequest.*?open\(["\'][A-Z]+["\']\s*,\s*["\']([^"\']+)["\']',
        ]
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f'  ✅ API: {matches}')
        
        # 7. Extrair ID do vídeo
        print('\n🔑 Extraindo ID do vídeo...')
        # megaembed.link/#xxxxx
        video_id = url.split('#')[-1] if '#' in url else url.split('/')[-1]
        print(f'  ID: {video_id}')
        
        # 8. Tentar API conhecida
        print('\n📡 Tentando APIs conhecidas...')
        apis_to_try = [
            f'https://megaembed.link/api/v1/video?id={video_id}',
            f'https://megaembed.link/api/source/{video_id}',
            f'https://megaembed.link/ajax/embed/{video_id}',
        ]
        for api in apis_to_try:
            try:
                r2 = requests.get(api, headers={**HEADERS, 'Referer': url}, timeout=10)
                print(f'  {api}: {r2.status_code}')
                if r2.status_code == 200 and r2.text:
                    print(f'    Resposta: {r2.text[:200]}')
            except Exception as e:
                print(f'  {api}: Erro - {e}')
        
        return html
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return None


def analyze_playerembedapi(url):
    """Analisa PlayerEmbedAPI"""
    print(f'\n{"="*70}')
    print(f'🔍 PLAYEREMBEDAPI: {url}')
    print('='*70)
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        html = r.text
        
        # Salvar HTML
        with open('playerembedapi_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'📄 HTML salvo ({len(html)} chars)')
        
        # 1. Extrair parâmetro v
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        video_id = params.get('v', [''])[0]
        print(f'🔑 Video ID: {video_id}')
        
        # 2. Procurar scripts
        print('\n📜 Analisando scripts...')
        scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html)
        print(f'  Scripts externos: {scripts}')
        
        inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(inline_scripts):
            if len(script.strip()) > 100:
                print(f'\n  Script inline {i+1}:')
                print(f'  {script[:300]}...')
        
        # 3. Procurar por funções de decodificação
        print('\n🔐 Procurando funções de decodificação...')
        decode_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*\{[^}]*(?:atob|btoa|decode|decrypt)',
            r'(\w+)\s*=\s*function\s*\([^)]*\)\s*\{[^}]*(?:atob|btoa|decode|decrypt)',
        ]
        for pattern in decode_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f'  ✅ Função encontrada: {matches}')
        
        # 4. Procurar por variáveis com dados
        print('\n📊 Procurando variáveis de dados...')
        var_patterns = [
            r'var\s+(\w+)\s*=\s*["\']([^"\']{20,})["\']',
            r'let\s+(\w+)\s*=\s*["\']([^"\']{20,})["\']',
            r'const\s+(\w+)\s*=\s*["\']([^"\']{20,})["\']',
        ]
        for pattern in var_patterns:
            matches = re.findall(pattern, html)
            for name, value in matches[:5]:
                print(f'  {name}: {value[:50]}...')
                # Tentar decodificar base64
                try:
                    decoded = base64.b64decode(value).decode('utf-8')
                    print(f'    → Base64 decodificado: {decoded[:100]}')
                except:
                    pass
        
        # 5. Procurar por iframes
        print('\n🖼️ Iframes:')
        iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
        for iframe in iframes:
            print(f'  {iframe}')
        
        # 6. Tentar APIs
        print('\n📡 Tentando APIs...')
        apis = [
            f'https://playerembedapi.link/api/source?v={video_id}',
            f'https://playerembedapi.link/api/video/{video_id}',
            f'https://playerembedapi.link/embed/{video_id}',
        ]
        for api in apis:
            try:
                r2 = requests.get(api, headers={**HEADERS, 'Referer': url}, timeout=10)
                print(f'  {api}: {r2.status_code}')
                if r2.status_code == 200:
                    print(f'    {r2.text[:200]}')
            except Exception as e:
                print(f'  {api}: {e}')
        
        return html
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()
        return None


def main():
    # URLs de teste
    megaembed_urls = [
        'https://megaembed.link/#rckhv6',
        'https://megaembed.link/#gsbqjz',
    ]
    
    playerembedapi_urls = [
        'https://playerembedapi.link/?v=izD1HrKWL',
        'https://playerembedapi.link/?v=o_4s_DFJuL',
    ]
    
    print('\n' + '='*70)
    print('🔬 ENGENHARIA REVERSA - MEGAEMBED & PLAYEREMBEDAPI')
    print('='*70)
    
    # Analisar MegaEmbed
    for url in megaembed_urls[:1]:
        analyze_megaembed(url)
    
    # Analisar PlayerEmbedAPI
    for url in playerembedapi_urls[:1]:
        analyze_playerembedapi(url)


if __name__ == '__main__':
    main()
