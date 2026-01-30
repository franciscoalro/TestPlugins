#!/usr/bin/env python3
import re

with open('iamcdn_player.js', 'r', encoding='utf-8') as f:
    script = f.read()

# Encontrar a funcao SoTrym completa
print('=== EXTRAINSoTRYM ===')
idx = script.find('window[\'SoTrym\']')
if idx > 0:
    # Pegar contexto maior
    context = script[max(0,idx-2000):idx+2000]
    print(f'Contexto:\n{context}')

# Procurar por _0x23a5f1
print('\n=== PROCURANDO _0x23a5f1 ===')
idx2 = script.find('_0x23a5f1')
if idx2 > 0:
    context2 = script[max(0,idx2-500):idx2+1500]
    print(f'Contexto _0x23a5f1:\n{context2}')

# Procurar funcoes que parecem decriptar
print('\n=== FUNCOES SUSPEITAS ===')
# Padroes de funcoes ofuscadas
funcs = re.findall(r'function\s+(_0x[a-f0-9]+)\s*\([^)]*\)\s*\{[^}]{100,500}\}', script)
print(f'Funcoes ofuscadas encontradas: {len(funcs)}')

# Procurar por palavras como "media" ou "file" no script
print('\n=== REFERENCIAS A MEDIA ===')
if '"media"' in script:
    print('Encontrado "media"')
if "'media'" in script:
    print("Encontrado 'media'")

# Procurar por substituicoes de string
print('\n=== SUBSTITUICOES ===')
replacements = re.findall(r'replace\s*\(', script)
print(f'Chamadas replace: {len(replacements)}')
