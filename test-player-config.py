#!/usr/bin/env python3
import requests
import re
import json

url = 'https://playerembedapi.link/?v=4PHWs34H0'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
    'Referer': 'https://playerthree.online'
}

response = requests.get(url, headers=headers, timeout=15)
html = response.text

print('=== PROCURANDO CONFIGURACOES DO PLAYER ===')

# Procurar por JSON embutido no HTML
json_pattern = re.findall(r'<script[^>]*>.*?({[^<]+"file"[^}]+}).*?</script>', html, re.DOTALL | re.IGNORECASE)
print(f'\nJSONs com "file": {len(json_pattern)}')

# Procurar por setup do jwplayer
jw_setup = re.findall(r'jwplayer\(["\'][^"\']*["\']\)\.setup\(([^)]+)\)', html, re.DOTALL | re.IGNORECASE)
print(f'\nSetup JWPlayer: {len(jw_setup)}')
for s in jw_setup[:3]:
    print(f'  {s[:500]}')

# Procurar por playerInstance
player_instance = re.findall(r'playerInstance[^=]*=\s*([^;]+)', html, re.IGNORECASE)
print(f'\nPlayerInstance: {len(player_instance)}')

# Procurar por config ou options
config = re.findall(r'(config|options|setup)\s*[=:]\s*({[^}]+})', html, re.IGNORECASE)
print(f'\nConfigs/Options: {len(config)}')
for c in config[:5]:
    print(f'  {c}')

# Procurar por data-* attributes
data_attrs = re.findall(r'data-[a-z-]+=["\']([^"\']+)["\']', html, re.IGNORECASE)
print(f'\nData attributes: {len(data_attrs)}')
for d in data_attrs[:10]:
    print(f'  {d}')

# Procurar por id ou hash do video
video_id = re.findall(r'[?&]v=([a-zA-Z0-9]+)', url)
if video_id:
    vid = video_id[0]
    print(f'\nVideo ID: {vid}')
    # Procurar por este ID no HTML
    if vid in html:
        print(f'  [OK] ID encontrado no HTML')
        # Mostrar contexto
        idx = html.find(vid)
        print(f'  Contexto: ...{html[max(0,idx-50):idx+len(vid)+50]}...')

# Procurar por window.variaveis
window_vars = re.findall(r'window\.([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;\n]+)', html)
print(f'\nWindow variables: {len(window_vars)}')
for v in window_vars[:15]:
    name, val = v
    if any(x in val.lower() for x in ['url', 'src', 'file', 'video', 'stream', 'http']):
        print(f'  window.{name} = {val[:100]}')

# Procurar por fetch ou XMLHttpRequest
fetch_calls = re.findall(r'fetch\(["\']([^"\']+)["\']', html, re.IGNORECASE)
print(f'\nFetch calls: {len(fetch_calls)}')
for f in fetch_calls[:5]:
    print(f'  {f}')

# Procurar por API endpoints
api_patterns = re.findall(r'["\']([^"\']*api[^"\']*)["\']', html, re.IGNORECASE)
print(f'\nAPI endpoints: {len(api_patterns)}')
for a in api_patterns[:10]:
    print(f'  {a}')

# Procurar por embed ou iframe src dinamico
iframe_src = re.findall(r'iframe.*src.*=.*["\']([^"\']+)["\']', html, re.IGNORECASE)
print(f'\nIframe src dinamicos: {len(iframe_src)}')
for i in iframe_src[:5]:
    print(f'  {i}')

# Mostrar todo o HTML se for pequeno
if len(html) < 15000:
    print('\n=== HTML COMPLETO ===')
    # Formatando para melhor leitura
    html_formatted = html.replace('><', '>\n<')
    print(html_formatted[:3000])
    if len(html) > 3000:
        print('\n... (truncado)')
