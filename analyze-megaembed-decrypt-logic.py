#!/usr/bin/env python3
"""
Análise profunda do JavaScript do MegaEmbed para extrair lógica de decrypt
"""

import requests
import re

def analyze():
    print("[*] Baixando JavaScript do MegaEmbed...")
    
    # Baixar página
    resp = requests.get("https://megaembed.link/")
    html = resp.text
    
    # Encontrar JS
    js_pattern = r'/assets/index-[A-Za-z0-9_-]+\.js'
    js_match = re.search(js_pattern, html)
    
    if not js_match:
        print("[!] JS não encontrado")
        return
    
    js_url = f"https://megaembed.link{js_match.group(0)}"
    print(f"[+] JS: {js_url}")
    
    js_resp = requests.get(js_url)
    js = js_resp.text
    
    print(f"[+] Tamanho: {len(js)} bytes")
    
    # Procurar padrões específicos de crypto
    print("\n[*] Procurando padrões de criptografia...")
    
    # 1. Procurar funções de decrypt
    decrypt_funcs = re.findall(r'function\s+\w*[Dd]ecrypt\w*\s*\([^)]*\)\s*\{[^}]{1,500}', js)
    print(f"\n[DECRYPT FUNCTIONS]: {len(decrypt_funcs)}")
    for f in decrypt_funcs[:3]:
        print(f"  {f[:150]}...")
    
    # 2. Procurar uso de TextEncoder/crypto
    crypto_patterns = [
        (r'crypto\.subtle\.[a-zA-Z]+', 'crypto.subtle'),
        (r'new\s+TextEncoder', 'TextEncoder'),
        (r'CryptoJS\.[A-Z]+', 'CryptoJS'),
        (r'aes-[a-z]+-[a-z]+', 'AES mode'),
        (r'AES-CBC|AES-GCM|AES-CTR', 'AES mode explicit'),
    ]
    
    for pattern, name in crypto_patterns:
        matches = re.findall(pattern, js, re.IGNORECASE)
        if matches:
            print(f"\n[{name}]: {len(matches)} - {set(matches)}")
    
    # 3. Procurar derivação de chave
    print("\n[*] Procurando derivação de chave...")
    key_derivation = re.findall(r'.{50}(hostname|location\.host|window\.location).{100}', js)
    for kd in key_derivation[:5]:
        print(f"  {kd[:150]}...")
    
    # 4. Procurar a função que processa /api/v1/info
    print("\n[*] Procurando processamento da API...")
    api_context = re.findall(r'.{200}/api/v1/info.{200}', js)
    for ctx in api_context[:2]:
        print(f"  {ctx}")
    
    # 5. Procurar hex decode
    hex_patterns = re.findall(r'.{50}(fromCharCode|parseInt.*16|hex).{50}', js, re.IGNORECASE)
    print(f"\n[HEX DECODE]: {len(hex_patterns)} padrões")
    
    # 6. Salvar trecho relevante
    # Procurar onde 'info' é processado
    info_idx = js.find('/api/v1/info')
    if info_idx > 0:
        snippet = js[max(0, info_idx-1000):info_idx+2000]
        with open("megaembed_api_snippet.js", "w", encoding="utf-8") as f:
            f.write(snippet)
        print(f"\n[*] Snippet salvo em megaembed_api_snippet.js")
    
    # 7. Procurar padrão específico de decrypt com hex
    print("\n[*] Procurando padrão de decrypt hex...")
    hex_decrypt = re.findall(r'[a-zA-Z_$]+\s*\(\s*[a-zA-Z_$]+\s*,\s*["\'][a-fA-F0-9]{32,}["\']\s*\)', js)
    for hd in hex_decrypt[:5]:
        print(f"  {hd}")

if __name__ == "__main__":
    analyze()
