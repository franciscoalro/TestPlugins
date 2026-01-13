#!/usr/bin/env python3
"""
Analisa o core.bundle.js para encontrar a lógica de descriptografia
"""

import requests
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def main():
    print("🔍 Baixando core.bundle.js...")
    
    url = "https://iamcdn.net/player-v2/core.bundle.js"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers, timeout=30)
    bundle = response.text
    
    print(f"✅ Tamanho: {len(bundle)} chars")
    
    # Salvar para análise
    with open("core_bundle_new.js", "w", encoding="utf-8") as f:
        f.write(bundle)
    print("✅ Salvo em core_bundle_new.js")
    
    # Procurar funções importantes
    print("\n🔍 Procurando padrões importantes...")
    
    patterns = [
        (r'SoTrym', "Função SoTrym"),
        (r'decrypt', "Decrypt"),
        (r'AES', "AES"),
        (r'CryptoJS', "CryptoJS"),
        (r'atob', "atob (base64)"),
        (r'JSON\.parse', "JSON.parse"),
        (r'\.m3u8', "m3u8"),
        (r'\.mp4', "mp4"),
        (r'googleapis', "Google APIs"),
        (r'storage\.google', "Google Storage"),
        (r'jwplayer', "JWPlayer"),
        (r'sources', "sources"),
        (r'file:', "file:"),
        (r'"file"', '"file"'),
        (r'media', "media"),
    ]
    
    for pattern, name in patterns:
        matches = list(re.finditer(pattern, bundle, re.IGNORECASE))
        if matches:
            print(f"\n✅ {name}: {len(matches)} ocorrências")
            # Mostrar contexto da primeira ocorrência
            if matches:
                pos = matches[0].start()
                context = bundle[max(0, pos-50):min(len(bundle), pos+150)]
                print(f"   Contexto: ...{context}...")
    
    # Procurar a função que processa o media
    print("\n🔍 Procurando função de processamento de media...")
    
    # Procurar padrão de descriptografia
    decrypt_patterns = [
        r'function\s+\w+\s*\([^)]*\)\s*\{[^}]*decrypt[^}]*\}',
        r'\.decrypt\s*\([^)]+\)',
        r'CryptoJS\.[^(]+\([^)]+\)',
    ]
    
    for pattern in decrypt_patterns:
        matches = re.findall(pattern, bundle)
        if matches:
            print(f"\n✅ Padrão de decrypt encontrado:")
            for m in matches[:3]:
                print(f"   {m[:200]}...")

if __name__ == "__main__":
    main()
