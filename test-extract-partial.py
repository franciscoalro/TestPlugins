#!/usr/bin/env python3
import requests
import re
import base64

url = 'https://playerembedapi.link/?v=4PHWs34H0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Referer': 'https://playerthree.online'
}

response = requests.get(url, headers=headers, timeout=15)
html = response.text

# Extrair a string datas
match = re.search(r'const\s+datas\s*=\s*"([^"]+)"', html)
if match:
    datas = match.group(1)
    decoded = base64.b64decode(datas)
    
    # Decodificar como latin-1 para visualizacao
    text = decoded.decode('latin-1')
    
    print('=== ESTRUTURA DO JSON ===')
    # O JSON comeca corretamente, vamos ver ate onde e valido
    # Encontrar a posicao onde o "media" comeca
    media_start = text.find('"media":"')
    if media_start > 0:
        print(f'Campo "media" comeca na posicao: {media_start}')
        print(f'JSON antes do media:')
        print(text[:media_start+9])  # +9 para incluir "media":"
        
        # Ver o que vem depois do media
        rest = text[media_start+9:]
        print(f'\nConteudo de "media" (primeiros 200 bytes):')
        print(repr(rest[:200]))
        
        # Tentar encontrar onde o JSON termina (procurar por "," ou "}" apos os dados binarios)
        # Procurar por padroes que indicam fim do campo media
        end_patterns = ['","', '"}', '","config"', '"}']
        for pattern in end_patterns:
            pos = rest.find(pattern)
            if pos > 0:
                print(f'\nPossivel fim do campo "media" na posicao {pos}: {repr(pattern)}')
                print(f'Resto do JSON: {rest[pos:200]}')
                break
    
    # Verificar a estrutura completa
    print('\n=== ANALISE DE ESTRUTURA ===')
    print(f'Tamanho total: {len(decoded)} bytes')
    
    # Tentar identificar se e XOR ou outro tipo de criptografia simples
    # Verificar os primeiros bytes do campo media
    media_bytes = decoded[media_start+9:]
    print(f'\nPrimeiros 50 bytes do campo media (hex): {media_bytes[:50].hex()}')
    print(f'Primeiros 50 bytes do campo media (repr): {repr(media_bytes[:50])}')
    
    # Tentar XOR com valores comuns
    print('\n=== TENTATIVAS DE DECODIFICACAO ===')
    
    # Tentar XOR com 0x95 (primeiro byte)
    key = media_bytes[0]
    xor_result = bytes([b ^ key for b in media_bytes[:100]])
    print(f'XOR com 0x{key:02x}: {repr(xor_result)}')
    
    # Tentar ver se e base64 dentro do campo
    try:
        b64_decoded = base64.b64decode(media_bytes[:100])
        print(f'Base64 decode: {repr(b64_decoded[:50])}')
    except:
        print('Nao e base64 valido')
    
    # Verificar se o id do usuario ou md5 sao usados como chave
    print(f'\nuser_id: 482120')
    print(f'md5_id: 28975276')
    print(f'slug: 4PHWs34H0')
