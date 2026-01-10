#!/usr/bin/env python3
import requests
import re

def test_direct_video():
    print("🎥 TESTE LINK DIRETO DE VÍDEO")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Passo 1: Obter player
    print("1. Obtendo player...")
    page = session.get("https://www.maxseries.one/series/assistir-breaking-bad-a-quimica-do-mal-online")
    
    iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', page.text)
    if iframe_match:
        player_url = iframe_match.group(1)
        if player_url.startswith('//'):
            player_url = 'https:' + player_url
        print(f"✅ Player: {player_url}")
        
        # Passo 2: Acessar player
        print("2. Acessando player...")
        player_response = session.get(player_url)
        player_html = player_response.text
        
        print(f"✅ Player acessível: {player_response.status_code}")
        
        # Passo 3: Procurar vídeos
        print("3. Procurando links de vídeo...")
        
        # Padrões de vídeo
        patterns = [
            r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.m3u8[^"\']*)["\']',
            r'file:\s*["\']([^"\']+\.mp4[^"\']*)["\']',
            r'["\']([^"\']*https?://[^"\']*\.mp4[^"\']*)["\']',
            r'source:\s*["\']([^"\']+)["\']',
            r'src:\s*["\']([^"\']+)["\']'
        ]
        
        found_videos = []
        for pattern in patterns:
            matches = re.findall(pattern, player_html)
            for match in matches:
                if match.startswith('http') and ('.m3u8' in match or '.mp4' in match):
                    found_videos.append(match)
        
        if found_videos:
            print(f"🎥 {len(found_videos)} links encontrados:")
            for i, video in enumerate(found_videos):
                print(f"   {i+1}. {video}")
                
                # Testar primeiro link
                if i == 0:
                    try:
                        test_response = session.head(video, timeout=5)
                        print(f"      Status: {test_response.status_code}")
                    except:
                        print("      Status: Não testável")
        else:
            print("❌ Nenhum link direto encontrado")
            
            # Verificar se tem JavaScript
            if 'jwplayer' in player_html.lower():
                print("💡 Player usa JWPlayer - pode precisar de JavaScript")
            if 'eval(function(' in player_html:
                print("💡 JavaScript empacotado detectado")
            
            # Mostrar parte do HTML para debug
            print("\n📄 Amostra do HTML do player:")
            lines = player_html.split('\n')
            for line in lines[:20]:
                if 'file' in line.lower() or 'source' in line.lower() or 'src' in line.lower():
                    print(f"   {line.strip()[:100]}")
    else:
        print("❌ Nenhum iframe encontrado")

if __name__ == "__main__":
    test_direct_video()