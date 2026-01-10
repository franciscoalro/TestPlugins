#!/usr/bin/env python3
import requests
import re

def test_player():
    print("🎬 TESTE PLAYER MAXSERIES")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # URL específica que sabemos que tem player
    test_url = "https://www.maxseries.one/series/assistir-breaking-bad-a-quimica-do-mal-online"
    
    try:
        print(f"🔍 Acessando: {test_url}")
        response = session.get(test_url, timeout=15)
        
        if response.status_code == 200:
            print("✅ Página acessível")
            
            # Extrair iframe
            iframe_matches = re.findall(r'<iframe[^>]+src="([^"]+)"', response.text)
            
            if iframe_matches:
                iframe_url = iframe_matches[0]
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
                
                print(f"🎬 Player encontrado: {iframe_url}")
                
                # Testar player
                try:
                    player_response = session.get(iframe_url, timeout=15)
                    
                    if player_response.status_code == 200:
                        print("✅ Player acessível")
                        
                        # Identificar tipo
                        player_type = "Desconhecido"
                        if "megaembed" in iframe_url.lower():
                            player_type = "MegaEmbed"
                        elif "playerembedapi" in iframe_url.lower():
                            player_type = "PlayerEmbedAPI"
                        elif any(d in iframe_url.lower() for d in ["myvidplay", "bysebuho", "g9r6", "doodstream"]):
                            player_type = "DoodStream Clone"
                        
                        print(f"🎯 Tipo: {player_type}")
                        
                        # Análise específica por tipo
                        if player_type == "MegaEmbed":
                            print("\n📋 Análise MegaEmbed:")
                            
                            # Extrair ID
                            video_id = None
                            if "#" in iframe_url:
                                video_id = iframe_url.split("#")[-1]
                            elif "?v=" in iframe_url:
                                video_id = re.search(r'[?&]v=([^&]+)', iframe_url)
                                if video_id:
                                    video_id = video_id.group(1)
                            
                            if video_id:
                                print(f"   🆔 Video ID: {video_id}")
                                
                                # Testar API
                                api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
                                try:
                                    api_response = session.get(api_url, timeout=10)
                                    print(f"   🔗 API Status: {api_response.status_code}")
                                    if api_response.status_code == 200:
                                        api_data = api_response.text[:200]
                                        print(f"   📄 API Response: {api_data}...")
                                except Exception as e:
                                    print(f"   ❌ API Erro: {e}")
                            
                            # Procurar padrões no HTML
                            video_patterns = [
                                r'file:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                                r'source:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                                r'["\']([^"\']+\.m3u8[^"\']*)["\']'
                            ]
                            
                            for pattern in video_patterns:
                                matches = re.findall(pattern, player_response.text)
                                if matches:
                                    print(f"   🎥 M3U8 encontrado: {matches[0][:60]}...")
                                    break
                        
                        elif player_type == "PlayerEmbedAPI":
                            print("\n📋 Análise PlayerEmbedAPI:")
                            
                            # Procurar redirecionamentos
                            redirect_patterns = [
                                r'["\']([^"\']*short\.icu[^"\']*)["\']',
                                r'["\']([^"\']*abyss\.to[^"\']*)["\']',
                                r'["\']([^"\']*storage\.googleapis\.com[^"\']*)["\']'
                            ]
                            
                            for pattern in redirect_patterns:
                                matches = re.findall(pattern, player_response.text)
                                if matches:
                                    print(f"   🔗 Redirect encontrado: {matches[0][:60]}...")
                        
                        elif player_type == "DoodStream Clone":
                            print("\n📋 Análise DoodStream:")
                            
                            # Procurar pass_md5
                            md5_pattern = r'/pass_md5/([^"\'&\s]+)'
                            md5_matches = re.findall(md5_pattern, player_response.text)
                            
                            if md5_matches:
                                print(f"   🔑 pass_md5 encontrado: {md5_matches[0]}")
                                
                                # Testar endpoint
                                host = re.match(r'https?://[^/]+', iframe_url).group(0)
                                md5_url = f"{host}/pass_md5/{md5_matches[0]}"
                                
                                try:
                                    md5_response = session.get(md5_url, headers={'Referer': iframe_url}, timeout=10)
                                    print(f"   🔗 MD5 Status: {md5_response.status_code}")
                                    if md5_response.status_code == 200:
                                        base_url = md5_response.text.strip()
                                        print(f"   📄 Base URL: {base_url[:60]}...")
                                except Exception as e:
                                    print(f"   ❌ MD5 Erro: {e}")
                        
                        # Verificar se precisa JavaScript
                        js_indicators = [
                            ("P.A.C.K.E.R.", "eval(function(p,a,c,k,e" in player_response.text),
                            ("JWPlayer", "jwplayer" in player_response.text.lower()),
                            ("Video Element", "<video" in player_response.text.lower()),
                            ("HLS.js", "hls.js" in player_response.text.lower())
                        ]
                        
                        print("\n🔧 Indicadores JavaScript:")
                        for name, found in js_indicators:
                            status = "✅" if found else "❌"
                            print(f"   {status} {name}")
                        
                    else:
                        print(f"❌ Player erro: {player_response.status_code}")
                
                except Exception as e:
                    print(f"❌ Erro no player: {e}")
            else:
                print("❌ Nenhum iframe encontrado")
        else:
            print(f"❌ Página erro: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    print("\n✅ TESTE CONCLUÍDO")

if __name__ == "__main__":
    test_player()