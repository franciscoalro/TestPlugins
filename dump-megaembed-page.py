#!/usr/bin/env python3
"""
Dump completo da página megaembed para análise
"""

import requests

url = "https://megaembed.link/#xez5rx"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Referer': 'https://playerthree.online/',
}

response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"\n{'='*80}\nHTML COMPLETO:\n{'='*80}\n")
print(response.text)

# Salvar
with open('megaembed_page_dump.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"\n{'='*80}\n✅ Salvo em megaembed_page_dump.html\n{'='*80}")
