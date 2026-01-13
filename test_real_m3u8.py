import requests
import time

video_id = '3wnuij'
ts = int(time.time())
url = f'https://sipt.marvellaholdings.sbs/v4/x6b/{video_id}/cf-master.{ts}.txt'

print(f'URL: {url}')
print(f'Timestamp: {ts}')
print()

r = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
    'Referer': 'https://megaembed.link/'
}, timeout=10)

print(f'Status: {r.status_code}')
print()
print('CONTEUDO:')
print(r.text)
