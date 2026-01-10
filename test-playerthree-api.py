#!/usr/bin/env python3
"""
Teste para extrair link direto do PlayerThree
Foco: Encontrar API calls ou endpoints que retornam URLs de vídeo
"""

import requests
import re
import json
from urllib.parse import urljoin, urlparse

def test_playerthree_api():
    print("🎯 TESTE PLAYERTHREE API - LINK DIRETO")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    player_url = "https://playerthree.online/embed/breakingbad/"
    
    try:
        # 1. Analisar HTML do player
        print("🔍 1. Analisando HTML do player...")
        response = session.get(player_url, timeout=15)
        html = response.text
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 HTML size: {len(html)} chars")
        
        # 2. Procurar endpoints de API
        print("\n🔍 2. Procurando endpoints de API...")
        
        api_patterns = [
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*ajax[^"\']*)["\']',
            r'["\']([^"\']*episodio[^"\']*)["\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'url:\s*["\']([^"\']+)["\']'
        ]
        
        found_apis = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if match.startswith('/') or match.startswith('http'):
                    found_apis.add(match)
        
        print(f"🔗 APIs encontradas: {len(found_apis)}")
        for api in list(found_apis)[:10]:  # Mostrar apenas 10
            print(f"   - {api}")
        
        # 3. Extrair ID do episódio/série
        print("\n🔍 3. Extraindo IDs...")
        
        # Procurar IDs no HTML
        id_patterns = [
            r'episode[_-]?id["\']?\s*[:=]\s*["\']?(\d+)',
            r'video[_-]?id["\']?\s*[:=]\s*["\']?(\d+)',
            r'id["\']?\s*[:=]\s*["\']?(\d+)',
            r'data-episode["\']?\s*[:=]\s*["\']?(\d+)'
        ]
        
        found_ids = set()
        for pattern in id_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            found_ids.update(matches)
        
        print(f"🆔 IDs encontrados: {list(found_ids)}")
        
        # 4. Testar endpoints comuns do PlayerThree
        print("\n🔍 4. Testando endpoints comuns...")
        
        base_url = "https://playerthree.online"
        test_endpoints = [
            "/api/episode/",
            "/api/video/",
            "/episodio/",
            "/ajax/episode/",
            "/get_video/",
            "/player/",
            "/source/"
        ]
        
        # Testar com IDs encontrados
        for endpoint in test_endpoints:
            for ep_id in list(found_ids)[:3]:  # Testar apenas 3 IDs
                test_url = f"{base_url}{endpoint}{ep_id}"
                try:
                    print(f"🔗 Testando: {test_url}")
                    api_response = session.get(
                        test_url,
                        headers={'Referer': player_url},
                        timeout=10
                    )
                    
                    if api_response.status_code == 200:
                        print(f"   ✅ Sucesso: {api_response.status_code}")
                        
                        # Verificar se retorna JSON
                        try:
                            json_data = api_response.json()
                            print(f"   📄 JSON: {str(json_data)[:200]}...")
                            
                            # Procurar URLs de vídeo no JSON
                            json_str = json.dumps(json_data)
                            video_urls = re.findall(r'https?://[^"\']+\.(?:m3u8|mp4)[^"\']*', json_str)
                            if video_urls:
                                print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                                return video_urls[0]
                                
                        except:
                            # Não é JSON, verificar HTML
                            response_text = api_response.text
                            video_urls = re.findall(r'https?://[^"\']+\.(?:m3u8|mp4)[^"\']*', response_text)
                            if video_urls:
                                print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                                return video_urls[0]
                    else:
                        print(f"   ❌ Erro: {api_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Erro: {str(e)[:50]}")
        
        # 5. Procurar no JavaScript inline
        print("\n🔍 5. Analisando JavaScript inline...")
        
        # Extrair todos os scripts
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for i, script in enumerate(script_matches):
            if len(script) > 100:  # Apenas scripts grandes
                print(f"📜 Script {i+1}: {len(script)} chars")
                
                # Procurar configurações de vídeo
                video_configs = re.findall(r'(?:file|source|src):\s*["\']([^"\']+)["\']', script)
                for config in video_configs:
                    if '.m3u8' in config or '.mp4' in config:
                        print(f"   🎥 Config encontrada: {config}")
                        if config.startswith('http'):
                            return config
                
                # Procurar URLs completas
                full_urls = re.findall(r'https?://[^"\']+\.(?:m3u8|mp4)[^"\']*', script)
                if full_urls:
                    print(f"   🎥 URL completa: {full_urls[0]}")
                    return full_urls[0]
        
        # 6. Tentar método de força bruta com breakingbad
        print("\n🔍 6. Tentativa com série específica...")
        
        series_endpoints = [
            f"{base_url}/api/series/breakingbad",
            f"{base_url}/episodio/breakingbad/1/1",  # S01E01
            f"{base_url}/player/breakingbad",
            f"{base_url}/source/breakingbad"
        ]
        
        for endpoint in series_endpoints:
            try:
                print(f"🔗 Testando: {endpoint}")
                response = session.get(endpoint, headers={'Referer': player_url}, timeout=10)
                
                if response.status_code == 200:
                    print(f"   ✅ Sucesso: {response.status_code}")
                    
                    # Procurar vídeos na resposta
                    video_urls = re.findall(r'https?://[^"\']+\.(?:m3u8|mp4)[^"\']*', response.text)
                    if video_urls:
                        print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                        return video_urls[0]
                else:
                    print(f"   ❌ Erro: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)[:50]}")
        
        print("\n❌ NENHUM LINK DIRETO ENCONTRADO")
        print("💡 PlayerThree pode usar:")
        print("   - Autenticação por token")
        print("   - JavaScript complexo para gerar URLs")
        print("   - WebSocket ou outras tecnologias")
        print("   - Proteção anti-bot")
        
        return None
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None

if __name__ == "__main__":
    result = test_playerthree_api()
    if result:
        print(f"\n🏆 SUCESSO! Link direto: {result}")
    else:
        print(f"\n❌ Falhou em encontrar link direto")