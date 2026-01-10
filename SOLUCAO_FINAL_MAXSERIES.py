#!/usr/bin/env python3
"""
🏆 SOLUÇÃO FINAL - MAXSERIES PROVIDER
Implementação HTTP pura baseada na engenharia reversa completa
"""

import requests
import re
import json
import time
import random
import string
from urllib.parse import urljoin, urlparse

class MaxSeriesHTTPExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
    
    def extract_maxseries_video(self, maxseries_url):
        """Extração completa do MaxSeries - HTTP puro"""
        print(f"🎬 EXTRAÇÃO MAXSERIES: {maxseries_url}")
        print("=" * 80)
        
        try:
            # PASSO 1: Obter iframe do player
            print("📡 PASSO 1: Obtendo iframe do player...")
            
            response = self.session.get(maxseries_url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Erro na página: {response.status_code}")
                return None
            
            # Extrair iframe
            iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', response.text)
            if not iframe_match:
                print("❌ Nenhum iframe encontrado")
                return None
            
            player_url = iframe_match.group(1)
            if player_url.startswith('//'):
                player_url = 'https:' + player_url
            
            print(f"✅ Player URL: {player_url}")
            
            # PASSO 2: Identificar tipo de player e extrair
            if 'playerthree' in player_url.lower():
                return self.extract_playerthree_sources(player_url)
            elif 'megaembed' in player_url.lower():
                return self.extract_megaembed_direct(player_url)
            elif 'playerembedapi' in player_url.lower():
                return self.extract_playerembedapi_direct(player_url)
            elif any(d in player_url.lower() for d in ['myvidplay', 'bysebuho', 'g9r6', 'doodstream']):
                return self.extract_doodstream_direct(player_url)
            else:
                print(f"⚠️ Player desconhecido: {player_url}")
                return None
                
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            return None
    
    def extract_playerthree_sources(self, player_url):
        """Extrair sources do PlayerThree via AJAX"""
        print(f"\n🎯 EXTRAÇÃO PLAYERTHREE")
        print("-" * 40)
        
        try:
            # Extrair série da URL
            series_match = re.search(r'/embed/([^/]+)', player_url)
            if not series_match:
                print("❌ Não conseguiu extrair série da URL")
                return None
            
            series_name = series_match.group(1)
            print(f"📺 Série: {series_name}")
            
            # Acessar player para obter estrutura
            response = self.session.get(player_url, timeout=15)
            html = response.text
            
            # Extrair primeiro episódio (ID)
            episode_match = re.search(r'data-episode-id="(\d+)"', html)
            if not episode_match:
                print("❌ Nenhum episódio encontrado")
                return None
            
            episode_id = episode_match.group(1)
            print(f"🆔 Episode ID: {episode_id}")
            
            # Chamar endpoint /episodio/{id} para obter sources
            base_domain = urlparse(player_url).netloc
            episodio_url = f"https://{base_domain}/episodio/{episode_id}"
            
            print(f"🔗 Chamando: {episodio_url}")
            
            ajax_headers = {
                'Referer': player_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            episodio_response = self.session.get(episodio_url, headers=ajax_headers, timeout=10)
            
            if episodio_response.status_code == 200:
                print("✅ Episódio carregado com sucesso")
                
                # Extrair botões source
                source_buttons = re.findall(r'data-source="([^"]+)"', episodio_response.text)
                
                if source_buttons:
                    print(f"🔘 Sources encontrados: {len(source_buttons)}")
                    
                    for i, source_url in enumerate(source_buttons):
                        print(f"   {i+1}. {source_url}")
                        
                        # Processar cada source
                        video_url = self.process_source_url(source_url, player_url)
                        if video_url:
                            return video_url
                else:
                    print("❌ Nenhum source encontrado")
            else:
                print(f"❌ Erro no episódio: {episodio_response.status_code}")
            
            return None
            
        except Exception as e:
            print(f"❌ Erro PlayerThree: {e}")
            return None
    
    def process_source_url(self, source_url, referer):
        """Processar URL de source específica"""
        print(f"\n🔍 Processando source: {source_url}")
        
        try:
            if 'megaembed' in source_url.lower():
                return self.extract_megaembed_direct(source_url, referer)
            elif 'playerembedapi' in source_url.lower():
                return self.extract_playerembedapi_direct(source_url, referer)
            elif any(d in source_url.lower() for d in ['myvidplay', 'bysebuho', 'g9r6', 'doodstream']):
                return self.extract_doodstream_direct(source_url, referer)
            else:
                # Extrator genérico
                return self.extract_generic_source(source_url, referer)
                
        except Exception as e:
            print(f"❌ Erro ao processar source: {e}")
            return None
    
    def extract_megaembed_direct(self, megaembed_url, referer=None):
        """Extrair vídeo direto do MegaEmbed - com decriptação"""
        print(f"🎯 MEGAEMBED: {megaembed_url}")
        
        try:
            # Extrair ID do vídeo
            video_id = None
            if '#' in megaembed_url:
                video_id = megaembed_url.split('#')[-1]
            elif '?v=' in megaembed_url:
                video_id = re.search(r'[?&]v=([^&]+)', megaembed_url)
                if video_id:
                    video_id = video_id.group(1)
            
            if not video_id:
                print("❌ ID do vídeo não encontrado")
                return None
            
            print(f"🆔 Video ID: {video_id}")
            
            # Método 1: Tentar API com decriptação
            api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
            
            api_headers = {
                'Referer': referer or megaembed_url,
                'Accept': '*/*',
                'Origin': 'https://megaembed.link'
            }
            
            api_response = self.session.get(api_url, headers=api_headers, timeout=10)
            
            if api_response.status_code == 200:
                print("✅ API MegaEmbed respondeu")
                
                # Verificar se é JSON ou dados encriptados
                content_type = api_response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    try:
                        json_data = api_response.json()
                        video_url = self.extract_video_from_json(json_data)
                        if video_url:
                            print(f"🎥 MEGAEMBED JSON: {video_url}")
                            return video_url
                    except Exception as e:
                        print(f"⚠️ Erro JSON: {e}")
                
                elif 'octet-stream' in content_type or len(api_response.text) > 1000:
                    print("🔐 Dados encriptados detectados")
                    
                    # Tentar decriptar (hex decode + possível AES)
                    try:
                        hex_data = api_response.text.strip()
                        if all(c in '0123456789abcdef' for c in hex_data.lower()):
                            # É hex válido
                            decoded_bytes = bytes.fromhex(hex_data)
                            
                            # Tentar diferentes decodificações
                            try:
                                # UTF-8
                                decoded_text = decoded_bytes.decode('utf-8')
                                print(f"📄 Hex decoded: {decoded_text[:200]}...")
                                
                                # Procurar vídeos no texto decodificado
                                video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', decoded_text)
                                if video_urls:
                                    print(f"🎥 MEGAEMBED HEX: {video_urls[0]}")
                                    return video_urls[0]
                            except:
                                pass
                            
                            # Se não funcionou, pode ser AES encriptado
                            print("🔐 Dados podem estar AES encriptados")
                    except Exception as e:
                        print(f"⚠️ Erro decriptação: {e}")
            
            # Método 2: Acessar página embed diretamente
            print(f"\n🌐 Tentando página embed...")
            embed_url = f"https://megaembed.link/#{video_id}"
            
            embed_response = self.session.get(embed_url, headers={'Referer': referer or megaembed_url}, timeout=15)
            
            if embed_response.status_code == 200:
                html = embed_response.text
                
                # Procurar vídeos no HTML
                video_patterns = [
                    r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
                    r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
                    r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
                    r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        video_url = matches[0]
                        if self.is_video_url(video_url):
                            print(f"🎥 MEGAEMBED HTML: {video_url}")
                            return video_url
                
                # Procurar configurações do player
                config_patterns = [
                    r'jwplayer\([^)]*\)\.setup\(\s*({[^}]+})\s*\)',
                    r'player\.setup\(\s*({[^}]+})\s*\)'
                ]
                
                for pattern in config_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        try:
                            # Tentar extrair file do config
                            file_match = re.search(r'["\']file["\']\s*:\s*["\']([^"\']+)["\']', match)
                            if file_match:
                                video_url = file_match.group(1)
                                if self.is_video_url(video_url):
                                    print(f"🎥 MEGAEMBED CONFIG: {video_url}")
                                    return video_url
                        except:
                            pass
            
            return None
            
        except Exception as e:
            print(f"❌ Erro MegaEmbed: {e}")
            return None
    
    def extract_playerembedapi_direct(self, playerembedapi_url, referer=None):
        """Extrair vídeo direto do PlayerEmbedAPI - seguir cadeia completa"""
        print(f"🎯 PLAYEREMBEDAPI: {playerembedapi_url}")
        
        try:
            # Passo 1: Acessar PlayerEmbedAPI
            response = self.session.get(playerembedapi_url, headers={'Referer': referer or playerembedapi_url}, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                
                # Procurar vídeos diretos primeiro
                gcs_pattern = r'https?://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*'
                gcs_matches = re.findall(gcs_pattern, html)
                
                if gcs_matches:
                    video_url = gcs_matches[0]
                    print(f"🎥 PLAYEREMBEDAPI GCS DIRETO: {video_url}")
                    return video_url
                
                # Procurar redirecionamentos
                redirect_patterns = [
                    r'window\.location\s*=\s*["\']([^"\']+)["\']',
                    r'location\.href\s*=\s*["\']([^"\']+)["\']',
                    r'["\']([^"\']*abyss\.to[^"\']*)["\']',
                    r'["\']([^"\']*short\.icu[^"\']*)["\']'
                ]
                
                redirect_urls = []
                for pattern in redirect_patterns:
                    matches = re.findall(pattern, html)
                    redirect_urls.extend(matches)
                
                # Remover duplicatas e URLs inválidas
                redirect_urls = list(set([url for url in redirect_urls if url.startswith('http')]))
                
                print(f"🔗 Redirects encontrados: {len(redirect_urls)}")
                
                # Seguir cadeia de redirects
                for redirect_url in redirect_urls[:3]:  # Máximo 3 redirects
                    video_url = self.follow_redirect_chain(redirect_url, playerembedapi_url, max_depth=3)
                    if video_url:
                        return video_url
            
            return None
            
        except Exception as e:
            print(f"❌ Erro PlayerEmbedAPI: {e}")
            return None
    
    def follow_redirect_chain(self, url, referer, max_depth=3, current_depth=0):
        """Seguir cadeia de redirects recursivamente"""
        if current_depth >= max_depth:
            print(f"   ⚠️ Max depth atingido: {url}")
            return None
        
        try:
            print(f"   {'  ' * current_depth}🔗 Nível {current_depth + 1}: {url}")
            
            response = self.session.get(url, headers={'Referer': referer}, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                html = response.text
                
                # Procurar vídeos diretos
                video_patterns = [
                    r'https?://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                    r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        if self.is_video_url(match) and 'playerembedapi' not in match:
                            print(f"   {'  ' * current_depth}🎥 VÍDEO ENCONTRADO: {match}")
                            return match
                
                # Procurar mais redirects
                redirect_patterns = [
                    r'window\.location\s*=\s*["\']([^"\']+)["\']',
                    r'location\.href\s*=\s*["\']([^"\']+)["\']',
                    r'document\.location\s*=\s*["\']([^"\']+)["\']',
                    r'["\']([^"\']*short\.icu[^"\']*)["\']',
                    r'["\']([^"\']*abyss\.to[^"\']*)["\']'
                ]
                
                for pattern in redirect_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        if match.startswith('http') and match != url:
                            # Recursão para próximo nível
                            result = self.follow_redirect_chain(match, url, max_depth, current_depth + 1)
                            if result:
                                return result
                
                # Se chegou aqui e é short.icu, tentar acessar diretamente
                if 'short.icu' in url:
                    print(f"   {'  ' * current_depth}🔄 Short.icu detectado, seguindo redirect HTTP...")
                    
                    # Fazer request sem allow_redirects para capturar Location header
                    no_redirect_response = self.session.get(url, headers={'Referer': referer}, timeout=10, allow_redirects=False)
                    
                    if no_redirect_response.status_code in [301, 302, 303, 307, 308]:
                        location = no_redirect_response.headers.get('Location')
                        if location and location.startswith('http'):
                            print(f"   {'  ' * current_depth}📍 Location header: {location}")
                            return self.follow_redirect_chain(location, url, max_depth, current_depth + 1)
            
            return None
            
        except Exception as e:
            print(f"   {'  ' * current_depth}❌ Erro redirect: {e}")
            return None
    
    def extract_doodstream_direct(self, dood_url, referer=None):
        """Extrair vídeo direto do DoodStream (algoritmo do MaxSeries)"""
        print(f"🎯 DOODSTREAM: {dood_url}")
        
        try:
            # Converter /d/ para /e/
            embed_url = dood_url.replace('/d/', '/e/')
            
            response = self.session.get(embed_url, headers={'Referer': referer or dood_url}, timeout=15)
            html = response.text
            host = re.match(r'https?://[^/]+', response.url).group(0)
            
            # Procurar pass_md5
            md5_match = re.search(r'/pass_md5/[^"\'&\s]+', html)
            if not md5_match:
                print("❌ pass_md5 não encontrado")
                return None
            
            md5_path = md5_match.group(0)
            md5_url = host + md5_path
            
            print(f"🔑 pass_md5: {md5_url}")
            
            # Obter base URL
            md5_response = self.session.get(md5_url, headers={'Referer': response.url}, timeout=10)
            base_url = md5_response.text.strip()
            
            if not base_url.startswith('http'):
                print(f"❌ Base URL inválida: {base_url}")
                return None
            
            # Montar URL final (algoritmo do MaxSeries)
            token = md5_path.split('/')[-1]
            expiry = int(time.time() * 1000)  # timestamp em ms
            hash_table = self.create_hash_table()
            
            final_url = f"{base_url}{hash_table}?token={token}&expiry={expiry}"
            
            print(f"🎥 DOODSTREAM FINAL: {final_url}")
            return final_url
            
        except Exception as e:
            print(f"❌ Erro DoodStream: {e}")
            return None
    
    def extract_generic_source(self, source_url, referer):
        """Extrator genérico para qualquer source"""
        print(f"🎯 GENÉRICO: {source_url}")
        
        try:
            response = self.session.get(source_url, headers={'Referer': referer}, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                
                # Padrões universais de vídeo
                video_patterns = [
                    r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
                    r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
                    r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
                    r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html)
                    for match in matches:
                        if self.is_video_url(match):
                            print(f"🎥 GENÉRICO VÍDEO: {match}")
                            return match
            
            return None
            
        except Exception as e:
            print(f"❌ Erro genérico: {e}")
            return None
    
    def extract_video_from_json(self, data):
        """Extrair URL de vídeo de dados JSON"""
        if isinstance(data, dict):
            video_fields = ['file', 'url', 'source', 'src', 'video', 'stream', 'link', 'hls', 'm3u8', 'mp4']
            
            for field in video_fields:
                if field in data and isinstance(data[field], str):
                    if self.is_video_url(data[field]):
                        return data[field]
            
            # Procurar em sources
            if 'sources' in data and isinstance(data['sources'], list):
                for source in data['sources']:
                    if isinstance(source, dict):
                        result = self.extract_video_from_json(source)
                        if result:
                            return result
            
            # Procurar recursivamente
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self.extract_video_from_json(value)
                    if result:
                        return result
        
        elif isinstance(data, list):
            for item in data:
                result = self.extract_video_from_json(item)
                if result:
                    return result
        
        return None
    
    def is_video_url(self, url):
        """Verificar se é URL de vídeo válida"""
        if not url or not isinstance(url, str):
            return False
        
        if not url.startswith('http'):
            return False
        
        video_indicators = ['.m3u8', '.mp4', '.mkv', '.avi', '.webm', '/hls/', '/video/', '/stream/', 'master.txt', 'storage.googleapis.com']
        return any(indicator in url.lower() for indicator in video_indicators)
    
    def create_hash_table(self):
        """Criar hash table para DoodStream"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(random.choice(alphabet) for _ in range(10))

def test_maxseries_complete():
    """Teste completo do MaxSeries"""
    print("🚀 TESTE COMPLETO - MAXSERIES HTTP EXTRACTOR")
    print("=" * 80)
    
    # URLs de teste
    test_urls = [
        "https://www.maxseries.one/series/assistir-terra-de-pecados-online",
        "https://www.maxseries.one/series/assistir-breaking-bad-a-quimica-do-mal-online"
    ]
    
    extractor = MaxSeriesHTTPExtractor()
    
    for test_url in test_urls:
        print(f"\n🎬 TESTANDO: {test_url}")
        print("-" * 60)
        
        video_url = extractor.extract_maxseries_video(test_url)
        
        if video_url:
            print(f"\n🏆 SUCESSO! LINK DIRETO CAPTURADO:")
            print(f"🎥 {video_url}")
            
            # Testar link
            try:
                test_response = extractor.session.head(video_url, timeout=10)
                print(f"✅ Link testado: {test_response.status_code}")
                
                content_type = test_response.headers.get('Content-Type', '')
                content_length = test_response.headers.get('Content-Length', '')
                
                if content_type:
                    print(f"📄 Content-Type: {content_type}")
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    print(f"📏 Tamanho: {size_mb:.1f} MB")
                
                # Retornar primeiro sucesso
                return video_url
                
            except Exception as e:
                print(f"⚠️ Erro ao testar: {e}")
        else:
            print(f"\n❌ FALHOU EM CAPTURAR LINK DIRETO")
    
    return None

if __name__ == "__main__":
    result = test_maxseries_complete()
    
    if result:
        print(f"\n🎯 IMPLEMENTAÇÃO PARA MAXSERIES PROVIDER:")
        print("=" * 60)
        print("✅ Usar este algoritmo HTTP no método loadLinks()")
        print("✅ Substituir WebView por chamadas HTTP diretas")
        print("✅ Melhor performance e confiabilidade")
        print("✅ Funciona sem JavaScript/WebView")
    else:
        print(f"\n💡 FALLBACK RECOMENDADO:")
        print("   Manter WebView como backup para casos complexos")