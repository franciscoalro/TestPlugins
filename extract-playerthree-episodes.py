#!/usr/bin/env python3
"""
EXTRAÇÃO PLAYERTHREE - Episódios Específicos
Baseado na análise do HTML: usar IDs de episódios para AJAX
"""

import requests
import re
import json
import time

def extract_playerthree_episodes():
    print("🎯 EXTRAÇÃO PLAYERTHREE - EPISÓDIOS")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive'
    })
    
    base_url = "https://playerthree.online"
    player_url = "https://playerthree.online/embed/synden/"
    
    # IDs extraídos do HTML
    episodes = [
        {"season_id": "12962", "episode_id": "255703", "name": "1 - You've Been Warned"},
        {"season_id": "12962", "episode_id": "255704", "name": "2 - Unidentified Man #1"},
        {"season_id": "12962", "episode_id": "255705", "name": "3 - Brothers"},
        {"season_id": "12962", "episode_id": "255706", "name": "4 - Järven"},
        {"season_id": "12962", "episode_id": "255707", "name": "5 - Queen Bee - Final de Temporada"}
    ]
    
    print(f"📺 Encontrados {len(episodes)} episódios")
    
    # Testar primeiro episódio
    episode = episodes[0]
    season_id = episode["season_id"]
    episode_id = episode["episode_id"]
    
    print(f"\n🎬 Testando: {episode['name']}")
    print(f"   Season ID: {season_id}")
    print(f"   Episode ID: {episode_id}")
    
    # 1. Testar endpoint /episodio/ com ID
    print(f"\n🔍 1. Testando endpoint /episodio/...")
    
    episodio_endpoints = [
        f"/episodio/{episode_id}",
        f"/episodio/{season_id}_{episode_id}",
        f"/episodio/{season_id}/{episode_id}",
        f"/api/episodio/{episode_id}",
        f"/ajax/episodio/{episode_id}"
    ]
    
    for endpoint in episodio_endpoints:
        video_url = test_endpoint(session, base_url + endpoint, player_url)
        if video_url:
            return video_url
    
    # 2. Testar com hash fragment (como no HTML)
    print(f"\n🔍 2. Testando hash fragments...")
    
    hash_url = f"{player_url}#{season_id}_{episode_id}"
    print(f"🔗 Hash URL: {hash_url}")
    
    try:
        response = session.get(hash_url, headers={'Referer': player_url}, timeout=15)
        if response.status_code == 200:
            print("✅ Hash URL acessível")
            
            # Procurar JavaScript que carrega o episódio
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', response.text, re.DOTALL)
            for script in scripts:
                if 'episodio' in script or 'episode' in script:
                    print(f"📜 Script com episódio: {script[:200]}...")
                    
                    # Procurar URLs de vídeo
                    video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', script)
                    if video_urls:
                        print(f"🎥 VÍDEO HASH: {video_urls[0]}")
                        return video_urls[0]
    except Exception as e:
        print(f"❌ Erro hash: {e}")
    
    # 3. Simular AJAX que o JavaScript faria
    print(f"\n🔍 3. Simulando AJAX do JavaScript...")
    
    ajax_data_variations = [
        {"episode_id": episode_id},
        {"season_id": season_id, "episode_id": episode_id},
        {"id": episode_id},
        {"ep": episode_id},
        {"season": season_id, "episode": episode_id},
        {"s": season_id, "e": episode_id}
    ]
    
    ajax_endpoints = [
        "/episodio",
        "/api/episode", 
        "/ajax/episode",
        "/get_episode",
        "/load_episode",
        "/player/episode"
    ]
    
    for endpoint in ajax_endpoints:
        for data in ajax_data_variations:
            video_url = test_post_endpoint(session, base_url + endpoint, player_url, data)
            if video_url:
                return video_url
    
    # 4. Tentar acessar arquivos JavaScript do player
    print(f"\n🔍 4. Analisando JavaScript do player...")
    
    js_files = [
        "/static/js/app.js",
        "/static/js/jwplayer.js"
    ]
    
    for js_file in js_files:
        try:
            js_url = base_url + js_file
            print(f"📜 Analisando: {js_url}")
            
            response = session.get(js_url, timeout=10)
            if response.status_code == 200:
                js_content = response.text
                print(f"   ✅ JS carregado: {len(js_content)} chars")
                
                # Procurar endpoints no JavaScript
                endpoints_in_js = re.findall(r'["\']([^"\']*(?:episodio|episode|api)[^"\']*)["\']', js_content)
                
                if endpoints_in_js:
                    print(f"   🔗 Endpoints no JS: {endpoints_in_js[:5]}")
                    
                    for endpoint in endpoints_in_js[:5]:
                        if endpoint.startswith('/'):
                            video_url = test_endpoint(session, base_url + endpoint.replace('{id}', episode_id), player_url)
                            if video_url:
                                return video_url
                
                # Procurar padrões de configuração
                config_patterns = [
                    r'jwplayer\([^)]*\)\.setup\(\s*({[^}]+})\s*\)',
                    r'file:\s*["\']([^"\']+)["\']',
                    r'source:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in config_patterns:
                    matches = re.findall(pattern, js_content)
                    if matches:
                        print(f"   🎯 Padrão encontrado: {matches[:3]}")
                        
                        for match in matches:
                            if is_video_url(match):
                                print(f"   🎥 VÍDEO JS: {match}")
                                return match
        
        except Exception as e:
            print(f"   ❌ Erro JS: {e}")
    
    # 5. Tentar com diferentes User-Agents (mobile, etc.)
    print(f"\n🔍 5. Testando com User-Agent mobile...")
    
    mobile_headers = session.headers.copy()
    mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
    
    try:
        response = session.get(f"{base_url}/episodio/{episode_id}", headers=mobile_headers, timeout=10)
        if response.status_code == 200:
            print("✅ Mobile endpoint funcionou")
            
            video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
            if video_urls:
                print(f"🎥 VÍDEO MOBILE: {video_urls[0]}")
                return video_urls[0]
    except Exception as e:
        print(f"❌ Erro mobile: {e}")
    
    print(f"\n❌ NENHUM LINK DIRETO ENCONTRADO")
    return None

def test_endpoint(session, url, referer):
    """Testar endpoint GET"""
    try:
        print(f"🔗 GET: {url}")
        
        response = session.get(url, headers={'Referer': referer}, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Sucesso: {response.status_code}")
            
            # Tentar JSON
            try:
                json_data = response.json()
                print(f"   📄 JSON: {str(json_data)[:150]}...")
                
                video_url = extract_video_from_json(json_data)
                if video_url:
                    print(f"   🎥 VÍDEO JSON: {video_url}")
                    return video_url
            except:
                # HTML/texto
                content = response.text
                print(f"   📄 Conteúdo: {len(content)} chars")
                
                # Procurar vídeos
                video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', content)
                if video_urls:
                    print(f"   🎥 VÍDEO HTML: {video_urls[0]}")
                    return video_urls[0]
                
                # Procurar botões com data-source
                source_buttons = re.findall(r'data-source="([^"]+)"', content)
                if source_buttons:
                    print(f"   🔘 Botões source: {source_buttons}")
                    for source in source_buttons:
                        if is_video_url(source):
                            print(f"   🎥 VÍDEO SOURCE: {source}")
                            return source
        else:
            print(f"   ❌ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:50]}")
    
    return None

def test_post_endpoint(session, url, referer, data):
    """Testar endpoint POST"""
    try:
        print(f"🔗 POST: {url} - Data: {data}")
        
        headers = {
            'Referer': referer,
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = session.post(url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ POST Sucesso: {response.status_code}")
            
            try:
                json_data = response.json()
                video_url = extract_video_from_json(json_data)
                if video_url:
                    print(f"   🎥 VÍDEO POST: {video_url}")
                    return video_url
            except:
                video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
                if video_urls:
                    print(f"   🎥 VÍDEO POST: {video_urls[0]}")
                    return video_urls[0]
        else:
            print(f"   ❌ POST Erro: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ POST Erro: {str(e)[:30]}")
    
    return None

def extract_video_from_json(data):
    """Extrair vídeo de JSON"""
    if isinstance(data, dict):
        video_fields = ['file', 'url', 'source', 'src', 'video', 'stream', 'link', 'hls', 'm3u8', 'mp4']
        
        for field in video_fields:
            if field in data and isinstance(data[field], str):
                if is_video_url(data[field]):
                    return data[field]
        
        # Procurar em sources
        if 'sources' in data and isinstance(data['sources'], list):
            for source in data['sources']:
                if isinstance(source, dict):
                    result = extract_video_from_json(source)
                    if result:
                        return result
        
        # Recursivo
        for value in data.values():
            if isinstance(value, (dict, list)):
                result = extract_video_from_json(value)
                if result:
                    return result
    
    elif isinstance(data, list):
        for item in data:
            result = extract_video_from_json(item)
            if result:
                return result
    
    return None

def is_video_url(url):
    """Verificar se é URL de vídeo"""
    if not url or not isinstance(url, str) or not url.startswith('http'):
        return False
    
    video_indicators = ['.m3u8', '.mp4', '.mkv', '.avi', '.webm', '/hls/', '/video/', '/stream/', 'master.txt']
    return any(indicator in url.lower() for indicator in video_indicators)

if __name__ == "__main__":
    result = extract_playerthree_episodes()
    
    if result:
        print(f"\n🏆 SUCESSO! Link direto encontrado:")
        print(f"🎥 {result}")
        
        # Testar link
        try:
            session = requests.Session()
            test_response = session.head(result, timeout=10)
            print(f"✅ Link testado: {test_response.status_code}")
            
            content_type = test_response.headers.get('Content-Type', '')
            if content_type:
                print(f"📄 Content-Type: {content_type}")
        except Exception as e:
            print(f"⚠️ Erro ao testar: {e}")
    else:
        print(f"\n💡 CONCLUSÃO:")
        print("   PlayerThree usa JavaScript complexo para carregar vídeos")
        print("   Recomendação: Implementar WebView com interceptação de rede")
        print("   O MaxSeries Provider já tem essa funcionalidade implementada")