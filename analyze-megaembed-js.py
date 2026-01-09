#!/usr/bin/env python3
"""
Analisa o JavaScript do MegaEmbed para entender a decriptação
"""

import requests
import re
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://megaembed.link/',
}

def get_main_js():
    """Baixa o JS principal do MegaEmbed"""
    
    # Primeiro, pegar a página principal para encontrar o JS
    print("1. Buscando página principal...")
    resp = requests.get("https://megaembed.link/", headers=HEADERS, timeout=30)
    
    # Encontrar arquivos JS
    js_files = re.findall(r'src="(/assets/[^"]+\.js)"', resp.text)
    print(f"   Arquivos JS encontrados: {len(js_files)}")
    
    for js_file in js_files:
        print(f"   - {js_file}")
    
    # Baixar o index JS (geralmente contém a lógica principal)
    index_js = None
    for js in js_files:
        if 'index' in js.lower():
            index_js = js
            break
    
    if not index_js and js_files:
        index_js = js_files[0]
    
    if index_js:
        print(f"\n2. Baixando: {index_js}")
        js_url = f"https://megaembed.link{index_js}"
        js_resp = requests.get(js_url, headers=HEADERS, timeout=30)
        
        print(f"   Tamanho: {len(js_resp.text)} bytes")
        
        # Salvar
        with open('megaembed_index.js', 'w', encoding='utf-8') as f:
            f.write(js_resp.text)
        print("   Salvo em: megaembed_index.js")
        
        return js_resp.text
    
    return None

def analyze_js(js_code):
    """Analisa o código JS procurando padrões de decriptação"""
    
    print("\n3. Analisando código JS...")
    
    # Padrões de interesse
    patterns = {
        'decrypt': r'decrypt|decipher|decode',
        'aes': r'aes|AES|crypto',
        'key': r'key\s*[=:]\s*["\'][^"\']+["\']',
        'iv': r'iv\s*[=:]\s*["\'][^"\']+["\']',
        'api_call': r'api/v1/info',
        'fetch': r'fetch\s*\([^)]+\)',
        'hex': r'hex|fromCharCode',
        'base64': r'atob|btoa|base64',
        'json_parse': r'JSON\.parse',
    }
    
    print("\n   Padrões encontrados:")
    for name, pattern in patterns.items():
        matches = re.findall(pattern, js_code, re.I)
        if matches:
            print(f"   - {name}: {len(matches)} ocorrências")
            if len(matches) <= 5:
                for m in matches[:3]:
                    print(f"     '{m[:50]}...'")
    
    # Procurar funções de decriptação
    print("\n4. Procurando funções de decriptação...")
    
    # Padrão comum: função que recebe dados criptografados
    decrypt_patterns = [
        r'function\s+\w*[Dd]ecrypt\w*\s*\([^)]*\)\s*\{[^}]{50,500}\}',
        r'const\s+\w*[Dd]ecrypt\w*\s*=\s*\([^)]*\)\s*=>\s*\{[^}]{50,500}\}',
        r'[Dd]ecrypt\s*:\s*function\s*\([^)]*\)\s*\{[^}]{50,500}\}',
    ]
    
    for pattern in decrypt_patterns:
        matches = re.findall(pattern, js_code, re.S)
        if matches:
            print(f"\n   Função de decriptação encontrada:")
            for m in matches[:2]:
                print(f"   {m[:300]}...")
    
    # Procurar uso da API
    print("\n5. Procurando uso da API...")
    api_pattern = r'.{0,100}api/v1/info.{0,200}'
    matches = re.findall(api_pattern, js_code)
    if matches:
        for m in matches[:3]:
            print(f"   {m[:150]}...")
    
    # Procurar chaves hardcoded
    print("\n6. Procurando chaves/secrets...")
    key_patterns = [
        r'["\'][a-fA-F0-9]{32}["\']',  # MD5-like
        r'["\'][a-fA-F0-9]{64}["\']',  # SHA256-like
        r'["\'][A-Za-z0-9+/]{20,}={0,2}["\']',  # Base64
    ]
    
    for pattern in key_patterns:
        matches = re.findall(pattern, js_code)
        if matches:
            print(f"   Possíveis chaves ({len(matches)}):")
            for m in matches[:5]:
                print(f"     {m[:50]}...")

def get_prod_js():
    """Baixa o prod.js que pode conter a lógica de decriptação"""
    
    print("\n7. Baixando prod.js...")
    
    # URL do prod.js (visto nos logs)
    prod_url = "https://megaembed.link/assets/prod-CZuje_L2.js"
    
    try:
        resp = requests.get(prod_url, headers=HEADERS, timeout=30)
        print(f"   Status: {resp.status_code}")
        print(f"   Tamanho: {len(resp.text)} bytes")
        
        with open('megaembed_prod.js', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("   Salvo em: megaembed_prod.js")
        
        return resp.text
    except Exception as e:
        print(f"   Erro: {e}")
        return None

def main():
    print("="*60)
    print("ANÁLISE DO JAVASCRIPT DO MEGAEMBED")
    print("="*60)
    
    # Baixar e analisar JS principal
    js_code = get_main_js()
    if js_code:
        analyze_js(js_code)
    
    # Baixar prod.js
    prod_js = get_prod_js()
    if prod_js:
        print("\n" + "="*60)
        print("ANÁLISE DO PROD.JS")
        print("="*60)
        analyze_js(prod_js)

if __name__ == "__main__":
    main()
