#!/usr/bin/env python3
"""
Teste específico para Projeto Prometheus
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import subprocess

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
}

def main():
    print('=' * 60)
    print('🎬 TESTE: Projeto Prometheus')
    print('=' * 60)
    
    series_url = 'https://www.maxseries.one/series/assistir-projeto-prometheus-online'
    
    # 1. Carregar página da série
    print(f'\n📺 Carregando série...')
    r = requests.get(series_url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    title = soup.select_one('.data h1')
    print(f'   Título: {title.text.strip() if title else "N/A"}')
    
    # 2. Encontrar iframe
    iframe = soup.select_one('iframe')
    if not iframe:
        print('❌ Iframe não encontrado')
        return
    
    iframe_src = iframe.get('src', '')
    if iframe_src.startswith('//'):
        iframe_src = 'https:' + iframe_src
    print(f'   Iframe: {iframe_src}')
    
    # 3. Carregar iframe
    print(f'\n🖼️ Carregando iframe...')
    r2 = requests.get(iframe_src, headers={**HEADERS, 'Referer': series_url}, timeout=30)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    
    # 4. Listar temporadas
    seasons = soup2.select('ul.header-navigation li[data-season-id]')
    print(f'   Temporadas: {len(seasons)}')
    
    # 5. Listar episódios
    episodes = soup2.select('li[data-episode-id]')
    print(f'   Episódios: {len(episodes)}')
    
    if not episodes:
        print('❌ Nenhum episódio encontrado')
        return
    
    # Pegar primeiro episódio
    ep = episodes[0]
    ep_id = ep.get('data-episode-id', '')
    print(f'\n📺 Episódio 1 - ID: {ep_id}')
    
    # 6. AJAX para players
    print(f'\n📡 Buscando players via AJAX...')
    ajax_url = f'https://playerthree.online/episodio/{ep_id}'
    
    ajax_headers = {
        **HEADERS,
        'Referer': iframe_src,
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    r3 = requests.get(ajax_url, headers=ajax_headers, timeout=30)
    soup3 = BeautifulSoup(r3.text, 'html.parser')
    
    # 7. Extrair players
    buttons = soup3.select('button[data-source]')
    players = []
    
    print(f'   Botões encontrados: {len(buttons)}')
    
    for btn in buttons:
        name = btn.text.strip()
        source = btn.get('data-source', '')
        if source and 'youtube' not in source.lower():
            players.append({'name': name, 'url': source})
            print(f'   → {name}: {source}')
    
    if not players:
        print('❌ Nenhum player encontrado')
        return
    
    # 8. Tentar extrair de cada player
    print(f'\n{"="*60}')
    print('🎯 TENTANDO EXTRAIR VÍDEO')
    print('='*60)
    
    video_url = None
    
    for player in players:
        url = player['url']
        name = player['name']
        
        print(f'\n🔍 {name}: {url[:50]}...')
        
        try:
            r4 = requests.get(url, headers={**HEADERS, 'Referer': iframe_src}, timeout=30)
            
            # Procurar m3u8/mp4 no HTML
            patterns = [
                r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'"file"\s*:\s*"([^"]+)"',
                r'"url"\s*:\s*"([^"]+)"',
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            ]
            
            for p in patterns:
                matches = re.findall(p, r4.text)
                for m in matches:
                    if m.startswith('http') and 'logo' not in m.lower() and 'thumb' not in m.lower():
                        print(f'   ✅ Encontrado: {m[:80]}')
                        video_url = m
                        break
                if video_url:
                    break
            
            if video_url:
                break
                
            # Verificar se tem eval/packed
            if 'eval(function(p,a,c,k,e,d)' in r4.text:
                print('   📦 JS packed detectado')
                
                # Tentar desofuscar
                packed = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('([^']+)',(\d+),(\d+),'([^']+)'", r4.text, re.DOTALL)
                if packed:
                    p, a, c, k = packed.groups()
                    a, c = int(a), int(c)
                    k = k.split('|')
                    
                    def e_func(c_val):
                        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        result = ''
                        while c_val > 0:
                            result = chars[c_val % a] + result
                            c_val //= a
                        return result or '0'
                    
                    unpacked = p
                    for i in range(c - 1, -1, -1):
                        if i < len(k) and k[i]:
                            unpacked = re.sub(r'\b' + e_func(i) + r'\b', k[i], unpacked)
                    
                    # Procurar no código desofuscado
                    urls = re.findall(r'https?://[^\s"\'\\]+\.(?:m3u8|mp4)[^\s"\'\\]*', unpacked)
                    if urls:
                        video_url = urls[0]
                        print(f'   ✅ Unpacked: {video_url[:80]}')
                        break
            
            # Verificar API específica
            if 'megaembed' in url.lower():
                id_match = re.search(r'#([a-zA-Z0-9]+)', url)
                if id_match:
                    mega_id = id_match.group(1)
                    api_url = f'https://megaembed.link/api/v1/video?id={mega_id}&w=1920&h=1080&r=playerthree.online'
                    r5 = requests.get(api_url, headers={**HEADERS, 'Referer': url}, timeout=30)
                    print(f'   API response: {r5.text[:100]}')
                    
        except Exception as e:
            print(f'   ❌ Erro: {e}')
    
    # 9. Resultado
    print(f'\n{"="*60}')
    if video_url:
        print('✅ VÍDEO ENCONTRADO!')
        print(f'URL: {video_url}')
        
        # Abrir no VLC
        vlc_path = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
        try:
            subprocess.Popen([vlc_path, video_url, '--http-referrer', iframe_src])
            print('✅ VLC aberto!')
        except:
            print(f'📋 Copie a URL acima e abra no VLC')
    else:
        print('❌ Não foi possível extrair link direto')
        print('\n📋 Players disponíveis para teste manual:')
        for p in players:
            print(f'   {p["name"]}: {p["url"]}')
    print('='*60)

if __name__ == '__main__':
    main()
