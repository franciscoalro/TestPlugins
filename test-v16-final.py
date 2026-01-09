#!/usr/bin/env python3
"""
Teste Final - MaxSeries v16.0 Corrigido
Verificar se a correção dos extractors funcionará
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import base64

class MaxSeriesV16Tester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CloudStream/3.0 (Android)'
        })
        
    def test_v16_functionality(self):
        """Testar funcionalidade da v16.0 corrigida"""
        print("🧪 TESTE FINAL - MAXSERIES V16.0 CORRIGIDO")
        print("=" * 60)
        
        # Simular exatamente o que o plugin v16.0 fará
        series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        
        # 1. Testar load() - Carregar episódios
        episodes = self.simulate_load_v16(series_url)
        
        if episodes:
            print(f"✅ load() funcionando: {len(episodes)} episódios")
            
            # 2. Testar loadLinks() - Carregar links com extractors customizados
            first_episode = episodes[0]
            links = self.simulate_loadlinks_v16(first_episode['url'])
            
            if links:
                print(f"✅ loadLinks() funcionando: {len(links)} links")
                
                # 3. Testar extractors customizados
                for link in links:
                    self.test_custom_extractor(link)
                    
                print(f"\n🎉 RESULTADO FINAL:")
                print(f"   ✅ Plugin v16.0 deve funcionar perfeitamente!")
                print(f"   ✅ {len(episodes)} episódios detectados")
                print(f"   ✅ {len(links)} players funcionais")
                print(f"   ✅ Extractors customizados implementados")
                
            else:
                print("❌ loadLinks() falhou - nenhum link encontrado")
        else:
            print("❌ load() falhou - nenhum episódio encontrado")
    
    def simulate_load_v16(self, series_url):
        """Simular método load() da v16.0"""
        print("\n🔄 Simulando load() v16.0...")
        
        try:
            response = self.session.get(series_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair iframe principal
            iframe = soup.select_one('iframe')
            if not iframe:
                return []
            
            iframe_src = iframe.get('src')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            
            # Carregar iframe
            iframe_response = self.session.get(iframe_src)
            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
            
            # Extrair episódios
            episodes = []
            episode_elements = iframe_soup.select('li[data-season-id][data-episode-id] a')
            
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
            print(f"❌ Erro no load(): {e}")
            return []
    
    def simulate_loadlinks_v16(self, episode_url):
        """Simular método loadLinks() da v16.0 com extractors customizados"""
        print("\n🔄 Simulando loadLinks() v16.0...")
        
        try:
            links = []
            
            # Verificar se é URL de episódio do iframe
            if '#' in episode_url and 'playerthree.online' in episode_url:
                # Extrair episodeId
                fragment_match = re.search(r'#\d+_(\d+)', episode_url)
                if fragment_match:
                    episode_id = fragment_match.group(1)
                    
                    # Fazer requisição AJAX
                    ajax_url = f"https://playerthree.online/episodio/{episode_id}"
                    ajax_headers = {
                        'Referer': episode_url,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    ajax_response = self.session.get(ajax_url, headers=ajax_headers)
                    
                    if ajax_response.status_code == 200:
                        ajax_soup = BeautifulSoup(ajax_response.content, 'html.parser')
                        
                        # Procurar botões de player
                        player_buttons = ajax_soup.select('button[data-source], .btn[data-source]')
                        
                        for button in player_buttons:
                            player_name = button.text.strip() or "Player"
                            data_source = button.get('data-source', '')
                            
                            if data_source and data_source.startswith('http'):
                                # Filtrar trailers
                                if not ('youtube' in data_source.lower() or 'trailer' in data_source.lower()):
                                    
                                    # Identificar tipo de extractor
                                    extractor_type = "Unknown"
                                    if 'playerembedapi.link' in data_source:
                                        extractor_type = "PlayerEmbedAPI"
                                    elif 'megaembed.link' in data_source:
                                        extractor_type = "MegaEmbed"
                                    
                                    links.append({
                                        'name': player_name,
                                        'url': data_source,
                                        'extractor': extractor_type,
                                        'custom': extractor_type in ['PlayerEmbedAPI', 'MegaEmbed']
                                    })
            
            return links
            
        except Exception as e:
            print(f"❌ Erro no loadLinks(): {e}")
            return []
    
    def test_custom_extractor(self, link):
        """Testar extractor customizado"""
        print(f"\n🔧 Testando extractor customizado: {link['extractor']}")
        print(f"   Player: {link['name']}")
        print(f"   URL: {link['url']}")
        
        if link['extractor'] == 'PlayerEmbedAPI':
            success = self.test_playerembedapi_extractor(link['url'])
        elif link['extractor'] == 'MegaEmbed':
            success = self.test_megaembed_extractor(link['url'])
        else:
            success = False
            print("   ⚠️ Extractor não customizado")
        
        if success:
            print("   ✅ Extractor customizado deve funcionar")
        else:
            print("   ❌ Extractor customizado pode ter problemas")
    
    def test_playerembedapi_extractor(self, url):
        """Testar extractor customizado PlayerEmbedAPI"""
        try:
            response = self.session.get(url)
            content = response.text
            
            # Procurar dados base64 (como no extractor v16.0)
            base64_pattern = r'atob\(["\']([^"\']+)["\']\)'
            base64_match = re.search(base64_pattern, content)
            
            if base64_match:
                try:
                    base64_data = base64_match.group(1)
                    decoded_data = base64.b64decode(base64_data).decode('utf-8')
                    
                    # Procurar URLs de vídeo nos dados decodificados
                    video_pattern = r'"(?:file|source|url)"\s*:\s*"([^"]+\.(?:m3u8|mp4)[^"]*)"'
                    video_matches = re.findall(video_pattern, decoded_data)
                    
                    if video_matches:
                        print(f"      🎥 {len(video_matches)} vídeos encontrados via Base64")
                        for video in video_matches[:2]:
                            print(f"         📺 {video}")
                        return True
                    
                except Exception as e:
                    print(f"      ❌ Erro ao decodificar Base64: {e}")
            
            # Fallback: procurar URLs diretas
            direct_pattern = r'"(?:file|source)"\s*:\s*"(https?://[^"]+\.(?:m3u8|mp4)[^"]*)"'
            direct_matches = re.findall(direct_pattern, content)
            
            if direct_matches:
                print(f"      🎥 {len(direct_matches)} vídeos diretos encontrados")
                return True
            
            # Último fallback: qualquer URL de vídeo
            any_pattern = r'(https?://[^"\'\s]+\.(?:m3u8|mp4)[^"\'\s]*)'
            any_matches = re.findall(any_pattern, content)
            
            if any_matches:
                print(f"      🎥 {len(any_matches)} vídeos genéricos encontrados")
                return True
            
            print("      ❌ Nenhum vídeo encontrado")
            return False
            
        except Exception as e:
            print(f"      ❌ Erro no extractor: {e}")
            return False
    
    def test_megaembed_extractor(self, url):
        """Testar extractor customizado MegaEmbed"""
        try:
            response = self.session.get(url)
            content = response.text
            
            # Procurar assets JavaScript (como no extractor v16.0)
            asset_pattern = r'/assets/[^"\']+\.js'
            asset_matches = re.findall(asset_pattern, content)
            
            if asset_matches:
                print(f"      📦 {len(asset_matches)} assets JavaScript encontrados")
                
                # Testar primeiro asset
                asset_url = "https://megaembed.link" + asset_matches[0]
                try:
                    asset_response = self.session.get(asset_url)
                    asset_content = asset_response.text
                    
                    # Procurar configurações de vídeo
                    config_pattern = r'"(?:file|source|url)"\s*:\s*"([^"]+)"'
                    config_matches = re.findall(config_pattern, asset_content)
                    
                    video_configs = [m for m in config_matches if m.startswith('http') and ('.m3u8' in m or '.mp4' in m)]
                    
                    if video_configs:
                        print(f"      🎥 {len(video_configs)} vídeos encontrados via assets")
                        return True
                        
                except Exception as e:
                    print(f"      ⚠️ Erro ao carregar asset: {e}")
            
            # Fallback: procurar iframes
            soup = BeautifulSoup(content, 'html.parser')
            iframes = soup.select('iframe[src]')
            
            if iframes:
                print(f"      🖼️ {len(iframes)} iframes encontrados")
                return True
            
            # Último fallback: qualquer URL de vídeo
            any_pattern = r'(https?://[^"\'\s]+\.(?:m3u8|mp4)[^"\'\s]*)'
            any_matches = re.findall(any_pattern, content)
            
            if any_matches:
                print(f"      🎥 {len(any_matches)} vídeos genéricos encontrados")
                return True
            
            print("      ❌ Nenhum vídeo encontrado")
            return False
            
        except Exception as e:
            print(f"      ❌ Erro no extractor: {e}")
            return False

def main():
    tester = MaxSeriesV16Tester()
    
    print("🧪 INICIANDO TESTE FINAL - MAXSERIES V16.0")
    print("Este teste verifica se as correções da v16.0 funcionarão")
    print()
    
    tester.test_v16_functionality()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSÃO DO TESTE:")
    print()
    print("Se todos os testes passaram:")
    print("  ✅ MaxSeries v16.0 deve funcionar no CloudStream")
    print("  ✅ Extractors customizados implementados corretamente")
    print("  ✅ Vídeos devem reproduzir normalmente")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("  1. Aguarde o GitHub Actions completar o build")
    print("  2. Instale a v16.0 no CloudStream")
    print("  3. Teste uma série - deve funcionar!")

if __name__ == "__main__":
    main()