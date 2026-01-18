#!/usr/bin/env python3
"""
Extrair a chave de criptografia real do JavaScript do MegaEmbed
Procurar por strings hardcoded que possam ser a chave
"""

import re

with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔑 PROCURANDO CHAVE HARDCODED NO JAVASCRIPT")
print("=" * 80)

# 1. Procurar por strings de 16, 24 ou 32 caracteres (tamanhos de chave AES)
print("\n📌 Procurando strings de tamanho de chave AES...")
key_sizes = [16, 24, 32]  # AES-128, AES-192, AES-256
for size in key_sizes:
    # Procurar strings ASCII
    pattern = rf'["\']([a-zA-Z0-9]{{' + str(size) + r'}})["\']'
    matches = re.findall(pattern, js_content)
    if matches:
        unique = list(set(matches))[:20]
        print(f"\n   Strings de {size} caracteres ({size*8}-bit):")
        for match in unique:
            print(f"      {match}")

# 2. Procurar por "key" seguido de string
print("\n📌 Procurando 'key' seguido de string...")
key_patterns = [
    r'key\s*[:=]\s*["\']([^"\']{8,64})["\']',
    r'["\']key["\']:\s*["\']([^"\']{8,64})["\']',
    r'const\s+\w*[Kk]ey\w*\s*=\s*["\']([^"\']{8,64})["\']',
]

for pattern in key_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} chave(s):")
        for match in list(set(matches))[:10]:
            print(f"      {match}")

# 3. Procurar por funções que geram chaves
print("\n📌 Procurando funções de geração de chave...")
keygen_patterns = [
    r'function\s+(\w*[Kk]ey\w*)\s*\([^)]*\)\s*{([^}]{0,500})}',
    r'const\s+(\w*[Kk]ey\w*)\s*=\s*\([^)]*\)\s*=>\s*{([^}]{0,500})}',
]

for pattern in keygen_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} função(ões):")
        for func_name, func_body in matches[:5]:
            print(f"\n      Função: {func_name}")
            print(f"      Corpo: {func_body[:300]}")

# 4. Procurar por derivação de chave (PBKDF2, etc)
print("\n📌 Procurando derivação de chave...")
derivation_keywords = ['pbkdf2', 'derive', 'hash', 'sha256', 'md5']
for keyword in derivation_keywords:
    pattern = rf'{keyword}[^;]{{0,200}}'
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ '{keyword}': {len(matches)} ocorrência(s)")
        for match in matches[:3]:
            clean = re.sub(r'\s+', ' ', match).strip()
            print(f"      {clean[:150]}")

# 5. Procurar por uso do video ID na geração da chave
print("\n📌 Procurando uso do video ID...")
id_patterns = [
    r'location\.hash[^;]{0,300}',
    r'videoId[^;]{0,200}',
    r'id\s*[:=][^;]{0,200}',
]

for pattern in id_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} uso(s):")
        for match in matches[:5]:
            clean = re.sub(r'\s+', ' ', match).strip()
            print(f"      {clean[:200]}")

# 6. Procurar por strings base64 que possam ser chaves
print("\n📌 Procurando strings Base64...")
b64_pattern = r'["\']([A-Za-z0-9+/]{16,}={0,2})["\']'
matches = re.findall(b64_pattern, js_content)
if matches:
    # Filtrar apenas strings que parecem ser chaves (múltiplo de 4, tamanho razoável)
    potential_keys = [m for m in matches if len(m) % 4 == 0 and 16 <= len(m) <= 64]
    if potential_keys:
        print(f"   ✅ Encontrado {len(potential_keys)} string(s) Base64 potenciais:")
        for key in list(set(potential_keys))[:10]:
            print(f"      {key}")

# 7. Procurar por "3wnuij" (o video ID do exemplo)
print("\n📌 Procurando referências ao video ID '3wnuij'...")
if '3wnuij' in js_content:
    print("   ✅ Video ID encontrado no código!")
    # Extrair contexto
    idx = js_content.find('3wnuij')
    context = js_content[max(0, idx-200):min(len(js_content), idx+200)]
    print(f"   Contexto: {context}")
else:
    print("   ❌ Video ID não encontrado (esperado, é dinâmico)")

# 8. Procurar por crypto.subtle.importKey
print("\n📌 Procurando importKey...")
importkey_pattern = r'importKey\([^)]{0,500}\)'
matches = re.findall(importkey_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} uso(s) de importKey:")
    for match in matches[:3]:
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      {clean[:300]}")

print("\n" + "=" * 80)
print("💡 ANÁLISE:")
print("   A chave provavelmente é:")
print("   1. Derivada do video ID (location.hash)")
print("   2. Hardcoded em uma string de 16/32 caracteres")
print("   3. Gerada por uma função específica")
print("=" * 80)
