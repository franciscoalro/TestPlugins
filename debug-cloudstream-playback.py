#!/usr/bin/env python3
"""
Diagnóstico Específico - CloudStream Playback
Simula exatamente o que acontece quando você clica em um episódio
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

class CloudStreamPlaybackDebugger:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CloudStream/3.0 (Android)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
        })
        
    def debug_complete_flow(self):
        """Debug completo do fluxo CloudStream"""
        print("🔍 DIAGNÓSTICO CLOUDSTREAM - MAXSERIES V15.1")
        print("=" * 60)
        
        # Testar série específica
        series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        print(f"📺 TESTANDO: {series_url}")
        
        # 1. Simular load() - Carregar série
        episodes = self.simulate_load_series(series_url)
        
        if episodes:
            print(f"\n✅ {len(episodes)} episódios encontrados")
            
            # 2. Simular loadLinks() - Carregar links do primeiro episódio
            first_episode = episodes[0]
            print(f"\n🎯 TESTANDO EPISÓDIO: {first_episode['name']}")
            print(f"   URL: {first_episode['url']}")
            
            links = self.simulate_loadlinks_detailed(first_episode['url'])
            
            if links:
                print(f"\n✅ {len(links)} links encontrados")
                
                # 3. Testar cada extractor
                for link in links:
                    self.test_extractor_detailed(link)
            else:
                print("\n❌ PROBLEMA: Nenhum link encontrado")
                self.diagnose_loadlinks_failure(first_episode['url'])
        else:
            print("\n❌ PROBLEMA: Nenhum episódio encontrado")
            self.diagnose_load_failure(series_url)
    
    def simulate_load_series(self, series_url):
        """Simular método load() do plugin"""
        print("\n🔄 1. SIMULANDO MÉTODO load()...")
        
        try:
            # Carregar página da série
            response = self.session.get(series_url, timeout=15)
            print(f"   Status da série: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ Erro ao carregar série: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair título
            title = soup.select_one('.data h1, h1, .entry-title')
            title_text = title.text.strip() if title else "Unknown"
            print(f"   Título: {title_text}")
            
            # Procurar iframe principal
            iframe = soup.select_one('iframe')
            if not iframe:
                print("   ❌ Nenhum iframe encontrado na página")
                return []
            
            iframe_src = iframe.get('src', '')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            
            print(f"   Iframe encontrado: {iframe_src}")
            
            # Carregar iframe
            iframe_response = self.session.get(iframe_src, timeout=15)
            print(f"   Status do iframe: {iframe_response.status_code}")
            
            if iframe_response.status_code != 200:
                print(f"   ❌ Erro ao carregar iframe: {iframe_response.status_code}")
                return []
            
            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
            
            # Procurar episódios (método do plugin v15.1)
            episode_elements = iframe_soup.select('li[data-season-id][data-episode-id] a')
            print(f"   Elementos de episódio: {len(episode_elements)}")
            
            episodes = []
            for i, element in enumerate(episode_elements):
                parent = element.parent
                if parent:
                    episode_id = parent.get('data-episode-id', '')
                    href = element.get('href', '')
                    
                    if href and episode_id:
                        episode_url = iframe_src + href if href.startswith('#') else href
                        
                        episodes.append({
                            'name': f"Episódio {i+1}",
                            'episode': i+1,
                            'season': 1,
                            'url': episode_url,
                            'episode_id': episode_id
                        })
                        
                        print(f"   ✅ Episódio {i+1}: {episode_url}")
            
            return episodes
            
        except Exception as e:
            print(f"   ❌ Erro no load(): {e}")
            return []
    
    def simulate_loadlinks_detailed(self, episode_url):
        """Simular método loadLinks() com debug detalhado"""
        print("\n🔄 2. SIMULANDO MÉTODO loadLinks()...")
        print(f"   URL do episódio: {episode_url}")
        
        links = []
        
        try:
            # Verificar se é URL de iframe com fragmento
            if '#' in episode_url and 'playerthree.online' in episode_url:
                print("   ✅ Detectado episódio do iframe playerthree")
                
                # Extrair episodeId (formato: #12962_255703)
                fragment_match = re.search(r'#\d+_(\d+)', episode_url)
                if fragment_match:
                    episode_id = fragment_match.group(1)
                    print(f"   ✅ Episode ID extraído: {episode_id}")
                    
                    # Fazer requisição AJAX (como no plugin v15.1)
                    ajax_url = f"https://playerthree.online/episodio/{episode_id}"
                    print(f"   📡 Fazendo requisição AJAX: {ajax_url}")
                    
                    ajax_headers = {
                        'Referer': episode_url,
                        'X-Requested-With': 'XMLHttpRequest',
                        'User-Agent': 'CloudStream/3.0 (Android)'
                    }
                    
                    ajax_response = self.session.get(ajax_url, headers=ajax_headers, timeout=15)
                    print(f"   📡 Status AJAX: {ajax_response.status_code}")
                    
                    if ajax_response.status_code == 200:
                        print("   ✅ Resposta AJAX recebida com sucesso")
                        
                        # Salvar resposta para debug
                        with open('debug_ajax_response.html', 'w', encoding='utf-8') as f:
                            f.write(ajax_response.text)
                        print("   💾 Resposta salva em: debug_ajax_response.html")
                        
                        ajax_soup = BeautifulSoup(ajax_response.content, 'html.parser')
                        
                        # Procurar botões de player (como no plugin)
                        player_buttons = ajax_soup.select('button[data-source], .btn[data-source], button[data-show-player]')
                        print(f"   🎮 Botões de player encontrados: {len(player_buttons)}")
                        
                        for i, button in enumerate(player_buttons):
                            player_name = button.text.strip() or f"Player #{i+1}"
                            data_source = button.get('data-source', '')
                            
                            print(f"   🎯 Player {i+1}: {player_name}")
                            print(f"      data-source: {data_source}")
                            
                            if data_source and data_source.startswith('http'):
                                # Verificar se não é trailer
                                is_trailer = ('youtube' in data_source.lower() or 
                                            'trailer' in data_source.lower())
                                
                                if not is_trailer:
                                    links.append({
                                        'name': player_name,
                                        'url': data_source,
                                        'quality': 'Unknown',
                                        'extractor': self.identify_extractor(data_source)
                                    })
                                    print(f"      ✅ Link válido adicionado")
                                else:
                                    print(f"      🚨 Trailer ignorado")
                            else:
                                print(f"      ❌ data-source inválido")
                    else:
                        print(f"   ❌ Erro na requisição AJAX: {ajax_response.status_code}")
                        print(f"   📄 Resposta: {ajax_response.text[:200]}...")
                else:
                    print("   ❌ Não foi possível extrair episodeId da URL")
            else:
                print("   ❌ URL não é do formato esperado (iframe playerthree)")
                
        except Exception as e:
            print(f"   ❌ Erro no loadLinks(): {e}")
        
        return links
    
    def identify_extractor(self, url):
        """Identificar qual extractor CloudStream usará"""
        extractors = {
            'playerembedapi.link': 'PlayerEmbedAPI',
            'megaembed.link': 'MegaEmbed',
            'doodstream.com': 'DoodStream',
            'streamtape.com': 'StreamTape',
            'mixdrop.co': 'MixDrop'
        }
        
        for domain, extractor in extractors.items():
            if domain in url:
                return extractor
        
        return 'Unknown'
    
    def test_extractor_detailed(self, link):
        """Testar extractor específico com debug detalhado"""
        print(f"\n🧪 3. TESTANDO EXTRACTOR: {link['extractor']}")
        print(f"   Player: {link['name']}")
        print(f"   URL: {link['url']}")
        
        try:
            # Testar acesso ao link
            response = self.session.get(link['url'], timeout=15)
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Link acessível")
                
                # Analisar conteúdo da página do player
                content = response.text
                
                # Procurar indicadores de vídeo
                video_indicators = {
                    'jwplayer': 'JWPlayer detectado',
                    'videojs': 'VideoJS detectado', 
                    'plyr': 'Plyr detectado',
                    'video': 'Tag video detectada',
                    'source': 'Tag source detectada',
                    '.m3u8': 'Stream HLS detectado',
                    '.mp4': 'Vídeo MP4 detectado'
                }
                
                found_indicators = []
                for indicator, description in video_indicators.items():
                    if indicator in content.lower():
                        found_indicators.append(description)
                
                if found_indicators:
                    print("   🎥 Indicadores de vídeo encontrados:")
                    for indicator in found_indicators:
                        print(f"      ✅ {indicator}")
                    
                    # Procurar URLs de vídeo específicas
                    self.extract_video_urls(content, link['extractor'])
                else:
                    print("   ⚠️ Nenhum indicador de vídeo encontrado")
                    print("   🔍 Procurando iframes aninhados...")
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    iframes = soup.select('iframe[src]')
                    
                    if iframes:
                        print(f"   🖼️ {len(iframes)} iframes encontrados:")
                        for i, iframe in enumerate(iframes[:3]):
                            iframe_src = iframe.get('src')
                            print(f"      {i+1}. {iframe_src}")
                    else:
                        print("   ❌ Nenhum iframe encontrado")
            else:
                print(f"   ❌ Link inacessível: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar extractor: {e}")
    
    def extract_video_urls(self, content, extractor):
        """Extrair URLs de vídeo do conteúdo"""
        print("   🔍 Procurando URLs de vídeo...")
        
        # Padrões específicos por extractor
        patterns = {
            'PlayerEmbedAPI': [
                r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
                r'"source"\s*:\s*"([^"]+\.mp4[^"]*)"',
                r'file:\s*"([^"]+)"'
            ],
            'MegaEmbed': [
                r'"file"\s*:\s*"([^"]+)"',
                r'source:\s*"([^"]+)"',
                r'src:\s*"([^"]+)"'
            ]
        }
        
        extractor_patterns = patterns.get(extractor, patterns['PlayerEmbedAPI'])
        
        video_urls = []
        for pattern in extractor_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match and ('http' in match or match.startswith('//')):
                    if match.startswith('//'):
                        match = 'https:' + match
                    video_urls.append(match)
        
        if video_urls:
            print(f"   🎯 {len(video_urls)} URLs de vídeo encontradas:")
            for i, url in enumerate(video_urls[:3]):
                print(f"      {i+1}. {url}")
                self.test_video_url(url)
        else:
            print("   ❌ Nenhuma URL de vídeo encontrada")
    
    def test_video_url(self, video_url):
        """Testar URL de vídeo específica"""
        try:
            response = self.session.head(video_url, timeout=10)
            content_type = response.headers.get('Content-Type', '')
            
            if response.status_code == 200:
                if 'video' in content_type or 'application/vnd.apple.mpegurl' in content_type:
                    print(f"         ✅ VÍDEO VÁLIDO: {content_type}")
                else:
                    print(f"         ⚠️ Tipo: {content_type}")
            else:
                print(f"         ❌ Status: {response.status_code}")
                
        except Exception as e:
            print(f"         ❌ Erro: {e}")
    
    def diagnose_loadlinks_failure(self, episode_url):
        """Diagnosticar falha no loadLinks"""
        print("\n🔍 DIAGNÓSTICO DE FALHA - loadLinks()")
        print("=" * 40)
        
        print("Possíveis causas:")
        print("1. ❌ Requisição AJAX falhando")
        print("2. ❌ Episode ID não extraído corretamente")
        print("3. ❌ Estrutura HTML mudou")
        print("4. ❌ Bloqueio por User-Agent")
        
        # Testar requisição AJAX manualmente
        if '#' in episode_url:
            fragment_match = re.search(r'#\d+_(\d+)', episode_url)
            if fragment_match:
                episode_id = fragment_match.group(1)
                ajax_url = f"https://playerthree.online/episodio/{episode_id}"
                
                print(f"\n🧪 Testando AJAX manualmente: {ajax_url}")
                
                try:
                    response = self.session.get(ajax_url)
                    print(f"Status: {response.status_code}")
                    print(f"Content-Length: {len(response.content)}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        buttons = soup.select('button, .btn')
                        print(f"Botões encontrados: {len(buttons)}")
                        
                        for button in buttons[:3]:
                            print(f"  - {button.get('class', [])} | {button.text.strip()}")
                            print(f"    data-source: {button.get('data-source', 'N/A')}")
                    
                except Exception as e:
                    print(f"Erro: {e}")
    
    def diagnose_load_failure(self, series_url):
        """Diagnosticar falha no load"""
        print("\n🔍 DIAGNÓSTICO DE FALHA - load()")
        print("=" * 40)
        
        try:
            response = self.session.get(series_url)
            print(f"Status da série: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                iframes = soup.select('iframe')
                print(f"Iframes encontrados: {len(iframes)}")
                
                for i, iframe in enumerate(iframes):
                    src = iframe.get('src', '')
                    print(f"  {i+1}. {src}")
            
        except Exception as e:
            print(f"Erro: {e}")

def main():
    debugger = CloudStreamPlaybackDebugger()
    
    print("🔍 INICIANDO DIAGNÓSTICO CLOUDSTREAM")
    print("Este diagnóstico simula exatamente o que acontece no CloudStream")
    print("quando você clica em um episódio para assistir")
    print()
    
    debugger.debug_complete_flow()
    
    print("\n" + "=" * 60)
    print("🎯 INTERPRETAÇÃO DOS RESULTADOS:")
    print()
    print("✅ Se vídeos válidos foram encontrados:")
    print("   → O plugin está funcionando, problema pode ser no CloudStream")
    print()
    print("❌ Se nenhum vídeo foi encontrado:")
    print("   → Problema no plugin, precisa de correção")
    print()
    print("⚠️ Se links foram encontrados mas não são vídeos:")
    print("   → Extractors podem não estar funcionando corretamente")

if __name__ == "__main__":
    main()