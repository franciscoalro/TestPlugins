#!/usr/bin/env python3
"""
Analisar app.js para entender como os players são carregados
"""

import requests
import re

def analyze_app_js():
    print("📜 ANALISANDO APP.JS")
    print("=" * 40)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # URL do app.js
    app_js_url = "https://playerthree.online/static/js/app.js?v=1757386115"
    
    try:
        print(f"📥 Carregando: {app_js_url}")
        response = session.get(app_js_url)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📏 Tamanho: {len(response.text)} chars")
        
        js_content = response.text
        
        # Salvar para análise
        with open('app.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print("💾 JavaScript salvo em: app.js")
        
        # Procurar por padrões importantes
        print("\n🔍 PROCURANDO PADRÕES IMPORTANTES:")
        
        patterns = [
            (r'function.*click.*{[^}]*}', 'Funções de clique'),
            (r'data-source.*=', 'Configuração data-source'),
            (r'playerembedapi\.link', 'PlayerEmbedAPI'),
            (r'megaembed\.link', 'MegaEmbed'),
            (r'gleam\.redirect', 'Gleam redirect'),
            (r'createElement.*button', 'Criação de botões'),
            (r'innerHTML.*=.*button', 'Inserção de botões'),
            (r'#\d+_\d+', 'Padrão de episódios'),
            (r'ajax.*post', 'Chamadas AJAX'),
            (r'fetch.*post', 'Chamadas Fetch')
        ]
        
        for pattern, description in patterns:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            if matches:
                print(f"  🎯 {description}: {len(matches)} matches")
                for match in matches[:2]:
                    print(f"    📜 {str(match)[:100]}...")
        
        # Procurar especificamente por lógica de carregamento de players
        print("\n🎮 PROCURANDO LÓGICA DE PLAYERS:")
        
        # Dividir em funções
        functions = re.findall(r'function\s+\w+[^{]*{[^}]*(?:{[^}]*}[^}]*)*}', js_content)
        print(f"📋 Funções encontradas: {len(functions)}")
        
        for i, func in enumerate(functions[:5]):
            if 'player' in func.lower() or 'click' in func.lower():
                print(f"  🎯 Função {i}: {func[:150]}...")
        
        # Procurar por event listeners
        event_patterns = [
            r'addEventListener\([^)]+\)',
            r'\.click\([^)]*\)',
            r'\.on\([^)]+\)',
            r'\$\([^)]+\)\.click'
        ]
        
        print("\n🖱️ PROCURANDO EVENT LISTENERS:")
        for pattern in event_patterns:
            matches = re.findall(pattern, js_content)
            if matches:
                print(f"  🎯 {pattern}: {len(matches)} matches")
                for match in matches[:2]:
                    print(f"    📜 {match}")
        
        # Procurar por URLs hardcoded
        print("\n🔗 PROCURANDO URLS HARDCODED:")
        url_patterns = [
            r'https://playerembedapi\.link[^"\'>\s]*',
            r'https://megaembed\.link[^"\'>\s]*',
            r'https://[^"\'>\s]*embed[^"\'>\s]*'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, js_content)
            if matches:
                print(f"  🎯 {pattern}: {len(matches)} matches")
                for match in matches:
                    print(f"    🔗 {match}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    analyze_app_js()