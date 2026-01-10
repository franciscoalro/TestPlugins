import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

# Testar AJAX do episodio
ep_id = '255703'  # Primeiro episodio de Terra de Pecados
ajax_url = f'https://playerthree.online/episodio/{ep_id}'

print(f'Testando: {ajax_url}')
r = requests.get(ajax_url, headers={
    **headers, 
    'Referer': 'https://playerthree.online/embed/synden/', 
    'X-Requested-With': 'XMLHttpRequest'
}, timeout=15)

print(f'Status: {r.status_code}')
print(f'Response ({len(r.text)} chars):')
print(r.text[:1500])

# Procurar sources
sources = re.findall(r'data-source=["\']([^"\']+)["\']', r.text)
print(f'\nSources encontradas: {sources}')

# Procurar outros patterns de video
video_patterns = [
    r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
    r'(https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*)',
    r'(https?://megaembed[^"\'<>\s]+)',
    r'(https?://playerembedapi[^"\'<>\s]+)',
    r'(https?://myvidplay[^"\'<>\s]+)',
    r'(https?://dood[^"\'<>\s]+)',
]
for p in video_patterns:
    matches = re.findall(p, r.text, re.IGNORECASE)
    if matches:
        print(f'Pattern {p[:30]}...: {matches[:3]}')
