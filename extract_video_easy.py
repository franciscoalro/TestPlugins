#!/usr/bin/env python3
"""
Script Simplificado para Extração de Vídeos - MaxSeries
Uso: python extract_video_easy.py <URL_DO_EPISODIO>
Exemplo: python extract_video_easy.py https://maxseries.one/episodio/12345
"""

import sys
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def extract_video_links(episode_url):
    """Extrai links de vídeo de um episódio do MaxSeries"""
    
    print(f"\n🔍 Analisando: {episode_url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://maxseries.one/'
    }
    
    try:
        # 1. Buscar página do episódio
        print("📥 Baixando página do episódio...")
        response = requests.get(episode_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Encontrar iframes de players
        print("🎬 Procurando players de vídeo...")
        iframes = soup.find_all('iframe')
        
        video_sources = []
        
        for idx, iframe in enumerate(iframes, 1):
            src = iframe.get('src', '')
            if not src:
                continue
                
            # Normalizar URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(episode_url, src)
            
            print(f"\n  Player {idx}: {src}")
            
            # Identificar tipo de player
            player_type = "Desconhecido"
            if 'megaembed' in src.lower():
                player_type = "MegaEmbed"
            elif 'playerembedapi' in src.lower() or 'playerthree' in src.lower():
                player_type = "PlayerEmbedAPI"
            elif 'doodstream' in src.lower():
                player_type = "DoodStream"
            
            video_sources.append({
                'url': src,
                'type': player_type,
                'index': idx
            })
        
        # 3. Tentar extrair links diretos
        print("\n🔗 Tentando extrair links diretos M3U8...\n")
        
        for source in video_sources:
            print(f"  [{source['type']}] {source['url']}")
            
            try:
                # Tentar buscar o player
                player_response = requests.get(source['url'], headers=headers, timeout=10)
                
                # Procurar por M3U8 no HTML
                m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', player_response.text)
                
                if m3u8_matches:
                    print(f"    ✅ M3U8 encontrado: {m3u8_matches[0]}")
                    source['m3u8'] = m3u8_matches[0]
                else:
                    print(f"    ⚠️  M3U8 não encontrado diretamente")
                    
            except Exception as e:
                print(f"    ❌ Erro ao acessar player: {str(e)}")
        
        # 4. Resumo
        print("\n" + "="*60)
        print("📊 RESUMO DA EXTRAÇÃO")
        print("="*60)
        
        for source in video_sources:
            print(f"\n🎥 Player {source['index']} - {source['type']}")
            print(f"   URL: {source['url']}")
            if 'm3u8' in source:
                print(f"   ✅ M3U8: {source['m3u8']}")
            else:
                print(f"   ⚠️  Requer extração avançada (WebView/Selenium)")
        
        return video_sources
        
    except requests.RequestException as e:
        print(f"❌ Erro ao acessar URL: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return []

def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python extract_video_easy.py <URL_DO_EPISODIO>")
        print("   Exemplo: python extract_video_easy.py https://maxseries.one/episodio/12345")
        sys.exit(1)
    
    episode_url = sys.argv[1]
    
    if not episode_url.startswith('http'):
        print("❌ URL inválida. Deve começar com http:// ou https://")
        sys.exit(1)
    
    video_sources = extract_video_links(episode_url)
    
    if not video_sources:
        print("\n❌ Nenhum player de vídeo encontrado.")
        sys.exit(1)
    
    print("\n✅ Extração concluída!")
    print("\n💡 Dica: Para players que requerem WebView, use o script 'extract_video_advanced.py'")

if __name__ == "__main__":
    main()
