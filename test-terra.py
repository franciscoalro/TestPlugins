import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}

# 1. Pegar página da série
url = 'https://www.maxseries.one/series/terra-de-pecados/'
r = requests.get(url, headers=headers, timeout=15)
print('Status serie:', r.status_code)

# Procurar iframe
iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', r.text)
if iframe_match:
    iframe_url = iframe_match.group(1)
    print('Iframe URL:', iframe_url)
    
    # 2. Acessar o iframe (playerthree)
    if 'playerthree' in iframe_url:
        r2 = requests.get(iframe_url, headers={**headers, 'Referer': url}, timeout=15)
        print('Status playerthree:', r2.status_code)
        print('HTML playerthree (primeiros 2000 chars):')
        print(r2.text[:2000])
        print('\n--- Procurando patterns ---')
        
        # Procurar qualquer coisa com episodio/ep/data
        patterns = [
            r'data-ep=["\']([^"\']+)["\']',
            r'episodio/(\d+)',
            r'ep["\']:\s*["\']?(\d+)',
            r'#\d+_(\d+)',
            r'gleam\.config',
            r'sources?\s*[:=]',
        ]
        for p in patterns:
            matches = re.findall(p, r2.text, re.IGNORECASE)
            if matches:
                print(f'{p}: {matches[:5]}')
else:
    print('Iframe nao encontrado')
