import requests
import time

video_id = '3wnuij'
ts = int(time.time())
base_url = f'https://sipt.marvellaholdings.sbs/v4/x6b/{video_id}'

# Testar playlist 1080p
playlist_url = f'{base_url}/index-f2-v1-a1.txt'
print(f'Playlist 1080p: {playlist_url}')

r = requests.get(playlist_url, headers={
    'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0',
    'Referer': 'https://megaembed.link/'
}, timeout=10)

print(f'Status: {r.status_code}')
print()

if r.status_code == 200:
    print('PLAYLIST 1080p:')
    print(r.text[:1000])
    
    # Extrair primeiro segmento
    import re
    segments = re.findall(r'(seg-\d+-[^.]+\.ts)', r.text)
    if segments:
        seg_url = f'{base_url}/{segments[0]}'
        print(f'\nPrimeiro segmento: {seg_url}')
        
        # Testar se segmento existe (HEAD request)
        r2 = requests.head(seg_url, headers={
            'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0',
            'Referer': 'https://megaembed.link/'
        }, timeout=10)
        print(f'Segmento status: {r2.status_code}')
        print(f'Content-Type: {r2.headers.get("Content-Type", "N/A")}')
        print(f'Content-Length: {r2.headers.get("Content-Length", "N/A")} bytes')
