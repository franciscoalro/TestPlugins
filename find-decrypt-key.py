#!/usr/bin/env python3
"""
Procurar a chave de descriptografia no JavaScript do MegaEmbed
"""

import re
import json

with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔑 PROCURANDO CHAVE DE DESCRIPTOGRAFIA")
print("=" * 80)

# 1. Procurar imports de crypto
print("\n📌 Procurando imports de bibliotecas crypto...")
crypto_imports = [
    r'import.*crypto.*from',
    r'require\(["\']crypto["\']',
    r'import.*aes.*from',
    r'require\(["\']crypto-js["\']',
    r'from\s+["\']crypto-js["\']',
]

for pattern in crypto_imports:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado: {matches[:3]}")

# 2. Procurar funções decrypt
print("\n📌 Procurando funções de decrypt...")
decrypt_patterns = [
    r'function\s+(\w*decrypt\w*)\s*\([^)]*\)\s*{([^}]{0,800})}',
    r'const\s+(\w*decrypt\w*)\s*=\s*\([^)]*\)\s*=>\s*{([^}]{0,800})}',
    r'(\w+)\.decrypt\s*\(',
]

decrypt_functions = []
for pattern in decrypt_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} função(ões)")
        for match in matches[:5]:
            if isinstance(match, tuple) and len(match) >= 2:
                func_name, func_body = match[0], match[1]
                print(f"\n      Função: {func_name}")
                print(f"      Corpo: {func_body[:400]}")
                decrypt_functions.append((func_name, func_body))
            else:
                print(f"      Uso: {match}")

# 3. Procurar strings que parecem chaves (32 ou 64 chars hex)
print("\n📌 Procurando strings que parecem chaves...")
key_patterns = [
    r'["\']([a-f0-9]{32})["\']',  # MD5/128-bit
    r'["\']([a-f0-9]{64})["\']',  # SHA256/256-bit
    r'key\s*[:=]\s*["\']([^"\']{16,64})["\']',
    r'secret\s*[:=]\s*["\']([^"\']{16,64})["\']',
]

potential_keys = set()
for pattern in key_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        for key in matches[:10]:
            if len(key) >= 16:  # Chaves devem ter pelo menos 16 chars
                potential_keys.add(key)
                print(f"   🔑 Possível chave: {key[:50]}...")

# 4. Procurar AES especificamente
print("\n📌 Procurando uso de AES...")
aes_patterns = [
    r'AES\.decrypt\([^)]{0,200}\)',
    r'AES\.encrypt\([^)]{0,200}\)',
    r'CryptoJS\.AES\.[^(]+\([^)]{0,200}\)',
    r'aes[^(]*\([^)]{0,200}\)',
]

for pattern in aes_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} uso(s) de AES:")
        for match in matches[:5]:
            print(f"      {match[:150]}")

# 5. Procurar processamento da resposta da API
print("\n📌 Procurando processamento da resposta da API player...")
response_patterns = [
    r'\/api\/v1\/player[^;]{0,500}\.then\([^}]{0,500}\)',
    r'fetch\([^)]*player[^)]*\)[^;]{0,500}',
    r'response\s*=>\s*{[^}]{0,500}decrypt[^}]{0,500}}',
]

for pattern in response_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} processamento(s):")
        for match in matches[:3]:
            clean = re.sub(r'\s+', ' ', match).strip()
            print(f"      {clean[:300]}")

# 6. Procurar por "player" e "decrypt" próximos
print("\n📌 Procurando 'player' e 'decrypt' próximos...")
combined = r'.{0,300}player.{0,100}decrypt.{0,300}'
matches = re.findall(combined, js_content, re.IGNORECASE)
if matches:
    print(f"   ✅ Encontrado {len(matches)} trecho(s):")
    for match in matches[:3]:
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      {clean[:400]}")

# 7. Procurar hexToBytes ou similar
print("\n📌 Procurando conversões hex...")
hex_patterns = [
    r'function\s+(\w*hex\w*)\s*\([^)]*\)\s*{([^}]{0,300})}',
    r'const\s+(\w*hex\w*)\s*=\s*\([^)]*\)\s*=>\s*{([^}]{0,300})}',
    r'\.unhexlify\(',
    r'Buffer\.from\([^)]*,\s*["\']hex["\']',
]

for pattern in hex_patterns:
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ Encontrado {len(matches)} conversão(ões):")
        for match in matches[:3]:
            if isinstance(match, tuple):
                print(f"      Função: {match[0]}")
            else:
                print(f"      {match[:100]}")

# 8. Procurar por palavras-chave relacionadas
print("\n📌 Procurando palavras-chave relacionadas...")
keywords = ['cipher', 'decipher', 'iv', 'salt', 'pbkdf', 'hmac']
for keyword in keywords:
    pattern = rf'\b{keyword}\b[^;]{{0,200}}'
    matches = re.findall(pattern, js_content, re.IGNORECASE)
    if matches:
        print(f"   ✅ '{keyword}': {len(matches)} ocorrência(s)")
        for match in matches[:2]:
            clean = re.sub(r'\s+', ' ', match).strip()
            print(f"      {clean[:150]}")

print("\n" + "=" * 80)
print("💡 PRÓXIMOS PASSOS:")
print("   1. Analisar as funções decrypt encontradas")
print("   2. Testar as chaves potenciais")
print("   3. Verificar se usa AES-CBC, AES-GCM, ou outro modo")
print("   4. Procurar o IV (Initialization Vector)")
print("=" * 80)
