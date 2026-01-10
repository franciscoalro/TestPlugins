#!/usr/bin/env python3
"""
Debug PlayerEmbedAPI Redirect Chain
"""

import requests
import re

def debug_playerembedapi():
    print("🔍 DEBUG PLAYEREMBEDAPI")
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
    
    url = "https://playerembedapi.link/?v=kBJLtxCD3"
    
    print(f"🔗 URL: {url}")
    
    try:
        # Passo 1: Acessar PlayerEmbedAPI
        print(f"\n📡 PASSO 1: Acessando PlayerEmbedAPI...")
        
        response = session.get(url, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"🔗 Final URL: {response.url}")
        print(f"📏 Content: {len(response.text)} chars")
        
        html = response.text
        
        # Procurar padrões de redirecionamento
        print(f"\n🔍 PROCURANDO REDIRECIONAMENTOS...")
        
        redirect_patterns = [
            (r'["\']([^"\']*short\.icu[^"\']*)["\']', 'short.icu'),
            (r'["\']([^"\']*abyss\.to[^"\']*)["\']', 'abyss.to'),
            (r'["\']([^"\']*storage\.googleapis\.com[^"\']*)["\']', 'GCS'),
            (r'location\.href\s*=\s*["\']([^"\']+)["\']', 'JS redirect'),
            (r'window\.location\s*=\s*["\']([^"\']+)["\']', 'Window redirect'),
            (r'document\.location\s*=\s*["\']([^"\']+)["\']', 'Document redirect')
        ]
        
        found_redirects = []
        
        for pattern, name in redirect_patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f"   🔗 {name}: {matches[:3]}")
                found_redirects.extend(matches)
        
        # Procurar vídeos diretos
        print(f"\n🎥 PROCURANDO VÍDEOS DIRETOS...")
        
        video_patterns = [
            r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
            r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
            r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f"   🎥 Vídeo direto: {matches[0]}")
                return matches[0]
        
        # Seguir redirecionamentos encontrados
        if found_redirects:
            print(f"\n🔄 SEGUINDO REDIRECIONAMENTOS...")
            
            for redirect_url in found_redirects[:3]:  # Máximo 3 redirects
                if not redirect_url.startswith('http'):
                    continue
                
                print(f"\n   🔗 Seguindo: {redirect_url}")
                
                try:
                    redirect_response = session.get(redirect_url, headers={'Referer': url}, timeout=10)
                    
                    print(f"      📊 Status: {redirect_response.status_code}")
                    print(f"      🔗 Final URL: {redirect_response.url}")
                    
                    if redirect_response.status_code == 200:
                        redirect_html = redirect_response.text
                        
                        # Procurar vídeos no redirect
                        for pattern in video_patterns:
                            matches = re.findall(pattern, redirect_html)
                            if matches:
                                print(f"      🎥 VÍDEO REDIRECT: {matches[0]}")
                                return matches[0]
                        
                        # Procurar mais redirects
                        for pattern, name in redirect_patterns:
                            matches = re.findall(pattern, redirect_html)
                            if matches:
                                print(f"      🔗 Mais redirects {name}: {matches[:2]}")
                                
                                # Seguir um nível mais profundo
                                for next_redirect in matches[:1]:
                                    if next_redirect.startswith('http') and next_redirect != redirect_url:
                                        print(f"\n         🔗 Nível 2: {next_redirect}")
                                        
                                        try:
                                            level2_response = session.get(next_redirect, headers={'Referer': redirect_url}, timeout=10)
                                            
                                            if level2_response.status_code == 200:
                                                # Procurar vídeos no nível 2
                                                for pattern in video_patterns:
                                                    matches = re.findall(pattern, level2_response.text)
                                                    if matches:
                                                        print(f"            🎥 VÍDEO NÍVEL 2: {matches[0]}")
                                                        return matches[0]
                                        except Exception as e:
                                            print(f"            ❌ Erro nível 2: {e}")
                
                except Exception as e:
                    print(f"      ❌ Erro redirect: {e}")
        
        # Se não encontrou nada, mostrar parte do HTML para análise
        print(f"\n📄 HTML SAMPLE (primeiros 1000 chars):")
        print("-" * 50)
        print(html[:1000])
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    return None

if __name__ == "__main__":
    result = debug_playerembedapi()
    
    if result:
        print(f"\n🏆 VÍDEO ENCONTRADO: {result}")
        
        # Testar o link
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
        print(f"\n💡 CONCLUSÃO: PlayerEmbedAPI requer análise mais profunda")