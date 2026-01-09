#!/usr/bin/env python3
"""
Análise do core.bundle.js para encontrar a lógica de decriptação
"""

import re

def analyze_bundle():
    print('='*70)
    print('🔬 Análise do core.bundle.js')
    print('='*70)
    
    with open('core_bundle.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    print(f'📄 Arquivo: {len(js)} caracteres')
    
    # 1. Procurar por AES-CTR
    print('\n🔐 Procurando AES-CTR...')
    aes_matches = list(re.finditer(r'.{100}AES-CTR.{200}', js))
    for i, match in enumerate(aes_matches[:3]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 2. Procurar por decrypt
    print('\n🔓 Procurando decrypt...')
    decrypt_matches = list(re.finditer(r'.{50}decrypt.{100}', js, re.IGNORECASE))
    for i, match in enumerate(decrypt_matches[:5]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 3. Procurar por crypto.subtle
    print('\n🔑 Procurando crypto.subtle...')
    crypto_matches = list(re.finditer(r'.{50}crypto\.subtle.{100}', js, re.IGNORECASE))
    for i, match in enumerate(crypto_matches[:3]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 4. Procurar por importKey
    print('\n🗝️ Procurando importKey...')
    key_matches = list(re.finditer(r'.{50}importKey.{100}', js, re.IGNORECASE))
    for i, match in enumerate(key_matches[:3]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 5. Procurar por sources/file
    print('\n🎬 Procurando sources/file...')
    sources_matches = list(re.finditer(r"['\"]sources['\"]\s*:\s*\[", js))
    for i, match in enumerate(sources_matches[:3]):
        pos = match.start()
        context = js[pos:pos+300]
        print(f'\n   Match {i+1}:')
        print(f'   {context}')
    
    # 6. Procurar por funções que processam media
    print('\n📼 Procurando processamento de media...')
    media_matches = list(re.finditer(r'.{30}\.media.{100}', js))
    for i, match in enumerate(media_matches[:5]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 7. Procurar por TextDecoder (usado para converter bytes em string)
    print('\n📝 Procurando TextDecoder...')
    decoder_matches = list(re.finditer(r'.{50}TextDecoder.{100}', js))
    for i, match in enumerate(decoder_matches[:3]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 8. Procurar por chaves hardcoded
    print('\n🔑 Procurando chaves hardcoded...')
    # Procurar por arrays de números (possíveis chaves)
    key_arrays = re.findall(r'\[(\d+,\d+,\d+,\d+,\d+,\d+,\d+,\d+[^\]]*)\]', js)
    for arr in key_arrays[:10]:
        nums = [int(x) for x in arr.split(',') if x.strip().isdigit()]
        if 8 <= len(nums) <= 32:
            print(f'   Possível chave ({len(nums)} bytes): {nums[:16]}...')
            # Converter para string se possível
            try:
                as_str = ''.join(chr(n) for n in nums if 32 <= n < 127)
                if len(as_str) > 4:
                    print(f'      Como string: {as_str}')
            except:
                pass
    
    # 9. Procurar por base64 decode
    print('\n🔄 Procurando base64 decode...')
    b64_matches = list(re.finditer(r'.{30}(atob|btoa|base64).{100}', js, re.IGNORECASE))
    for i, match in enumerate(b64_matches[:5]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')
    
    # 10. Procurar pela função principal de setup do player
    print('\n🎮 Procurando setup do player...')
    setup_matches = list(re.finditer(r'function.{0,50}setup.{0,200}sources', js, re.IGNORECASE))
    for i, match in enumerate(setup_matches[:3]):
        print(f'\n   Match {i+1}:')
        print(f'   {match.group()}')


if __name__ == '__main__':
    analyze_bundle()
