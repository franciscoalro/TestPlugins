#!/usr/bin/env python3
"""
Teste Rápido - MaxSeries Provider
Verifica se está capturando links corretamente
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse
import time

class MaxSeriesQuickTest:
    def __init__(self):
        self.base_url = "https://www.maxseries.one"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def test_homepage(self):
        """Teste 1: Verificar se consegue acessar homepage"""
        print("🔍 Teste 1: Acessando homepage...")
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Homepage acessível: {response.status_code}")
                
                # Verificar se tem conteúdo
                content_items = re.findall(r'<article class="item"', response.text)
                print(f"📺 Encontrados {len(content_items)} itens na homepage")
                return True
            else:
                print(f"❌ Erro na homepage: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao acessar homepage: {e}")
            return False
    
    def test_search(self):
        """Teste 2: Verificar busca"""
        print("\n🔍 Teste 2: Testando busca...")
        try:
            search_url = f"{self.base_url}/?s=breaking+bad"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Busca funcionando: {response.status_code}")
                
                # Verificar resultados
                results = re.findall(r'<div class="result-item"', response.text)
                print(f"🔎 Encontrados {len(results)} resultados para 'breaking bad'")
                
                # Extrair primeiro resultado
                title_match = re.search(r'<div class="details">.*?<div class="title">.*?<a[^>]*>([^<]+)</a>', response.text, re.DOTALL)
                if title_match:
                    print(f"📺 Primeiro resultado: {title_match.group(1).strip()}")
                    return True
                else:
                    print("⚠️ Nenhum título encontrado nos resultados")
                    return False
            else:
                print(f"❌ Erro na busca: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return False
    
    def test_content_page(self):
        """Teste 3: Verificar página de conteúdo"""
        print("\n🔍 Teste 3: Testando página de conteúdo...")
        try:
            # Pegar primeiro item da homepage
            homepage = self.session.get(self.base_url, timeout=10)
            
            # Extrair link do primeiro item
            item_match = re.search(r'<article class="item">.*?<div class="data">.*?<h3>.*?<a href="([^"]+)"', homepage.text, re.DOTALL)
            
            if not item_match:
                print("❌ Não conseguiu extrair link de conteúdo da homepage")
                return False
                
            content_url = item_match.group(1)
            print(f"🔗 Testando: {content_url}")
            
            response = self.session.get(content_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Página de conteúdo acessível: {response.status_code}")
                
                # Verificar se tem iframe (player)
                iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', response.text)
                if iframe_match:
                    iframe_url = iframe_match.group(1)
                    if iframe_url.startswith('//'):
                        iframe_url = 'https:' + iframe_url
                    print(f"🎬 Player encontrado: {iframe_url}")
                    return iframe_url
                else:
                    print("⚠️ Nenhum iframe/player encontrado")
                    return False
            else:
                print(f"❌ Erro na página de conteúdo: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao testar página de conteúdo: {e}")
            return False
    
    def test_player_extraction(self, player_url):
        """Teste 4: Verificar extração do player"""
        print(f"\n🔍 Teste 4: Testando extração do player...")
        print(f"🎬 Player URL: {player_url}")
        
        try:
            response = self.session.get(player_url, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ Player acessível: {response.status_code}")
                
                # Verificar tipo de player
                player_type = "Desconhecido"
                if "megaembed" in player_url.lower():
                    player_type = "MegaEmbed"
                elif "playerembedapi" in player_url.lower():
                    player_type = "PlayerEmbedAPI"
                elif any(domain in player_url.lower() for domain in ["myvidplay", "bysebuho", "g9r6", "doodstream"]):
                    player_type = "DoodStream Clone"
                
                print(f"🎯 Tipo de player: {player_type}")
                
                # Tentar encontrar padrões de vídeo
                video_patterns = [
                    r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                    r'source:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                    r'["\']([^"\']*storage\.googleapis\.com[^"\']*\.mp4[^"\']*)["\']',
                    r'/pass_md5/([^"\']+)',
                    r'["\']([^"\']+\.mp4[^"\']*)["\']'
                ]
                
                found_patterns = []
                for pattern in video_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        found_patterns.extend(matches)
                
                if found_patterns:
                    print(f"🎥 Padrões de vídeo encontrados: {len(found_patterns)}")
                    for i, pattern in enumerate(found_patterns[:3]):  # Mostrar apenas os 3 primeiros
                        print(f"   {i+1}. {pattern[:80]}...")
                    return True
                else:
                    print("⚠️ Nenhum padrão de vídeo encontrado no HTML")
                    
                    # Verificar se precisa de JavaScript
                    if "eval(function(p,a,c,k,e" in response.text:
                        print("🔧 Player usa JavaScript empacotado (P.A.C.K.E.R.)")
                    if "jwplayer" in response.text.lower():
                        print("🔧 Player usa JWPlayer")
                    if "<video" in response.text.lower():
                        print("🔧 Player tem elemento <video>")
                    
                    return False
            else:
                print(f"❌ Erro ao acessar player: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar player: {e}")
            return False
    
    def test_doodstream_api(self):
        """Teste 5: Verificar se DoodStream clones estão funcionando"""
        print(f"\n🔍 Teste 5: Testando DoodStream clones...")
        
        dood_domains = [
            "https://myvidplay.com",
            "https://bysebuho.com", 
            "https://g9r6.com"
        ]
        
        working_domains = []
        
        for domain in dood_domains:
            try:
                print(f"🔗 Testando: {domain}")
                response = self.session.get(domain, timeout=8)
                if response.status_code == 200:
                    print(f"   ✅ {domain} - OK")
                    working_domains.append(domain)
                else:
                    print(f"   ❌ {domain} - {response.status_code}")
            except Exception as e:
                print(f"   ❌ {domain} - Erro: {str(e)[:50]}")
        
        print(f"📊 Domínios DoodStream funcionando: {len(working_domains)}/{len(dood_domains)}")
        return len(working_domains) > 0
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🚀 TESTE RÁPIDO - MAXSERIES PROVIDER")
        print("=" * 50)
        
        results = {}
        
        # Teste 1: Homepage
        results['homepage'] = self.test_homepage()
        
        # Teste 2: Busca
        results['search'] = self.test_search()
        
        # Teste 3: Página de conteúdo
        player_url = self.test_content_page()
        results['content_page'] = bool(player_url)
        
        # Teste 4: Player (se encontrou)
        if player_url:
            results['player_extraction'] = self.test_player_extraction(player_url)
        else:
            results['player_extraction'] = False
        
        # Teste 5: DoodStream domains
        results['doodstream_domains'] = self.test_doodstream_api()
        
        # Resumo
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES:")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, result in results.items():
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n🎯 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
        
        if passed_tests >= 3:
            print("🏆 MAXSERIES ESTÁ FUNCIONANDO CORRETAMENTE!")
        elif passed_tests >= 2:
            print("⚠️ MAXSERIES FUNCIONANDO PARCIALMENTE")
        else:
            print("❌ MAXSERIES COM PROBLEMAS SÉRIOS")
        
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = MaxSeriesQuickTest()
    tester.run_all_tests()