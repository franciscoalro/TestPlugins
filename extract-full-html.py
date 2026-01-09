#!/usr/bin/env python3
"""
Extrair HTML completo para análise
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def extract_full_html():
    print("📄 EXTRAINDO HTML COMPLETO")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    episode_url = "https://playerthree.online/embed/synden/#12962_255703"
    
    try:
        response = session.get(episode_url)
        html_content = response.text
        
        print(f"✅ Status: {response.status_code}")
        print(f"📏 HTML Length: {len(html_content)}")
        
        # Salvar HTML completo
        with open('episode_full.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("💾 HTML salvo em: episode_full.html")
        
        # Procurar especificamente por botões de player
        print("\n🔍 PROCURANDO BOTÕES DE PLAYER:")
        
        # Padrões específicos do HTML que vimos antes
        button_patterns = [
            r'<button[^>]*data-source[^>]*>.*?</button>',
            r'<button[^>]*data-show-player[^>]*>.*?</button>',
            r'class="btn"[^>]*data-source[^>]*',
            r'#1 Dublado',
            r'#2 Dublado',
            r'playerembedapi\.link',
            r'megaembed\.link'
        ]
        
        for pattern in button_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"  🎯 Padrão '{pattern[:30]}...': {len(matches)} matches")
                for match in matches[:2]:
                    print(f"    📺 {str(match)[:150]}...")
        
        # Procurar por JavaScript que pode carregar players dinamicamente
        print("\n📜 PROCURANDO JAVASCRIPT DE PLAYERS:")
        
        js_patterns = [
            r'function.*player.*{[^}]*}',
            r'\.innerHTML\s*=.*player',
            r'document\.createElement.*button',
            r'data-source.*=',
            r'gleam\.redirect.*function'
        ]
        
        for pattern in js_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"  🎯 JS Padrão '{pattern[:30]}...': {len(matches)} matches")
                for match in matches[:1]:
                    print(f"    📜 {str(match)[:200]}...")
        
        # Extrair todo o JavaScript
        soup = BeautifulSoup(html_content, 'html.parser')
        scripts = soup.select('script')
        
        print(f"\n📜 SCRIPTS ENCONTRADOS: {len(scripts)}")
        
        for i, script in enumerate(scripts):
            content = script.string or ''
            src = script.get('src')
            
            if src:
                print(f"  📜 Script {i}: {src}")
            elif content:
                print(f"  📜 Script {i}: Inline ({len(content)} chars)")
                
                # Procurar por configurações importantes
                if 'gleam' in content:
                    print(f"    🎬 Contém gleam")
                if 'player' in content.lower():
                    print(f"    🎮 Contém player")
                if 'button' in content.lower():
                    print(f"    🔘 Contém button")
                if 'data-source' in content:
                    print(f"    🎯 Contém data-source")
        
        # Procurar especificamente pelo HTML que vimos no exemplo do usuário
        print("\n🔍 PROCURANDO ESTRUTURA VIEWPLAYER:")
        
        viewplayer_patterns = [
            r'<div class="choose-player"[^>]*>.*?</div>',
            r'<div id="players"[^>]*>.*?</div>',
            r'<button[^>]*#1 Dublado[^>]*>',
            r'<button[^>]*#2 Dublado[^>]*>'
        ]
        
        for pattern in viewplayer_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"  🎯 ViewPlayer '{pattern[:30]}...': {len(matches)} matches")
                for match in matches[:1]:
                    print(f"    📺 {str(match)[:300]}...")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    extract_full_html()