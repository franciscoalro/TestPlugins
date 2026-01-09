#!/usr/bin/env python3
"""
Teste de extração de links do MaxSeries para reprodução no VLC
"""

import requests
from bs4 import BeautifulSoup
import re
import subprocess
import json

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_series_page():
    """Busca uma série no MaxSeries"""
    print("🔍 Buscando séries no MaxSeries...")
    
    url = "https://www.maxseries.one/series/"
    response = requests.get(url, headers=HEADERS, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erro ao acessar: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Pegar primeira série
    article = soup.select_one("article.item")
    if article:
        link = article.select_one(".data h3 a")
        if link:
            title = link.text.strip()
            href = link.get("href")
            print(f"✅ Série encontrada: {title}")
            print(f"   URL: {href}")
            return href
    
    return None

def get_iframe_from_series(series_url):
    """Extrai o iframe da página da série"""
    print(f"\n🖼️ Carregando página da série...")
    
    response = requests.get(series_url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    iframe = soup.select_one("iframe")
    if iframe:
        src = iframe.get("src", "")
        if src.startswith("//"):
            src = "https:" + src
        print(f"✅ Iframe encontrado: {src}")
        return src
    
    print("❌ Nenhum iframe encontrado")
    return None

def get_episodes_from_iframe(iframe_url):
    """Extrai episódios do iframe"""
    print(f"\n📺 Carregando iframe para buscar episódios...")
    
    response = requests.get(iframe_url, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    episodes = []
    
    # Buscar links de episódios
    ep_links = soup.select("li[data-episode-id] a")
    for ep in ep_links[:5]:  # Pegar apenas os 5 primeiros
        href = ep.get("href", "")
        episode_id = ep.parent.get("data-episode-id", "")
        if episode_id:
            episodes.append({
                "id": episode_id,
                "href": href,
                "full_url": f"{iframe_url}{href}" if href.startswith("#") else href
            })
    
    if episodes:
        print(f"✅ {len(episodes)} episódios encontrados")
        for ep in episodes:
            print(f"   - Episódio ID: {ep['id']}")
    else:
        print("❌ Nenhum episódio encontrado")
    
    return episodes

def get_players_from_episode(iframe_base_url, episode_id):
    """Faz requisição AJAX para obter players do episódio"""
    print(f"\n📡 Buscando players do episódio {episode_id}...")
    
    # Extrair base URL
    base_match = re.match(r"(https?://[^/]+)", iframe_base_url)
    if not base_match:
        print("❌ Não foi possível extrair base URL")
        return []
    
    base_url = base_match.group(1)
    ajax_url = f"{base_url}/episodio/{episode_id}"
    
    print(f"   AJAX URL: {ajax_url}")
    
    ajax_headers = {
        **HEADERS,
        "Referer": iframe_base_url,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    response = requests.get(ajax_url, headers=ajax_headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erro AJAX: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    players = []
    buttons = soup.select("button[data-source], .btn[data-source]")
    
    for btn in buttons:
        name = btn.text.strip() or "Player"
        source = btn.get("data-source", "")
        
        if source and source.startswith("http"):
            # Ignorar YouTube e trailers
            if "youtube" not in source.lower() and "trailer" not in source.lower():
                players.append({
                    "name": name,
                    "url": source
                })
    
    if players:
        print(f"✅ {len(players)} players encontrados:")
        for p in players:
            print(f"   - {p['name']}: {p['url'][:60]}...")
    else:
        print("❌ Nenhum player encontrado")
    
    return players

def extract_video_from_player(player_url):
    """Tenta extrair o link de vídeo direto do player"""
    print(f"\n🎬 Tentando extrair vídeo de: {player_url[:60]}...")
    
    try:
        response = requests.get(player_url, headers=HEADERS, timeout=30)
        
        # Procurar por links de vídeo no HTML/JS
        patterns = [
            r'file\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'file\s*:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'source\s*:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'["\']([^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*\.mp4[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                if match.startswith("http") and "logo" not in match.lower():
                    print(f"✅ Link de vídeo encontrado: {match[:80]}...")
                    return match
        
        # Se não encontrou, verificar se é MegaEmbed
        if "megaembed" in player_url.lower():
            print("   🔍 Detectado MegaEmbed, tentando API...")
            return extract_megaembed(player_url)
        
        print("❌ Nenhum link de vídeo encontrado no player")
        return None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def extract_megaembed(url):
    """Extrai vídeo do MegaEmbed usando API descoberta no HAR"""
    print("   📡 Tentando API MegaEmbed...")
    
    # Extrair ID do MegaEmbed
    id_match = re.search(r'[#/]([a-zA-Z0-9]+)$', url)
    if not id_match:
        return None
    
    mega_id = id_match.group(1)
    print(f"   ID: {mega_id}")
    
    # Tentar API de vídeo
    api_url = f"https://megaembed.link/api/v1/video?id={mega_id}&w=1920&h=1080&r=playerthree.online"
    
    api_headers = {
        **HEADERS,
        "Referer": "https://megaembed.link/",
        "Origin": "https://megaembed.link"
    }
    
    try:
        response = requests.get(api_url, headers=api_headers, timeout=30)
        print(f"   API Response: {response.status_code}")
        
        if response.status_code == 200:
            # Tentar parsear JSON
            try:
                data = response.json()
                if "url" in data:
                    return data["url"]
                if "file" in data:
                    return data["file"]
            except:
                # Procurar URL no texto
                matches = re.findall(r'["\']([^"\']+\.m3u8[^"\']*)["\']', response.text)
                if matches:
                    return matches[0]
    except Exception as e:
        print(f"   ❌ Erro API: {e}")
    
    return None

def play_in_vlc(video_url, referer=None):
    """Reproduz o vídeo no VLC"""
    print(f"\n🎬 Tentando reproduzir no VLC...")
    print(f"   URL: {video_url[:80]}...")
    
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        "vlc"
    ]
    
    vlc_path = None
    for path in vlc_paths:
        try:
            subprocess.run([path, "--version"], capture_output=True, timeout=5)
            vlc_path = path
            break
        except:
            continue
    
    if not vlc_path:
        print("❌ VLC não encontrado!")
        print(f"\n📋 Copie este link e abra manualmente no VLC:")
        print(f"   {video_url}")
        return False
    
    cmd = [vlc_path, video_url]
    
    if referer:
        cmd.extend(["--http-referrer", referer])
    
    print(f"✅ Abrindo VLC...")
    subprocess.Popen(cmd)
    return True

def main():
    print("=" * 60)
    print("🎬 TESTE MaxSeries → VLC")
    print("=" * 60)
    
    # 1. Buscar série
    series_url = get_series_page()
    if not series_url:
        print("\n❌ Não foi possível encontrar uma série")
        return
    
    # 2. Obter iframe
    iframe_url = get_iframe_from_series(series_url)
    if not iframe_url:
        print("\n❌ Não foi possível encontrar iframe")
        return
    
    # 3. Obter episódios
    episodes = get_episodes_from_iframe(iframe_url)
    if not episodes:
        print("\n❌ Não foi possível encontrar episódios")
        return
    
    # 4. Obter players do primeiro episódio
    first_ep = episodes[0]
    players = get_players_from_episode(iframe_url, first_ep["id"])
    
    if not players:
        print("\n❌ Não foi possível encontrar players")
        return
    
    # 5. Tentar extrair vídeo de cada player
    video_url = None
    for player in players:
        video_url = extract_video_from_player(player["url"])
        if video_url:
            break
    
    if not video_url:
        print("\n❌ Não foi possível extrair link de vídeo direto")
        print("\n📋 Players encontrados (tente abrir manualmente):")
        for p in players:
            print(f"   {p['name']}: {p['url']}")
        return
    
    # 6. Reproduzir no VLC
    play_in_vlc(video_url, iframe_url)
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 60)

if __name__ == "__main__":
    main()
