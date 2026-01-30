#!/usr/bin/env python3
import requests
import re

url = 'https://playerembedapi.link/?v=4PHWs34H0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Referer': 'https://playerthree.online'
}

response = requests.get(url, headers=headers, timeout=15)
html = response.text

print('=== ANALISE COMPLETA DO HTML ===')
print(f'Tamanho: {len(html)} chars')
print()

# Procurar por 'eval' ou ofuscacao
if 'eval(' in html.lower():
    print('[!] Codigo usa eval() - possivelmente ofuscado')

# Procurar todas as URLs https
urls = re.findall(r'https?://[^"<>\s\'\)]+', html)
print(f'\nTotal de URLs encontradas: {len(urls)}')
for u in urls[:20]:
    print(f'  {u[:100]}')

# Procurar por iframe
iframes = re.findall(r'<iframe[^>]+>', html, re.IGNORECASE)
print(f'\nIframes: {len(iframes)}')
for f in iframes[:5]:
    print(f'  {f}')

# Procurar por json embed
embeds = re.findall(r'embed[^{]*{[^}]+}', html, re.IGNORECASE)
print(f'\nPossiveis embeds: {len(embeds)}')

# Procurar por 'src' em qualquer lugar
srcs = re.findall(r'src[=:]["\']([^"\']+)["\']', html, re.IGNORECASE)
print(f'\nAtributos src: {len(srcs)}')
for s in srcs[:10]:
    print(f'  {s}')

# Procurar variaveis de video no JavaScript
video_vars = re.findall(r'(var|let|const)\s+(video|url|src|file|stream)[^=]*=\s*["\']([^"\']+)["\']', html, re.IGNORECASE)
print(f'\nVariaveis de video: {len(video_vars)}')
for v in video_vars[:10]:
    print(f'  {v}')

# Mostrar trechos do HTML que podem ter video
print('\n=== TRECHOS DO HTML ===')
lines = html.split('\n')
for i, line in enumerate(lines):
    if 'video' in line.lower() or 'src=' in line.lower() or 'source' in line.lower():
        print(f'Linha {i}: {line[:150]}')
        if i > 50:
            break
