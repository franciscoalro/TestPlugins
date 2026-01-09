#!/usr/bin/env python3
"""
Análise Profunda dos Players - MaxSeries
Investigar por que os extractors CloudStream não funcionam
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

class DeepPlayerAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def analyze_all_players(self):
        """Analisar todos os players encontrados"""
        print("🔬 ANÁLISE PROFUNDA DOS PLAYERS")
        print("=" * 50)
        
        # Players reais encontrados
        players = [
            {
                'name': 'PlayerEmbedAPI',
                'url': 'https://playerembedapi.link/?v=kBJLtxCD3',
                'extractor': 'PlayerEmbedAPI'
            },
            {
                'name': 'MegaEmbed',
                'url': 'https://megaembed.link/#3wnuij',
                'extractor': 'MegaEmbed'
            }
        ]
        
        for player in players:
            print(f"\n{'='*60}")
            self.analyze_player_deep(player)
    
    def analyze_player_deep(self, player):
        """Análise profunda de um player específico"""
        print(f"🎮 ANALISANDO: {player['name']}")
        print(f"   URL: {player['url']}")
        print(f"   Extractor esperado: {player['extractor']}")
        
        try:
            # Carregar página do player
            response = self.session.get(player['url'], timeout=15)
            print(f"   📡 Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ Erro ao carregar: {response.status_code}")
                return
            
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Salvar HTML para análise
            filename = f"player_{player['name'].lower()}_analysis.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   💾 HTML salvo em: {filename}")
            
            # 1. Analisar estrutura HTML
            self.analyze_html_structure(soup, player['name'])
            
            # 2. Analisar JavaScript
            self.analyze_javascript(content, player['name'])
            
            # 3. Procurar URLs de vídeo
            self.find_video_urls(content, player['name'])
            
            # 4. Analisar iframes aninhados
            self.analyze_nested_iframes(soup, player['name'])
            
            # 5. Testar padrões específicos do extractor
            self.test_extractor_patterns(content, player['extractor'])
            
        except Exception as e:
            print(f"   ❌ Erro na análise: {e}")
    
    def analyze_html_structure(self, soup, player_name):
        """Analisar estrutura HTML do player"""
        print(f"\n   🏗️ ESTRUTURA HTML - {player_name}")
        
        # Elementos de vídeo
        video_elements = soup.select('video, source')
        print(f"      Tags de vídeo: {len(video_elements)}")
        
        for video in video_elements:
            src = video.get('src', '')
            if src:
                print(f"         📺 {video.name}: {src}")
        
        # Iframes
        iframes = soup.select('iframe')
        print(f"      Iframes: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            src = iframe.get('src', '')
            print(f"         🖼️ Iframe {i+1}: {src}")
        
        # Divs de player
        player_divs = soup.select('div[id*="player"], div[class*="player"], div[id*="video"], div[class*="video"]')
        print(f"      Divs de player: {len(player_divs)}")
        
        for div in player_divs:
            div_id = div.get('id', '')
            div_class = ' '.join(div.get('class', []))
            print(f"         📦 ID: {div_id}, Class: {div_class}")
    
    def analyze_javascript(self, content, player_name):
        """Analisar JavaScript do player"""
        print(f"\n   🔧 JAVASCRIPT - {player_name}")
        
        # Procurar scripts inline
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.select('script')
        
        print(f"      Scripts encontrados: {len(scripts)}")
        
        js_patterns = {
            'jwplayer': r'jwplayer\([^)]+\)',
            'videojs': r'videojs\([^)]+\)',
            'plyr': r'new Plyr\([^)]+\)',
            'file_config': r'"file"\s*:\s*"([^"]+)"',
            'source_config': r'"source"\s*:\s*"([^"]+)"',
            'sources_array': r'"sources"\s*:\s*\[([^\]]+)\]',
            'm3u8_urls': r'https?://[^"\s]+\.m3u8[^"\s]*',
            'mp4_urls': r'https?://[^"\s]+\.mp4[^"\s]*'
        }
        
        for script in scripts:
            script_content = script.string or ''
            if len(script_content) > 50:  # Apenas scripts com conteúdo
                print(f"\n      📜 Script ({len(script_content)} chars):")
                
                for pattern_name, pattern in js_patterns.items():
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    if matches:
                        print(f"         ✅ {pattern_name}: {len(matches)} matches")
                        for match in matches[:3]:  # Primeiros 3
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else match[1]
                            print(f"            🎯 {match}")
    
    def find_video_urls(self, content, player_name):
        """Procurar URLs de vídeo no conteúdo"""
        print(f"\n   🎥 URLS DE VÍDEO - {player_name}")
        
        # Padrões para diferentes tipos de vídeo
        video_patterns = {
            'HLS (m3u8)': r'https?://[^"\s]+\.m3u8[^"\s]*',
            'MP4': r'https?://[^"\s]+\.mp4[^"\s]*',
            'DASH': r'https?://[^"\s]+\.mpd[^"\s]*',
            'WebM': r'https?://[^"\s]+\.webm[^"\s]*',
            'Generic Video': r'"(?:file|source|src)"\s*:\s*"(https?://[^"]+)"'
        }
        
        total_found = 0
        
        for pattern_name, pattern in video_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"      ✅ {pattern_name}: {len(matches)} encontradas")
                total_found += len(matches)
                
                for match in matches[:2]:  # Primeiras 2
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    print(f"         🎯 {match}")
                    
                    # Testar se a URL é válida
                    self.test_video_url_quick(match)
        
        if total_found == 0:
            print("      ❌ Nenhuma URL de vídeo encontrada")
    
    def analyze_nested_iframes(self, soup, player_name):
        """Analisar iframes aninhados"""
        print(f"\n   🖼️ IFRAMES ANINHADOS - {player_name}")
        
        iframes = soup.select('iframe[src]')
        
        if not iframes:
            print("      ❌ Nenhum iframe encontrado")
            return
        
        print(f"      📊 {len(iframes)} iframes encontrados")
        
        for i, iframe in enumerate(iframes[:3]):  # Primeiros 3
            src = iframe.get('src', '')
            if src:
                print(f"\n      🖼️ Iframe {i+1}: {src}")
                
                # Tentar carregar iframe
                try:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        # URL relativa
                        base_url = player_name.lower().replace('embed', '') + '.link'
                        src = f'https://{base_url}{src}'
                    
                    iframe_response = self.session.get(src, timeout=10)
                    print(f"         📡 Status: {iframe_response.status_code}")
                    
                    if iframe_response.status_code == 200:
                        iframe_content = iframe_response.text
                        
                        # Procurar vídeos no iframe
                        video_matches = re.findall(r'https?://[^"\s]+\.(?:m3u8|mp4)[^"\s]*', iframe_content)
                        if video_matches:
                            print(f"         🎥 Vídeos no iframe: {len(video_matches)}")
                            for video in video_matches[:2]:
                                print(f"            📺 {video}")
                        else:
                            print("         ❌ Nenhum vídeo no iframe")
                    
                except Exception as e:
                    print(f"         ❌ Erro ao carregar iframe: {e}")
    
    def test_extractor_patterns(self, content, extractor_name):
        """Testar padrões específicos do extractor CloudStream"""
        print(f"\n   🔍 PADRÕES DO EXTRACTOR - {extractor_name}")
        
        # Padrões conhecidos dos extractors CloudStream
        extractor_patterns = {
            'PlayerEmbedAPI': {
                'config_pattern': r'var\s+config\s*=\s*({[^}]+})',
                'jwplayer_setup': r'jwplayer\([^)]+\)\.setup\(([^)]+)\)',
                'file_pattern': r'"file"\s*:\s*"([^"]+)"',
                'sources_pattern': r'"sources"\s*:\s*\[([^\]]+)\]'
            },
            'MegaEmbed': {
                'player_setup': r'player\s*=\s*new\s+[^(]+\(([^)]+)\)',
                'source_pattern': r'"source"\s*:\s*"([^"]+)"',
                'url_pattern': r'"url"\s*:\s*"([^"]+)"',
                'embed_pattern': r'embed\s*:\s*"([^"]+)"'
            }
        }
        
        patterns = extractor_patterns.get(extractor_name, {})
        
        if not patterns:
            print(f"      ⚠️ Padrões não definidos para {extractor_name}")
            return
        
        found_any = False
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"      ✅ {pattern_name}: {len(matches)} matches")
                found_any = True
                
                for match in matches[:2]:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    
                    # Limitar tamanho da saída
                    display_match = match[:100] + '...' if len(match) > 100 else match
                    print(f"         🎯 {display_match}")
        
        if not found_any:
            print(f"      ❌ Nenhum padrão do {extractor_name} encontrado")
            print(f"      💡 Isso explica por que o extractor CloudStream falha")
    
    def test_video_url_quick(self, url):
        """Teste rápido de URL de vídeo"""
        try:
            response = self.session.head(url, timeout=5)
            content_type = response.headers.get('Content-Type', '')
            
            if response.status_code == 200:
                if 'video' in content_type or 'application/vnd.apple.mpegurl' in content_type:
                    print(f"            ✅ VÍDEO VÁLIDO ({content_type})")
                else:
                    print(f"            ⚠️ Tipo: {content_type}")
            else:
                print(f"            ❌ Status: {response.status_code}")
                
        except:
            print(f"            ❌ Inacessível")

def main():
    analyzer = DeepPlayerAnalyzer()
    
    print("🔬 INICIANDO ANÁLISE PROFUNDA DOS PLAYERS")
    print("Esta análise vai descobrir por que os extractors CloudStream não funcionam")
    print()
    
    analyzer.analyze_all_players()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSÕES DA ANÁLISE:")
    print()
    print("Se nenhuma URL de vídeo foi encontrada:")
    print("  → Os players usam JavaScript complexo para carregar vídeos")
    print("  → CloudStream extractors podem estar desatualizados")
    print("  → Pode ser necessário criar extractors customizados")
    print()
    print("Se URLs foram encontradas mas não funcionam:")
    print("  → Problema de autenticação ou headers")
    print("  → Vídeos podem exigir tokens específicos")
    print()
    print("📁 Arquivos gerados para análise manual:")
    print("  - player_playerembedapi_analysis.html")
    print("  - player_megaembed_analysis.html")

if __name__ == "__main__":
    main()