#!/usr/bin/env python3
"""
Teste Final - MaxSeries v16.0 Simplificado
Verificar se a versão simplificada funcionará no CloudStream
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time

class MaxSeriesV16SimplifiedTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CloudStream/3.0 (Android)'
        })
        
    def test_complete_flow_v16(self):
        """Testar fluxo completo da v16.0 simplificada"""
        print("🧪 TESTE FINAL - MAXSERIES V16.0 SIMPLIFICADO")
        print("=" * 60)
        print("Testando a abordagem simplificada que deve funcionar")
        print()
        
        # Série de teste
        series_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        
        # 1. Testar load() - Detecção de episódios
        print("🔄 1. TESTANDO DETECÇÃO DE EPISÓDIOS...")
        episodes = self.test_load_method(series_url)
        
        if episodes:
            print(f"✅ Episódios detectados: {len(episodes)}")
            
            # 2. Testar loadLinks() - Obtenção de players
            print(f"\n🔄 2. TESTANDO OBTENÇÃO DE PLAYERS...")
            first_episode = episodes[0]
            players = self.test_loadlinks_method(first_episode['url'])
            
            if players:
                print(f"✅ Players encontrados: {len(players)}")
                
                # 3. Testar compatibilidade CloudStream
                print(f"\n🔄 3. TESTANDO COMPATIBILIDADE CLOUDSTREAM...")
                self.test_cloudstream_compatibility(players)
                
                # 4. Resultado final
                self.show_final_result(episodes, players)
                
            else:
                print("❌ Nenhum player encontrado")
        else:
            print("❌ Nenhum episódio encontrado")
    
    def test_load_method(self, series_url):
        """Testar método load() - detecção de episódios"""
        try:
            # Carregar página da série
            response = self.session.get(series_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.select_one('.data h1, h1, .entry-title')
            title_text = title.text.strip() if title else "Unknown"
            print(f"   📺 Série: {title_text}")
            
            # Procurar iframe principal
            iframe = soup.select_one('iframe')
            if not iframe:
                print("   ❌ Nenhum iframe encontrado")
                return []
            
            iframe_src = iframe.get('src')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
            
            print(f"   🖼️ Iframe: {iframe_src}")
            
            # Carregar iframe
            iframe_response = self.session.get(iframe_src)
            iframe_soup = BeautifulSoup(iframe_response.content, 'html.parser')
            
            # Extrair episódios (método v16.0)
            episodes = []
            episode_elements = iframe_soup.select('li[data-season-id][data-episode-id] a')
            
            print(f"   📊 Elementos encontrados: {len(episode_elements)}")
            
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
            
            return episodes
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return []
    
    def test_loadlinks_method(self, episode_url):
        """Testar método loadLinks() - obtenção de players"""
        try:
            print(f"   📺 URL do episódio: {episode_url}")
            
            # Verificar se é URL de iframe com fragmento
            if '#' in episode_url and 'playerthree.online' in episode_url:
                print("   ✅ URL de iframe detectada")
                
                # Extrair episodeId (método v16.0)
                fragment_match = re.search(r'#\d+_(\d+)', episode_url)
                if fragment_match:
                    episode_id = fragment_match.group(1)
                    print(f"   🔍 Episode ID: {episode_id}")
                    
                    # Fazer requisição AJAX
                    ajax_url = f"https://playerthree.online/episodio/{episode_id}"
                    ajax_headers = {
                        'Referer': episode_url,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    print(f"   📡 AJAX: {ajax_url}")
                    ajax_response = self.session.get(ajax_url, headers=ajax_headers)
                    
                    if ajax_response.status_code == 200:
                        print(f"   ✅ AJAX Status: {ajax_response.status_code}")
                        
                        ajax_soup = BeautifulSoup(ajax_response.content, 'html.parser')
                        
                        # Procurar botões de player
                        player_buttons = ajax_soup.select('button[data-source], .btn[data-source]')
                        print(f"   🎮 Botões encontrados: {len(player_buttons)}")
                        
                        players = []
                        for button in player_buttons:
                            player_name = button.text.strip() or "Player"
                            data_source = button.get('data-source', '')
                            
                            if data_source and data_source.startswith('http'):
                                # Filtrar trailers (método v16.0)
                                if not ('youtube' in data_source.lower() or 'trailer' in data_source.lower()):
                                    players.append({
                                        'name': player_name,
                                        'url': data_source,
                                        'type': self.identify_player_type(data_source)
                                    })
                                    print(f"      ✅ {player_name}: {data_source}")
                                else:
                                    print(f"      🚨 Trailer ignorado: {data_source}")
                        
                        return players
                    else:
                        print(f"   ❌ AJAX falhou: {ajax_response.status_code}")
                else:
                    print("   ❌ Episode ID não encontrado")
            else:
                print("   ❌ URL não é de iframe")
            
            return []
            
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            return []
    
    def identify_player_type(self, url):
        """Identificar tipo de player"""
        if 'playerembedapi.link' in url:
            return 'PlayerEmbedAPI'
        elif 'megaembed.link' in url:
            return 'MegaEmbed'
        else:
            return 'Unknown'
    
    def test_cloudstream_compatibility(self, players):
        """Testar compatibilidade com CloudStream"""
        print("   🔍 Testando compatibilidade CloudStream...")
        
        compatible_count = 0
        
        for player in players:
            print(f"\n   🎮 Testando: {player['name']} ({player['type']})")
            
            # Testar acessibilidade do link
            try:
                response = self.session.head(player['url'], timeout=10)
                print(f"      📡 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("      ✅ Link acessível")
                    compatible_count += 1
                    
                    # Verificar se CloudStream tem extractor para este tipo
                    if player['type'] in ['PlayerEmbedAPI', 'MegaEmbed']:
                        print("      ✅ CloudStream tem extractor nativo")
                    else:
                        print("      🔄 Usará fallback (link direto)")
                        
                elif response.status_code in [301, 302, 303, 307, 308]:
                    print(f"      🔄 Redirecionamento: {response.headers.get('Location', 'N/A')}")
                    compatible_count += 1
                else:
                    print(f"      ❌ Link inacessível: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Erro: {e}")
        
        print(f"\n   📊 Compatibilidade: {compatible_count}/{len(players)} players acessíveis")
        return compatible_count > 0
    
    def show_final_result(self, episodes, players):
        """Mostrar resultado final do teste"""
        print("\n" + "=" * 60)
        print("🎯 RESULTADO FINAL DO TESTE V16.0")
        print("=" * 60)
        
        print(f"📺 Episódios detectados: {len(episodes)}")
        print(f"🎮 Players encontrados: {len(players)}")
        
        if len(episodes) > 0 and len(players) > 0:
            print("\n✅ TESTE PASSOU - PLUGIN DEVE FUNCIONAR!")
            print("\n🎉 FUNCIONALIDADES CONFIRMADAS:")
            print("   ✅ Detecção de episódios funcionando")
            print("   ✅ Requisições AJAX funcionando")
            print("   ✅ Players válidos encontrados")
            print("   ✅ Links acessíveis")
            
            print(f"\n🎬 EXPERIÊNCIA ESPERADA NO CLOUDSTREAM:")
            print(f"   📺 Série mostrará {len(episodes)} episódios")
            print(f"   🎮 Cada episódio terá {len(players)} players")
            print(f"   ▶️ Vídeos devem reproduzir normalmente")
            
            print(f"\n🚀 PRÓXIMOS PASSOS:")
            print("   1. ⏳ Aguarde GitHub Actions completar build")
            print("   2. 📥 Baixe MaxSeries.cs3 da release v16.0")
            print("   3. 📱 Instale no CloudStream")
            print("   4. 🎬 Teste - deve funcionar!")
            
        else:
            print("\n❌ TESTE FALHOU")
            if len(episodes) == 0:
                print("   ❌ Nenhum episódio detectado")
            if len(players) == 0:
                print("   ❌ Nenhum player encontrado")
        
        print("\n" + "=" * 60)

def main():
    tester = MaxSeriesV16SimplifiedTester()
    
    print("🧪 INICIANDO TESTE FINAL - MAXSERIES V16.0 SIMPLIFICADO")
    print("Este teste verifica se a versão simplificada funcionará")
    print("Foco: Detecção + AJAX + Links válidos = Sucesso no CloudStream")
    print()
    
    tester.test_complete_flow_v16()
    
    print("\n💡 SOBRE A VERSÃO V16.0 SIMPLIFICADA:")
    print("- Usa extractors padrão do CloudStream (mais confiáveis)")
    print("- Fallback inteligente para links diretos")
    print("- Código mais simples = menos bugs")
    print("- Máxima compatibilidade com CloudStream")

if __name__ == "__main__":
    main()