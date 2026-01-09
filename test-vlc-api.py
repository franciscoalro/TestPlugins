#!/usr/bin/env python3
"""
Teste usando APIs descobertas
"""
import requests
import re
import subprocess
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def try_bysebuho_api(video_id):
    """Tenta API do Bysebuho"""
    print(f'\n🔍 Bysebuho API para: {video_id}')
    
    # API descoberta
    api_url = f'https://bysebuho.com/api/videos/{video_id}/embed/details'
    
    headers = {
        **HEADERS,
        'Referer': f'https://bysebuho.com/e/{video_id}',
        'Origin': 'https://bysebuho.com',
    }
    
    try:
        r = requests.get(api_url, headers=headers, timeout=30)
        print(f'  Status: {r.status_code}')
        
        if r.status_code == 200:
            data = r.json()
            print(f'  Response: {json.dumps(data, indent=2)[:500]}')
            
            # Procurar URL de vídeo
            if 'result' in data:
                result = data['result']
                if isinstance(result, dict):
                    for key in ['url', 'file', 'source', 'video', 'stream']:
                        if key in result:
                            print(f'✅ {key}: {result[key]}')
                            return result[key]
            
            # Procurar em qualquer lugar
            text = json.dumps(data)
            patterns = [
                r'"([^"]+\.m3u8[^"]*)"',
                r'"([^"]+\.mp4[^"]*)"',
            ]
            for p in patterns:
                matches = re.findall(p, text)
                for m in matches:
                    if m.startswith('http'):
                        print(f'✅ Encontrado: {m}')
                        return m
                        
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_bysebuho_direct(video_id):
    """Tenta método direto Bysebuho/Doodstream"""
    print(f'\n🔍 Bysebuho direto: {video_id}')
    
    url = f'https://bysebuho.com/e/{video_id}'
    
    headers = {
        **HEADERS,
        'Referer': url,
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        
        # Procurar pass_md5
        match = re.search(r"\$\.get\('(/pass_md5/[^']+)'", r.text)
        if not match:
            match = re.search(r"'/pass_md5/([^']+)'", r.text)
        
        if match:
            pass_path = match.group(1) if match.group(1).startswith('/') else '/pass_md5/' + match.group(1)
            pass_url = 'https://bysebuho.com' + pass_path
            print(f'  Pass URL: {pass_url}')
            
            r2 = requests.get(pass_url, headers=headers, timeout=30)
            print(f'  Pass Status: {r2.status_code}')
            print(f'  Pass Response: {r2.text[:200]}')
            
            if r2.status_code == 200 and r2.text.startswith('http'):
                # Construir URL final
                base = r2.text.strip()
                
                # Procurar makePlay ou token
                token_match = re.search(r"makePlay\([^)]*'([^']+)'", r.text)
                if token_match:
                    token = token_match.group(1)
                    video_url = f'{base}{token}?token={token}&expiry={int(__import__("time").time() * 1000)}'
                    print(f'✅ URL: {video_url[:100]}...')
                    return video_url
                else:
                    # Tentar sem token
                    video_url = base
                    print(f'✅ URL base: {video_url}')
                    return video_url
        
        # Procurar direto no HTML
        patterns = [
            r'source\s*:\s*["\']([^"\']+)["\']',
            r'file\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for p in patterns:
            matches = re.findall(p, r.text)
            for m in matches:
                if '.m3u8' in m or '.mp4' in m:
                    print(f'✅ Encontrado: {m}')
                    return m
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    
    return None

def try_megaembed_api(video_id):
    """Tenta API do MegaEmbed"""
    print(f'\n🔍 MegaEmbed API para: {video_id}')
    
    headers = {
        **HEADERS,
        'Referer': 'https://megaembed.link/',
        'Origin': 'https://megaembed.link',
    }
    
    # Tentar diferentes endpoints
    endpoints = [
        f'https://megaembed.link/api/v1/video?id={video_id}&w=1920&h=1080&r=playerthree.online',
        f'https://megaembed.link/api/v1/info?id={video_id}',
        f'https://megaembed.link/api/source/{video_id}',
    ]
    
    for api_url in endpoints:
        try:
            print(f'  Tentando: {api_url}')
            r = requests.get(api_url, headers=headers, timeout=30)
            print(f'  Status: {r.status_code}')
            
            if r.status_code == 200:
                print(f'  Response: {r.text[:300]}')
                
                # Procurar URL
                patterns = [
                    r'"url"\s*:\s*"([^"]+)"',
                    r'"file"\s*:\s*"([^"]+)"',
                    r'"source"\s*:\s*"([^"]+)"',
                    r'([^"\']+\.m3u8[^"\']*)',
                ]
                
                for p in patterns:
                    matches = re.findall(p, r.text)
                    for m in matches:
                        if m.startswith('http') and ('m3u8' in m or 'mp4' in m):
                            print(f'✅ Encontrado: {m}')
                            return m
                            
        except Exception as e:
            print(f'  Erro: {e}')
    
    return None

def play_in_vlc(video_url, referer=None):
    """Reproduz no VLC"""
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
    except Exception as e:
        print(f'❌ Erro VLC: {e}')
        print(f'\n📋 Copie a URL: {video_url}')
        return False

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC (APIs)')
    print('=' * 60)
    
    video_url = None
    
    # Tentar Bysebuho
    video_url = try_bysebuho_api('cnox47bzdraa')
    
    if not video_url:
        video_url = try_bysebuho_direct('cnox47bzdraa')
    
    if not video_url:
        video_url = try_megaembed_api('rckhv6')
    
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        play_in_vlc(video_url, 'https://bysebuho.com/')
    else:
        print('❌ Não foi possível extrair link direto')
        print('\nOs players usam proteção avançada contra scraping.')
        print('Seria necessário executar JavaScript completo.')
    print('=' * 60)

if __name__ == '__main__':
    main()
