#!/usr/bin/env python3
"""
Teste específico da API MegaEmbed
"""

import requests
import re

def test_megaembed():
    print("🔬 TESTE API MEGAEMBED")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
    })
    
    video_id = "3wnuij"
    megaembed_url = f"https://megaembed.link/#{video_id}"
    
    print(f"🎬 MegaEmbed URL: {megaembed_url}")
    print(f"🆔 Video ID: {video_id}")
    
    # 1. Testar API direta
    print("\n🔍 1. Testando API direta...")
    api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
    
    try:
        response = session.get(api_url, headers={
            'Referer': megaembed_url,
            'Origin': 'https://megaembed.link'
        }, timeout=10)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📄 Response: {response.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Acessar página principal do MegaEmbed
    print("\n🔍 2. Acessando página principal...")
    
    try:
        page_response = session.get(megaembed_url, timeout=15)
        html = page_response.text
        
        print(f"✅ Status: {page_response.status_code}")
        print(f"📄 HTML Size: {len(html)} chars")
        
        # Salvar HTML para análise
        with open('megaembed_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("💾 HTML salvo em: megaembed_response.html")
        
        # Procurar padrões de vídeo
        video_patterns = [
            r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'source:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
            r'hls:\s*["\']([^"\']+)["\']',
            r'playUrl:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f"🎥 Padrão encontrado: {matches[0]}")
        
        # Procurar scripts
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for i, script in enumerate(scripts):
            if len(script) > 100:
                print(f"\n📜 Script {i+1}: {len(script)} chars")
                print(f"   Preview: {script[:200]}...")
                
                # Procurar configurações
                if 'file' in script or 'source' in script or 'hls' in script:
                    print("   🎯 Contém configuração de vídeo!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Testar outros endpoints
    print("\n🔍 3. Testando outros endpoints...")
    
    endpoints = [
        f"/api/video/{video_id}",
        f"/api/source/{video_id}",
        f"/embed/{video_id}",
        f"/player/{video_id}",
        f"/v/{video_id}"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"https://megaembed.link{endpoint}"
            print(f"🔗 Testando: {url}")
            
            resp = session.get(url, headers={'Referer': megaembed_url}, timeout=8)
            
            if resp.status_code == 200:
                print(f"   ✅ Sucesso: {resp.status_code}")
                
                # Procurar vídeos
                video_urls = re.findall(r'https?://[^"\'<>\s]+\.(?:m3u8|mp4)[^"\'<>\s]*', resp.text)
                if video_urls:
                    print(f"   🎥 VÍDEO: {video_urls[0]}")
                    return video_urls[0]
            else:
                print(f"   ❌ Erro: {resp.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)[:50]}")
    
    return None

if __name__ == "__main__":
    result = test_megaembed()
    if result:
        print(f"\n🏆 VÍDEO ENCONTRADO: {result}")
    else:
        print(f"\n❌ Nenhum vídeo encontrado")