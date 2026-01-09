#!/usr/bin/env python3
"""
Engenharia reversa profunda - Decodificação dos dados
"""

import requests
import re
import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def analyze_megaembed_api():
    """Analisa a resposta da API do MegaEmbed"""
    print('\n' + '='*70)
    print('🔬 MEGAEMBED - Análise da API')
    print('='*70)
    
    video_id = 'rckhv6'
    api_url = f'https://megaembed.link/api/v1/video?id={video_id}'
    
    r = requests.get(api_url, headers={**HEADERS, 'Referer': f'https://megaembed.link/#{video_id}'})
    encrypted_data = r.text
    
    print(f'📦 Dados criptografados ({len(encrypted_data)} chars):')
    print(f'   {encrypted_data[:100]}...')
    
    # Tentar decodificar como hex
    print('\n🔐 Tentando decodificar...')
    try:
        hex_decoded = bytes.fromhex(encrypted_data)
        print(f'   Hex decoded ({len(hex_decoded)} bytes): {hex_decoded[:50]}...')
    except:
        print('   ❌ Não é hex válido')
    
    # Tentar base64
    try:
        b64_decoded = base64.b64decode(encrypted_data)
        print(f'   Base64 decoded: {b64_decoded[:50]}...')
    except:
        print('   ❌ Não é base64 válido')
    
    # Analisar padrão dos dados
    print('\n📊 Análise do padrão:')
    print(f'   Comprimento: {len(encrypted_data)}')
    print(f'   Caracteres únicos: {len(set(encrypted_data))}')
    print(f'   É hexadecimal: {all(c in "0123456789abcdef" for c in encrypted_data.lower())}')
    
    # Buscar página principal para encontrar chave de decriptação
    print('\n🔍 Buscando chave de decriptação na página...')
    page_url = f'https://megaembed.link/#{video_id}'
    r2 = requests.get(page_url, headers=HEADERS)
    html = r2.text
    
    # Procurar por chaves/secrets
    key_patterns = [
        r'key\s*[=:]\s*["\']([^"\']+)["\']',
        r'secret\s*[=:]\s*["\']([^"\']+)["\']',
        r'iv\s*[=:]\s*["\']([^"\']+)["\']',
        r'CryptoJS\.AES\.decrypt\([^,]+,\s*["\']([^"\']+)["\']',
        r'aes.*?["\']([a-zA-Z0-9+/=]{16,})["\']',
    ]
    
    for pattern in key_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f'   ✅ Padrão {pattern[:30]}...: {matches}')
    
    # Procurar scripts externos que podem ter a lógica
    print('\n📜 Scripts externos:')
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
    for script in scripts:
        print(f'   {script}')
        if 'megaembed' in script or 'player' in script:
            try:
                r3 = requests.get(script if script.startswith('http') else f'https://megaembed.link{script}', headers=HEADERS, timeout=10)
                js_content = r3.text
                print(f'      Conteúdo ({len(js_content)} chars)')
                
                # Procurar funções de decrypt
                decrypt_funcs = re.findall(r'decrypt|decipher|decode', js_content, re.IGNORECASE)
                if decrypt_funcs:
                    print(f'      ✅ Funções de decrypt encontradas!')
                    
                    # Extrair contexto
                    for match in re.finditer(r'.{0,100}(decrypt|decipher).{0,100}', js_content, re.IGNORECASE):
                        print(f'      → {match.group()[:150]}...')
            except Exception as e:
                print(f'      ❌ Erro: {e}')


def analyze_playerembedapi_data():
    """Analisa os dados do PlayerEmbedAPI"""
    print('\n' + '='*70)
    print('🔬 PLAYEREMBEDAPI - Análise dos dados')
    print('='*70)
    
    url = 'https://playerembedapi.link/?v=izD1HrKWL'
    r = requests.get(url, headers=HEADERS)
    html = r.text
    
    # Extrair a variável datas
    datas_match = re.search(r'const\s+datas\s*=\s*["\']([^"\']+)["\']', html)
    if datas_match:
        datas_b64 = datas_match.group(1)
        print(f'📦 datas (base64): {datas_b64[:80]}...')
        
        try:
            decoded = base64.b64decode(datas_b64)
            print(f'\n🔓 Decodificado ({len(decoded)} bytes):')
            
            # Tentar como JSON
            try:
                json_data = json.loads(decoded)
                print(f'   ✅ JSON válido!')
                print(json.dumps(json_data, indent=2)[:500])
            except:
                # Pode ter caracteres especiais
                print(f'   Raw: {decoded[:200]}...')
                
                # Tentar limpar e parsear
                try:
                    # Remover caracteres de controle
                    cleaned = decoded.decode('utf-8', errors='ignore')
                    print(f'   Cleaned: {cleaned[:200]}...')
                    
                    # Procurar por URLs
                    urls = re.findall(r'https?://[^\s"\'<>\\]+', cleaned)
                    if urls:
                        print(f'\n   🎬 URLs encontradas:')
                        for u in urls:
                            print(f'      {u}')
                except:
                    pass
        except Exception as e:
            print(f'   ❌ Erro ao decodificar: {e}')
    
    # Procurar por outras variáveis importantes
    print('\n🔍 Outras variáveis importantes:')
    
    # Procurar setup do JWPlayer
    jwplayer_match = re.search(r'jwplayer\([^)]+\)\.setup\((\{.*?\})\)', html, re.DOTALL)
    if jwplayer_match:
        print(f'   ✅ JWPlayer setup encontrado!')
        setup = jwplayer_match.group(1)
        print(f'   {setup[:300]}...')
    
    # Procurar por fetch/API calls
    fetch_matches = re.findall(r"fetch\(['\"]([^'\"]+)['\"]", html)
    if fetch_matches:
        print(f'\n   📡 Fetch calls:')
        for f in fetch_matches:
            print(f'      {f}')
    
    # Procurar por sources
    sources_match = re.search(r'sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
    if sources_match:
        print(f'\n   🎬 Sources:')
        print(f'      {sources_match.group(1)[:200]}...')


def try_decrypt_megaembed():
    """Tenta decriptar dados do MegaEmbed com chaves comuns"""
    print('\n' + '='*70)
    print('🔐 Tentando decriptar MegaEmbed')
    print('='*70)
    
    video_id = 'rckhv6'
    api_url = f'https://megaembed.link/api/v1/video?id={video_id}'
    
    r = requests.get(api_url, headers={**HEADERS, 'Referer': f'https://megaembed.link/#{video_id}'})
    encrypted_hex = r.text
    
    # Converter hex para bytes
    try:
        encrypted_bytes = bytes.fromhex(encrypted_hex)
    except:
        print('❌ Dados não são hex válido')
        return
    
    print(f'📦 Dados ({len(encrypted_bytes)} bytes)')
    
    # Chaves comuns usadas em players de vídeo
    common_keys = [
        video_id,
        video_id * 2,
        'megaembed',
        'megaembedkey',
        'secretkey',
        '0123456789abcdef',
        'abcdef0123456789',
        hashlib.md5(video_id.encode()).hexdigest()[:16],
        hashlib.md5(video_id.encode()).hexdigest(),
    ]
    
    for key in common_keys:
        try:
            # Preparar chave (16, 24 ou 32 bytes para AES)
            key_bytes = key.encode()[:32].ljust(32, b'\0')
            
            # Tentar AES-ECB
            cipher = AES.new(key_bytes[:16], AES.MODE_ECB)
            decrypted = cipher.decrypt(encrypted_bytes)
            
            # Verificar se parece válido
            try:
                text = decrypted.decode('utf-8')
                if '{' in text or 'http' in text:
                    print(f'✅ Possível sucesso com chave "{key}":')
                    print(f'   {text[:200]}')
            except:
                pass
                
        except Exception as e:
            pass
    
    # Tentar AES-CBC com IV = primeiros 16 bytes
    print('\n🔐 Tentando AES-CBC...')
    if len(encrypted_bytes) > 16:
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        for key in common_keys:
            try:
                key_bytes = key.encode()[:16].ljust(16, b'\0')
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)
                
                try:
                    text = unpad(decrypted, 16).decode('utf-8')
                    if '{' in text or 'http' in text:
                        print(f'✅ Sucesso com chave "{key}":')
                        print(f'   {text[:200]}')
                except:
                    pass
            except:
                pass


def main():
    analyze_megaembed_api()
    analyze_playerembedapi_data()
    
    # Instalar pycryptodome se necessário
    try:
        try_decrypt_megaembed()
    except ImportError:
        print('\n⚠️ Para tentar decriptar, instale: pip install pycryptodome')


if __name__ == '__main__':
    main()
