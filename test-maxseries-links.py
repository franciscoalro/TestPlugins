#!/usr/bin/env python3
"""
Teste Direto MaxSeries - Encontrar Links Reais
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def test_maxseries_direct():
    print("🔍 TESTE DIRETO MAXSERIES")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # 1. Testar série específica
    series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
    print(f"📺 Testando série: {series_url}")
    
    try:
        response = session.get(series_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Título: {soup.title.text if soup.title else 'N/A'}")
        
        # 2. Procurar iframe
        iframe = soup.select_one('iframe')
        if iframe:
            iframe_src = iframe.get('src')
            print(f"🖼️ Iframe encontrado: {iframe_src}")
            
            # 3. Carregar iframe
            if iframe_src:
                if iframe_src.startswith('//'):
                    iframe_src = 'https:' + iframe_src
                
                print(f"📥 Carregando iframe: {iframe_src}")
                iframe_response = session.get(iframe_src)
                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                
                print(f"✅ Iframe Status: {iframe_response.status_code}")
                print(f"📄 Iframe Título: {iframe_soup.title.text if iframe_soup.title else 'N/A'}")
                
                # 4. Procurar episódios
                episode_links = iframe_soup.select('a[href*="#"]')
                print(f"📺 Links de episódios encontrados: {len(episode_links)}")
                
                episode_urls = []
                for i, link in enumerate(episode_links[:3]):
                    href = link.get('href')
                    if href and '#' in href:
                        full_url = iframe_src + href if href.startswith('#') else href
                        episode_urls.append(full_url)
                        print(f"  Episódio {i+1}: {full_url}")
                
                # 5. Testar primeiro episódio
                if episode_urls:
                    test_episode_url = episode_urls[0]
                    print(f"\n🎬 Testando episódio: {test_episode_url}")
                    
                    episode_response = session.get(test_episode_url)
                    episode_soup = BeautifulSoup(episode_response.content, 'html.parser')
                    
                    print(f"✅ Episódio Status: {episode_response.status_code}")
                    
                    # 6. Procurar players
                    player_buttons = episode_soup.select('button[data-source], .btn[data-source]')
                    print(f"🎮 Botões de player encontrados: {len(player_buttons)}")
                    
                    for i, button in enumerate(player_buttons):
                        data_source = button.get('data-source', '')
                        button_text = button.get_text(strip=True)
                        
                        print(f"  Player {i+1}: {button_text} -> {data_source}")
                        
                        # Verificar se é trailer/YouTube
                        if 'youtube' in data_source.lower() or 'trailer' in data_source.lower():
                            print(f"    🚨 TRAILER DETECTADO!")
                        elif data_source and data_source.startswith('http'):
                            print(f"    🎯 PLAYER VÁLIDO!")
                            
                            # Testar o player
                            try:
                                player_response = session.get(data_source)
                                print(f"    📊 Player Status: {player_response.status_code}")
                                
                                if player_response.status_code == 200:
                                    player_soup = BeautifulSoup(player_response.content, 'html.parser')
                                    
                                    # Procurar vídeos no player
                                    video_elements = player_soup.select('video[src], source[src]')
                                    if video_elements:
                                        print(f"    📹 Vídeos encontrados: {len(video_elements)}")
                                        for video in video_elements:
                                            src = video.get('src')
                                            print(f"      🎥 Vídeo: {src}")
                                    
                                    # Procurar m3u8/mp4 no HTML
                                    content = player_response.text
                                    video_patterns = [
                                        r'https?://[^"\s]+\.m3u8[^"\s]*',
                                        r'https?://[^"\s]+\.mp4[^"\s]*',
                                        r'"file"\s*:\s*"([^"]+)"',
                                        r'"source"\s*:\s*"([^"]+)"'
                                    ]
                                    
                                    for pattern in video_patterns:
                                        matches = re.findall(pattern, content)
                                        if matches:
                                            print(f"    🎯 URLs encontradas ({pattern[:20]}...): {len(matches)}")
                                            for match in matches[:3]:
                                                print(f"      📺 {match}")
                                
                            except Exception as e:
                                print(f"    ❌ Erro ao testar player: {e}")
                    
                    # 7. Procurar gleam.config
                    scripts = episode_soup.select('script')
                    for script in scripts:
                        content = script.string or ''
                        if 'gleam.config' in content:
                            print(f"🎬 gleam.config encontrado!")
                            
                            # Extrair configuração
                            gleam_match = re.search(r'gleam\.config\s*=\s*({[^}]+})', content)
                            if gleam_match:
                                try:
                                    config_str = gleam_match.group(1)
                                    print(f"📋 Configuração gleam: {config_str[:200]}...")
                                except Exception as e:
                                    print(f"❌ Erro ao extrair gleam: {e}")
        
        else:
            print("❌ Nenhum iframe encontrado")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_maxseries_direct()