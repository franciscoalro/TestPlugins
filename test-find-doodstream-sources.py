#!/usr/bin/env python3
"""
Find DoodStream Sources in MaxSeries
"""

import requests
import re

def find_doodstream_sources():
    print("🔍 PROCURANDO SOURCES DOODSTREAM")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive'
    })
    
    # Testar diferentes séries e episódios
    test_series = [
        {
            'name': 'Terra de Pecados',
            'url': 'https://www.maxseries.one/series/assistir-terra-de-pecados-online',
            'player': 'https://playerthree.online/embed/synden/',
            'episodes': ['255703', '255704', '255705']
        },
        {
            'name': 'Breaking Bad',
            'url': 'https://www.maxseries.one/series/assistir-breaking-bad-a-quimica-do-mal-online',
            'player': 'https://playerthree.online/embed/breakingbad/',
            'episodes': ['3630', '3631', '3632']
        }
    ]
    
    doodstream_domains = [
        'myvidplay.com', 'bysebuho.com', 'g9r6.com',
        'doodstream.com', 'dood.to', 'dood.watch', 'dood.pm'
    ]
    
    for serie in test_series:
        print(f"\n📺 SÉRIE: {serie['name']}")
        print("-" * 40)
        
        for episode_id in serie['episodes']:
            print(f"\n🎬 Episódio ID: {episode_id}")
            
            try:
                # Chamar endpoint /episodio/{id}
                episodio_url = f"https://playerthree.online/episodio/{episode_id}"
                
                response = session.get(
                    episodio_url, 
                    headers={'Referer': serie['player']}, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Episódio carregado")
                    
                    # Extrair todos os sources
                    source_buttons = re.findall(r'data-source="([^"]+)"', response.text)
                    
                    if source_buttons:
                        print(f"   🔘 Sources encontrados: {len(source_buttons)}")
                        
                        for i, source_url in enumerate(source_buttons):
                            print(f"      {i+1}. {source_url}")
                            
                            # Verificar se é DoodStream
                            is_doodstream = any(domain in source_url.lower() for domain in doodstream_domains)
                            
                            if is_doodstream:
                                print(f"         🎯 DOODSTREAM ENCONTRADO!")
                                
                                # Testar extração DoodStream
                                video_url = test_doodstream_extraction(source_url, serie['player'])
                                if video_url:
                                    print(f"         🎥 VÍDEO EXTRAÍDO: {video_url}")
                                    return video_url
                            
                            elif 'megaembed' in source_url.lower():
                                print(f"         🔐 MegaEmbed (encriptado)")
                            elif 'playerembedapi' in source_url.lower():
                                print(f"         🔗 PlayerEmbedAPI (redirect chain)")
                            else:
                                print(f"         ❓ Desconhecido")
                    else:
                        print(f"   ❌ Nenhum source encontrado")
                else:
                    print(f"   ❌ Erro: {response.status_code}")
            
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    return None

def test_doodstream_extraction(url, referer):
    """Testar extração DoodStream usando algoritmo do MaxSeries"""
    print(f"         🔧 Testando extração DoodStream...")
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': referer
        })
        
        # Converter /d/ para /e/
        embed_url = url.replace('/d/', '/e/')
        
        response = session.get(embed_url, timeout=15)
        
        if response.status_code == 200:
            html = response.text
            host = re.match(r'https?://[^/]+', response.url).group(0)
            
            # Procurar pass_md5
            md5_match = re.search(r'/pass_md5/[^"\'&\s]+', html)
            if md5_match:
                md5_path = md5_match.group(0)
                md5_url = host + md5_path
                
                print(f"         🔑 pass_md5: {md5_url}")
                
                # Obter base URL
                md5_response = session.get(md5_url, headers={'Referer': response.url}, timeout=10)
                base_url = md5_response.text.strip()
                
                if base_url.startswith('http'):
                    # Montar URL final
                    import time
                    import string
                    import random
                    
                    token = md5_path.split('/')[-1]
                    expiry = int(time.time() * 1000)
                    
                    # Hash table
                    alphabet = string.ascii_letters + string.digits
                    hash_table = ''.join(random.choice(alphabet) for _ in range(10))
                    
                    final_url = f"{base_url}{hash_table}?token={token}&expiry={expiry}"
                    
                    print(f"         ✅ URL final gerada")
                    return final_url
                else:
                    print(f"         ❌ Base URL inválida: {base_url}")
            else:
                print(f"         ❌ pass_md5 não encontrado")
        else:
            print(f"         ❌ Erro embed: {response.status_code}")
    
    except Exception as e:
        print(f"         ❌ Erro extração: {e}")
    
    return None

if __name__ == "__main__":
    result = find_doodstream_sources()
    
    if result:
        print(f"\n🏆 SUCESSO! DoodStream extraído:")
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
        print(f"\n💡 CONCLUSÃO:")
        print("   - PlayerEmbedAPI/MegaEmbed requerem WebView para bypass de proteções")
        print("   - HTTP puro funciona para DoodStream quando disponível")
        print("   - MaxSeries Provider já tem implementação híbrida otimizada")