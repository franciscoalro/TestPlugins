#!/usr/bin/env python3
"""
Teste Completo de Reprodução - MaxSeries
Simula exatamente o que o plugin CloudStream fará
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

class MaxSeriesPlaybackTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.main_url = "https://www.maxseries.one"
        
    def test_complete_flow(self):
        """Testar fluxo completo: série -> episódio -> players -> vídeo"""
        print("🎬 TESTE COMPLETO DE REPRODUÇÃO MAXSERIES")
        print("=" * 60)
        
        # 1. Testar série específica
        series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"📺 1. TESTANDO SÉRIE: {series_url}")
        
        try:
            # Simular método load() do plugin
            series_episodes = self.simulate_load_method(series_url)
            
            if series_episodes:
                print(f"✅ Episódios encontrados: {len(series_episodes)}")
                
                # 2. Testar primeiro episódio
                first_episode = series_episodes[0]
                print(f"\n🎯 2. TESTANDO EPISÓDIO: {first_episode['name']}")
                print(f"   URL: {first_episode['url']}")
                
                # Simular método loadLinks() do plugin
                video_links = self.simulate_loadlinks_method(first_episode['url'])
                
                if video_links:
                    print(f"✅ Links de vídeo encontrados: {len(video_links)}")
                    
                    # 3. Testar cada link de vídeo
                    for i, link in enumerate(video_links):
                        print(f"\n🎮 3.{i+1} TESTANDO PLAYER: {link['name']}")
                        self.test_video_link(link['url'], link['name'])
                else:
                    print("❌ Nenhum link de vídeo encontrado")
            else:
                print("❌ Nenhum episódio encontrado")
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    
    def simulate_load_method(self, series_url):
        """Simular método load() do plugin CloudStream"""
        print("🔄 Simulando método load()...")
        
        try:
            response = self.session.get(series_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair informações básicas
            title = soup.select_one('.data h1, h1, .entry-title')
            title_text = title.text.strip() if title else "Unknown"
            
            print(f"   Título: {title_text}")
            
            # Procurar iframe principal
            iframe = soup.select_one('iframe')
            if not iframe:
                print("❌ Nenhum iframe encontrado")
                return []
            
            iframe_src = iframe.get('src')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            
            print(f"   Iframe: {iframe_src}")
            
            # Carregar iframe
            iframe_response = self.session.get(iframe_src)
            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
            
            # Extrair episódios
            episodes = []
            episode_elements = iframe_soup.select('li[data-season-id][data-episode-id] a')
            
            print(f"   Elementos de episódio encontrados: {len(episode_elements)}")
            
            for i, element in enumerate(episode_elements):
                episode_id = element.parent.get('data-episode-id') if element.parent else ''
                href = element.get('href')
                
                if href and episode_id:
                    episode_url = iframe_src + href if href.startswith('#') else href
                    
                    episodes.append({
                        'name': f"Episódio {i+1}",
                        'episode': i+1,
                        'season': 1,
                        'url': episode_url,
                        'episode_id': episode_id
                    })
            
            return episodes
            
        except Exception as e:
            print(f"❌ Erro no simulate_load_method: {e}")
            return []
    
    def simulate_loadlinks_method(self, episode_url):
        """Simular método loadLinks() do plugin CloudStream"""
        print("🔄 Simulando método loadLinks()...")
        
        try:
            video_links = []
            
            # Verificar se é URL de episódio do iframe
            if '#' in episode_url and 'playerthree.online' in episode_url:
                print("   Detectado episódio do iframe playerthree")
                
                # Extrair episodeId (formato: #12962_255703)
                fragment_match = re.search(r'#\d+_(\d+)', episode_url)
                if fragment_match:
                    episode_id = fragment_match.group(1)
                    print(f"   Episode ID extraído: {episode_id}")
                    
                    # Fazer requisição AJAX (como no plugin v15.1)
                    base_url = "https://playerthree.online"
                    ajax_url = f"{base_url}/episodio/{episode_id}"
                    
                    print(f"   Fazendo requisição AJAX: {ajax_url}")
                    
                    ajax_headers = {
                        'Referer': episode_url,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    ajax_response = self.session.get(ajax_url, headers=ajax_headers)
                    
                    if ajax_response.status_code == 200:
                        print(f"   ✅ AJAX Response: {ajax_response.status_code}")
                        
                        ajax_soup = BeautifulSoup(ajax_response.content, 'html.parser')
                        
                        # Procurar botões de player
                        player_buttons = ajax_soup.select('button[data-source], .btn[data-source], button[data-show-player]')
                        print(f"   Players encontrados: {len(player_buttons)}")
                        
                        for button in player_buttons:
                            player_name = button.text.strip() or "Player"
                            data_source = button.get('data-source', '')
                            
                            if data_source and data_source.startswith('http'):
                                # Filtrar trailers
                                if not ('youtube' in data_source.lower() or 'trailer' in data_source.lower()):
                                    video_links.append({
                                        'name': player_name,
                                        'url': data_source,
                                        'quality': 'Unknown'
                                    })
                                    print(f"   ✅ Player válido: {player_name} -> {data_source}")
                                else:
                                    print(f"   🚨 Trailer ignorado: {data_source}")
                    else:
                        print(f"   ❌ Erro AJAX: {ajax_response.status_code}")
                else:
                    print("   ❌ Não foi possível extrair episodeId")
            
            return video_links
            
        except Exception as e:
            print(f"❌ Erro no simulate_loadlinks_method: {e}")
            return []
    
    def test_video_link(self, video_url, player_name):
        """Testar se o link de vídeo realmente funciona"""
        print(f"🔍 Testando player: {player_name}")
        print(f"   URL: {video_url}")
        
        try:
            # Fazer requisição HEAD para verificar se o link existe
            head_response = self.session.head(video_url, timeout=10, allow_redirects=True)
            print(f"   Status HEAD: {head_response.status_code}")
            
            if head_response.status_code == 200:
                print("   ✅ Link acessível")
                
                # Tentar carregar a página do player
                player_response = self.session.get(video_url, timeout=15)
                print(f"   Status GET: {player_response.status_code}")
                
                if player_response.status_code == 200:
                    player_soup = BeautifulSoup(player_response.content, 'html.parser')
                    
                    # Procurar elementos de vídeo
                    video_elements = player_soup.select('video[src], source[src]')
                    if video_elements:
                        print(f"   🎥 Elementos de vídeo encontrados: {len(video_elements)}")
                        for video in video_elements:
                            src = video.get('src')
                            print(f"      📺 Vídeo: {src}")
                    
                    # Procurar URLs de vídeo no HTML/JavaScript
                    content = player_response.text
                    
                    # Padrões de vídeo
                    video_patterns = [
                        r'https?://[^"\s]+\.m3u8[^"\s]*',
                        r'https?://[^"\s]+\.mp4[^"\s]*',
                        r'"file"\s*:\s*"([^"]+)"',
                        r'"source"\s*:\s*"([^"]+)"',
                        r'"src"\s*:\s*"([^"]+)"'
                    ]
                    
                    video_found = False
                    for pattern in video_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"   🎯 URLs de vídeo encontradas ({len(matches)}):")
                            for match in matches[:3]:  # Mostrar primeiras 3
                                if isinstance(match, tuple):
                                    match = match[0] if match[0] else match[1]
                                
                                if match and match.startswith('http'):
                                    print(f"      📺 {match}")
                                    video_found = True
                                    
                                    # Testar se o vídeo realmente existe
                                    self.test_direct_video(match)
                    
                    if not video_found:
                        print("   ⚠️ Nenhuma URL de vídeo encontrada no HTML")
                        
                        # Procurar iframes aninhados
                        iframes = player_soup.select('iframe[src]')
                        if iframes:
                            print(f"   🖼️ Iframes aninhados encontrados: {len(iframes)}")
                            for iframe in iframes[:2]:  # Testar primeiros 2
                                iframe_src = iframe.get('src')
                                print(f"      🔗 Iframe: {iframe_src}")
                                self.test_nested_iframe(iframe_src)
                
                else:
                    print(f"   ❌ Erro ao carregar player: {player_response.status_code}")
            
            elif head_response.status_code in [301, 302, 303, 307, 308]:
                print(f"   🔄 Redirecionamento: {head_response.headers.get('Location', 'N/A')}")
            else:
                print(f"   ❌ Link inacessível: {head_response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - Link muito lento")
        except requests.exceptions.ConnectionError:
            print("   🔌 Erro de conexão")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    def test_direct_video(self, video_url):
        """Testar URL de vídeo direta"""
        try:
            # Fazer requisição HEAD para verificar o vídeo
            video_response = self.session.head(video_url, timeout=10)
            content_type = video_response.headers.get('Content-Type', '')
            content_length = video_response.headers.get('Content-Length', '0')
            
            print(f"        📊 Status: {video_response.status_code}")
            print(f"        📊 Tipo: {content_type}")
            print(f"        📊 Tamanho: {content_length} bytes")
            
            if video_response.status_code == 200:
                if 'video' in content_type or 'application/vnd.apple.mpegurl' in content_type:
                    print("        ✅ VÍDEO VÁLIDO ENCONTRADO!")
                    return True
                else:
                    print(f"        ⚠️ Tipo de conteúdo inesperado: {content_type}")
            else:
                print(f"        ❌ Vídeo inacessível: {video_response.status_code}")
                
        except Exception as e:
            print(f"        ❌ Erro ao testar vídeo: {e}")
        
        return False
    
    def test_nested_iframe(self, iframe_url):
        """Testar iframe aninhado"""
        try:
            if iframe_url.startswith('//'):
                iframe_url = 'https:' + iframe_url
            elif iframe_url.startswith('/'):
                iframe_url = 'https://playerthree.online' + iframe_url
            
            iframe_response = self.session.get(iframe_url, timeout=10)
            
            if iframe_response.status_code == 200:
                print(f"        ✅ Iframe carregado: {iframe_response.status_code}")
                
                # Procurar vídeos no iframe
                iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
                video_elements = iframe_soup.select('video[src], source[src]')
                
                if video_elements:
                    print(f"        🎥 Vídeos no iframe: {len(video_elements)}")
                    for video in video_elements:
                        src = video.get('src')
                        if src:
                            print(f"          📺 {src}")
                            self.test_direct_video(src)
            else:
                print(f"        ❌ Erro no iframe: {iframe_response.status_code}")
                
        except Exception as e:
            print(f"        ❌ Erro no iframe: {e}")

def main():
    tester = MaxSeriesPlaybackTester()
    
    print("🎬 INICIANDO TESTE COMPLETO DE REPRODUÇÃO")
    print("Este teste simula exatamente o que o plugin CloudStream v15.1 fará")
    print()
    
    # Testar fluxo completo
    tester.test_complete_flow()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO DO TESTE:")
    print("✅ Se vídeos válidos foram encontrados = Plugin funcionará")
    print("❌ Se nenhum vídeo foi encontrado = Plugin precisa de ajustes")
    print("⚠️ Se apenas iframes = Pode precisar de extractors adicionais")

if __name__ == "__main__":
    main()