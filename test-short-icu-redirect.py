#!/usr/bin/env python3
"""
Test Short.icu Redirect Chain
"""

import requests
import re

def test_short_icu_redirect():
    print("🔍 TEST SHORT.ICU REDIRECT")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive'
    })
    
    url = "https://short.icu/K8R6OOjS7"
    referer = "https://abyss.to"
    
    print(f"🔗 URL: {url}")
    print(f"📄 Referer: {referer}")
    
    try:
        # Método 1: Sem allow_redirects para capturar Location header
        print(f"\n📡 MÉTODO 1: Capturar Location header...")
        
        response = session.get(url, headers={'Referer': referer}, timeout=10, allow_redirects=False)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location')
            if location:
                print(f"📍 Location: {location}")
                
                # Seguir o Location
                if location.startswith('http'):
                    print(f"\n🔄 Seguindo Location...")
                    
                    final_response = session.get(location, headers={'Referer': url}, timeout=15)
                    
                    print(f"📊 Final Status: {final_response.status_code}")
                    print(f"🔗 Final URL: {final_response.url}")
                    
                    if final_response.status_code == 200:
                        html = final_response.text
                        
                        # Procurar vídeos
                        video_patterns = [
                            r'https?://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                            r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                            r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*'
                        ]
                        
                        for pattern in video_patterns:
                            matches = re.findall(pattern, html)
                            if matches:
                                video_url = matches[0]
                                print(f"🎥 VÍDEO ENCONTRADO: {video_url}")
                                return video_url
                        
                        print(f"📄 HTML Sample: {html[:500]}...")
        
        # Método 2: Com allow_redirects
        print(f"\n📡 MÉTODO 2: Com allow_redirects...")
        
        response2 = session.get(url, headers={'Referer': referer}, timeout=15, allow_redirects=True)
        
        print(f"📊 Status: {response2.status_code}")
        print(f"🔗 Final URL: {response2.url}")
        
        if response2.status_code == 200:
            html = response2.text
            
            # Procurar vídeos
            video_patterns = [
                r'https?://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*'
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    video_url = matches[0]
                    print(f"🎥 VÍDEO MÉTODO 2: {video_url}")
                    return video_url
            
            print(f"📄 HTML Sample: {html[:500]}...")
        
        # Método 3: Simular JavaScript redirect
        print(f"\n📡 MÉTODO 3: Simular JavaScript...")
        
        # Primeiro, obter a página
        js_response = session.get(url, headers={'Referer': referer}, timeout=15)
        
        if js_response.status_code == 200:
            html = js_response.text
            
            # Procurar padrões de redirect JavaScript
            js_patterns = [
                r'window\.location\s*=\s*["\']([^"\']+)["\']',
                r'location\.href\s*=\s*["\']([^"\']+)["\']',
                r'document\.location\s*=\s*["\']([^"\']+)["\']',
                r'setTimeout\([^)]*["\']([^"\']*https?://[^"\']+)["\']',
                r'redirect\(["\']([^"\']+)["\']'
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, html)
                if matches:
                    redirect_url = matches[0]
                    print(f"🔗 JS Redirect: {redirect_url}")
                    
                    if redirect_url.startswith('http'):
                        js_final = session.get(redirect_url, headers={'Referer': url}, timeout=15)
                        
                        if js_final.status_code == 200:
                            # Procurar vídeos
                            for pattern in video_patterns:
                                matches = re.findall(pattern, js_final.text)
                                if matches:
                                    video_url = matches[0]
                                    print(f"🎥 VÍDEO JS: {video_url}")
                                    return video_url
            
            print(f"📄 JS HTML Sample: {html[:500]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return None

if __name__ == "__main__":
    result = test_short_icu_redirect()
    
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
        print(f"\n💡 CONCLUSÃO: Short.icu pode requerer JavaScript ou cookies específicos")