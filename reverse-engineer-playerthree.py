#!/usr/bin/env python3
"""
ENGENHARIA REVERSA - PlayerThree
Objetivo: Replicar via HTTP puro o que o JavaScript faz no navegador
Capturar requisições reais e extrair links diretos de vídeo
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse, parse_qs
import base64

class PlayerThreeReverseEngineer:
    def __init__(self):
        self.session = requests.Session()
        
        # Headers que simulam navegador real
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(self.base_headers)
    
    def analyze_player_requests(self, player_url):
        """Analisar todas as requisições que o player faz"""
        print(f"🔍 ENGENHARIA REVERSA: {player_url}")
        print("=" * 80)
        
        try:
            # 1. Requisição inicial do player
            print("📡 1. Requisição inicial do player...")
            
            response = self.session.get(player_url, timeout=15)
            html = response.text
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 HTML Size: {len(html)} chars")
            
            # Extrair cookies importantes
            cookies = dict(response.cookies)
            if cookies:
                print(f"🍪 Cookies recebidos: {list(cookies.keys())}")
            
            # 2. Analisar JavaScript para encontrar endpoints
            print("\n📡 2. Analisando JavaScript para endpoints...")
            
            # Procurar por URLs de API no JavaScript
            api_patterns = [
                r'["\']([^"\']*(?:api|ajax|episodio|video|source)[^"\']*)["\']',
                r'url:\s*["\']([^"\']+)["\']',
                r'endpoint:\s*["\']([^"\']+)["\']',
                r'fetch\(\s*["\']([^"\']+)["\']',
                r'\.get\(\s*["\']([^"\']+)["\']',
                r'\.post\(\s*["\']([^"\']+)["\']'
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if ('/' in match and 
                        not match.startswith('data:') and 
                        not match.endswith('.css') and 
                        not match.endswith('.js') and
                        not match.endswith('.png') and
                        not match.endswith('.jpg')):
                        found_endpoints.add(match)
            
            print(f"🔗 Endpoints encontrados: {len(found_endpoints)}")
            for endpoint in list(found_endpoints)[:15]:
                print(f"   - {endpoint}")
            
            # 3. Extrair dados do player (IDs, tokens, etc.)
            print("\n📡 3. Extraindo dados do player...")
            
            # Procurar por dados estruturados
            data_patterns = [
                (r'episode[_-]?id["\']?\s*[:=]\s*["\']?(\w+)', 'Episode ID'),
                (r'video[_-]?id["\']?\s*[:=]\s*["\']?(\w+)', 'Video ID'),
                (r'series[_-]?id["\']?\s*[:=]\s*["\']?(\w+)', 'Series ID'),
                (r'token["\']?\s*[:=]\s*["\']([^"\']+)', 'Token'),
                (r'key["\']?\s*[:=]\s*["\']([^"\']+)', 'Key'),
                (r'hash["\']?\s*[:=]\s*["\']([^"\']+)', 'Hash'),
                (r'csrf["\']?\s*[:=]\s*["\']([^"\']+)', 'CSRF'),
                (r'nonce["\']?\s*[:=]\s*["\']([^"\']+)', 'Nonce')
            ]
            
            extracted_data = {}
            for pattern, name in data_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    extracted_data[name] = matches[0]
                    print(f"   🔑 {name}: {matches[0]}")
            
            # 4. Procurar por configuração JWPlayer
            print("\n📡 4. Procurando configuração JWPlayer...")
            
            jwplayer_patterns = [
                r'jwplayer\([^)]*\)\.setup\(\s*({[^}]+})\s*\)',
                r'playerInstance\.setup\(\s*({[^}]+})\s*\)',
                r'setup\(\s*({[^}]+file[^}]+})\s*\)',
                r'jwplayer\([^)]*\)\.load\(\s*({[^}]+})\s*\)'
            ]
            
            for pattern in jwplayer_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        # Tentar parsear configuração
                        config_clean = self.clean_js_object(match)
                        config = json.loads(config_clean)
                        
                        print(f"🎬 JWPlayer config encontrado:")
                        print(f"   📄 Config: {json.dumps(config, indent=2)[:500]}...")
                        
                        # Extrair URL de vídeo se existir
                        video_url = self.extract_video_from_config(config)
                        if video_url:
                            print(f"   🎥 VÍDEO DIRETO: {video_url}")
                            return video_url
                            
                    except Exception as e:
                        print(f"   ⚠️ Erro ao parsear config: {e}")
            
            # 5. Testar endpoints encontrados
            print("\n📡 5. Testando endpoints encontrados...")
            
            base_domain = urlparse(player_url).netloc
            
            for endpoint in found_endpoints:
                if self.should_test_endpoint(endpoint):
                    video_url = self.test_endpoint(endpoint, player_url, base_domain, extracted_data)
                    if video_url:
                        return video_url
            
            # 6. Tentar endpoints comuns baseados na URL
            print("\n📡 6. Testando endpoints comuns...")
            
            # Extrair série da URL
            series_match = re.search(r'/embed/([^/]+)', player_url)
            series_name = series_match.group(1) if series_match else 'breakingbad'
            
            common_endpoints = [
                f"/api/episode/{series_name}",
                f"/api/video/{series_name}",
                f"/episodio/{series_name}",
                f"/ajax/episode/{series_name}",
                f"/get_video/{series_name}",
                f"/player/source/{series_name}",
                f"/embed/source/{series_name}",
                f"/api/series/{series_name}/episodes",
                f"/api/v1/episode/{series_name}",
                f"/source/{series_name}"
            ]
            
            for endpoint in common_endpoints:
                video_url = self.test_endpoint(endpoint, player_url, base_domain, extracted_data)
                if video_url:
                    return video_url
            
            # 7. Tentar com diferentes métodos HTTP
            print("\n📡 7. Testando métodos POST...")
            
            post_endpoints = [
                "/api/episode",
                "/ajax/video",
                "/get_source",
                "/player/load"
            ]
            
            post_data = {
                'series': series_name,
                'episode': '1',
                'season': '1'
            }
            
            # Adicionar dados extraídos ao POST
            post_data.update(extracted_data)
            
            for endpoint in post_endpoints:
                video_url = self.test_post_endpoint(endpoint, player_url, base_domain, post_data)
                if video_url:
                    return video_url
            
            print("\n❌ NENHUM LINK DIRETO ENCONTRADO VIA HTTP")
            print("💡 Possíveis causas:")
            print("   - Player usa WebSocket")
            print("   - Requer autenticação complexa")
            print("   - URLs geradas dinamicamente via JavaScript")
            print("   - Proteção anti-bot avançada")
            
            return None
            
        except Exception as e:
            print(f"❌ Erro na engenharia reversa: {e}")
            return None
    
    def clean_js_object(self, js_obj):
        """Limpar objeto JavaScript para JSON válido"""
        # Remover comentários
        js_obj = re.sub(r'//.*?\n', '\n', js_obj)
        js_obj = re.sub(r'/\*.*?\*/', '', js_obj, flags=re.DOTALL)
        
        # Corrigir aspas
        js_obj = re.sub(r'(\w+):', r'"\1":', js_obj)  # Adicionar aspas nas chaves
        js_obj = re.sub(r"'([^']*)'", r'"\1"', js_obj)  # Trocar aspas simples por duplas
        
        # Remover trailing commas
        js_obj = re.sub(r',\s*}', '}', js_obj)
        js_obj = re.sub(r',\s*]', ']', js_obj)
        
        return js_obj
    
    def extract_video_from_config(self, config):
        """Extrair URL de vídeo da configuração JWPlayer"""
        # Procurar em diferentes locais
        if isinstance(config, dict):
            # Direto no file
            if 'file' in config and isinstance(config['file'], str):
                if self.is_video_url(config['file']):
                    return config['file']
            
            # Em sources
            if 'sources' in config and isinstance(config['sources'], list):
                for source in config['sources']:
                    if isinstance(source, dict) and 'file' in source:
                        if self.is_video_url(source['file']):
                            return source['file']
            
            # Em playlist
            if 'playlist' in config and isinstance(config['playlist'], list):
                for item in config['playlist']:
                    if isinstance(item, dict):
                        video_url = self.extract_video_from_config(item)
                        if video_url:
                            return video_url
        
        return None
    
    def should_test_endpoint(self, endpoint):
        """Verificar se endpoint vale a pena testar"""
        skip_patterns = [
            '.css', '.js', '.png', '.jpg', '.gif', '.ico',
            'google', 'facebook', 'twitter', 'analytics',
            'ads', 'cdn.', 'static.'
        ]
        
        for pattern in skip_patterns:
            if pattern in endpoint.lower():
                return False
        
        return True
    
    def test_endpoint(self, endpoint, referer, base_domain, data=None):
        """Testar endpoint específico"""
        try:
            # Construir URL completa
            if endpoint.startswith('http'):
                url = endpoint
            elif endpoint.startswith('/'):
                url = f"https://{base_domain}{endpoint}"
            else:
                url = f"https://{base_domain}/{endpoint}"
            
            print(f"🔗 Testando: {url}")
            
            # Headers específicos para API
            api_headers = {
                'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            response = self.session.get(url, headers=api_headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso: {response.status_code}")
                
                # Tentar parsear como JSON
                try:
                    json_data = response.json()
                    print(f"   📄 JSON: {str(json_data)[:200]}...")
                    
                    video_url = self.extract_video_from_json(json_data)
                    if video_url:
                        print(f"   🎥 VÍDEO ENCONTRADO: {video_url}")
                        return video_url
                        
                except:
                    # Não é JSON, procurar no texto
                    video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
                    if video_urls:
                        print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                        return video_urls[0]
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}")
        
        return None
    
    def test_post_endpoint(self, endpoint, referer, base_domain, post_data):
        """Testar endpoint com POST"""
        try:
            url = f"https://{base_domain}{endpoint}"
            print(f"🔗 POST: {url}")
            print(f"   📤 Data: {post_data}")
            
            post_headers = {
                'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            
            response = self.session.post(url, data=post_data, headers=post_headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso: {response.status_code}")
                
                try:
                    json_data = response.json()
                    video_url = self.extract_video_from_json(json_data)
                    if video_url:
                        print(f"   🎥 VÍDEO ENCONTRADO: {video_url}")
                        return video_url
                except:
                    video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
                    if video_urls:
                        print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                        return video_urls[0]
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}")
        
        return None
    
    def extract_video_from_json(self, data):
        """Extrair URL de vídeo de dados JSON"""
        if isinstance(data, dict):
            # Campos comuns para URLs de vídeo
            video_fields = ['file', 'url', 'source', 'src', 'video', 'stream', 'link', 'hls', 'm3u8', 'mp4']
            
            for field in video_fields:
                if field in data and isinstance(data[field], str):
                    if self.is_video_url(data[field]):
                        return data[field]
            
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
        if not url or not isinstance(url, str) or not url.startswith('http'):
            return False
        
        video_indicators = ['.m3u8', '.mp4', '.mkv', '.avi', '.webm', '/hls/', '/video/', '/stream/', 'master.txt']
        return any(indicator in url.lower() for indicator in video_indicators)

def main():
    """Função principal"""
    print("🚀 ENGENHARIA REVERSA - PLAYERTHREE")
    print("Objetivo: Capturar link direto via HTTP puro")
    print("=" * 80)
    
    # URL do player para testar
    player_url = "https://playerthree.online/embed/breakingbad/"
    
    engineer = PlayerThreeReverseEngineer()
    video_url = engineer.analyze_player_requests(player_url)
    
    if video_url:
        print(f"\n🏆 SUCESSO! LINK DIRETO CAPTURADO:")
        print(f"🎥 {video_url}")
        
        # Testar se o link funciona
        try:
            test_response = engineer.session.head(video_url, timeout=10)
            print(f"✅ Link testado: {test_response.status_code}")
            
            content_type = test_response.headers.get('Content-Type', '')
            if content_type:
                print(f"📄 Content-Type: {content_type}")
        except Exception as e:
            print(f"⚠️ Erro ao testar link: {e}")
    else:
        print(f"\n❌ FALHOU EM CAPTURAR LINK DIRETO")
        print("💡 Recomendação: Usar WebView como fallback")

if __name__ == "__main__":
    main()