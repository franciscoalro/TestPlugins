#!/usr/bin/env python3
"""
Análise do algoritmo de geração de token do MegaEmbed
"""

import re
import json

# Ler o JS baixado
with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔍 ANALISANDO GERAÇÃO DE TOKEN DO MEGAEMBED")
print("=" * 80)

# 1. Procurar funções relacionadas a token
print("\n📌 Procurando funções de token...")
token_patterns = [
    r'function\s+(\w*[Tt]oken\w*)\s*\([^)]*\)\s*{([^}]{0,500})}',
    r'const\s+(\w*[Tt]oken\w*)\s*=\s*\([^)]*\)\s*=>\s*{([^}]{0,500})}',
    r'(\w+)\s*:\s*function\s*\([^)]*\)\s*{[^}]*token[^}]{0,300}}',
]

found_functions = []
for pattern in token_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} função(ões) com padrão: {pattern[:50]}...")
        for match in matches[:3]:
            if isinstance(match, tuple):
                print(f"      - {match[0]}")
                found_functions.append(match)

# 2. Procurar uso de location.hash
print("\n📌 Procurando uso de location.hash...")
hash_patterns = [
    r'location\.hash[^;]{0,200}',
    r'window\.location\.hash[^;]{0,200}',
    r'\.hash\.(?:slice|substring|replace)[^;]{0,200}',
]

for pattern in hash_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} uso(s):")
        for match in matches[:5]:
            print(f"      {match[:100]}")

# 3. Procurar chamadas à API player
print("\n📌 Procurando chamadas à API /api/v1/player...")
api_patterns = [
    r'["\']\/api\/v1\/player[^"\']*["\'][^;]{0,300}',
    r'fetch\([^)]*player[^)]{0,200}\)',
    r'axios\.[a-z]+\([^)]*player[^)]{0,200}\)',
]

for pattern in api_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} chamada(s):")
        for match in matches[:3]:
            print(f"      {match[:150]}")

# 4. Procurar funções de encoding/crypto
print("\n📌 Procurando funções de encoding/crypto...")
crypto_keywords = ['btoa', 'atob', 'encrypt', 'decrypt', 'encode', 'decode', 'hash', 'md5', 'sha']
for keyword in crypto_keywords:
    # Procurar definições de função
    pattern = rf'function\s+\w*{keyword}\w*\s*\([^)]*\)\s*{{[^}}]{{0,300}}}}'
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ {keyword}: {len(matches)} função(ões)")
        for match in matches[:1]:
            print(f"      {match[:200]}")

# 5. Procurar padrão específico: t= ou token=
print("\n📌 Procurando padrões de query string com token...")
query_patterns = [
    r'[?&]t=\$\{[^}]+\}',
    r'[?&]token=\$\{[^}]+\}',
    r'[?&]t=["\']?\+[^&\s]+',
]

for pattern in query_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} padrão(ões):")
        for match in matches[:5]:
            print(f"      {match}")

# 6. Procurar por Base64 do hash
print("\n📌 Procurando conversão Base64 do hash...")
b64_patterns = [
    r'btoa\([^)]*hash[^)]{0,100}\)',
    r'btoa\([^)]*location[^)]{0,100}\)',
    r'Buffer\.from\([^)]*hash[^)]{0,100}\)',
]

for pattern in b64_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} conversão(ões):")
        for match in matches[:3]:
            print(f"      {match}")

# 7. Extrair trecho específico com "player" e "hash"
print("\n📌 Procurando trechos que mencionam 'player' E 'hash' juntos...")
combined_pattern = r'.{0,200}(?:player|api/v1/player).{0,100}(?:hash|location\.hash).{0,200}'
matches = re.findall(combined_pattern, js_content, re.IGNORECASE)
if matches:
    print(f"   ✅ Encontrado {len(matches)} trecho(s):")
    for match in matches[:3]:
        # Limpar e mostrar
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      {clean[:200]}")

# 8. Procurar inicialização/setup
print("\n📌 Procurando código de inicialização...")
init_patterns = [
    r'(?:init|setup|start|load)\w*\s*[=:]\s*(?:function|\([^)]*\)\s*=>)\s*{[^}]{0,500}}',
    r'useEffect\([^)]{0,300}\)',
]

for pattern in init_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} função(ões) de init")
        # Não mostrar conteúdo (muito grande)

print("\n" + "=" * 80)
print("💡 DICA: Procure por padrões como:")
print("   - btoa(location.hash.slice(1))")
print("   - Base64.encode(hash)")
print("   - hash.replace('#', '')")
print("=" * 80)
