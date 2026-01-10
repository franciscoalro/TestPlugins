#!/usr/bin/env python3
"""
Debug MegaEmbed API Response
"""

import requests
import re

def debug_megaembed_api():
    print("🔍 DEBUG MEGAEMBED API")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Referer': 'https://megaembed.link/',
        'Origin': 'https://megaembed.link'
    })
    
    video_id = "3wnuij"
    api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
    
    print(f"🔗 API URL: {api_url}")
    
    try:
        response = session.get(api_url, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        print(f"📝 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.text)}")
        
        print(f"\n📄 RAW RESPONSE:")
        print("-" * 40)
        print(response.text[:500])
        print("-" * 40)
        
        # Tentar diferentes parsers
        print(f"\n🔍 TENTATIVAS DE PARSING:")
        
        # 1. JSON
        try:
            json_data = response.json()
            print(f"✅ JSON: {json_data}")
        except Exception as e:
            print(f"❌ JSON: {e}")
        
        # 2. HTML parsing
        if '<' in response.text:
            print("🌐 Resposta parece ser HTML")
            
            # Procurar vídeos no HTML
            video_patterns = [
                r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
                r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
                r'file:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
                r'source:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']',
                r'src:\s*["\']([^"\']+\.(?:m3u8|mp4)[^"\']*)["\']'
            ]
            
            for i, pattern in enumerate(video_patterns):
                matches = re.findall(pattern, response.text)
                if matches:
                    print(f"   🎥 Padrão {i+1}: {matches[:3]}")
        
        # 3. Procurar redirecionamentos
        redirect_patterns = [
            r'location\.href\s*=\s*["\']([^"\']+)["\']',
            r'window\.location\s*=\s*["\']([^"\']+)["\']',
            r'document\.location\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in redirect_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                print(f"🔗 Redirect: {matches}")
        
        # 4. Procurar dados base64 ou encoded
        if 'atob(' in response.text or 'btoa(' in response.text:
            print("🔐 Contém dados base64")
        
        # 5. Tentar diferentes endpoints
        print(f"\n🔍 TESTANDO OUTROS ENDPOINTS:")
        
        other_endpoints = [
            f"https://megaembed.link/api/info?id={video_id}",
            f"https://megaembed.link/info?id={video_id}",
            f"https://megaembed.link/embed/{video_id}",
            f"https://megaembed.link/player/{video_id}",
            f"https://megaembed.link/#{video_id}"
        ]
        
        for endpoint in other_endpoints:
            try:
                resp = session.get(endpoint, timeout=10)
                print(f"   {endpoint}: {resp.status_code} ({len(resp.text)} chars)")
                
                if resp.status_code == 200 and len(resp.text) > 100:
                    # Procurar vídeos
                    video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', resp.text)
                    if video_urls:
                        print(f"      🎥 VÍDEO: {video_urls[0]}")
                        return video_urls[0]
            except Exception as e:
                print(f"   {endpoint}: ❌ {e}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    return None

if __name__ == "__main__":
    result = debug_megaembed_api()
    
    if result:
        print(f"\n🏆 VÍDEO ENCONTRADO: {result}")
    else:
        print(f"\n💡 CONCLUSÃO: MegaEmbed requer análise mais profunda")