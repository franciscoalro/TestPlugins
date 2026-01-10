#!/usr/bin/env python3
"""
ANÁLISE PROFUNDA - PlayerThree (synden)
Foco: Capturar requisições reais e encontrar endpoints funcionais
"""

import requests
import re
import json
import time
from urllib.parse import urljoin, urlparse

def deep_playerthree_analysis():
    print("🔬 ANÁLISE PROFUNDA - PLAYERTHREE (SYNDEN)")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive'
    })
    
    player_url = "https://playerthree.online/embed/synden/"
    
    try:
        # 1. Analisar HTML do player em detalhes
        print("🔍 1. Análise detalhada do HTML...")
        response = session.get(player_url, timeout=15)
        html = response.text
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 HTML: {len(html)} chars")
        
        # Salvar HTML para análise manual
        with open('playerthree_synden.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("💾 HTML salvo em: playerthree_synden.html")
        
        # 2. Extrair todos os scripts
        print("\n🔍 2. Extraindo scripts...")
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        
        for i, script in enumerate(scripts):
            if len(script.strip()) > 20:
                print(f"\n📜 Script {i+1}: {len(script)} chars")
                print(f"   Conteúdo: {script[:200]}...")
                
                # Procurar padrões específicos
                patterns = [
                    (r'jwplayer\([^)]*\)', 'JWPlayer init'),
                    (r'setup\s*\(', 'Setup call'),
                    (r'file:\s*["\']([^"\']+)["\']', 'File config'),
                    (r'source:\s*["\']([^"\']+)["\']', 'Source config'),
                    (r'playlist:\s*\[', 'Playlist config'),
                    (r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)', 'Video URL'),
                    (r'/api/[^"\'<>\s]+', 'API endpoint'),
                    (r'/ajax/[^"\'<>\s]+', 'AJAX endpoint'),
                    (r'fetch\([^)]+\)', 'Fetch call'),
                    (r'XMLHttpRequest', 'XHR usage')
                ]
                
                for pattern, desc in patterns:
                    matches = re.findall(pattern, script, re.IGNORECASE)
                    if matches:
                        print(f"   🎯 {desc}: {matches}")
        
        # 3. Procurar meta tags e dados estruturados
        print("\n🔍 3. Procurando meta dados...")
        
        meta_patterns = [
            (r'<meta[^>]+property="og:video"[^>]+content="([^"]+)"', 'OpenGraph Video'),
            (r'<meta[^>]+name="video"[^>]+content="([^"]+)"', 'Video Meta'),
            (r'data-video="([^"]+)"', 'Data Video'),
            (r'data-source="([^"]+)"', 'Data Source'),
            (r'data-episode="([^"]+)"', 'Data Episode')
        ]
        
        for pattern, desc in meta_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"🏷️ {desc}: {matches}")
        
        # 4. Tentar diferentes variações de endpoints
        print("\n🔍 4. Testando variações de endpoints...")
        
        base_url = "https://playerthree.online"
        series_name = "synden"
        
        # Endpoints mais específicos
        test_endpoints = [
            f"/embed/{series_name}/1",
            f"/embed/{series_name}/1/1", 
            f"/embed/{series_name}/s1e1",
            f"/player/{series_name}",
            f"/video/{series_name}",
            f"/stream/{series_name}",
            f"/api/{series_name}",
            f"/api/v1/{series_name}",
            f"/api/episode/{series_name}/1",
            f"/api/video/{series_name}/1",
            f"/ajax/{series_name}",
            f"/source/{series_name}",
            f"/get/{series_name}",
            f"/load/{series_name}",
            f"/{series_name}/1",
            f"/{series_name}/episode/1"
        ]
        
        for endpoint in test_endpoints:
            try:
                url = base_url + endpoint
                print(f"🔗 Testando: {url}")
                
                # Headers específicos para cada tipo
                if '/api/' in endpoint:
                    headers = {
                        'Referer': player_url,
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                else:
                    headers = {'Referer': player_url}
                
                resp = session.get(url, headers=headers, timeout=8)
                
                if resp.status_code == 200:
                    print(f"   ✅ Sucesso: {resp.status_code}")
                    
                    # Verificar se retorna JSON
                    try:
                        json_data = resp.json()
                        print(f"   📄 JSON: {str(json_data)[:150]}...")
                        
                        # Procurar vídeo no JSON
                        video_url = extract_video_from_data(json_data)
                        if video_url:
                            print(f"   🎥 VÍDEO ENCONTRADO: {video_url}")
                            return video_url
                    except:
                        # Não é JSON, verificar HTML
                        content = resp.text
                        print(f"   📄 HTML: {len(content)} chars")
                        
                        # Procurar vídeos no conteúdo
                        video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', content)
                        if video_urls:
                            print(f"   🎥 VÍDEO ENCONTRADO: {video_urls[0]}")
                            return video_urls[0]
                        
                        # Procurar iframes aninhados
                        iframe_matches = re.findall(r'<iframe[^>]+src="([^"]+)"', content)
                        if iframe_matches:
                            print(f"   🖼️ Iframe aninhado: {iframe_matches[0]}")
                            # Recursivamente analisar iframe
                            nested_video = analyze_nested_iframe(session, iframe_matches[0], url)
                            if nested_video:
                                return nested_video
                
                elif resp.status_code == 404:
                    print(f"   ❌ 404 - Não encontrado")
                else:
                    print(f"   ⚠️ Status: {resp.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)[:50]}")
        
        # 5. Tentar métodos POST
        print("\n🔍 5. Testando métodos POST...")
        
        post_endpoints = [
            "/api/episode",
            "/ajax/video", 
            "/get_source",
            "/load_video"
        ]
        
        post_data_variations = [
            {'series': series_name, 'episode': '1'},
            {'series': series_name, 'season': '1', 'episode': '1'},
            {'name': series_name, 'ep': '1'},
            {'video': series_name},
            {'id': series_name}
        ]
        
        for endpoint in post_endpoints:
            for post_data in post_data_variations:
                try:
                    url = base_url + endpoint
                    print(f"🔗 POST: {url} - Data: {post_data}")
                    
                    headers = {
                        'Referer': player_url,
                        'Accept': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                    
                    resp = session.post(url, data=post_data, headers=headers, timeout=8)
                    
                    if resp.status_code == 200:
                        print(f"   ✅ POST Sucesso: {resp.status_code}")
                        
                        try:
                            json_data = resp.json()
                            video_url = extract_video_from_data(json_data)
                            if video_url:
                                print(f"   🎥 VÍDEO POST: {video_url}")
                                return video_url
                        except:
                            video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', resp.text)
                            if video_urls:
                                print(f"   🎥 VÍDEO POST: {video_urls[0]}")
                                return video_urls[0]
                    
                except Exception as e:
                    print(f"   ❌ POST Erro: {str(e)[:30]}")
        
        print("\n❌ NENHUM LINK DIRETO ENCONTRADO")
        return None
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None

def analyze_nested_iframe(session, iframe_url, referer):
    """Analisar iframe aninhado"""
    try:
        if iframe_url.startswith('//'):
            iframe_url = 'https:' + iframe_url
        elif iframe_url.startswith('/'):
            iframe_url = 'https://playerthree.online' + iframe_url
        
        print(f"   🔍 Analisando iframe: {iframe_url}")
        
        response = session.get(iframe_url, headers={'Referer': referer}, timeout=10)
        
        if response.status_code == 200:
            # Procurar vídeos no iframe
            video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', response.text)
            if video_urls:
                return video_urls[0]
        
    except Exception as e:
        print(f"   ❌ Erro no iframe: {e}")
    
    return None

def extract_video_from_data(data):
    """Extrair URL de vídeo de qualquer estrutura de dados"""
    if isinstance(data, dict):
        # Campos comuns
        video_fields = ['file', 'url', 'source', 'src', 'video', 'stream', 'link', 'hls', 'm3u8', 'mp4', 'playlist']
        
        for field in video_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str) and is_video_url(value):
                    return value
        
        # Procurar recursivamente
        for value in data.values():
            if isinstance(value, (dict, list)):
                result = extract_video_from_data(value)
                if result:
                    return result
    
    elif isinstance(data, list):
        for item in data:
            result = extract_video_from_data(item)
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
    result = deep_playerthree_analysis()
    
    if result:
        print(f"\n🏆 SUCESSO! Link direto encontrado:")
        print(f"🎥 {result}")
    else:
        print(f"\n💡 RECOMENDAÇÕES:")
        print("   1. Usar WebView com JavaScript injection")
        print("   2. Simular cliques em botões de play")
        print("   3. Interceptar requisições de rede")
        print("   4. Aguardar carregamento do JWPlayer")