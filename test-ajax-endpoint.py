#!/usr/bin/env python3
"""
Testar endpoint AJAX que retorna os players reais
"""

import requests
from bs4 import BeautifulSoup
import json

def test_ajax_endpoint():
    print("🎯 TESTANDO ENDPOINT AJAX DOS PLAYERS")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://playerthree.online/embed/synden/',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    # Endpoint descoberto: /episodio/{episodeId}
    base_url = "https://playerthree.online"
    episode_id = "255703"  # Primeiro episódio de Terra de Pecados
    
    ajax_url = f"{base_url}/episodio/{episode_id}"
    
    print(f"📡 Testando: {ajax_url}")
    
    try:
        response = session.get(ajax_url)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📏 Tamanho: {len(response.text)} chars")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Salvar resposta
            with open('ajax_response.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("💾 Resposta salva em: ajax_response.html")
            
            # Analisar HTML retornado
            soup = BeautifulSoup(html_content, 'html.parser')
            
            print(f"\n🔍 ANÁLISE DA RESPOSTA AJAX:")
            
            # Procurar botões de player
            player_buttons = soup.select('button[data-source], .btn[data-source], button[data-show-player]')
            print(f"🎮 Botões de player encontrados: {len(player_buttons)}")
            
            for i, button in enumerate(player_buttons):
                data_source = button.get('data-source', '')
                data_show_player = button.get('data-show-player', '')
                button_text = button.get_text(strip=True)
                
                print(f"  🎯 Player {i+1}: {button_text}")
                print(f"    data-source: {data_source}")
                print(f"    data-show-player: {data_show_player}")
                
                # Verificar se é trailer
                if 'youtube' in data_source.lower() or 'trailer' in data_source.lower():
                    print(f"    🚨 TRAILER DETECTADO!")
                elif data_source and data_source.startswith('http'):
                    print(f"    ✅ PLAYER VÁLIDO!")
            
            # Procurar divs de player
            player_divs = soup.select('div[id*="player"], .choose-player, #players')
            print(f"\n📦 Divs de player: {len(player_divs)}")
            
            for div in player_divs:
                print(f"  📦 {div.get('id', 'no-id')} - {div.get('class', 'no-class')}")
            
            # Procurar scripts com configurações
            scripts = soup.select('script')
            print(f"\n📜 Scripts: {len(scripts)}")
            
            for script in scripts:
                content = script.string or ''
                if 'gleam' in content or 'player' in content.lower():
                    print(f"  📜 Script com configurações: {len(content)} chars")
                    if len(content) < 500:
                        print(f"    📄 {content}")
            
            # Mostrar HTML completo se for pequeno
            if len(html_content) < 2000:
                print(f"\n📄 HTML COMPLETO:")
                print(html_content)
        
        else:
            print(f"❌ Erro: Status {response.status_code}")
            print(f"📄 Resposta: {response.text[:500]}...")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def test_multiple_episodes():
    """Testar múltiplos episódios"""
    print("\n🎬 TESTANDO MÚLTIPLOS EPISÓDIOS")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://playerthree.online/embed/synden/',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    base_url = "https://playerthree.online"
    episode_ids = ["255703", "255704", "255705"]  # Primeiros 3 episódios
    
    for i, episode_id in enumerate(episode_ids):
        print(f"\n📺 Episódio {i+1} (ID: {episode_id}):")
        
        ajax_url = f"{base_url}/episodio/{episode_id}"
        
        try:
            response = session.get(ajax_url)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Contar players
                player_buttons = soup.select('button[data-source], .btn[data-source]')
                print(f"  Players: {len(player_buttons)}")
                
                # Mostrar URLs dos players
                for j, button in enumerate(player_buttons[:3]):
                    data_source = button.get('data-source', '')
                    if data_source:
                        print(f"    Player {j+1}: {data_source}")
            
        except Exception as e:
            print(f"  ❌ Erro: {e}")

if __name__ == "__main__":
    test_ajax_endpoint()
    test_multiple_episodes()