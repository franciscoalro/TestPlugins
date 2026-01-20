#!/usr/bin/env python3
"""
Analisa JavaScript do MegaEmbed para encontrar chave de descriptografia
Baseado nos logs v125 que mostram resposta criptografada
"""

import requests
import re
import json
from urllib.parse import urljoin

# URLs dos arquivos JavaScript
BASE_URL = "https://megaembed.link"
JS_FILES = [
    "/assets/prod-cvEtvBo1.js",
    "/assets/index-CZ_ja_1t.js",
    "/assets/vidstack-player-default-layout-BpV3Dvv2.js"
]

def download_js(url):
    """Baixa arquivo JavaScript"""
    try:
        print(f"📥 Baixando: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"✅ Baixado: {len(response.text)} chars")
        return response.text
    except Exception as e:
        print(f"❌ Erro ao baixar {url}: {e}")
        return None

def find_decrypt_patterns(js_code):
    """Procura padrões de descriptografia no JavaScript"""
    patterns = {
        "AES Keys": [
            r'key\s*[:=]\s*["\']([a-fA-F0-9]{32,64})["\']',
            r'aes[Kk]ey\s*[:=]\s*["\']([^"\']+)["\']',
            r'secret\s*[:=]\s*["\']([^"\']+)["\']',
            r'decrypt[Kk]ey\s*[:=]\s*["\']([^"\']+)["\']'
        ],
        "IV (Initialization Vector)": [
            r'iv\s*[:=]\s*["\']([a-fA-F0-9]{32})["\']',
            r'initVector\s*[:=]\s*["\']([^"\']+)["\']'
        ],
        "Decrypt Functions": [
            r'function\s+decrypt\s*\([^)]*\)\s*\{[^}]{0,500}\}',
            r'decrypt\s*[:=]\s*function\s*\([^)]*\)\s*\{[^}]{0,500}\}',
            r'\.decrypt\s*\([^)]+\)',
            r'CryptoJS\.AES\.decrypt',
            r'atob\s*\(',
            r'fromCharCode'
        ],
        "API Calls": [
            r'/api/v1/info\?id=',
            r'fetch\s*\([^)]*api[^)]*\)',
            r'axios\.[get|post]\s*\([^)]*api[^)]*\)'
        ],
        "Base64/Hex": [
            r'atob\s*\([^)]+\)',
            r'btoa\s*\([^)]+\)',
            r'Buffer\.from\s*\([^)]+\)',
            r'toString\s*\(\s*["\']hex["\']\s*\)',
            r'toString\s*\(\s*["\']base64["\']\s*\)'
        ]
    }
    
    results = {}
    
    for category, pattern_list in patterns.items():
        matches = []
        for pattern in pattern_list:
            found = re.findall(pattern, js_code, re.IGNORECASE | re.MULTILINE)
            if found:
                matches.extend(found)
        
        if matches:
            results[category] = matches
    
    return results

def find_hardcoded_keys(js_code):
    """Procura chaves hardcoded (32 ou 64 caracteres hex)"""
    # Chaves AES-256 (64 hex chars) ou AES-128 (32 hex chars)
    key_pattern = r'["\']([a-fA-F0-9]{32,64})["\']'
    matches = re.findall(key_pattern, js_code)
    
    # Filtrar chaves únicas
    unique_keys = list(set(matches))
    
    return unique_keys

def analyze_api_response_handling(js_code):
    """Analisa como a resposta da API é processada"""
    patterns = [
        r'\.then\s*\(\s*(?:response|res|r)\s*=>\s*\{([^}]{0,500})\}',
        r'\.json\s*\(\s*\)\.then\s*\([^)]+\)\s*\{([^}]{0,500})\}',
        r'response\.data\s*=\s*([^;]+)',
        r'JSON\.parse\s*\([^)]+\)'
    ]
    
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, js_code, re.MULTILINE | re.DOTALL)
        results.extend(matches)
    
    return results

def main():
    print("=" * 60)
    print("🔍 ANÁLISE MEGAEMBED CRYPTO v2")
    print("=" * 60)
    print()
    
    all_js_code = ""
    
    # Baixar todos os arquivos JS
    for js_file in JS_FILES:
        url = urljoin(BASE_URL, js_file)
        js_code = download_js(url)
        
        if js_code:
            all_js_code += f"\n\n/* ===== {js_file} ===== */\n\n" + js_code
            
            # Salvar arquivo individual
            filename = js_file.split('/')[-1]
            with open(f"megaembed_{filename}", "w", encoding="utf-8") as f:
                f.write(js_code)
            print(f"💾 Salvo: megaembed_{filename}")
    
    print()
    print("=" * 60)
    print("🔎 PROCURANDO PADRÕES DE CRIPTOGRAFIA")
    print("=" * 60)
    print()
    
    # Analisar padrões
    patterns = find_decrypt_patterns(all_js_code)
    
    for category, matches in patterns.items():
        print(f"\n📌 {category}:")
        for match in matches[:10]:  # Limitar a 10 resultados
            if isinstance(match, tuple):
                match = match[0] if match else ""
            
            # Truncar se muito longo
            if len(str(match)) > 200:
                print(f"  - {str(match)[:200]}...")
            else:
                print(f"  - {match}")
    
    print()
    print("=" * 60)
    print("🔑 PROCURANDO CHAVES HARDCODED")
    print("=" * 60)
    print()
    
    keys = find_hardcoded_keys(all_js_code)
    if keys:
        print(f"✅ Encontradas {len(keys)} chaves potenciais:")
        for i, key in enumerate(keys[:20], 1):  # Limitar a 20
            print(f"  {i}. {key} ({len(key)} chars)")
    else:
        print("❌ Nenhuma chave hardcoded encontrada")
    
    print()
    print("=" * 60)
    print("📡 ANALISANDO PROCESSAMENTO DE API")
    print("=" * 60)
    print()
    
    api_handling = analyze_api_response_handling(all_js_code)
    if api_handling:
        print(f"✅ Encontrados {len(api_handling)} trechos de processamento:")
        for i, code in enumerate(api_handling[:5], 1):
            print(f"\n  [{i}]")
            print(f"  {code[:300]}...")
    else:
        print("❌ Nenhum processamento de API encontrado")
    
    # Salvar código completo
    with open("megaembed_all_js.txt", "w", encoding="utf-8") as f:
        f.write(all_js_code)
    
    print()
    print("=" * 60)
    print("💾 ARQUIVOS SALVOS:")
    print("=" * 60)
    print("  - megaembed_prod-cvEtvBo1.js")
    print("  - megaembed_index-CZ_ja_1t.js")
    print("  - megaembed_vidstack-player-default-layout-BpV3Dvv2.js")
    print("  - megaembed_all_js.txt (todos combinados)")
    print()
    print("🔍 Próximo passo: Analisar manualmente os arquivos para encontrar a lógica de descriptografia")
    print()

if __name__ == "__main__":
    main()
