#!/usr/bin/env python3
"""
Test AbyssCDN Access with Different Headers
"""

import requests
import re
import time

def test_abysscdn_access():
    print("🔍 TEST ABYSSCDN ACCESS")
    print("=" * 40)
    
    url = "https://abysscdn.com/?v=K8R6OOjS7"
    
    # Diferentes combinações de headers
    header_combinations = [
        {
            'name': 'Chrome Desktop',
            'headers': {
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
                'Referer': 'https://short.icu/'
            }
        },
        {
            'name': 'PlayerEmbedAPI Referer',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': 'https://playerembedapi.link/',
                'Origin': 'https://playerembedapi.link',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        },
        {
            'name': 'Abyss Referer',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': 'https://abyss.to/',
                'Origin': 'https://abyss.to',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        },
        {
            'name': 'Mobile',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                'Referer': 'https://short.icu/'
            }
        }
    ]
    
    for combo in header_combinations:
        print(f"\n🧪 TESTANDO: {combo['name']}")
        print("-" * 30)
        
        session = requests.Session()
        session.headers.update(combo['headers'])
        
        try:
            response = session.get(url, timeout=15)
            
            print(f"📊 Status: {response.status_code}")
            print(f"🔗 Final URL: {response.url}")
            print(f"📏 Content: {len(response.text)} chars")
            
            if response.status_code == 200:
                html = response.text
                
                # Procurar vídeos
                video_patterns = [
                    r'https?://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                    r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
                    r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
                ]
                
                for pattern in video_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        video_url = matches[0]
                        if is_video_url(video_url):
                            print(f"🎥 VÍDEO ENCONTRADO: {video_url}")
                            return video_url
                
                # Mostrar sample do HTML
                print(f"📄 HTML Sample: {html[:300]}...")
                
                # Procurar mais redirects
                redirect_patterns = [
                    r'window\.location\s*=\s*["\']([^"\']+)["\']',
                    r'location\.href\s*=\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in redirect_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        redirect_url = matches[0]
                        print(f"🔗 Redirect encontrado: {redirect_url}")
                        
                        if redirect_url.startswith('http'):
                            redirect_response = session.get(redirect_url, timeout=10)
                            
                            if redirect_response.status_code == 200:
                                for video_pattern in video_patterns:
                                    video_matches = re.findall(video_pattern, redirect_response.text)
                                    if video_matches:
                                        video_url = video_matches[0]
                                        if is_video_url(video_url):
                                            print(f"🎥 VÍDEO REDIRECT: {video_url}")
                                            return video_url
            
            elif response.status_code == 403:
                print("❌ 403 Forbidden - Headers insuficientes")
            else:
                print(f"❌ Erro: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Pequena pausa entre tentativas
        time.sleep(1)
    
    return None

def is_video_url(url):
    """Verificar se é URL de vídeo válida"""
    if not url or not isinstance(url, str):
        return False
    
    if not url.startswith('http'):
        return False
    
    video_indicators = ['.m3u8', '.mp4', '.mkv', '.avi', '.webm', '/hls/', '/video/', '/stream/', 'master.txt', 'storage.googleapis.com']
    return any(indicator in url.lower() for indicator in video_indicators)

if __name__ == "__main__":
    result = test_abysscdn_access()
    
    if result:
        print(f"\n🏆 SUCESSO! Vídeo encontrado:")
        print(f"🎥 {result}")
        
        # Testar o link
        try:
            session = requests.Session()
            test_response = session.head(result, timeout=10)
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
        print(f"\n💡 CONCLUSÃO: AbyssCDN requer autenticação específica ou cookies")
        print("   Recomendação: Focar em DoodStream que já funciona no MaxSeries")