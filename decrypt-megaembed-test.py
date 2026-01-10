#!/usr/bin/env python3
"""
Tenta descriptografar resposta da API do MegaEmbed
"""

import hashlib
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

# Dados capturados
API_URL = "https://megaembed.link/api/v1/info?id=Yzg0NjI0NjI="
HOSTNAME = "megaembed.link"

def derive_key(hostname):
    """Deriva chave AES do hostname (como o JS faz)"""
    # Método 1: SHA256 do hostname
    key = hashlib.sha256(hostname.encode()).digest()
    return key

def try_decrypt(encrypted_hex, key):
    """Tenta descriptografar com AES-CBC"""
    try:
        encrypted = binascii.unhexlify(encrypted_hex)
        
        # IV geralmente são os primeiros 16 bytes
        iv = encrypted[:16]
        ciphertext = encrypted[16:]
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode('utf-8')
    except Exception as e:
        return f"Erro: {e}"

# Buscar dados da API
print(f"[*] Buscando: {API_URL}")
resp = requests.get(API_URL, headers={"Referer": "https://megaembed.link/"})
encrypted_hex = resp.text.strip()
print(f"[*] Dados criptografados ({len(encrypted_hex)} chars): {encrypted_hex[:100]}...")

# Tentar várias derivações de chave
print("\n[*] Tentando descriptografar...")

keys_to_try = [
    ("SHA256(hostname)", hashlib.sha256(HOSTNAME.encode()).digest()),
    ("MD5(hostname)", hashlib.md5(HOSTNAME.encode()).digest()),
    ("hostname[:16]", (HOSTNAME * 2)[:16].encode()),
    ("hostname[:32]", (HOSTNAME * 3)[:32].encode()),
]

for name, key in keys_to_try:
    result = try_decrypt(encrypted_hex, key)
    print(f"\n[{name}]")
    if not result.startswith("Erro"):
        print(f"  SUCESSO: {result[:200]}")
    else:
        print(f"  {result}")
