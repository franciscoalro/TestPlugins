#!/usr/bin/env python3
"""
Replica a lógica de decriptação do MegaEmbed em Python
Baseado na análise do megaembed_index.js
"""

import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import re

# Funções encontradas no JavaScript:
# v() - gera a chave baseada em window.location.hash
# T() - gera o IV baseada em window.location
# S() - decripta usando AES-CBC

# Código JS original (simplificado):
"""
v = () => {
    const hash = window.location.hash;  // Ex: "#3wnuij"
    const k = "10";
    const O = 110;
    const j = 1;
    let N = "";
    
    // Converte caractere especial para string de dígitos
    const B = p("ᵟ").toString().split("");
    for (let pe = 0; pe < B.length; pe++) 
        N += g(k + B[pe]);
    
    N += g(p(hash, k/10));  // Adiciona baseado no hash
    N += N.slice(1, 3);
    N += g(O, O-1, O+7);  // Adiciona "nmo"
    
    const oe = "3579".split("");
    N += g(oe[3] + oe[2], oe[1] + oe[2]);
    N += g(oe[0]*j+j+oe[3], oe[0]*j+j+oe[3]);
    N += g(oe[3]*k + oe[3]*j, oe.reverse().join("").slice(0,2));
    
    return encode(N);  // Retorna Uint8Array de 16 bytes
}

T = () => {
    const protocol = window.location.protocol;  // "https:"
    const k = protocol + "//";
    const hostname = window.location.hostname;
    const j = protocol.length * k.length;  // 6 * 8 = 48
    const N = 1;
    let B = "";
    
    for (let Le = N; Le < 10; Le++)
        B += g(Le + j);  // Caracteres 49-57 (1-9 + 48)
    
    let oe = "";
    oe = N + oe + N + oe + N;  // "111"
    
    const pe = oe.length * p(hostname);  // 3 * charCode
    const Qe = oe * N + protocol.length;  // 111 + 6 = 117
    const P = Qe + 4;  // 121
    const ie = p(protocol, N);  // charCode de protocol[1]
    const Se = ie * N - 2;
    
    B += g(j, oe, pe, Qe, P, ie, Se);
    
    return encode(B);  // Retorna Uint8Array de 16 bytes
}
"""

def char_code_at(s, index=0):
    """Equivalente a JavaScript charCodeAt"""
    if index < len(s):
        return ord(s[index])
    return 0

def from_char_code(*codes):
    """Equivalente a String.fromCharCode"""
    result = ""
    for code in codes:
        if isinstance(code, str):
            # Se for string, converter para int
            try:
                code = int(code)
            except:
                continue
        if 0 <= code <= 0x10FFFF:
            result += chr(code)
    return result

def generate_key(video_hash):
    """
    Replica a função v() do JavaScript
    Gera a chave AES baseada no hash do vídeo
    """
    # Constantes do JS
    k = "10"
    O = 110
    j = 1
    
    N = ""
    
    # O caractere especial "ᵟ" (U+1D5F) - seu charCode é 7519
    special_char = "ᵟ"
    B = list(str(char_code_at(special_char)))  # "7519" -> ["7", "5", "1", "9"]
    
    # Primeira parte: converter dígitos do charCode especial
    for digit in B:
        N += from_char_code(int(k + digit))  # "107", "105", "101", "109" -> k, i, e, m
    
    # Segunda parte: baseado no hash
    hash_char_code = char_code_at(video_hash, int(int(k) / 10))  # hash[1]
    N += from_char_code(hash_char_code)
    
    # Terceira parte: slice
    N += N[1:3]
    
    # Quarta parte: caracteres fixos
    N += from_char_code(O, O-1, O+7)  # n, m, u
    
    # Quinta parte: baseado em "3579"
    oe = list("3579")
    N += from_char_code(int(oe[3] + oe[2]), int(oe[1] + oe[2]))  # 97, 57 -> a, 9
    N += from_char_code(int(oe[0])*j + j + int(oe[3]), int(oe[0])*j + j + int(oe[3]))  # 13, 13
    
    # Sexta parte
    reversed_oe = oe[::-1]  # ["9", "7", "5", "3"]
    N += from_char_code(
        int(oe[3]) * int(k) + int(oe[3]) * j,  # 9*10 + 9*1 = 99 -> c
        int("".join(reversed_oe[:2]))  # "97" -> a
    )
    
    # Converter para bytes (UTF-8)
    key_bytes = N.encode('utf-8')
    
    # Garantir 16 bytes
    if len(key_bytes) < 16:
        key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
    elif len(key_bytes) > 16:
        key_bytes = key_bytes[:16]
    
    return key_bytes

def generate_iv():
    """
    Replica a função T() do JavaScript
    Gera o IV AES baseado na URL
    """
    # Simulando window.location para megaembed.link
    protocol = "https:"
    hostname = "megaembed.link"
    
    k = protocol + "//"  # "https://"
    j = len(protocol) * len(k)  # 6 * 8 = 48
    N = 1
    
    B = ""
    
    # Primeira parte: caracteres 49-57 (dígitos 1-9 deslocados)
    for Le in range(N, 10):
        B += from_char_code(Le + j)  # 49, 50, ..., 57
    
    # Segunda parte
    oe = str(N) + "" + str(N) + "" + str(N)  # "111"
    
    pe = len(oe) * char_code_at(hostname)  # 3 * ord('m') = 3 * 109 = 327
    Qe = int(oe) * N + len(protocol)  # 111 + 6 = 117
    P = Qe + 4  # 121
    ie = char_code_at(protocol, N)  # ord('t') = 116
    Se = ie * N - 2  # 114
    
    B += from_char_code(j, int(oe), pe, Qe, P, ie, Se)
    
    # Converter para bytes
    iv_bytes = B.encode('utf-8')
    
    # Garantir 16 bytes
    if len(iv_bytes) < 16:
        iv_bytes = iv_bytes + b'\x00' * (16 - len(iv_bytes))
    elif len(iv_bytes) > 16:
        iv_bytes = iv_bytes[:16]
    
    return iv_bytes

def hex_to_bytes(hex_string):
    """Converte hex string para bytes"""
    return bytes.fromhex(hex_string)

def decrypt_megaembed(encrypted_hex, video_id):
    """
    Decripta os dados da API do MegaEmbed
    """
    # Gerar chave baseada no ID do vídeo (hash)
    key = generate_key(video_id)
    iv = generate_iv()
    
    print(f"Video ID: {video_id}")
    print(f"Key (hex): {key.hex()}")
    print(f"Key (str): {key}")
    print(f"IV (hex): {iv.hex()}")
    print(f"IV (str): {iv}")
    
    # Converter hex para bytes
    encrypted_bytes = hex_to_bytes(encrypted_hex)
    
    # Decriptar
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_bytes)
        
        # Tentar remover padding
        try:
            decrypted = unpad(decrypted, AES.block_size)
        except:
            pass
        
        return decrypted
    except Exception as e:
        print(f"Erro na decriptação: {e}")
        return None

def test_decryption():
    """Testa a decriptação com dados reais"""
    print("="*60)
    print("TESTE DE DECRIPTAÇÃO MEGAEMBED")
    print("="*60)
    
    # Buscar dados da API
    video_id = "3wnuij"
    api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://megaembed.link/',
        'Origin': 'https://megaembed.link',
    }
    
    print(f"\n1. Buscando dados para ID: {video_id}")
    resp = requests.get(api_url, headers=headers, timeout=30)
    encrypted_hex = resp.text
    
    print(f"   Tamanho: {len(encrypted_hex)} caracteres")
    print(f"   Primeiros 64 chars: {encrypted_hex[:64]}")
    
    print(f"\n2. Gerando chave e IV...")
    
    # Testar decriptação
    print(f"\n3. Tentando decriptar...")
    result = decrypt_megaembed(encrypted_hex, video_id)
    
    if result:
        print(f"\n4. Resultado ({len(result)} bytes):")
        
        # Tentar decodificar como UTF-8
        try:
            text = result.decode('utf-8')
            print(f"   Texto: {text[:500]}...")
            
            # Tentar parsear como JSON
            try:
                data = json.loads(text)
                print(f"\n   JSON válido!")
                print(json.dumps(data, indent=2)[:1000])
                return data
            except:
                print("   Não é JSON válido")
        except:
            print(f"   Bytes (hex): {result[:100].hex()}...")
    else:
        print("   Falha na decriptação")
    
    # Tentar variações
    print("\n5. Tentando variações...")
    
    # Variação 1: Hash com #
    print("\n   Variação 1: Hash com #")
    result = decrypt_megaembed(encrypted_hex, "#" + video_id)
    if result:
        try:
            text = result.decode('utf-8', errors='ignore')
            if '{' in text:
                print(f"   Possível JSON: {text[:200]}...")
        except:
            pass
    
    # Variação 2: Diferentes índices para o hash
    for idx in range(6):
        print(f"\n   Variação 2.{idx}: Índice {idx} do hash")
        key = generate_key_variant(video_id, idx)
        iv = generate_iv()
        
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(hex_to_bytes(encrypted_hex))
            text = decrypted.decode('utf-8', errors='ignore')
            if '{' in text and '"' in text:
                print(f"   Possível resultado: {text[:200]}...")
        except:
            pass
    
    return None

def generate_key_variant(video_hash, hash_index):
    """Variação da geração de chave com diferentes índices"""
    k = "10"
    O = 110
    j = 1
    
    N = ""
    
    special_char = "ᵟ"
    B = list(str(char_code_at(special_char)))
    
    for digit in B:
        N += from_char_code(int(k + digit))
    
    # Usar índice diferente
    if hash_index < len(video_hash):
        hash_char_code = char_code_at(video_hash, hash_index)
    else:
        hash_char_code = char_code_at(video_hash, 0)
    N += from_char_code(hash_char_code)
    
    N += N[1:3]
    N += from_char_code(O, O-1, O+7)
    
    oe = list("3579")
    N += from_char_code(int(oe[3] + oe[2]), int(oe[1] + oe[2]))
    N += from_char_code(int(oe[0])*j + j + int(oe[3]), int(oe[0])*j + j + int(oe[3]))
    
    reversed_oe = oe[::-1]
    N += from_char_code(
        int(oe[3]) * int(k) + int(oe[3]) * j,
        int("".join(reversed_oe[:2]))
    )
    
    key_bytes = N.encode('utf-8')
    
    if len(key_bytes) < 16:
        key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
    elif len(key_bytes) > 16:
        key_bytes = key_bytes[:16]
    
    return key_bytes

if __name__ == "__main__":
    test_decryption()
