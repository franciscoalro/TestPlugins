#!/usr/bin/env python3
"""
Debug v49 Loading Issue
Testa se há problemas na nova implementação que impedem o carregamento
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def debug_maxseries_v49():
    """Debug do problema de carregamento na v49"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    # Testar uma série específica
    test_url = "https://www.maxseries.one/episodio/the-walking-dead-1x1/"
    
    print(f"🔍 DEBUGANDO: {test_url}")
    print("=" * 80)
    
    try:
        # 1. Carregar página principal
        response = session.get(test_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"📄 Status da página: {response.status_code}")
        print(f"📏 Tamanho da página: {len(response.text)} chars")
        
        # 2. Verificar se há iframe
        iframe = soup.find('iframe')
        if not iframe:
            print("❌ PROBLEMA: Nenhum iframe encontrado na página!")
            return False
            
        iframe_src = iframe.get('src', '')
        if iframe_src.startswith('//'):
            iframe_src = 'https:' + iframe_src
            
        print(f"🖼️ Iframe encontrado: {iframe_src}")
        
        # 3. Verificar se é PlayterThree
        if 'playerthree' not in iframe_src:
            print("❌ PROBLEMA: Iframe não é PlayterThree!")
            return False
            
        print("✅ PlayterThree detectado")
        
        # 4. Carregar iframe para extrair episode IDs
        iframe_response = session.get(iframe_src, headers={"Referer": test_url})
        print(f"📄 Status do iframe: {iframe_response.status_code}")
        
        if iframe_response.status_code != 200:
            print("❌ PROBLEMA: Não foi possível carregar iframe!")
            return False
            
        iframe_html = iframe_response.text
        print(f"📏 Tamanho do iframe: {len(iframe_html)} chars")
        
        # 5. Procurar episode IDs
        episode_ids = re.findall(r'data-episode-id["\s]*=["\s]*["\']?(\d+)', iframe_html)
        print(f"🆔 Episode IDs encontrados: {len(episode_ids)} - {episode_ids[:5]}")
        
        if not episode_ids:
            print("❌ PROBLEMA: Nenhum episode ID encontrado!")
            return False
            
        # 6. Testar AJAX calls
        sources_found = []
        for ep_id in episode_ids[:3]:  # Testar apenas os primeiros 3
            print(f"\n🧪 Testando Episode ID: {ep_id}")
            
            ajax_url = f"https://playerthree.online/episodio/{ep_id}"
            ajax_response = session.get(
                ajax_url,
                headers={
                    "Referer": test_url,
                    "X-Requested-With": "XMLHttpRequest"
                }
            )
            
            print(f"   📄 AJAX Status: {ajax_response.status_code}")
            
            if ajax_response.status_code == 200:
                ajax_soup = BeautifulSoup(ajax_response.text, 'html.parser')
                
                # Procurar botões com data-show-player (v48/v49 fix)
                buttons = ajax_soup.select("button[data-show-player]")
                print(f"   🔘 Botões data-show-player: {len(buttons)}")
                
                for btn in buttons:
                    src = btn.get('data-source', '')
                    player_text = btn.get_text(strip=True)
                    
                    if src.startswith('http') and 'youtube' not in src.lower():
                        source_type = get_source_type(src)
                        sources_found.append({
                            'url': src,
                            'type': source_type,
                            'player_text': player_text,
                            'episode_id': ep_id
                        })
                        
                        print(f"   ✅ {source_type}: {src}")
                        
                        # Se é MegaEmbed, testar se a v49 consegue extrair
                        if source_type == "MegaEmbed":
                            print(f"   🔬 Testando extração MegaEmbed v49...")
                            test_megaembed_v49(src)
                
                # Se encontrou fontes, parar
                if buttons:
                    break
        
        print(f"\n📊 RESUMO:")
        print(f"   Total de fontes encontradas: {len(sources_found)}")
        
        for source in sources_found:
            print(f"   - {source['type']}: {source['player_text']}")
        
        if not sources_found:
            print("❌ PROBLEMA CRÍTICO: Nenhuma fonte encontrada!")
            print("   Isso explica por que o vídeo não carrega!")
            return False
        
        print("✅ Fontes encontradas - problema pode estar na extração")
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        return False

def test_megaembed_v49(megaembed_url):
    """Testa se a implementação v49 do MegaEmbed funciona"""
    print(f"      🎬 URL MegaEmbed: {megaembed_url}")
    
    # Extrair videoId
    video_id = extract_video_id(megaembed_url)
    if not video_id:
        print(f"      ❌ Não foi possível extrair videoId")
        return False
        
    print(f"      🆔 VideoId: {video_id}")
    
    # Testar construção por padrão (método v49)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    cdn_domains = [
        "stzm.marvellaholdings.sbs",
        "srcf.marvellaholdings.sbs", 
        "sbi6.marvellaholdings.sbs",
        "s6p9.marvellaholdings.sbs"
    ]
    
    possible_shards = ["x6b", "x7c", "x8d"]
    timestamp = int(__import__('time').time())
    
    for cdn in cdn_domains:
        for shard in possible_shards:
            constructed_url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
            
            try:
                print(f"      🧪 Testando: {constructed_url}")
                
                response = session.get(
                    constructed_url,
                    headers={"Referer": "https://megaembed.link/"},
                    timeout=5
                )
                
                print(f"      📄 Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text
                    if "#EXTM3U" in content:
                        print(f"      ✅ SUCESSO! Playlist HLS válida encontrada")
                        print(f"      📄 Preview: {content[:100]}...")
                        return True
                    else:
                        print(f"      ⚠️ Resposta não é playlist HLS")
                        
            except Exception as e:
                print(f"      ❌ Erro: {e}")
                continue
    
    print(f"      ❌ Método v49 falhou para este vídeo")
    return False

def extract_video_id(url):
    """Extrai videoId da URL MegaEmbed"""
    patterns = [
        r'#([a-zA-Z0-9]+)$',
        r'/embed/([a-zA-Z0-9]+)',
        r'/([a-zA-Z0-9]+)/?$',
        r'id=([a-zA-Z0-9]+)',
        r'v=([a-zA-Z0-9]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_source_type(url):
    """Identifica tipo de fonte"""
    url_lower = url.lower()
    
    if 'megaembed' in url_lower:
        return "MegaEmbed"
    elif 'playerembedapi' in url_lower:
        return "PlayerEmbedAPI"
    elif any(domain in url_lower for domain in ['myvidplay', 'bysebuho', 'g9r6', 'doodstream', 'dood.', 'vidplay']):
        return "DoodStream"
    else:
        return "Other"

if __name__ == "__main__":
    print("🔧 DEBUG MAXSERIES V49 - PROBLEMA DE CARREGAMENTO")
    print("Investigando por que o vídeo não carrega...")
    print("="*80)
    
    success = debug_maxseries_v49()
    
    if success:
        print("\n✅ Fontes foram encontradas - problema pode estar na extração")
        print("🔧 Recomendação: Verificar logs do CloudStream ou criar v50 com mais debug")
    else:
        print("\n❌ Problema crítico identificado!")
        print("🔧 Recomendação: Corrigir problema de detecção de fontes")