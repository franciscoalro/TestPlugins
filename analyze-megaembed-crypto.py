#!/usr/bin/env python3
"""
Analisa o JavaScript do MegaEmbed para encontrar a lógica de descriptografia
"""

import requests
import re

JS_URL = "https://megaembed.link/assets/index-CQ0L9dOW.js"

print(f"[*] Baixando: {JS_URL}")
resp = requests.get(JS_URL)
js_code = resp.text

print(f"[*] Tamanho: {len(js_code)} bytes")

# Procurar padrões de criptografia
patterns = [
    (r'AES|aes', 'AES'),
    (r'decrypt|Decrypt', 'decrypt'),
    (r'CryptoJS|crypto-js', 'CryptoJS'),
    (r'atob|btoa', 'base64'),
    (r'\.key|key\s*=|key:', 'key'),
    (r'iv\s*=|\.iv', 'IV'),
    (r'CBC|cbc', 'CBC mode'),
    (r'hex|Hex', 'hex'),
    (r'location\.hostname|window\.location', 'hostname'),
    (r'/api/v1/info', 'API endpoint'),
]

print("\n[*] Padrões encontrados:")
for pattern, name in patterns:
    matches = re.findall(pattern, js_code, re.IGNORECASE)
    if matches:
        print(f"  [{name}]: {len(matches)} ocorrências")

# Extrair funções relacionadas a crypto
print("\n[*] Procurando funções de crypto...")

# Procurar contexto ao redor de decrypt/AES
decrypt_contexts = []
for match in re.finditer(r'.{100}(decrypt|AES|crypto).{100}', js_code, re.IGNORECASE):
    decrypt_contexts.append(match.group(0))

if decrypt_contexts:
    print(f"\n[*] Contextos de crypto ({len(decrypt_contexts)}):")
    for i, ctx in enumerate(decrypt_contexts[:5]):
        print(f"\n--- Contexto {i+1} ---")
        print(ctx)

# Procurar uso de hostname
hostname_contexts = []
for match in re.finditer(r'.{50}(location\.hostname|hostname).{50}', js_code, re.IGNORECASE):
    hostname_contexts.append(match.group(0))

if hostname_contexts:
    print(f"\n[*] Contextos de hostname ({len(hostname_contexts)}):")
    for i, ctx in enumerate(hostname_contexts[:3]):
        print(f"\n--- Hostname {i+1} ---")
        print(ctx)

# Procurar a função que chama a API
api_contexts = []
for match in re.finditer(r'.{100}/api/v1/info.{100}', js_code):
    api_contexts.append(match.group(0))

if api_contexts:
    print(f"\n[*] Contextos da API ({len(api_contexts)}):")
    for ctx in api_contexts[:2]:
        print(f"\n{ctx}")

# Salvar JS para análise manual
with open("megaembed_index_full.js", "w", encoding="utf-8") as f:
    f.write(js_code)
print(f"\n[*] JS salvo em megaembed_index_full.js para análise manual")
