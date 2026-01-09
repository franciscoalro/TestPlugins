#!/usr/bin/env python3
"""
Extrair e replicar a lógica de decriptação do PlayerEmbedAPI
"""

import re
import json
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util import Counter

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

def analyze_decrypt_function():
    """Analisa a função de decrypt no bundle"""
    print('='*70)
    print('🔬 Extraindo lógica de decriptação')
    print('='*70)
    
    with open('core_bundle.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Procurar a classe que usa AES-CTR
    print('\n🔐 Procurando classe AES-CTR...')
    
    # Encontrar a classe completa
    aes_class_match = re.search(r'class\s+\w+\{constructor\(\)\{[^}]*AES-CTR[^}]*\}[^}]*\}', js, re.DOTALL)
    if aes_class_match:
        print(f'   Classe encontrada: {aes_class_match.group()[:500]}...')
    
    # Procurar por onde a chave é definida
    print('\n🔑 Procurando definição da chave...')
    
    # Procurar por setKey ou similar
    key_patterns = [
        r'setKey.{0,200}',
        r'this\[.key.\].{0,100}',
        r'importKey.{0,300}',
    ]
    
    for pattern in key_patterns:
        matches = re.findall(pattern, js)
        for m in matches[:3]:
            print(f'   {m[:150]}...')
    
    # Procurar por onde o media é processado
    print('\n📼 Procurando processamento do media...')
    
    # O campo media do JSON é processado em algum lugar
    media_process = re.findall(r'.{50}media.{100}', js)
    for m in media_process[:10]:
        if 'decrypt' in m.lower() or 'parse' in m.lower():
            print(f'   {m}')
    
    # Procurar por JSON.parse após decrypt
    print('\n📊 Procurando JSON.parse após decrypt...')
    json_parse = re.findall(r'.{100}decrypt.{0,50}JSON.{0,50}parse.{100}', js)
    for m in json_parse[:5]:
        print(f'   {m}')


def try_decrypt_media():
    """Tenta decriptar o campo media"""
    print('\n' + '='*70)
    print('🔓 Tentando decriptar campo media')
    print('='*70)
    
    # Obter dados do PlayerEmbedAPI
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    r = requests.get(url, headers=HEADERS)
    html = r.text
    
    # Extrair datas
    datas_match = re.search(r'const\s+datas\s*=\s*["\']([^"\']+)["\']', html)
    if not datas_match:
        print('❌ datas não encontrado')
        return
    
    datas_b64 = datas_match.group(1)
    decoded = base64.b64decode(datas_b64)
    
    print(f'📦 Dados decodificados ({len(decoded)} bytes)')
    
    # Extrair campos
    text = decoded.decode('utf-8', errors='replace')
    
    # Encontrar onde o media começa
    media_start = text.find('"media":"') + 9
    
    # O JSON tem estrutura: {"slug":"...","md5_id":...,"user_id":...,"media":"..."}
    # Precisamos extrair o media raw
    
    # Vamos parsear manualmente
    try:
        # Encontrar o início do media no bytes original
        media_marker = b'"media":"'
        media_pos = decoded.find(media_marker)
        if media_pos == -1:
            print('❌ Marcador media não encontrado')
            return
        
        media_start = media_pos + len(media_marker)
        
        # O media vai até o próximo " não escapado
        # Mas como tem bytes binários, vamos pegar até o final
        media_raw = decoded[media_start:]
        
        # Remover o final do JSON ("}
        if media_raw.endswith(b'"}'):
            media_raw = media_raw[:-2]
        elif media_raw.endswith(b'"'):
            media_raw = media_raw[:-1]
        
        print(f'\n📼 Media raw ({len(media_raw)} bytes):')
        print(f'   Primeiros 50 bytes: {media_raw[:50]}')
        print(f'   Hex: {media_raw[:30].hex()}')
        
        # Tentar diferentes abordagens de decriptação
        print('\n🔐 Tentando decriptar...')
        
        # O AES-CTR precisa de uma chave e um counter/nonce
        # Vamos tentar algumas chaves comuns
        
        video_id = 'izD1HrKWL'
        md5_id = '28973410'
        user_id = '482120'
        
        possible_keys = [
            video_id.encode().ljust(16, b'\0'),
            md5_id.encode().ljust(16, b'\0'),
            user_id.encode().ljust(16, b'\0'),
            (video_id + md5_id).encode()[:16],
            b'playerembedapi\0\0',
            b'iamcdn.net\0\0\0\0\0\0',
            bytes.fromhex('00' * 16),
        ]
        
        for key in possible_keys:
            try:
                # AES-CTR com counter inicial 0
                ctr = Counter.new(128, initial_value=0)
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                decrypted = cipher.decrypt(media_raw)
                
                # Verificar se parece válido
                try:
                    text = decrypted.decode('utf-8')
                    if '{' in text or 'http' in text or 'file' in text:
                        print(f'\n✅ Possível sucesso com chave {key}:')
                        print(f'   {text[:200]}')
                except:
                    pass
                    
            except Exception as e:
                pass
        
        # Tentar com os primeiros bytes como IV/nonce
        print('\n🔐 Tentando com IV dos primeiros bytes...')
        
        if len(media_raw) > 16:
            iv = media_raw[:16]
            ciphertext = media_raw[16:]
            
            for key in possible_keys:
                try:
                    # AES-CTR com IV
                    ctr = Counter.new(128, initial_value=int.from_bytes(iv, 'big'))
                    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                    decrypted = cipher.decrypt(ciphertext)
                    
                    try:
                        text = decrypted.decode('utf-8')
                        if '{' in text or 'http' in text:
                            print(f'\n✅ Sucesso com IV + chave {key}:')
                            print(f'   {text[:200]}')
                    except:
                        pass
                except:
                    pass
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()


def search_for_key_in_bundle():
    """Procura pela chave de criptografia no bundle"""
    print('\n' + '='*70)
    print('🔑 Procurando chave no bundle')
    print('='*70)
    
    with open('core_bundle.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    # Procurar por strings que parecem chaves
    # Chaves AES geralmente são 16, 24 ou 32 bytes
    
    # Procurar por strings base64 de tamanho apropriado
    b64_strings = re.findall(r'["\']([A-Za-z0-9+/]{20,50}={0,2})["\']', js)
    
    print(f'📝 Strings base64 encontradas: {len(b64_strings)}')
    
    for s in b64_strings[:20]:
        try:
            decoded = base64.b64decode(s)
            if 16 <= len(decoded) <= 32:
                print(f'   {s} -> {len(decoded)} bytes: {decoded[:20]}...')
        except:
            pass
    
    # Procurar por hex strings
    hex_strings = re.findall(r'["\']([0-9a-fA-F]{32,64})["\']', js)
    print(f'\n📝 Strings hex encontradas: {len(hex_strings)}')
    
    for s in hex_strings[:10]:
        print(f'   {s}')


if __name__ == '__main__':
    analyze_decrypt_function()
    search_for_key_in_bundle()
    try_decrypt_media()
