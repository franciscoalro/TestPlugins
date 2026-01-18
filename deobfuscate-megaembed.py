#!/usr/bin/env python3
"""
Desobfuscar código do MegaEmbed
"""

import re

with open('megaembed_index.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

print("🔓 DESOBFUSCANDO MEGAEMBED")
print("=" * 80)

# 1. Procurar definição da função g()
print("\n📌 Procurando função g()...")
g_patterns = [
    r'function\s+g\s*\([^)]*\)\s*{([^}]{0,500})}',
    r'const\s+g\s*=\s*\([^)]*\)\s*=>\s*{([^}]{0,500})}',
    r'var\s+g\s*=\s*function\s*\([^)]*\)\s*{([^}]{0,500})}',
]

for pattern in g_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        print(f"   ✅ Encontrado! Definição:")
        for match in matches[:1]:
            print(f"      {match[:300]}")

# 2. Procurar array de strings (comum em ofuscação)
print("\n📌 Procurando arrays de strings ofuscadas...")
array_patterns = [
    r'const\s+(\w+)\s*=\s*\[([^\]]{100,1000})\]',
    r'var\s+(\w+)\s*=\s*\[([^\]]{100,1000})\]',
]

string_arrays = []
for pattern in array_patterns:
    matches = re.findall(pattern, js_content)
    if matches:
        for var_name, array_content in matches[:5]:
            # Contar strings
            strings = re.findall(r'"([^"]*)"', array_content)
            if len(strings) > 10:  # Array grande de strings
                print(f"   ✅ Array '{var_name}' com {len(strings)} strings")
                string_arrays.append((var_name, strings))
                # Mostrar algumas strings relevantes
                relevant = [s for s in strings if any(k in s.lower() for k in ['split', 'slice', 'hash', 'replace', 'api', 'player'])]
                if relevant:
                    print(f"      Strings relevantes: {relevant[:10]}")

# 3. Procurar o contexto completo de location.hash
print("\n📌 Procurando contexto completo de location.hash...")
context_pattern = r'.{0,300}location\.hash.{0,300}'
matches = re.findall(context_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} contexto(s):")
    for i, match in enumerate(matches[:3]):
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"\n   [{i+1}] {clean[:400]}")

# 4. Procurar padrão específico: t= seguido de algo
print("\n📌 Procurando construção do parâmetro t=...")
t_param_pattern = r'["\']\/api\/v1\/player\?t=["\'][^;]{0,200}'
matches = re.findall(t_param_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} construção(ões):")
    for match in matches[:3]:
        print(f"      {match}")

# 5. Procurar concatenação com +
print("\n📌 Procurando concatenações com +...")
concat_pattern = r'["\']\/api\/v1\/player\?t=["\'][^;]*\+[^;]{0,200}'
matches = re.findall(concat_pattern, js_content)
if matches:
    print(f"   ✅ Encontrado {len(matches)} concatenação(ões):")
    for match in matches[:3]:
        clean = re.sub(r'\s+', ' ', match).strip()
        print(f"      {clean}")

# 6. Tentar encontrar o valor de g(600) e g(800)
print("\n📌 Tentando descobrir g(600) e g(800)...")
if string_arrays:
    var_name, strings = string_arrays[0]
    print(f"   Usando array '{var_name}' com {len(strings)} strings")
    
    # g() provavelmente é um accessor do array
    # Tentar índices comuns
    test_indices = [600, 800, 0, 1, 2, 3, 4, 5]
    for idx in test_indices:
        if idx < len(strings):
            value = strings[idx]
            if value and len(value) < 50:  # Strings curtas são mais relevantes
                print(f"   strings[{idx}] = '{value}'")

# 7. Procurar por "split" especificamente
print("\n📌 Procurando uso de 'split'...")
split_pattern = r'\.split\([^)]+\)'
matches = re.findall(split_pattern, js_content)
if matches:
    unique_splits = list(set(matches))[:10]
    print(f"   ✅ Encontrado {len(matches)} uso(s) de split:")
    for split in unique_splits:
        print(f"      {split}")

print("\n" + "=" * 80)
print("💡 HIPÓTESE:")
print("   O token provavelmente é: location.hash.split('#')[1]")
print("   Ou seja: apenas o ID sem o #")
print("   Exemplo: #xez5rx → token = xez5rx")
print("=" * 80)
