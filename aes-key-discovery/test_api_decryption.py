#!/usr/bin/env python3

"""
Script para fazer requisição real à API e testar decriptação
"""

import requests
import hashlib
import base64
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

# URL da API
API_URL = "https://playerembedapi.link/api/media"

# Vídeo de teste
TEST_VIDEO = "kBJLtxCD3"

def md5(text):
    """Gera hash MD5"""
    return hashlib.md5(text.encode()).hexdigest()

def get_video_data(video_id):
    """Faz requisição para obter dados do vídeo"""
    try:
        response = requests.get(f"{API_URL}?v={video_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao obter dados: {e}")
        return None

def decrypt_aes_cbc(encrypted_data, key_hex, iv_hex=None):
    """Decripta dados usando AES-CBC"""
    try:
        # Converter chave de hex para bytes
        key = bytes.fromhex(key_hex)
        
        # IV padrão (zeros) se não fornecido
        if iv_hex:
            iv = bytes.fromhex(iv_hex)
        else:
            iv = b'\x00' * 16
        
        # Decodificar base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Criar cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decriptar
        decrypted = cipher.decrypt(encrypted_bytes)
        
        # Remover padding
        decrypted = unpad(decrypted, AES.block_size)
        
        return decrypted.decode('utf-8')
    except Exception as e:
        return None

def decrypt_openssl_format(encrypted_data, password):
    """Decripta formato OpenSSL (Salted__)"""
    try:
        # Decodificar base64
        data = base64.b64decode(encrypted_data)
        
        # Verificar se começa com "Salted__"
        if data[:8] != b'Salted__':
            return None
        
        # Extrair salt
        salt = data[8:16]
        ciphertext = data[16:]
        
        # Derivar chave e IV usando EVP_BytesToKey (compatível com OpenSSL)
        key_iv = evp_bytes_to_key(password.encode(), salt, 32, 16)
        key = key_iv[:32]
        iv = key_iv[32:48]
        
        # Criar cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decriptar
        decrypted = cipher.decrypt(ciphertext)
        
        # Remover padding
        decrypted = unpad(decrypted, AES.block_size)
        
        return decrypted.decode('utf-8')
    except Exception as e:
        return None

def evp_bytes_to_key(password, salt, key_len, iv_len):
    """Implementação de EVP_BytesToKey (compatível com OpenSSL)"""
    m = []
    i = 0
    while len(b''.join(m)) < (key_len + iv_len):
        md = hashlib.md5()
        data = password + salt
        if i > 0:
            data = m[i - 1] + data
        md.update(data)
        m.append(md.digest())
        i += 1
    return b''.join(m)[:key_len + iv_len]

def test_formulas(data):
    """Testa todas as fórmulas possíveis"""
    user_id = str(data.get('user_id', ''))
    slug = data.get('slug', '')
    md5_id = str(data.get('md5_id', ''))
    encrypted_media = data.get('media', '')
    
    if not encrypted_media:
        print("❌ Campo 'media' não encontrado ou vazio")
        return
    
    print("\n📊 Dados Recebidos:")
    print(f"  user_id: {user_id}")
    print(f"  slug: {slug}")
    print(f"  md5_id: {md5_id}")
    print(f"  media: {encrypted_media[:50]}...")
    print()
    
    # Todas as combinações
    formulas = [
        ("user_id + slug + md5_id", user_id + slug + md5_id),
        ("user_id + md5_id + slug", user_id + md5_id + slug),
        ("slug + user_id + md5_id", slug + user_id + md5_id),
        ("slug + md5_id + user_id", slug + md5_id + user_id),
        ("md5_id + user_id + slug", md5_id + user_id + slug),
        ("md5_id + slug + user_id", md5_id + slug + user_id),
    ]
    
    print("🔑 Testando Fórmulas:\n")
    
    for i, (name, value) in enumerate(formulas, 1):
        hash_value = md5(value)
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"{i}. {name}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   Valor: {value}")
        print(f"   MD5:   {hash_value}")
        
        # Tentar decriptar com AES-CBC
        result = decrypt_aes_cbc(encrypted_media, hash_value)
        if result:
            print(f"   ✅ SUCESSO! (AES-CBC)")
            print(f"   📄 Dados decriptados:")
            print(f"   {result[:200]}...")
            print()
            print(f"   🎯 FÓRMULA CORRETA: {name}")
            return
        
        # Tentar decriptar formato OpenSSL
        result = decrypt_openssl_format(encrypted_media, value)
        if result:
            print(f"   ✅ SUCESSO! (OpenSSL Format)")
            print(f"   📄 Dados decriptados:")
            print(f"   {result[:200]}...")
            print()
            print(f"   🎯 FÓRMULA CORRETA: {name}")
            return
        
        print(f"   ❌ Falhou")
        print()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n⚠️  Nenhuma fórmula funcionou. Possíveis razões:")
    print("  1. Algoritmo diferente (AES-GCM, AES-CTR, etc.)")
    print("  2. IV (Initialization Vector) específico")
    print("  3. Formato de criptografia diferente")
    print("  4. Chave derivada de forma diferente")
    print("\n💡 Próximo passo: Usar Frida para capturar a chave em runtime")

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🔓 Teste de Decriptação - PlayerEmbedAPI                ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"📡 Fazendo requisição para: {API_URL}?v={TEST_VIDEO}")
    
    data = get_video_data(TEST_VIDEO)
    
    if data:
        print("✅ Dados recebidos com sucesso!")
        test_formulas(data)
    else:
        print("❌ Falha ao obter dados da API")
        print("\n💡 Você pode testar manualmente fornecendo os dados:")
        print("   python3 test_api_decryption.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
