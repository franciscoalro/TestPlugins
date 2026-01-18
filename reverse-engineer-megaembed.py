#!/usr/bin/env python3
"""
Reverse Engineering do MegaEmbed usando análise do JavaScript
Vamos procurar padrões específicos que revelam a chave e o algoritmo
"""

import re
import json

with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔬 REVERSE ENGINEERING DO MEGAEMBED")
print("=" * 80)

# 1. Procurar por arrays de números que possam ser chaves
print("\n📌 Procurando arrays de números (possíveis chaves)...")
array_patterns = [
    r'\[(\d+(?:,\s*\d+){15,31})\]',  # Array de 16-32 números
]

for pattern in array_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} array(s) de números:")
        for match in matches[:10]:
            numbers = [int(x.strip()) for x in match.split(',')]
            if len(numbers) in [16, 24, 32]:  # Tamanhos de chave AES
                hex_str = ''.join(f'{n:02x}' for n in numbers)
                print(f"      [{len(numbers)} bytes] {hex_str}")

# 2. Procurar por Uint8Array com valores hardcoded
print("\n📌 Procurando Uint8Array hardcoded...")
uint8_patterns = [
    r'new Uint8Array\(\[([0-9,\s]+)\]\)',
    r'Uint8Array\.from\(\[([0-9,\s]+)\]\)',
]

for pattern in uint8_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} Uint8Array(s):")
        for match in matches[:10]:
            numbers = [int(x.strip()) for x in match.split(',') if x.strip()]
            if 8 <= len(numbers) <= 32:
                hex_str = ''.join(f'{n:02x}' for n in numbers)
                print(f"      [{len(numbers)} bytes] {hex_str}")

# 3. Procurar por strings que são convertidas para bytes
print("\n📌 Procurando conversões de string para bytes...")
string_to_bytes_patterns = [
    r'(?:atob|btoa|Buffer\.from|TextEncoder)\(["\']([^"\']{8,64})["\']',
    r'["\']([a-zA-Z0-9+/=]{16,64})["\']\.split\(["\']["\']',
]

for pattern in string_to_bytes_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        unique = list(set(matches))[:10]
        print(f"   ✅ Encontrado {len(unique)} string(s):")
        for match in unique:
            if len(match) >= 8:
                print(f"      {match}")

# 4. Procurar por operações XOR (comum em ofuscação)
print("\n📌 Procurando operações XOR...")
xor_pattern = r'(\w+)\s*\^\s*(\w+)'
matches = re.findall(xor_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} operação(ões) XOR")
    # Procurar contexto de XOR com números
    xor_with_numbers = re.findall(r'(\w+)\s*\^\s*(\d+)', js_content)
    if xor_with_numbers:
        print(f"   ✅ XOR com números: {len(xor_with_numbers)} ocorrência(s)")
        for var, num in xor_with_numbers[:10]:
            print(f"      {var} ^ {num}")

# 5. Procurar por charCodeAt (conversão de string para bytes)
print("\n📌 Procurando charCodeAt...")
charcode_pattern = r'["\']([^"\']{8,32})["\'].*?charCodeAt'
matches = re.findall(charcode_pattern, js_content)
if matches:
    unique = list(set(matches))[:10]
    print(f"   ✅ Encontrado {len(unique)} string(s) com charCodeAt:")
    for match in unique:
        print(f"      {match}")
        # Converter para hex
        hex_str = ''.join(f'{ord(c):02x}' for c in match)
        print(f"         Hex: {hex_str}")

# 6. Procurar por funções que retornam arrays de bytes
print("\n📌 Procurando funções que retornam arrays...")
function_return_array = r'function\s+(\w+)\s*\([^)]*\)\s*{[^}]*return\s*\[([0-9,\s]+)\]'
matches = re.findall(function_return_array, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} função(ões):")
    for func_name, array_content in matches[:5]:
        numbers = [int(x.strip()) for x in array_content.split(',') if x.strip()]
        if 8 <= len(numbers) <= 32:
            hex_str = ''.join(f'{n:02x}' for n in numbers)
            print(f"      {func_name}() retorna [{len(numbers)} bytes]: {hex_str}")

# 7. Procurar por "magic numbers" comuns em criptografia
print("\n📌 Procurando magic numbers de criptografia...")
magic_numbers = {
    '0x67452301': 'MD5/SHA1 constant',
    '0x9e3779b9': 'TEA/XTEA constant',
    '0x61c88647': 'XXTEA constant',
    '0x5a827999': 'SHA1 constant',
    '0x6ed9eba1': 'SHA1 constant',
}

for magic, description in magic_numbers.items():
    if magic in js_content:
        print(f"   ✅ Encontrado {magic} ({description})")

# 8. Procurar por strings específicas relacionadas ao player
print("\n📌 Procurando strings relacionadas ao player...")
player_strings = [
    r'player["\']?\s*[:=]\s*["\']([^"\']{8,64})["\']',
    r'key["\']?\s*[:=]\s*["\']([^"\']{8,64})["\']',
    r'secret["\']?\s*[:=]\s*["\']([^"\']{8,64})["\']',
]

for pattern in player_strings:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        unique = list(set(matches))[:5]
        print(f"   ✅ Encontrado {len(unique)} string(s):")
        for match in unique:
            print(f"      {match}")

# 9. Procurar por fromCharCode (construção de strings)
print("\n📌 Procurando String.fromCharCode...")
fromcharcode_pattern = r'String\.fromCharCode\(([^)]+)\)'
matches = re.findall(fromcharcode_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} uso(s) de fromCharCode:")
    for match in matches[:10]:
        # Tentar avaliar se são números simples
        if re.match(r'^[\d,\s]+$', match):
            numbers = [int(x.strip()) for x in match.split(',') if x.strip()]
            if len(numbers) <= 32:
                try:
                    text = ''.join(chr(n) for n in numbers)
                    print(f"      {match[:50]}... → '{text}'")
                except:
                    pass

# 10. Procurar por padrões de derivação de chave do video ID
print("\n📌 Procurando derivação de chave do video ID...")
derivation_patterns = [
    r'location\.hash[^;]{0,500}',
    r'hash\.(?:slice|substring|substr)\([^)]+\)[^;]{0,200}',
]

for pattern in derivation_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} padrão(ões):")
        for match in matches[:3]:
            clean = re.sub(r'\s+', ' ', match).strip()
            print(f"      {clean[:300]}")

print("\n" + "=" * 80)
print("💡 PRÓXIMO PASSO:")
print("   Vamos procurar especificamente por:")
print("   1. Arrays de 16 bytes (128-bit key)")
print("   2. Arrays de 32 bytes (256-bit key)")
print("   3. Funções que processam location.hash")
print("=" * 80)
