#!/usr/bin/env python3
"""
ANÁLISE ESPECÍFICA - Terra de Pecados
URL: https://www.maxseries.one/series/assistir-terra-de-pecados-online
Objetivo: Engenharia reversa completa para capturar link direto
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse, parse_qs

class TerraDeSecadosAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        
        # Headers completos simulando navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def analyze_complete_flow(self):
        """Análise completa do fluxo Terra de Pecados"""
        print("🎬 ANÁLISE COMPLETA - TERRA DE PECADOS")
        print("=" * 80)
        
        target_url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
        
        try:
            # PASSO 1: Analisar página principal
            print("📡 PASSO 1: Analisando página principal...")
            response = self.session.get(target_url, timeout=15)
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 HTML Size: {len(response.text)} chars")
            
            # Extrair iframe do player
            iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', response.text)
            if not iframe_match:
                print("❌ Nenhum iframe encontrado")
                return None
            
            player_url = iframe_match.group(1)
            if player_url.startswith('//'):
                player_url = 'https:' + player_url
            
            print(f"🎬 Player URL: {player_url}")
            
            # PASSO 2: Analisar player
            print(f"\n📡 PASSO 2: Analisando player...")
            return self.analyze_player_deep(player_url)
            
        except Exception as e:
            print(f"❌ Erro na análise: {e}")
            return None
    
    def analyze_player_deep(self, player_url):
        """Análise profunda do player"""
        print(f"🔍 Analisando player: {player_url}")
        
        try:
            # Headers específicos para player
            player_headers = {
                'Referer': 'https://www.maxseries.one/',
                'Sec-Fetch-Dest': 'iframe',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            response = self.session.get(player_url, headers=player_headers, timeout=15)
            html = response.text
            
            print(f"✅ Player Status: {response.status_code}")
            print(f"📄 Player HTML Size: {len(html)} chars")
            
            # Identificar tipo de player
            player_type = self.identify_player_type(player_url, html)
            print(f"🎯 Tipo de Player: {player_type}")
            
            # Análise específica por tipo
            if player_type == "PlayerThree":
                return self.analyze_playerthree(player_url, html)
            elif player_type == "MegaEmbed":
                return self.analyze_megaembed(player_url, html)
            elif player_type == "PlayerEmbedAPI":
                return self.analyze_playerembedapi(player_url, html)
            elif player_type == "DoodStream":
                return self.analyze_doodstream(player_url, html)
            else:
                return self.analyze_generic_player(player_url, html)
                
        except Exception as e:
            print(f"❌ Erro no player: {e}")
            return None
    
    def identify_player_type(self, url, html):
        """Identificar tipo de player"""
        url_lower = url.lower()
        html_lower = html.lower()
        
        if 'playerthree' in url_lower:
            return "PlayerThree"
        elif 'megaembed' in url_lower:
            return "MegaEmbed"
        elif 'playerembedapi' in url_lower:
            return "PlayerEmbedAPI"
        elif any(d in url_lower for d in ['myvidplay', 'bysebuho', 'g9r6', 'doodstream']):
            return "DoodStream"
        elif 'jwplayer' in html_lower:
            return "JWPlayer"
        elif 'videojs' in html_lower:
            return "VideoJS"
        else:
            return "Generic"
    
    def analyze_playerthree(self, player_url, html):
        """Análise específica do PlayerThree"""
        print("\n🎯 ANÁLISE PLAYERTHREE")
        print("-" * 40)
        
        # 1. Procurar configuração JWPlayer
        print("🔍 1. Procurando configuração JWPlayer...")
        
        jwplayer_patterns = [
            r'jwplayer\([^)]*\)\.setup\(\s*({[^}]+})\s*\)',
            r'playerInstance\.setup\(\s*({[^}]+})\s*\)',
            r'setup\(\s*({[^}]+file[^}]+})\s*\)',
            r'jwplayer\([^)]*\)\.load\(\s*({[^}]+})\s*\)'
        ]
        
        for pattern in jwplayer_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                print(f"📄 Config encontrado: {match[:200]}...")
                video_url = self.extract_video_from_jwconfig(match)
                if video_url:
                    return video_url
        
        # 2. Procurar episódios via AJAX
        print("\n🔍 2. Procurando episódios via AJAX...")
        
        # Extrair série da URL
        series_match = re.search(r'/embed/([^/]+)', player_url)
        if series_match:
            series_name = series_match.group(1)
            print(f"📺 Série: {series_name}")
            
            # Tentar diferentes endpoints
            base_domain = urlparse(player_url).netloc
            
            ajax_endpoints = [
                f"/episodio/{series_name}",
                f"/api/episode/{series_name}",
                f"/ajax/episode/{series_name}",
                f"/get_video/{series_name}",
                f"/source/{series_name}"
            ]
            
            for endpoint in ajax_endpoints:
                video_url = self.test_ajax_endpoint(base_domain, endpoint, player_url)
                if video_url:
                    return video_url
        
        # 3. Procurar no JavaScript inline
        print("\n🔍 3. Analisando JavaScript inline...")
        
        # Extrair scripts
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for i, script in enumerate(script_matches):
            if len(script) > 50:  # Apenas scripts significativos
                print(f"📜 Script {i+1}: {len(script)} chars")
                
                # Procurar URLs de vídeo
                video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', script)
                if video_urls:
                    print(f"🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                    return video_urls[0]
                
                # Procurar configurações
                config_patterns = [
                    r'file:\s*["\']([^"\']+)["\']',
                    r'source:\s*["\']([^"\']+)["\']',
                    r'src:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in config_patterns:
                    matches = re.findall(pattern, script)
                    for match in matches:
                        if self.is_video_url(match):
                            print(f"🎥 CONFIG VÍDEO: {match}")
                            return match
        
        return None
    
    def analyze_megaembed(self, player_url, html):
        """Análise específica do MegaEmbed"""
        print("\n🎯 ANÁLISE MEGAEMBED")
        print("-" * 40)
        
        # Extrair ID do vídeo
        video_id = None
        if '#' in player_url:
            video_id = player_url.split('#')[-1]
        elif '?v=' in player_url:
            video_id = re.search(r'[?&]v=([^&]+)', player_url)
            if video_id:
                video_id = video_id.group(1)
        
        if video_id:
            print(f"🆔 Video ID: {video_id}")
            
            # Testar API
            api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
            return self.test_megaembed_api(api_url, player_url)
        
        return None
    
    def analyze_playerembedapi(self, player_url, html):
        """Análise específica do PlayerEmbedAPI"""
        print("\n🎯 ANÁLISE PLAYEREMBEDAPI")
        print("-" * 40)
        
        # Procurar redirecionamentos
        redirect_patterns = [
            r'["\']([^"\']*short\.icu[^"\']*)["\']',
            r'["\']([^"\']*abyss\.to[^"\']*)["\']',
            r'["\']([^"\']*storage\.googleapis\.com[^"\']*)["\']'
        ]
        
        for pattern in redirect_patterns:
            matches = re.findall(pattern, html)
            if matches:
                redirect_url = matches[0]
                print(f"🔗 Redirect encontrado: {redirect_url}")
                return self.follow_redirect_chain(redirect_url, player_url)
        
        return None
    
    def analyze_doodstream(self, player_url, html):
        """Análise específica do DoodStream"""
        print("\n🎯 ANÁLISE DOODSTREAM")
        print("-" * 40)
        
        # Procurar pass_md5
        md5_pattern = r'/pass_md5/([^"\'&\s]+)'
        md5_matches = re.findall(md5_pattern, html)
        
        if md5_matches:
            md5_token = md5_matches[0]
            print(f"🔑 pass_md5 token: {md5_token}")
            
            host = re.match(r'https?://[^/]+', player_url).group(0)
            md5_url = f"{host}/pass_md5/{md5_token}"
            
            return self.extract_doodstream_video(md5_url, player_url)
        
        return None
    
    def analyze_generic_player(self, player_url, html):
        """Análise genérica para qualquer player"""
        print("\n🎯 ANÁLISE GENÉRICA")
        print("-" * 40)
        
        # Padrões universais
        universal_patterns = [
            r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
            r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
            r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
            r'src:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
        ]
        
        for pattern in universal_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if self.is_video_url(match):
                    print(f"🎥 VÍDEO GENÉRICO: {match}")
                    return match
        
        return None
    
    def test_ajax_endpoint(self, domain, endpoint, referer):
        """Testar endpoint AJAX"""
        try:
            url = f"https://{domain}{endpoint}"
            print(f"🔗 Testando AJAX: {url}")
            
            ajax_headers = {
                'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            response = self.session.get(url, headers=ajax_headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Sucesso: {response.status_code}")
                
                # Tentar JSON
                try:
                    json_data = response.json()
                    print(f"   📄 JSON: {str(json_data)[:200]}...")
                    
                    video_url = self.extract_video_from_json(json_data)
                    if video_url:
                        print(f"   🎥 VÍDEO JSON: {video_url}")
                        return video_url
                except:
                    # Procurar no HTML
                    video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
                    if video_urls:
                        print(f"   🎥 VÍDEO HTML: {video_urls[0]}")
                        return video_urls[0]
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}")
        
        return None
    
    def test_megaembed_api(self, api_url, referer):
        """Testar API do MegaEmbed"""
        try:
            print(f"🔗 Testando MegaEmbed API: {api_url}")
            
            api_headers = {
                'Referer': referer,
                'Accept': 'application/json',
                'Origin': 'https://megaembed.link'
            }
            
            response = self.session.get(api_url, headers=api_headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ API Sucesso: {response.status_code}")
                
                try:
                    json_data = response.json()
                    print(f"📄 API Response: {str(json_data)[:200]}...")
                    
                    video_url = self.extract_video_from_json(json_data)
                    if video_url:
                        print(f"🎥 VÍDEO API: {video_url}")
                        return video_url
                except Exception as e:
                    print(f"⚠️ Erro ao parsear JSON: {e}")
            else:
                print(f"❌ API Erro: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na API: {e}")
        
        return None
    
    def follow_redirect_chain(self, redirect_url, referer):
        """Seguir cadeia de redirecionamentos"""
        try:
            print(f"🔗 Seguindo redirect: {redirect_url}")
            
            response = self.session.get(redirect_url, headers={'Referer': referer}, timeout=10)
            
            # Procurar vídeo na resposta
            video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
            if video_urls:
                print(f"🎥 VÍDEO REDIRECT: {video_urls[0]}")
                return video_urls[0]
                
        except Exception as e:
            print(f"❌ Erro no redirect: {e}")
        
        return None
    
    def extract_doodstream_video(self, md5_url, referer):
        """Extrair vídeo do DoodStream"""
        try:
            print(f"🔗 Testando DoodStream: {md5_url}")
            
            response = self.session.get(md5_url, headers={'Referer': referer}, timeout=10)
            base_url = response.text.strip()
            
            if base_url.startswith('http'):
                # Montar URL final
                token = md5_url.split('/')[-1]
                expiry = int(time.time() * 1000)
                hash_table = self.create_hash_table()
                
                final_url = f"{base_url}{hash_table}?token={token}&expiry={expiry}"
                print(f"🎥 DOODSTREAM FINAL: {final_url}")
                return final_url
                
        except Exception as e:
            print(f"❌ Erro DoodStream: {e}")
        
        return None
    
    def extract_video_from_jwconfig(self, config_str):
        """Extrair vídeo da configuração JWPlayer"""
        try:
            # Limpar e parsear configuração
            config_clean = self.clean_js_object(config_str)
            config = json.loads(config_clean)
            
            return self.extract_video_from_json(config)
            
        except Exception as e:
            print(f"⚠️ Erro ao parsear JW config: {e}")
            return None
    
    def clean_js_object(self, js_obj):
        """Limpar objeto JavaScript para JSON válido"""
        # Remover comentários
        js_obj = re.sub(r'//.*?\n', '\n', js_obj)
        js_obj = re.sub(r'/\*.*?\*/', '', js_obj, flags=re.DOTALL)
        
        # Corrigir aspas
        js_obj = re.sub(r'(\w+):', r'"\1":', js_obj)
        js_obj = re.sub(r"'([^']*)'", r'"\1"', js_obj)
        
        # Remover trailing commas
        js_obj = re.sub(r',\s*}', '}', js_obj)
        js_obj = re.sub(r',\s*]', ']', js_obj)
        
        return js_obj
    
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
        import random
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(random.choice(alphabet) for _ in range(10))

def main():
    """Função principal"""
    print("🚀 ANÁLISE TERRA DE PECADOS")
    print("URL: https://www.maxseries.one/series/assistir-terra-de-pecados-online")
    print("=" * 80)
    
    analyzer = TerraDeSecadosAnalyzer()
    video_url = analyzer.analyze_complete_flow()
    
    if video_url:
        print(f"\n🏆 SUCESSO! LINK DIRETO CAPTURADO:")
        print(f"🎥 {video_url}")
        
        # Testar link
        try:
            test_response = analyzer.session.head(video_url, timeout=10)
            print(f"✅ Link testado: {test_response.status_code}")
            
            content_type = test_response.headers.get('Content-Type', '')
            content_length = test_response.headers.get('Content-Length', '')
            
            if content_type:
                print(f"📄 Content-Type: {content_type}")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"📏 Tamanho: {size_mb:.1f} MB")
                
        except Exception as e:
            print(f"⚠️ Erro ao testar: {e}")
    else:
        print(f"\n❌ FALHOU EM CAPTURAR LINK DIRETO")
        print("💡 Player pode requerer WebView ou JavaScript complexo")

if __name__ == "__main__":
    main()