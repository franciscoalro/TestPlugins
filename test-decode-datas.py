#!/usr/bin/env python3
import requests
import re
import base64
import json

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
    print(f'[OK] String datas encontrada! Tamanho: {len(datas)} chars')
    print(f'Primeiros 100 chars: {datas[:100]}')
    
    # Decodificar base64
    try:
        decoded = base64.b64decode(datas)
        print(f'\n[OK] Decodificado! Tamanho: {len(decoded)} bytes')
        
        # Tentar parse como JSON
        try:
            config = json.loads(decoded)
            print('\n[OK] JSON parseado com sucesso!')
            print('\n=== ESTRUTURA DO JSON ===')
            print(json.dumps(config, indent=2, ensure_ascii=False)[:3000])
            
            # Procurar por URLs de video
            print('\n=== PROCURANDO URLs DE VIDEO ===')
            config_str = json.dumps(config)
            
            # Padroes de URL
            patterns = [
                r'https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                r'https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*',
                r'https?://storage\.googleapis\.com/[^"\'<>\s]+',
            ]
            
            found_urls = []
            for pattern in patterns:
                urls = re.findall(pattern, config_str, re.IGNORECASE)
                for u in urls:
                    if u not in found_urls:
                        found_urls.append(u)
                        print(f'URL: {u}')
            
            # Procurar no dict
            def find_urls(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        new_path = f"{path}.{k}" if path else k
                        if isinstance(v, str) and ('http' in v or '.mp4' in v or '.m3u8' in v):
                            print(f'  {new_path}: {v[:100]}')
                        find_urls(v, new_path)
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        find_urls(v, f"{path}[{i}]")
            
            print('\n=== URLs NA ESTRUTURA ===')
            find_urls(config)
            
        except json.JSONDecodeError as e:
            print(f'[ERRO] Nao e JSON valido: {e}')
            print('Conteudo decodificado (primeiros 2000 chars):')
            print(decoded[:2000])
            
    except Exception as e:
        print(f'[ERRO] Falha ao decodificar base64: {e}')
else:
    print('[ERRO] String datas nao encontrada!')
    # Procurar por outras variaveis
    vars = re.findall(r'const\s+(\w+)\s*=\s*"([^"]{100,})"', html)
    print(f'\nVariaveis grandes encontradas: {len(vars)}')
    for name, val in vars:
        print(f'  {name}: {len(val)} chars')
