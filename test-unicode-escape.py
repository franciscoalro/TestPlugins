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
    decoded = base64.b64decode(datas)
    
    # O conteudo parece ter escapes unicode tipo \u0000
    # Vamos tentar decodificar como se fosse uma string JSON escaped
    text = decoded.decode('latin-1')
    
    print('=== TENTANDO DECODIFICAR ESCAPES ===')
    
    # Tentar processar escapes unicode manualmente
    # Substituir \uXXXX pela representacao correta
    import codecs
    
    # O texto parece ter escapes duplos, vamos tentar decodificar
    # Primeiro, vamos ver o raw
    print('Raw (primeiros 300 chars):')
    print(repr(text[:300]))
    
    # Tentar decodificar escapes unicode
    try:
        # Usar codec unicode_escape
        decoded_escapes = codecs.decode(text, 'unicode_escape')
        print(f'\n[unicode_escape] OK! Tamanho: {len(decoded_escapes)}')
        print(f'Primeiros 300 chars: {decoded_escapes[:300]}')
    except Exception as e:
        print(f'[unicode_escape] Falha: {e}')
    
    # Tentar substituir manualmente
    def unescape(s):
        # Substituir \uXXXX
        def replace_unicode(match):
            code = int(match.group(1), 16)
            try:
                return chr(code)
            except:
                return match.group(0)
        
        s = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, s)
        return s
    
    try:
        unescaped = unescape(text)
        print(f'\n[manual unescape] OK! Tamanho: {len(unescaped)}')
        print(f'Primeiros 300 chars: {repr(unescaped[:300])}')
        
        # Tentar parse como JSON
        try:
            config = json.loads(unescaped)
            print('\n[OK] JSON parseado!')
            print(json.dumps(config, indent=2, ensure_ascii=False)[:2000])
        except Exception as e:
            print(f'JSON parse falhou: {e}')
    except Exception as e:
        print(f'Manual unescape falhou: {e}')
    
    # Tentar outra abordagem - ver se o conteudo depois de media e base64
    print('\n=== ANALISE DO CAMPO MEDIA ===')
    media_start = text.find('"media":"') + 9
    rest = text[media_start:]
    
    # Encontrar o fim do campo media (procurar por "," ou "}")
    # Mas precisamos ignorar escapes
    end_pos = -1
    i = 0
    while i < len(rest):
        if rest[i] == '"' and (i == 0 or rest[i-1] != '\\'):
            # Verificar se e o fim do campo
            if i+1 < len(rest) and rest[i+1] in [',', '}']:
                end_pos = i
                break
        i += 1
    
    if end_pos > 0:
        media_content = rest[:end_pos]
        print(f'Media content length: {len(media_content)}')
        print(f'Media content (primeiros 200): {repr(media_content[:200])}')
        
        # Tentar decodificar escapes
        try:
            unescaped_media = unescape(media_content)
            print(f'\nMedia unescaped (primeiros 200): {repr(unescaped_media[:200])}')
            
            # Tentar base64
            try:
                b64_decoded = base64.b64decode(unescaped_media)
                print(f'\nBase64 decode OK! Tamanho: {len(b64_decoded)}')
                print(f'Conteudo: {repr(b64_decoded[:200])}')
            except Exception as e:
                print(f'Base64 falhou: {e}')
        except Exception as e:
            print(f'Unescape falhou: {e}')
