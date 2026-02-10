#!/usr/bin/env python3

"""
Procura a fórmula de derivação da chave AES
"""

import re
import sys

def find_key_formula(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("=" * 60)
    print("🔍 ANÁLISE DE FÓRMULA DA CHAVE AES")
    print("=" * 60)
    print()
    
    # 1. Procurar por importKey e contexto
    print("📌 PADRÃO 1: Contexto de importKey")
    print("-" * 60)
    
    importkey_matches = list(re.finditer(r'.{0,500}importKey.{0,500}', content, re.DOTALL))
    for i, match in enumerate(importkey_matches[:3], 1):
        print(f"\n🔸 Ocorrência {i}:")
        snippet = match.group(0)
        # Limpar e formatar
        snippet = re.sub(r'\s+', ' ', snippet)
        print(snippet[:800])
    
    print("\n" + "=" * 60)
    print("📌 PADRÃO 2: Concatenação de parâmetros")
    print("-" * 60)
    
    # 2. Procurar concatenações com user_id, slug, md5_id
    concat_patterns = [
        r'(user_id|slug|md5_id)\s*\+\s*(user_id|slug|md5_id)',
        r'concat\([^)]*(?:user_id|slug|md5_id)[^)]*\)',
        r'\$\{[^}]*(?:user_id|slug|md5_id)[^}]*\}',
        r'`[^`]*(?:user_id|slug|md5_id)[^`]*`'
    ]
    
    for pattern in concat_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 200)
            end = min(len(content), match.end() + 200)
            context = content[start:end]
            context = re.sub(r'\s+', ' ', context)
            print(f"\n🔸 Encontrado: {match.group(0)}")
            print(f"   Contexto: {context[:400]}")
    
    print("\n" + "=" * 60)
    print("📌 PADRÃO 3: Funções MD5/Hash")
    print("-" * 60)
    
    # 3. Procurar funções de hash
    hash_patterns = [
        r'MD5\([^)]+\)',
        r'md5\([^)]+\)',
        r'hash\([^)]+\)',
        r'digest\([^)]+\)'
    ]
    
    for pattern in hash_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            start = max(0, match.start() - 300)
            end = min(len(content), match.end() + 300)
            context = content[start:end]
            context = re.sub(r'\s+', ' ', context)
            print(f"\n🔸 Encontrado: {match.group(0)}")
            print(f"   Contexto: {context[:500]}")
    
    print("\n" + "=" * 60)
    print("📌 PADRÃO 4: TextEncoder (conversão para bytes)")
    print("-" * 60)
    
    # 4. Procurar TextEncoder
    encoder_matches = list(re.finditer(r'.{0,300}TextEncoder.{0,300}', content, re.DOTALL))
    for i, match in enumerate(encoder_matches[:5], 1):
        snippet = match.group(0)
        snippet = re.sub(r'\s+', ' ', snippet)
        print(f"\n🔸 Ocorrência {i}:")
        print(snippet[:600])
    
    print("\n" + "=" * 60)
    print("📌 PADRÃO 5: Variáveis com 'key' no nome")
    print("-" * 60)
    
    # 5. Procurar variáveis com 'key'
    key_vars = re.finditer(r'(var|let|const)\s+(\w*[Kk]ey\w*)\s*=\s*([^;]+)', content)
    for match in key_vars:
        print(f"\n🔸 {match.group(1)} {match.group(2)} = {match.group(3)[:200]}")
    
    print("\n" + "=" * 60)
    print("📌 PADRÃO 6: Possíveis fórmulas completas")
    print("-" * 60)
    
    # 6. Procurar padrões complexos que podem ser a fórmula
    formula_patterns = [
        r'(?:user_id|slug|md5_id)[^;]{0,200}(?:user_id|slug|md5_id)[^;]{0,200}(?:user_id|slug|md5_id)',
        r'MD5\([^)]*(?:user_id|slug|md5_id)[^)]*\)',
        r'encode\([^)]*(?:user_id|slug|md5_id)[^)]*\)'
    ]
    
    found_formulas = set()
    for pattern in formula_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            formula = match.group(0)
            formula = re.sub(r'\s+', ' ', formula)
            if len(formula) < 500 and formula not in found_formulas:
                found_formulas.add(formula)
                print(f"\n🔸 Possível fórmula:")
                print(f"   {formula}")
    
    print("\n" + "=" * 60)
    print("✅ ANÁLISE COMPLETA")
    print("=" * 60)
    print()
    print("💡 PRÓXIMOS PASSOS:")
    print("1. Revisar os padrões encontrados acima")
    print("2. Identificar a sequência: user_id + slug + md5_id (ou similar)")
    print("3. Verificar se há MD5() ou hash() aplicado")
    print("4. Testar a fórmula com valores conhecidos")
    print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 find_key_formula.py <arquivo.js>")
        sys.exit(1)
    
    find_key_formula(sys.argv[1])
