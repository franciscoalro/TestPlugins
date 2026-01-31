#!/usr/bin/env python3
import re

with open('iamcdn_player.js', 'r', encoding='utf-8') as f:
    script = f.read()

print(f'Tamanho do script: {len(script)} chars')

# Procurar por SoTrym
print('\n=== PROCURANDO SoTrym ===')
if 'SoTrym' in script:
    print('[OK] SoTrym encontrado')
    # Encontrar contexto
    idx = script.find('SoTrym')
    print(f'Contexto (primeira ocorrencia):')
    print(script[max(0,idx-100):idx+500])

# Procurar por funcoes de decriptacao
print('\n=== FUNCOES DE DECRIPTACAO ===')
crypto_funcs = re.findall(r'function\s+[a-zA-Z0-9_$]*[Dd]ecrypt[a-zA-Z0-9_$]*\s*\(', script)
print(f'Funcoes decrypt: {crypto_funcs}')

# Procurar por CryptoJS
cryptojs = re.findall(r'CryptoJS', script)
print(f'Referencias CryptoJS: {len(cryptojs)}')

# Procurar por AES
aes = re.findall(r'AES', script)
print(f'Referencias AES: {len(aes)}')

# Procurar por chave
print('\n=== POSSIVEIS CHAVES ===')
keys = re.findall(r'["\']([a-zA-Z0-9]{16,32})["\']', script)
print(f'Strings de 16-32 chars: {len(keys)}')
for k in keys[:10]:
    print(f'  {k}')

# Procurar por JSON.parse
json_parses = re.findall(r'JSON\.parse\s*\(', script)
print(f'\nJSON.parse calls: {len(json_parses)}')

# Procurar por atob
atobs = re.findall(r'atob\s*\(', script)
print(f'atob calls: {len(atobs)}')
