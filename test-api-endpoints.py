#!/usr/bin/env python3
import requests
import json

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
REFERER = "https://playerthree.online"

headers = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
    "Referer": REFERER
}

video_id = "4PHWs34H0"

# Testar varios endpoints possiveis
endpoints = [
    f"https://playerembedapi.link/api/video?v={video_id}",
    f"https://playerembedapi.link/api/video?id={video_id}",
    f"https://playerembedapi.link/api/sources?v={video_id}",
    f"https://playerembedapi.link/api/media?v={video_id}",
    f"https://playerembedapi.link/video?v={video_id}",
    f"https://playerembedapi.link/info?v={video_id}",
    f"https://playerembedapi.link/embed?v={video_id}",
    f"https://iamcdn.net/api/video?id={video_id}",
    f"https://abyss.to/api/video?v={video_id}",
]

print('=== TESTANDO ENDPOINTS ===')
for url in endpoints:
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        print(f'\n{url}')
        print(f'  Status: {response.status_code}')
        print(f'  Content-Type: {response.headers.get("Content-Type", "N/A")}')
        print(f'  Tamanho: {len(response.text)}')
        if response.status_code == 200 and len(response.text) > 0:
            # Ver se parece JSON
            if response.text.strip().startswith('{'):
                try:
                    data = response.json()
                    print(f'  [JSON] Keys: {list(data.keys())[:10]}')
                except:
                    print(f'  Conteudo: {response.text[:200]}')
            else:
                print(f'  Conteudo: {response.text[:200]}')
    except Exception as e:
        print(f'{url}')
        print(f'  Erro: {e}')

# Testar tambem POST
print('\n=== TESTANDO POST ===')
post_endpoints = [
    "https://playerembedapi.link/api/video",
    "https://playerembedapi.link/api/sources",
]

for url in post_endpoints:
    try:
        response = requests.post(url, headers=headers, json={"v": video_id}, timeout=10)
        print(f'\nPOST {url}')
        print(f'  Status: {response.status_code}')
        print(f'  Resposta: {response.text[:300]}')
    except Exception as e:
        print(f'POST {url}')
        print(f'  Erro: {e}')
