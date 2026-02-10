#!/usr/bin/env python3

"""
Análise avançada de padrões - Identifica possíveis fórmulas de chave
"""

import re
import sys
import hashlib
from collections import defaultdict

def analyze_file(filepath):
    """Análise completa do arquivo JavaScript"""
    
    print("=" * 80)
    print("🔬 ANÁLISE AVANÇADA DE PADRÕES")
    print("=" * 80)
    print()
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    results = {
        'importkey_contexts': [],
        'concatenations': [],
        'hash_functions': [],
        'encoder_usages': [],
        'key_variables': [],
        'possible_formulas': []
    }
    
    # 1. Analisar contextos de importKey
    print("📌 [1/6] Analisando contextos de importKey...")
    results['importkey_contexts'] = find_importkey_contexts(content)
    print(f"   Encontrados: {len(results['importkey_contexts'])} contextos")
    
    # 2. Encontrar concatenações
    print("📌 [2/6] Procurando concatenações de parâmetros...")
    results['concatenations'] = find_concatenations(content)
    print(f"   Encontradas: {len(results['concatenations'])} concatenações")
    
    # 3. Encontrar funções de hash
    print("📌 [3/6] Procurando funções de hash...")
    results['hash_functions'] = find_hash_functions(content)
    print(f"   Encontradas: {len(results['hash_functions'])} funções")
    
    # 4. Encontrar usos de TextEncoder
    print("📌 [4/6] Analisando TextEncoder...")
    results['encoder_usages'] = find_encoder_usages(content)
    print(f"   Encontrados: {len(results['encoder_usages'])} usos")
    
    # 5. Encontrar variáveis com 'key'
    print("📌 [5/6] Procurando variáveis de chave...")
    results['key_variables'] = find_key_variables(content)
    print(f"   Encontradas: {len(results['key_variables'])} variáveis")
    
    # 6. Identificar possíveis fórmulas
    print("📌 [6/6] Identificando possíveis fórmulas...")
    results['possible_formulas'] = identify_formulas(content, results)
    print(f"   Identificadas: {len(results['possible_formulas'])} fórmulas")
    
    print()
    print("=" * 80)
    print("📊 RESULTADOS")
    print("=" * 80)
    print()
    
    # Exibir resultados
    display_results(results)
    
    # Gerar testes
    print()
    print("=" * 80)
    print("🧪 TESTES SUGERIDOS")
    print("=" * 80)
    print()
    generate_tests(results)

def find_importkey_contexts(content):
    """Encontra contextos ao redor de importKey"""
    contexts = []
    
    for match in re.finditer(r'.{0,300}importKey.{0,300}', content, re.DOTALL):
        snippet = match.group(0)
        # Limpar
        snippet = re.sub(r'\s+', ' ', snippet)
        contexts.append(snippet)
    
    return contexts[:5]  # Limitar a 5

def find_concatenations(content):
    """Encontra concatenações de user_id, slug, md5_id"""
    concatenations = []
    
    patterns = [
        r'(user_id|slug|md5_id)\s*\+\s*(user_id|slug|md5_id)',
        r'`[^`]*\$\{[^}]*(user_id|slug|md5_id)[^}]*\}[^`]*`',
        r'concat\([^)]*(?:user_id|slug|md5_id)[^)]*\)',
        r'"[^"]*"\s*\+\s*(user_id|slug|md5_id)',
        r'(user_id|slug|md5_id)\s*\+\s*"[^"]*"'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]
            context = re.sub(r'\s+', ' ', context)
            concatenations.append({
                'match': match.group(0),
                'context': context
            })
    
    return concatenations[:10]

def find_hash_functions(content):
    """Encontra funções de hash"""
    hash_funcs = []
    
    patterns = [
        r'MD5\([^)]+\)',
        r'md5\([^)]+\)',
        r'SHA\d*\([^)]+\)',
        r'sha\d*\([^)]+\)',
        r'hash\([^)]+\)',
        r'digest\([^)]+\)'
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            start = max(0, match.start() - 150)
            end = min(len(content), match.end() + 150)
            context = content[start:end]
            context = re.sub(r'\s+', ' ', context)
            hash_funcs.append({
                'function': match.group(0),
                'context': context
            })
    
    return hash_funcs[:10]

def find_encoder_usages(content):
    """Encontra usos de TextEncoder"""
    encoders = []
    
    for match in re.finditer(r'.{0,200}TextEncoder.{0,200}', content, re.DOTALL):
        snippet = match.group(0)
        snippet = re.sub(r'\s+', ' ', snippet)
        encoders.append(snippet)
    
    return encoders[:5]

def find_key_variables(content):
    """Encontra variáveis com 'key' no nome"""
    key_vars = []
    
    pattern = r'(var|let|const)\s+(\w*[Kk]ey\w*)\s*=\s*([^;]+)'
    
    for match in re.finditer(pattern, content):
        key_vars.append({
            'type': match.group(1),
            'name': match.group(2),
            'value': match.group(3)[:200]
        })
    
    return key_vars[:10]

def identify_formulas(content, results):
    """Identifica possíveis fórmulas baseado nos resultados"""
    formulas = []
    
    # Procurar por padrões que combinam os 3 parâmetros
    pattern = r'(?:user_id|slug|md5_id)[^;]{0,300}(?:user_id|slug|md5_id)[^;]{0,300}(?:user_id|slug|md5_id)'
    
    for match in re.finditer(pattern, content, re.IGNORECASE):
        formula = match.group(0)
        formula = re.sub(r'\s+', ' ', formula)
        
        # Verificar se tem os 3 parâmetros
        has_user_id = 'user_id' in formula.lower()
        has_slug = 'slug' in formula.lower()
        has_md5_id = 'md5_id' in formula.lower()
        
        if has_user_id and has_slug and has_md5_id:
            formulas.append(formula)
    
    # Remover duplicatas
    formulas = list(set(formulas))
    
    return formulas[:5]

def display_results(results):
    """Exibe os resultados formatados"""
    
    # 1. Contextos de importKey
    if results['importkey_contexts']:
        print("🔑 CONTEXTOS DE IMPORTKEY:")
        print("-" * 80)
        for i, ctx in enumerate(results['importkey_contexts'], 1):
            print(f"\n{i}. {ctx[:500]}...")
    
    # 2. Concatenações
    if results['concatenations']:
        print("\n\n🔗 CONCATENAÇÕES ENCONTRADAS:")
        print("-" * 80)
        for i, concat in enumerate(results['concatenations'], 1):
            print(f"\n{i}. Match: {concat['match']}")
            print(f"   Contexto: {concat['context'][:300]}...")
    
    # 3. Funções de hash
    if results['hash_functions']:
        print("\n\n#️⃣ FUNÇÕES DE HASH:")
        print("-" * 80)
        for i, func in enumerate(results['hash_functions'], 1):
            print(f"\n{i}. Função: {func['function']}")
            print(f"   Contexto: {func['context'][:300]}...")
    
    # 4. Variáveis de chave
    if results['key_variables']:
        print("\n\n🔐 VARIÁVEIS DE CHAVE:")
        print("-" * 80)
        for i, var in enumerate(results['key_variables'], 1):
            print(f"\n{i}. {var['type']} {var['name']} = {var['value']}")
    
    # 5. Fórmulas possíveis
    if results['possible_formulas']:
        print("\n\n✨ POSSÍVEIS FÓRMULAS:")
        print("-" * 80)
        for i, formula in enumerate(results['possible_formulas'], 1):
            print(f"\n{i}. {formula[:400]}")

def generate_tests(results):
    """Gera testes baseados nas fórmulas encontradas"""
    
    # Valores de teste
    user_id = "482120"
    slug = "kBJLtxCD3"
    md5_id = "28930647"
    
    print("Valores de teste:")
    print(f"  user_id = {user_id}")
    print(f"  slug = {slug}")
    print(f"  md5_id = {md5_id}")
    print()
    
    # Gerar combinações comuns
    combinations = [
        ("user_id + slug + md5_id", f"{user_id}{slug}{md5_id}"),
        ("user_id + md5_id + slug", f"{user_id}{md5_id}{slug}"),
        ("slug + user_id + md5_id", f"{slug}{user_id}{md5_id}"),
        ("slug + md5_id + user_id", f"{slug}{md5_id}{user_id}"),
        ("md5_id + user_id + slug", f"{md5_id}{user_id}{slug}"),
        ("md5_id + slug + user_id", f"{md5_id}{slug}{user_id}"),
    ]
    
    print("Testes de combinações:")
    print("-" * 80)
    
    for desc, value in combinations:
        md5_hash = hashlib.md5(value.encode()).hexdigest()
        print(f"\n{desc}:")
        print(f"  Valor: {value}")
        print(f"  MD5:   {md5_hash}")
    
    print()
    print("-" * 80)
    print()
    print("💡 DICA: Compare estes hashes com a chave usada em importKey")
    print("         nos contextos encontrados acima.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python3 advanced_analysis.py <arquivo.js>")
        sys.exit(1)
    
    analyze_file(sys.argv[1])
