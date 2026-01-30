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

# Salvar HTML completo
with open('playerembedapi_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('HTML salvo em playerembedapi_full.html')

# Procurar pela parte final do script onde o video e carregado
# O HTML foi truncado, vamos ver o final
print('\n=== ULTIMOS 2000 CARACTERES DO HTML ===')
print(html[-2000:])

# Procurar por loadScript ou fetch de API
print('\n=== PROCURANDO API CALLS ===')
api_calls = re.findall(r'loadScript\(["\']([^"\']+)["\']\)', html)
print(f'loadScript calls: {api_calls}')

# Procurar por fetch completo
fetch_full = re.findall(r'fetch\(["\']([^"\']+)["\'][^)]*\)', html, re.DOTALL)
print(f'Fetch calls: {fetch_full}')

# Procurar por qualquer URL que pareca ser de API
api_url = re.findall(r'["\'](https?://[^"\']*api[^"\']*)["\']', html, re.IGNORECASE)
print(f'API URLs: {api_url}')

# Procurar por iamcdn
iamcdn = re.findall(r'iamcdn[^"\']*["\']([^"\']+)["\']', html)
print(f'iamcdn refs: {iamcdn}')

# Procurar pelo ID do video sendo usado
id_refs = re.findall(r'(id[:=]["\']?\d+)', html)
print(f'ID refs: {id_refs}')
