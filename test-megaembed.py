import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

# Testar MegaEmbed
megaembed_url = 'https://megaembed.link/#3wnuij'
video_id = '3wnuij'

# 1. Testar API
api_url = f'https://megaembed.link/api/v1/info?id={video_id}'
print(f'Testando API: {api_url}')

r = requests.get(api_url, headers={
    **headers,
    'Referer': megaembed_url,
    'Accept': 'application/json',
    'Origin': 'https://megaembed.link'
}, timeout=15)

print(f'Status: {r.status_code}')
print(f'Response: {r.text[:1000]}')

# 2. Testar página HTML
print(f'\n--- Testando HTML ---')
r2 = requests.get(megaembed_url, headers=headers, timeout=15)
print(f'Status HTML: {r2.status_code}')

# Procurar video URLs
patterns = [
    r'file:\s*["\']([^"\']+)["\']',
    r'source:\s*["\']([^"\']+)["\']',
    r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
    r'(https?://[^"\'<>\s]+\.mp4[^"\'<>\s]*)',
]
for p in patterns:
    matches = re.findall(p, r2.text, re.IGNORECASE)
    if matches:
        print(f'{p[:30]}...: {matches[:2]}')
