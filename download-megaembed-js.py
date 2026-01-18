#!/usr/bin/env python3
"""
Download e análise do JavaScript do MegaEmbed
"""

import requests
import re

# Baixar o JS principal
js_url = "https://megaembed.link/assets/index-CZ_ja_1t.js"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://megaembed.link/',
}

print(f"📥 Baixando: {js_url}")
response = requests.get(js_url, headers=headers)

if response.status_code == 200:
    js_content = response.text
    print(f"✅ Baixado: {len(js_content)} bytes")
    
    # Salvar
    with open('megaembed_index.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("💾 Salvo em: megaembed_index.js")
    
    # Análise básica
    print(f"\n{'='*80}\n🔍 ANÁLISE DO CÓDIGO:\n{'='*80}\n")
    
    # Procurar APIs
    api_patterns = [
        r'["\']/(api/[^"\']+)["\']',
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.[a-z]+\(["\']([^"\']+)["\']',
    ]
    
    apis_found = set()
    for pattern in api_patterns:
        matches = re.findall(pattern, js_content)
        apis_found.update(matches)
    
    if apis_found:
        print("🎯 APIs encontradas:")
        for api in sorted(apis_found):
            if 'api' in api.lower() or 'video' in api.lower() or 'source' in api.lower():
                print(f"   - {api}")
    
    # Procurar funções de decodificação
    print("\n🔐 Funções de decodificação:")
    if 'atob' in js_content:
        print("   ✅ atob() (Base64 decode)")
    if 'btoa' in js_content:
        print("   ✅ btoa() (Base64 encode)")
    if 'decrypt' in js_content.lower():
        print("   ✅ decrypt()")
    if 'decode' in js_content.lower():
        print("   ✅ decode()")
    
    # Procurar padrões de URL
    print("\n🔗 Padrões de URL:")
    url_patterns = re.findall(r'https?://[^\s\'"<>]+', js_content)
    unique_domains = set()
    for url in url_patterns:
        domain = re.match(r'https?://([^/]+)', url)
        if domain:
            unique_domains.add(domain.group(1))
    
    for domain in sorted(unique_domains):
        print(f"   - {domain}")
    
    # Procurar hash no código
    print("\n🆔 Procurando uso do hash (#):")
    hash_patterns = [
        r'location\.hash',
        r'window\.location\.hash',
        r'#[a-zA-Z0-9]+',
    ]
    
    for pattern in hash_patterns:
        if re.search(pattern, js_content):
            print(f"   ✅ Padrão encontrado: {pattern}")
    
    # Extrair trechos relevantes
    print(f"\n{'='*80}\n📝 TRECHOS RELEVANTES (primeiros 2000 chars):\n{'='*80}\n")
    print(js_content[:2000])
    
else:
    print(f"❌ Erro ao baixar: {response.status_code}")
