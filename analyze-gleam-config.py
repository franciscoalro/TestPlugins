#!/usr/bin/env python3
"""
Análise do gleam.config - MaxSeries
Entender como funciona o sistema de players
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_gleam_system():
    print("🎬 ANÁLISE DO SISTEMA GLEAM")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # URL do episódio
    episode_url = "https://playerthree.online/embed/synden/#12962_255703"
    print(f"📺 Analisando: {episode_url}")
    
    try:
        response = session.get(episode_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"✅ Status: {response.status_code}")
        
        # 1. Extrair gleam.config completo
        scripts = soup.select('script')
        gleam_config = None
        
        for script in scripts:
            content = script.string or ''
            if 'gleam.config' in content:
                print("🎯 gleam.config encontrado!")
                
                # Extrair configuração completa
                gleam_match = re.search(r'gleam\.config\s*=\s*({[^;]+});', content, re.DOTALL)
                if gleam_match:
                    config_str = gleam_match.group(1)
                    try:
                        # Limpar e parsear JSON
                        config_str = config_str.replace('\/', '/')
                        gleam_config = json.loads(config_str)
                        print("📋 Configuração gleam extraída:")
                        for key, value in gleam_config.items():
                            print(f"  {key}: {value}")
                    except Exception as e:
                        print(f"❌ Erro ao parsear JSON: {e}")
                        print(f"📄 Config raw: {config_str[:500]}...")
        
        # 2. Procurar função gleam.redirect
        redirect_function = None
        for script in scripts:
            content = script.string or ''
            if 'gleam.redirect' in content:
                print("🔄 gleam.redirect encontrado!")
                
                # Extrair função redirect
                redirect_match = re.search(r'gleam\.redirect\s*=\s*function[^}]+}[^}]*}', content, re.DOTALL)
                if redirect_match:
                    redirect_function = redirect_match.group(0)
                    print(f"📋 Função redirect: {redirect_function[:200]}...")
        
        # 3. Analisar HTML para encontrar players ocultos
        print("\n🔍 Procurando players ocultos...")
        
        # Procurar divs com IDs específicos
        player_divs = soup.select('div[id*="player"], div[class*="player"]')
        print(f"📦 Divs de player encontradas: {len(player_divs)}")
        
        for div in player_divs:
            print(f"  📦 {div.get('id', 'no-id')} - {div.get('class', 'no-class')}")
        
        # Procurar botões ocultos ou com display:none
        all_buttons = soup.select('button, .btn')
        print(f"🔘 Total de botões: {len(all_buttons)}")
        
        for i, button in enumerate(all_buttons):
            data_source = button.get('data-source')
            data_show_player = button.get('data-show-player')
            style = button.get('style', '')
            
            if data_source or data_show_player:
                print(f"  🎮 Botão {i}: {button.get_text(strip=True)}")
                print(f"    data-source: {data_source}")
                print(f"    data-show-player: {data_show_player}")
                print(f"    style: {style}")
                print(f"    visible: {'display:none' not in style}")
        
        # 4. Procurar no HTML completo por padrões de player
        html_content = response.text
        
        # Procurar URLs de player
        player_patterns = [
            r'https://playerembedapi\.link/[^"\'>\s]+',
            r'https://megaembed\.link/[^"\'>\s]+',
            r'https://[^"\'>\s]*embed[^"\'>\s]*',
            r'data-source=["\']([^"\']+)["\']'
        ]
        
        print("\n🎯 Procurando padrões de player no HTML:")
        for pattern in player_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                print(f"  📺 Padrão {pattern[:30]}...: {len(matches)} matches")
                for match in matches[:3]:
                    print(f"    🔗 {match}")
        
        # 5. Analisar redirector_url do gleam.config
        if gleam_config and 'redirector_url' in gleam_config:
            redirector_url = gleam_config['redirector_url']
            print(f"\n🔄 Analisando redirector: {redirector_url}")
            
            # Simular chamada do redirector
            if '{token}' in redirector_url:
                # Criar token de exemplo
                example_token = {
                    "type": "iframe",
                    "cc": None,
                    "url": "https://playerembedapi.link/?v=example"
                }
                
                import base64
                token = base64.b64encode(json.dumps(example_token).encode()).decode()
                test_redirector_url = redirector_url.replace('{token}', token)
                
                print(f"🧪 Testando redirector: {test_redirector_url}")
                
                try:
                    redirector_response = session.get(test_redirector_url)
                    print(f"✅ Redirector Status: {redirector_response.status_code}")
                    
                    if redirector_response.status_code == 200:
                        print(f"📄 Redirector Response: {redirector_response.text[:200]}...")
                except Exception as e:
                    print(f"❌ Erro no redirector: {e}")
        
        # 6. Procurar dados em JavaScript inline
        print("\n📜 Analisando JavaScript inline:")
        
        js_patterns = [
            r'var\s+players?\s*=\s*(\[[^\]]+\])',
            r'var\s+sources?\s*=\s*(\[[^\]]+\])',
            r'jwplayer\([^)]*\)\.setup\(([^)]+)\)',
            r'"file"\s*:\s*"([^"]+)"'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                print(f"  📺 JS Padrão {pattern[:30]}...: {len(matches)} matches")
                for match in matches[:2]:
                    print(f"    🔗 {str(match)[:100]}...")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analyze_gleam_system()