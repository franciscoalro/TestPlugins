#!/usr/bin/env python3
"""
Teste final de extração de links do MaxSeries para VLC
"""
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def extract_from_bysebuho(url):
    """Extrai vídeo do Bysebuho/Doodstream"""
    print(f'\n🔍 Tentando Bysebuho: {url}')
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        
        # Procurar padrões de vídeo
        patterns = [
            r"dsplayer\.hotkeys[^;how]+?source:\s*'([^']+)'",
            r"source\s*:\s*'([^']+\.m3u8[^']*)'",
            r"file\s*:\s*'([^']+\.m3u8[^']*)'",
            r"'([^']+\.m3u8[^']*)'",
            r'"([^"]+\.m3u8[^"]*)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, r.text)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Encontrado: {m[:80]}...')
                    return m
        
        # Doodstream específico
        if 'dood' in url.lower() or 'bysebuho' in url.lower():
            # Procurar token
            token_match = re.search(r"'(/pass_md5/[^']+)'", r.text)
            if token_match:
                token_url = 'https://bysebuho.com' + token_match.group(1)
                print(f'  Token URL: {token_url}')
                
                r2 = requests.get(token_url, headers={**HEADERS, 'Referer': url}, timeout=30)
                if r2.status_code == 200:
                    # Construir URL final
                    video_url = r2.text + '?token=' + token_match.group(1).split('/')[-1]
                    print(f'✅ Dood URL: {video_url[:80]}...')
                    return video_url
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    return None

def extract_from_megaembed(url):
    """Extrai vídeo do MegaEmbed usando API"""
    print(f'\n🔍 Tentando MegaEmbed: {url}')
    try:
        # Extrair ID
        id_match = re.search(r'#([a-zA-Z0-9]+)', url)
        if not id_match:
            id_match = re.search(r'/([a-zA-Z0-9]+)$', url)
        
        if not id_match:
            print('❌ ID não encontrado')
            return None
            
        mega_id = id_match.group(1)
        print(f'  ID: {mega_id}')
        
        # Tentar API de info primeiro
        info_url = f'https://megaembed.link/api/v1/info?id={mega_id}'
        print(f'  Info API: {info_url}')
        
        api_headers = {
            **HEADERS,
            'Referer': 'https://megaembed.link/',
            'Origin': 'https://megaembed.link'
        }
        
        r = requests.get(info_url, headers=api_headers, timeout=30)
        print(f'  Info Status: {r.status_code}')
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f'  Info: {json.dumps(data)[:200]}')
            except:
                pass
        
        # Tentar API de vídeo
        video_url = f'https://megaembed.link/api/v1/video?id={mega_id}&w=1920&h=1080&r=playerthree.online'
        print(f'  Video API: {video_url}')
        
        r2 = requests.get(video_url, headers=api_headers, timeout=30)
        print(f'  Video Status: {r2.status_code}')
        
        if r2.status_code == 200:
            # Procurar URL no response
            patterns = [
                r'"url"\s*:\s*"([^"]+)"',
                r'"file"\s*:\s*"([^"]+)"',
                r'"source"\s*:\s*"([^"]+)"',
                r'([^"\']+\.m3u8[^"\']*)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, r2.text)
                for m in matches:
                    if 'm3u8' in m or 'mp4' in m:
                        print(f'✅ Encontrado: {m[:80]}...')
                        return m
        
        # Tentar carregar página diretamente
        print('  Tentando página direta...')
        r3 = requests.get(url.replace('#', '/'), headers=api_headers, timeout=30)
        
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, r3.text)
            for m in matches:
                if m.startswith('http'):
                    print(f'✅ Encontrado: {m[:80]}...')
                    return m
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    return None

def extract_from_playerembedapi(url):
    """Extrai vídeo do PlayerEmbedAPI"""
    print(f'\n🔍 Tentando PlayerEmbedAPI: {url}')
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        
        # Procurar padrões
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']+\.mp4[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, r.text)
            for m in matches:
                if m.startswith('http') and 'logo' not in m.lower():
                    print(f'✅ Encontrado: {m[:80]}...')
                    return m
                    
    except Exception as e:
        print(f'❌ Erro: {e}')
    return None

def play_in_vlc(video_url, referer=None):
    """Reproduz no VLC"""
    print(f'\n🎬 Abrindo VLC...')
    print(f'URL: {video_url}')
    
    vlc_paths = [
        r'C:\Program Files\VideoLAN\VLC\vlc.exe',
        r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe',
    ]
    
    vlc_path = None
    for path in vlc_paths:
        try:
            subprocess.run([path, '--version'], capture_output=True, timeout=5)
            vlc_path = path
            break
        except:
            continue
    
    if not vlc_path:
        print('❌ VLC não encontrado!')
        print(f'\n📋 Copie e abra manualmente:')
        print(video_url)
        return False
    
    cmd = [vlc_path, video_url]
    if referer:
        cmd.extend(['--http-referrer', referer])
    
    subprocess.Popen(cmd)
    print('✅ VLC aberto!')
    return True

def main():
    print('=' * 60)
    print('🎬 TESTE MaxSeries → VLC')
    print('=' * 60)
    
    # 1. Buscar série
    print('\n📺 Buscando série...')
    url = 'https://www.maxseries.one/series/'
    r = requests.get(url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    articles = soup.select('article')
    series_url = None
    for art in articles[:5]:
        link = art.select_one('a')
        if link:
            href = link.get('href', '')
            if '/series/' in href:
                series_url = href
                title = art.select_one('.data h3')
                title_text = title.text.strip() if title else 'Série'
                print(f'✅ {title_text}')
                print(f'   {href}')
                break
    
    if not series_url:
        print('❌ Nenhuma série encontrada')
        return
    
    # 2. Carregar série e iframe
    print('\n🖼️ Carregando iframe...')
    r2 = requests.get(series_url, headers=HEADERS, timeout=30)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    iframe = soup2.select_one('iframe')
    if not iframe:
        print('❌ Iframe não encontrado')
        return
    
    iframe_src = iframe.get('src', '')
    if iframe_src.startswith('//'):
        iframe_src = 'https:' + iframe_src
    print(f'✅ {iframe_src}')
    
    # 3. Buscar episódios
    print('\n📺 Buscando episódios...')
    r3 = requests.get(iframe_src, headers=HEADERS, timeout=30)
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    
    eps = soup3.select('li[data-episode-id]')
    if not eps:
        print('❌ Nenhum episódio encontrado')
        return
    
    ep_id = eps[0].get('data-episode-id', '')
    print(f'✅ {len(eps)} episódios, usando ID: {ep_id}')
    
    # 4. AJAX para players
    print('\n📡 Buscando players...')
    ajax_url = f'https://playerthree.online/episodio/{ep_id}'
    ajax_headers = {
        **HEADERS,
        'Referer': iframe_src,
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    r4 = requests.get(ajax_url, headers=ajax_headers, timeout=30)
    soup4 = BeautifulSoup(r4.text, 'html.parser')
    
    buttons = soup4.select('button[data-source]')
    players = []
    for btn in buttons:
        source = btn.get('data-source', '')
        name = btn.text.strip()
        if source and 'youtube' not in source.lower():
            players.append({'name': name, 'url': source})
            print(f'✅ {name}: {source[:60]}...')
    
    if not players:
        print('❌ Nenhum player encontrado')
        return
    
    # 5. Tentar extrair vídeo de cada player
    print('\n' + '=' * 60)
    print('🎯 EXTRAINDO VÍDEO DIRETO')
    print('=' * 60)
    
    video_url = None
    
    for player in players:
        url = player['url']
        
        if 'bysebuho' in url.lower() or 'dood' in url.lower():
            video_url = extract_from_bysebuho(url)
        elif 'megaembed' in url.lower():
            video_url = extract_from_megaembed(url)
        elif 'playerembedapi' in url.lower():
            video_url = extract_from_playerembedapi(url)
        else:
            # Tentar genérico
            print(f'\n🔍 Tentando genérico: {url}')
            try:
                r = requests.get(url, headers=HEADERS, timeout=30)
                patterns = [
                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                    r'["\']([^"\']+\.mp4[^"\']*)["\']',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, r.text)
                    for m in matches:
                        if m.startswith('http') and 'logo' not in m.lower():
                            video_url = m
                            print(f'✅ Encontrado: {m[:80]}...')
                            break
                    if video_url:
                        break
            except Exception as e:
                print(f'❌ Erro: {e}')
        
        if video_url:
            break
    
    # 6. Resultado
    print('\n' + '=' * 60)
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        print(f'URL: {video_url}')
        play_in_vlc(video_url, iframe_src)
    else:
        print('❌ Não foi possível extrair link direto')
        print('\n📋 Players disponíveis (abra manualmente no navegador):')
        for p in players:
            print(f'  {p["name"]}: {p["url"]}')
    
    print('=' * 60)

if __name__ == '__main__':
    main()
