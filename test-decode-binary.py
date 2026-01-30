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
    
    # Decodificar base64
    decoded = base64.b64decode(datas)
    print(f'[OK] Decodificado! Tamanho: {len(decoded)} bytes')
    print(f'Primeiros 100 bytes (hex): {decoded[:100].hex()}')
    
    # Tentar detectar se e JSON com alguma codificacao
    print(f'\nPrimeiros 200 bytes como repr: {repr(decoded[:200])}')
    
    # Tentar diferentes codificacoes
    for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            text = decoded.decode(enc)
            print(f'\n[{enc}] Decodificacao OK')
            print(f'  Primeiros 500 chars: {text[:500]}')
            
            # Tentar parse como JSON
            try:
                config = json.loads(text)
                print(f'  [OK] JSON valido!')
                break
            except:
                pass
        except Exception as e:
            print(f'[{enc}] Falha: {e}')
    
    # Tentar encontrar URLs nos bytes
    print('\n=== PROCURANDO PADROES NOS BYTES ===')
    text_latin = decoded.decode('latin-1')
    
    # Procurar por https
    https = re.findall(r'https?://[^\s"<>\x00-\x1f]+', text_latin)
    print(f'URLs https: {len(https)}')
    for h in https[:10]:
        print(f'  {h}')
    
    # Procurar por .mp4 ou .m3u8
    mp4s = re.findall(r'[^\s"<>\x00-\x1f]*\.mp4[^\s"<>\x00-\x1f]*', text_latin, re.IGNORECASE)
    print(f'Referencias .mp4: {len(mp4s)}')
    for m in mp4s[:5]:
        print(f'  {m}')
    
    m3u8s = re.findall(r'[^\s"<>\x00-\x1f]*\.m3u8[^\s"<>\x00-\x1f]*', text_latin, re.IGNORECASE)
    print(f'Referencias .m3u8: {len(m3u8s)}')
    
    # Ver se tem "slug" ou outras chaves conhecidas
    if '"slug"' in text_latin:
        print('\n[OK] Encontrada chave "slug" no conteudo')
    if '"file"' in text_latin:
        print('[OK] Encontrada chave "file" no conteudo')
    if '"media"' in text_latin:
        print('[OK] Encontrada chave "media" no conteudo')
        
    # Tentar extrair o JSON de qualquer forma
    json_match = re.search(r'({.+})', text_latin, re.DOTALL)
    if json_match:
        try:
            possible_json = json_match.group(1)
            config = json.loads(possible_json)
            print('\n[OK] JSON extraido e parseado!')
            print(json.dumps(config, indent=2, ensure_ascii=False)[:2000])
        except Exception as e:
            print(f'\nTentativa de parse JSON falhou: {e}')
