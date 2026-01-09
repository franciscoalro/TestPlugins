#!/usr/bin/env python3
"""
Técnicas avançadas para extrair vídeo do MaxSeries
"""
import requests
import re
import subprocess
import base64
import json
from urllib.parse import unquote, urlparse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
}

def unpack_js(packed):
    """Desofusca JavaScript packed (p,a,c,k,e,d)"""
    try:
        # Extrair parâmetros do eval
        match = re.search(r"}\('(.+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)", packed, re.DOTALL)
        if not match:
            return None
        
        payload, radix, count, symbols = match.groups()
        radix = int(radix)
        count = int(count)
        symbols = symbols.split('|')
        
        # Função para converter base
        def base_convert(num, base):
            chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            result = ''
            while num > 0:
                result = chars[num % base] + result
                num //= base
            return result or '0'
        
        # Substituir símbolos
        def replacer(match):
            word = match.group(0)
            try:
                index = int(word, radix) if radix <= 36 else int(word)
                return symbols[index] if index < len(symbols) and symbols[index] else word
            except:
                return word
        
        unpacked = re.sub(r'\b\w+\b', replacer, payload)
        return unpacked
    except Exception as e:
        print(f'  Erro unpack: {e}')
        return None

def try_doodstream_technique(video_id):
    """Técnica específica para Doodstream/Bysebuho"""
    print(f'\n🔍 Técnica Doodstream: {video_id}')
    
    url = f'https://bysebuho.com/e/{video_id}'
    
    session = requests.Session()
    
    headers = {
        **HEADERS,
        'Referer': url,
    }
    
    try:
        r = session.get(url, headers=headers, timeout=30)
        
        # Procurar pass_md5 com diferentes padrões
        patterns = [
            r"\$\.get\('(/pass_md5/[^']+)'",
            r"'/pass_md5/([^']+)'",
            r'pass_md5/([a-zA-Z0-9/]+)',
        ]
        
        pass_path = None
        for p in patterns:
            match = re.search(p, r.text)
            if match:
                path = match.group(1)
                pass_path = path if path.startswith('/') else '/pass_md5/' + path
                break
        
        if pass_path:
            print(f'  Pass path: {pass_path}')
            
            pass_url = 'https://bysebuho.com' + pass_path
            r2 = session.get(pass_url, headers=headers, timeout=30)
            
            if r2.status_code == 200 and r2.text:
                base_url = r2.text.strip()
                print(f'  Base URL: {base_url[:80]}')
                
                # Procurar token no HTML original
                token_patterns = [
                    r"token=([a-zA-Z0-9]+)",
                    r"makePlay\([^)]*'([^']+)'",
                    r"'([a-zA-Z0-9]{10,})'",
                ]
                
                for tp in token_patterns:
                    tokens = re.findall(tp, r.text)
                    for token in tokens:
                        if len(token) > 5:
                            # Construir URL final
                            import time
                            video_url = f"{base_url}?token={token}&expiry={int(time.time()*1000)}"
                            print(f'✅ URL: {video_url[:100]}')
                            return video_url
                
                # Tentar sem token
                return base_url
        
        # Procurar em script packed
        packed = re.search(r"eval\(function\(p,a,c,k,e,d\).*?\)\)", r.text, re.DOTALL)
        if packed:
            print('  Encontrado JS packed, desofuscando...')
            unpacked = unpack_js(packed.group(0))
            if unpacked:
                # Procurar URL no código desofuscado
                urls = re.findall(r'https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*', unpacked)
                if urls:
                    print(f'✅ URL do packed: {urls[0][:100]}')
                    return urls[0]
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_filemoon_technique(url):
    """Técnica para Filemoon e similares"""
    print(f'\n🔍 Técnica Filemoon: {url[:60]}')
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        
        # Procurar eval packed
        packed_match = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('([^']+)',\s*(\d+),\s*(\d+),\s*'([^']+)'", r.text, re.DOTALL)
        
        if packed_match:
            print('  JS packed encontrado')
            
            # Tentar desofuscar
            p, a, c, k = packed_match.groups()
            a, c = int(a), int(c)
            k = k.split('|')
            
            def e(c_val):
                first = '' if c_val < a else e(c_val // a)
                c_val = c_val % a
                if c_val > 35:
                    second = chr(c_val + 29)
                else:
                    second = '0123456789abcdefghijklmnopqrstuvwxyz'[c_val]
                return first + second
            
            # Substituir
            for i in range(c - 1, -1, -1):
                if k[i]:
                    p = re.sub(r'\b' + e(i) + r'\b', k[i], p)
            
            # Procurar sources
            sources = re.findall(r'file\s*:\s*"([^"]+)"', p)
            if sources:
                print(f'✅ Source: {sources[0][:100]}')
                return sources[0]
            
            sources = re.findall(r'sources\s*:\s*\[\{[^}]*file\s*:\s*"([^"]+)"', p)
            if sources:
                print(f'✅ Source: {sources[0][:100]}')
                return sources[0]
                
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_jwplayer_technique(url):
    """Técnica para JWPlayer"""
    print(f'\n🔍 Técnica JWPlayer: {url[:60]}')
    
    try:
        r = requests.get(url, headers={**HEADERS, 'Referer': url}, timeout=30)
        
        # Padrões JWPlayer
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'sources\s*:\s*\[\s*\{\s*file\s*:\s*["\']([^"\']+)["\']',
            r'"file"\s*:\s*"([^"]+)"',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        
        for p in patterns:
            matches = re.findall(p, r.text)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ JWPlayer: {m[:100]}')
                    return m
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_hls_extraction(url):
    """Tenta extrair HLS de qualquer player"""
    print(f'\n🔍 Técnica HLS genérica: {url[:60]}')
    
    try:
        r = requests.get(url, headers={**HEADERS, 'Referer': url}, timeout=30)
        
        # Procurar qualquer m3u8
        m3u8_urls = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', r.text)
        
        for m in m3u8_urls:
            # Limpar URL
            m = m.split('"')[0].split("'")[0].split('<')[0]
            if 'logo' not in m.lower() and 'thumb' not in m.lower():
                print(f'✅ HLS: {m[:100]}')
                return m
        
        # Procurar mp4
        mp4_urls = re.findall(r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*', r.text)
        for m in mp4_urls:
            m = m.split('"')[0].split("'")[0].split('<')[0]
            if 'logo' not in m.lower() and 'thumb' not in m.lower():
                print(f'✅ MP4: {m[:100]}')
                return m
                
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_api_bruteforce(video_id, domain):
    """Tenta diferentes endpoints de API"""
    print(f'\n🔍 Bruteforce API: {domain}/{video_id}')
    
    endpoints = [
        f'https://{domain}/api/source/{video_id}',
        f'https://{domain}/api/video/{video_id}',
        f'https://{domain}/api/v1/video?id={video_id}',
        f'https://{domain}/api/v1/source?id={video_id}',
        f'https://{domain}/dl/{video_id}',
        f'https://{domain}/download/{video_id}',
        f'https://{domain}/stream/{video_id}',
        f'https://{domain}/embed/api/{video_id}',
    ]
    
    for endpoint in endpoints:
        try:
            r = requests.get(endpoint, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                print(f'  {endpoint}: {r.status_code}')
                
                # Procurar URL no response
                urls = re.findall(r'https?://[^\s"\'<>]+\.(?:m3u8|mp4)[^\s"\'<>]*', r.text)
                if urls:
                    print(f'✅ API: {urls[0][:100]}')
                    return urls[0]
                    
                # Tentar JSON
                try:
                    data = r.json()
                    for key in ['url', 'file', 'source', 'src', 'video', 'stream']:
                        if key in data:
                            print(f'✅ JSON {key}: {data[key][:100]}')
                            return data[key]
                except:
                    pass
        except:
            pass
    
    return None

def try_redirect_follow(url):
    """Segue redirects para encontrar URL final"""
    print(f'\n🔍 Seguindo redirects: {url[:60]}')
    
    try:
        r = requests.head(url, headers=HEADERS, timeout=30, allow_redirects=True)
        final_url = r.url
        
        if final_url != url:
            print(f'  Redirect: {final_url[:80]}')
            
            if '.m3u8' in final_url or '.mp4' in final_url:
                print(f'✅ Final: {final_url[:100]}')
                return final_url
                
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
    print(f'\n🎬 Abrindo VLC...')
    print(f'URL: {video_url}')
    
    vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
    
    try:
        cmd = [vlc_path, video_url]
        if referer:
            cmd.extend(['--http-referrer', referer])
        subprocess.Popen(cmd)
        print('✅ VLC aberto!')
        return True
    except:
        print(f'📋 Copie: {video_url}')
        return False

def main():
    print('=' * 60)
    print('🎬 TESTE AVANÇADO MaxSeries → VLC')
    print('=' * 60)
    
    # Players encontrados
    players = [
        {'name': 'Bysebuho', 'url': 'https://bysebuho.com/e/cnox47bzdraa', 'id': 'cnox47bzdraa'},
        {'name': 'MegaEmbed', 'url': 'https://megaembed.link/#rckhv6', 'id': 'rckhv6'},
        {'name': 'PlayerEmbedAPI', 'url': 'https://playerembedapi.link/?v=o_4s_DFJuL', 'id': 'o_4s_DFJuL'},
        {'name': 'G9R6', 'url': 'https://g9r6.com/3buub/cnox47bzdraa', 'id': 'cnox47bzdraa'},
    ]
    
    video_url = None
    
    for player in players:
        print(f'\n{"="*60}')
        print(f'🎯 Testando: {player["name"]}')
        print('='*60)
        
        # Técnica 1: Doodstream específico
        if 'bysebuho' in player['url'] or 'dood' in player['url']:
            video_url = try_doodstream_technique(player['id'])
            if video_url:
                break
        
        # Técnica 2: Filemoon
        video_url = try_filemoon_technique(player['url'])
        if video_url:
            break
        
        # Técnica 3: JWPlayer
        video_url = try_jwplayer_technique(player['url'])
        if video_url:
            break
        
        # Técnica 4: HLS genérico
        video_url = try_hls_extraction(player['url'])
        if video_url:
            break
        
        # Técnica 5: API bruteforce
        domain = urlparse(player['url']).netloc
        video_url = try_api_bruteforce(player['id'], domain)
        if video_url:
            break
        
        # Técnica 6: Redirect
        video_url = try_redirect_follow(player['url'])
        if video_url:
            break
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        play_in_vlc(video_url, players[0]['url'])
    else:
        print('❌ Nenhuma técnica funcionou')
        print('\nOs players usam proteção muito avançada.')
    print('=' * 60)

if __name__ == '__main__':
    main()
