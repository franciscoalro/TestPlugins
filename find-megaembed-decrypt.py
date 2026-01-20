#!/usr/bin/env python3
"""
Procura especificamente pela lógica de descriptografia da resposta da API
"""

import re

# Ler o arquivo JavaScript principal
with open("megaembed_index-CZ_ja_1t.js", "r", encoding="utf-8") as f:
    js_code = f.read()

print("=" * 60)
print("🔍 PROCURANDO LÓGICA DE DESCRIPTOGRAFIA")
print("=" * 60)
print()

# Procurar por /api/v1/info
api_pattern = r'/api/v1/info[^}]{0,2000}'
api_matches = re.findall(api_pattern, js_code, re.DOTALL)

if api_matches:
    print(f"✅ Encontradas {len(api_matches)} referências à API")
    for i, match in enumerate(api_matches[:3], 1):
        print(f"\n[{i}] Contexto da API:")
        print(match[:500])
        print("...")

# Procurar por funções que processam a resposta
response_patterns = [
    r'\.then\s*\(\s*(?:response|res|data)\s*=>\s*\{([^}]{0,1000})\}',
    r'async\s+function\s+\w+\s*\([^)]*\)\s*\{[^}]*api/v1/info[^}]{0,1000}\}',
    r'fetch\s*\([^)]*api/v1/info[^)]*\)\.then[^}]{0,1000}'
]

print("\n" + "=" * 60)
print("📡 PROCESSAMENTO DE RESPOSTA DA API")
print("=" * 60)

for pattern in response_patterns:
    matches = re.findall(pattern, js_code, re.DOTALL | re.IGNORECASE)
    if matches:
        print(f"\n✅ Padrão encontrado: {pattern[:50]}...")
        for i, match in enumerate(matches[:2], 1):
            print(f"\n[{i}]")
            print(match[:800])

# Procurar por hex decode ou similar
hex_patterns = [
    r'function\s+\w*[Dd]ecode\w*\s*\([^)]*\)\s*\{([^}]{0,500})\}',
    r'const\s+\w*[Dd]ecode\w*\s*=\s*\([^)]*\)\s*=>\s*\{([^}]{0,500})\}',
    r'\.match\s*\(/[a-f0-9]+/gi\)',
    r'parseInt\s*\([^,]+,\s*16\)',
    r'fromCharCode'
]

print("\n" + "=" * 60)
print("🔐 FUNÇÕES DE DECODE/DECRYPT")
print("=" * 60)

for pattern in hex_patterns:
    matches = re.findall(pattern, js_code, re.IGNORECASE)
    if matches:
        print(f"\n✅ Padrão: {pattern[:50]}...")
        for i, match in enumerate(matches[:3], 1):
            if isinstance(match, tuple):
                match = match[0] if match else ""
            print(f"\n[{i}] {match[:300]}")

# Procurar pelas chaves encontradas anteriormente
keys = [
    "e2719d58a985b3c9781ab030af78d30e",
    "edef8ba979d64acea3c827dcd51d21ed",
    "9a04f07998404286ab92e65be0885f95",
    "1077efecc0b24d02ace33c1e52e2fb4b"
]

print("\n" + "=" * 60)
print("🔑 CONTEXTO DAS CHAVES ENCONTRADAS")
print("=" * 60)

for key in keys:
    # Procurar contexto ao redor da chave (500 chars antes e depois)
    pattern = f'.{{0,500}}{key}.{{0,500}}'
    matches = re.findall(pattern, js_code, re.DOTALL)
    if matches:
        print(f"\n✅ Chave: {key}")
        for i, match in enumerate(matches[:1], 1):
            print(f"\nContexto:")
            print(match[:1000])

print("\n" + "=" * 60)
print("💡 DICA: Procure por:")
print("=" * 60)
print("  - Funções que recebem string hex e retornam texto")
print("  - Uso de CryptoJS, crypto-js, ou Web Crypto API")
print("  - Conversão de hex para bytes: parseInt(x, 16)")
print("  - XOR operations: ^")
print("  - String.fromCharCode aplicado em array")
print()
