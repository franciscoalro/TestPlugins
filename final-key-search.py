#!/usr/bin/env python3
"""
Última tentativa: procurar especificamente por:
1. Funções que geram chaves a partir de strings
2. Constantes usadas em crypto
3. Padrões de WebCrypto API
"""

import re

with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔎 BUSCA FINAL PELA CHAVE")
print("=" * 80)

# 1. Procurar por TextEncoder (conversão de string para bytes)
print("\n📌 Procurando TextEncoder (conversão string → bytes)...")
textencoder_pattern = r'new TextEncoder\(\)\.encode\(["\']([^"\']+)["\']\)'
matches = re.findall(textencoder_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} uso(s):")
    for match in list(set(matches))[:10]:
        print(f"      '{match}' → {match.encode().hex()}")

# 2. Procurar por strings próximas a "importKey"
print("\n📌 Procurando contexto de importKey...")
importkey_contexts = re.findall(r'.{0,200}importKey.{0,200}', js_content)
for ctx in importkey_contexts[:3]:
    clean = re.sub(r'\s+', ' ', ctx).strip()
    print(f"   {clean[:300]}")

# 3. Procurar por "this.key" (chave armazenada em objeto)
print("\n📌 Procurando 'this.key'...")
thiskey_pattern = r'this\.key\s*=\s*([^;]+)'
matches = re.findall(thiskey_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} atribuição(ões):")
    for match in matches[:10]:
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      this.key = {clean[:100]}")

# 4. Procurar por funções que retornam Uint8Array
print("\n📌 Procurando funções que retornam Uint8Array...")
uint8_return_pattern = r'function\s+(\w+)\([^)]*\)\s*{[^}]{0,200}return\s+new Uint8Array\([^)]+\)'
matches = re.findall(uint8_return_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} função(ões):")
    for func_name in matches[:10]:
        print(f"      {func_name}()")

# 5. Procurar por "expandKey" (comum em AES)
print("\n📌 Procurando 'expandKey'...")
expandkey_pattern = r'expandKey\([^)]*\)\s*{([^}]{0,500})}'
matches = re.findall(expandkey_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} implementação(ões):")
    for match in matches[:2]:
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      {clean[:300]}")

# 6. Procurar por strings que são usadas como chave
print("\n📌 Procurando padrão: variável = string; ... importKey(variável)...")
# Procurar variáveis que são strings e depois usadas em importKey
var_string_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*["\']([^"\']{16,32})["\']'
matches = re.findall(var_string_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} variável(is) com strings:")
    for var_name, string_value in matches[:20]:
        # Verificar se essa variável é usada em importKey
        if re.search(rf'importKey.*{var_name}', js_content):
            print(f"      ✅ {var_name} = '{string_value}' (USADA EM importKey!)")
            print(f"         Hex: {string_value.encode().hex()}")
        elif len(string_value) in [16, 24, 32]:
            print(f"      {var_name} = '{string_value}'")

# 7. Procurar por Buffer.from
print("\n📌 Procurando Buffer.from...")
buffer_from_pattern = r'Buffer\.from\(["\']([^"\']{8,64})["\']\s*,\s*["\']([^"\']+)["\']\)'
matches = re.findall(buffer_from_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} uso(s):")
    for data, encoding in matches[:10]:
        print(f"      Buffer.from('{data[:50]}...', '{encoding}')")

# 8. Procurar por strings base64 específicas
print("\n📌 Procurando strings base64 de 16/24/32 bytes...")
# Base64 de 16 bytes = 24 chars (com padding)
# Base64 de 32 bytes = 44 chars (com padding)
b64_pattern = r'["\']([A-Za-z0-9+/]{22}==|[A-Za-z0-9+/]{24}|[A-Za-z0-9+/]{42}==|[A-Za-z0-9+/]{44})["\']'
matches = re.findall(b64_pattern, js_content)
if matches:
    unique = list(set(matches))[:10]
    print(f"   ✅ Encontrado {len(unique)} string(s) base64:")
    for match in unique:
        print(f"      {match}")
        try:
            import base64
            decoded = base64.b64decode(match)
            print(f"         Decoded ({len(decoded)} bytes): {decoded.hex()}")
        except:
            pass

# 9. Procurar por "crypto.getRandomValues" (geração de chave aleatória)
print("\n📌 Procurando crypto.getRandomValues...")
if 'crypto.getRandomValues' in js_content or 'getRandomValues' in js_content:
    print("   ✅ Encontrado! A chave pode ser gerada aleatoriamente")
    getrandom_pattern = r'crypto\.getRandomValues\(([^)]+)\)'
    matches = re.findall(getrandom_pattern, js_content)
    if matches:
        for match in matches[:5]:
            print(f"      crypto.getRandomValues({match})")
else:
    print("   ❌ Não encontrado (chave provavelmente é hardcoded)")

# 10. Procurar por "pbkdf2" ou "deriveKey"
print("\n📌 Procurando derivação de chave (PBKDF2, deriveKey)...")
derivation_keywords = ['pbkdf2', 'deriveKey', 'deriveBits']
for keyword in derivation_keywords:
    if keyword in js_content:
        print(f"   ✅ Encontrado '{keyword}'!")
        pattern = rf'{keyword}\([^)]+\)'
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for match in matches[:3]:
            print(f"      {match}")

print("\n" + "=" * 80)
print("💡 RECOMENDAÇÃO FINAL:")
print("   Não conseguimos encontrar a chave hardcoded no JavaScript")
print("   A chave pode ser:")
print("   1. Gerada dinamicamente no runtime")
print("   2. Carregada de outro arquivo JS")
print("   3. Derivada de forma complexa")
print("\n   ✅ SOLUÇÃO: Use o script DevTools (capture-megaembed-key-devtools.js)")
print("      Ele vai interceptar a chave REAL quando o player carregar")
print("=" * 80)
