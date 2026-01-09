#!/usr/bin/env python3
"""
Tenta decriptar a resposta da API do MegaEmbed
Baseado nas chaves encontradas no JavaScript
"""

import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

# Chaves encontradas no megaembed_index.js
KEYS = {
    'CENC': '1077efecc0b24d02ace33c1e52e2fb4b',
    'CLEARKEY': 'e2719d58a985b3c9781ab030af78d30e',
    'PLAYREADY': '9a04f07998404286ab92e65be0885f95',
    'WIDEVINE': 'edef8ba979d64acea3c827dcd51d21ed',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://megaembed.link/',
    'Origin': 'https://megaembed.link',
}

def get_encrypted_data(video_id):
    """Busca dados criptografados da API"""
    api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
    resp = requests.get(api_url, headers=HEADERS, timeout=30)
    return resp.content

def try_decrypt_aes_cbc(data, key_hex, iv=None):
    """Tenta decriptar com AES-CBC"""
    try:
        key = bytes.fromhex(key_hex)
        
        # Se IV não fornecido, tentar primeiros 16 bytes
        if iv is None:
            if len(data) > 16:
                iv = data[:16]
                data = data[16:]
            else:
                iv = b'\x00' * 16
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(data)
        
        # Tentar remover padding
        try:
            decrypted = unpad(decrypted, AES.block_size)
        except:
            pass
        
        return decrypted
    except Exception as e:
        return None

def try_decrypt_aes_ecb(data, key_hex):
    """Tenta decriptar com AES-ECB"""
    try:
        key = bytes.fromhex(key_hex)
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(data)
        
        try:
            decrypted = unpad(decrypted, AES.block_size)
        except:
            pass
        
        return decrypted
    except Exception as e:
        return None

def is_valid_json(data):
    """Verifica se é JSON válido"""
    try:
        json.loads(data.decode('utf-8'))
        return True
    except:
        return False

def is_readable(data):
    """Verifica se contém texto legível"""
    try:
        text = data.decode('utf-8', errors='ignore')
        # Verificar se tem caracteres imprimíveis
        printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
        return printable / len(text) > 0.7 if text else False
    except:
        return False

def main():
    print("="*60)
    print("TENTATIVA DE DECRIPTAÇÃO - MegaEmbed API")
    print("="*60)
    
    video_id = "3wnuij"  # Terra de Pecados
    
    print(f"\n1. Buscando dados para ID: {video_id}")
    encrypted = get_encrypted_data(video_id)
    
    print(f"   Tamanho: {len(encrypted)} bytes")
    print(f"   Primeiros bytes (hex): {encrypted[:32].hex()}")
    
    # Verificar se é hex string
    try:
        encrypted_bytes = bytes.fromhex(encrypted.decode('utf-8'))
        print(f"   Convertido de hex: {len(encrypted_bytes)} bytes")
        encrypted = encrypted_bytes
    except:
        print("   Não é hex string, usando bytes diretos")
    
    print(f"\n2. Testando decriptação com chaves conhecidas...")
    
    for name, key in KEYS.items():
        print(f"\n   Testando {name} ({key}):")
        
        # AES-CBC
        result = try_decrypt_aes_cbc(encrypted, key)
        if result:
            if is_valid_json(result):
                print(f"      ✓ AES-CBC: JSON válido!")
                print(f"      {result[:200]}...")
                return result
            elif is_readable(result):
                print(f"      ? AES-CBC: Texto legível")
                print(f"      {result[:100]}...")
        
        # AES-CBC com IV zerado
        result = try_decrypt_aes_cbc(encrypted, key, b'\x00' * 16)
        if result:
            if is_valid_json(result):
                print(f"      ✓ AES-CBC (IV=0): JSON válido!")
                print(f"      {result[:200]}...")
                return result
            elif is_readable(result):
                print(f"      ? AES-CBC (IV=0): Texto legível")
                print(f"      {result[:100]}...")
        
        # AES-ECB
        result = try_decrypt_aes_ecb(encrypted, key)
        if result:
            if is_valid_json(result):
                print(f"      ✓ AES-ECB: JSON válido!")
                print(f"      {result[:200]}...")
                return result
            elif is_readable(result):
                print(f"      ? AES-ECB: Texto legível")
                print(f"      {result[:100]}...")
    
    print("\n3. Nenhuma chave funcionou. Tentando outras abordagens...")
    
    # Tentar XOR simples com cada chave
    for name, key in KEYS.items():
        key_bytes = bytes.fromhex(key)
        result = bytes(a ^ b for a, b in zip(encrypted, key_bytes * (len(encrypted) // len(key_bytes) + 1)))
        if is_readable(result):
            print(f"   XOR com {name}: {result[:100]}...")
    
    print("\n4. Analisando estrutura dos dados...")
    print(f"   Primeiros 64 bytes: {encrypted[:64]}")
    
    # Verificar se há padrões
    if len(encrypted) % 16 == 0:
        print("   Tamanho é múltiplo de 16 (compatível com AES)")
    
    # Verificar entropia
    unique_bytes = len(set(encrypted))
    print(f"   Bytes únicos: {unique_bytes}/256")
    
    return None

if __name__ == "__main__":
    try:
        from Crypto.Cipher import AES
    except ImportError:
        print("Instalando pycryptodome...")
        import subprocess
        subprocess.run(['pip', 'install', 'pycryptodome'])
        from Crypto.Cipher import AES
    
    main()
