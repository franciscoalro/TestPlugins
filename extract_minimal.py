#!/usr/bin/env python3
"""
ULTRA MINIMAL - Extracao em ~250ms
Versao minima para producao (50 linhas)
"""

import requests, re, base64, sys, time

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Accept': 'text/html'}
RE_DATAS = re.compile(r'const\s+datas\s*=\s*"([^"]+)"')
RE_SLUG = re.compile(r'"slug":"([^"]+)"')
RE_MD5 = re.compile(r'"md5_id":(\d+)')

def extract(url):
    start = time.time()
    html = requests.get(url, headers=HEADERS, timeout=5, verify=False).text
    b64 = RE_DATAS.search(html).group(1)
    decoded = base64.b64decode(b64 + '===').decode('utf-8', errors='replace')
    slug = RE_SLUG.search(decoded).group(1)
    md5 = RE_MD5.search(decoded).group(1)
    elapsed = (time.time() - start) * 1000
    return f"https://{slug}.sssrr.org/sora/{md5}/", elapsed

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else "https://playerembedapi.link/?v=rZeP5UzqD"
    print(f"Extraindo: {url}")
    cdn_url, ms = extract(url)
    print(f"CDN URL: {cdn_url}")
    print(f"Tempo: {ms:.2f} ms")
