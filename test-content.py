#!/usr/bin/env python3
import requests
import re
from urllib.parse import urljoin

def test_content():
    print("🎬 TESTE CONTEÚDO MAXSERIES")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://www.maxseries.one"
    
    try:
        # Testar página de séries
        print("🔍 Testando /series/...")
        series_response = session.get(f"{base_url}/series/", timeout=10)
        
        if series_response.status_code == 200:
            print("✅ Página de séries acessível")
            
            # Procurar links de séries específicas
            series_links = re.findall(r'href="([^"]*maxseries\.one/[^"]*(?:series|temporada)[^"]*)"', series_response.text)
            
            print(f"📺 Séries encontradas: {len(series_links)}")
            
            if series_links:
                # Testar primeira série
                test_series = series_links[0]
                print(f"\n🎯 Testando série: {test_series}")
                
                series_page = session.get(test_series, timeout=10)
                if series_page.status_code == 200:
                    print("✅ Página da série acessível")
                    
                    # Procurar player/iframe
                    iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', series_page.text)
                    
                    if iframes:
                        for iframe in iframes:
                            if iframe.startswith('//'):
                                iframe = 'https:' + iframe
                            print(f"🎬 Player: {iframe}")
                            
                            # Testar player
                            try:
                                player_response = session.get(iframe, timeout=10)
                                if player_response.status_code == 200:
                                    print("   ✅ Player acessível")
                                    
                                    # Identificar tipo e procurar padrões
                                    if "megaembed" in iframe.lower():
                                        print("   🎯 Tipo: MegaEmbed")
                                        # Procurar API call
                                        api_pattern = r'/api/v1/info\?id=([^"\'&]+)'
                                        if re.search(api_pattern, player_response.text):
                                            print("   ✅ API endpoint encontrado")
                                    
                                    elif "playerembedapi" in iframe.lower():
                                        print("   🎯 Tipo: PlayerEmbedAPI")
                                        # Procurar redirecionamentos
                                        if "short.icu" in player_response.text or "abyss.to" in player_response.text:
                                            print("   ✅ Cadeia de redirecionamento detectada")
                                    
                                    elif any(d in iframe.lower() for d in ["myvidplay", "bysebuho", "g9r6"]):
                                        print("   🎯 Tipo: DoodStream Clone")
                                        # Procurar pass_md5
                                        if "/pass_md5/" in player_response.text:
                                            print("   ✅ pass_md5 endpoint encontrado")
                                    
                                    # Procurar padrões de vídeo
                                    video_patterns = [
                                        r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                                        r'["\']([^"\']*storage\.googleapis\.com[^"\']*)["\']',
                                        r'/pass_md5/([^"\']+)',
                                        r'["\']([^"\']+\.mp4[^"\']*)["\']'
                                    ]
                                    
                                    found_videos = []
                                    for pattern in video_patterns:
                                        matches = re.findall(pattern, player_response.text)
                                        found_videos.extend(matches)
                                    
                                    if found_videos:
                                        print(f"   🎥 Padrões de vídeo: {len(found_videos)}")
                                        for vid in found_videos[:2]:
                                            print(f"      - {vid[:60]}...")
                                    else:
                                        print("   ⚠️ Nenhum padrão de vídeo encontrado")
                                        
                                        # Verificar se precisa JS
                                        if "eval(function(p,a,c,k,e" in player_response.text:
                                            print("   🔧 Requer JavaScript (P.A.C.K.E.R.)")
                                        if "<video" in player_response.text.lower():
                                            print("   🔧 Tem elemento <video>")
                                
                                else:
                                    print(f"   ❌ Player erro: {player_response.status_code}")
                            except Exception as e:
                                print(f"   ❌ Erro no player: {e}")
                    else:
                        print("⚠️ Nenhum iframe encontrado")
                else:
                    print(f"❌ Erro na série: {series_page.status_code}")
        else:
            print(f"❌ Erro em /series/: {series_response.status_code}")
        
        # Testar busca com termo específico
        print(f"\n🔍 Testando busca...")
        search_response = session.get(f"{base_url}/?s=breaking+bad", timeout=10)
        
        if search_response.status_code == 200:
            # Procurar primeiro resultado
            result_match = re.search(r'<div class="result-item">.*?<a href="([^"]+)"', search_response.text, re.DOTALL)
            if result_match:
                result_url = result_match.group(1)
                print(f"🎯 Primeiro resultado: {result_url}")
                
                result_page = session.get(result_url, timeout=10)
                if result_page.status_code == 200:
                    print("✅ Resultado acessível")
                    
                    # Verificar se tem player
                    result_iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', result_page.text)
                    if result_iframes:
                        print(f"🎬 Players no resultado: {len(result_iframes)}")
                    else:
                        print("⚠️ Nenhum player no resultado")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    print("\n✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_content()