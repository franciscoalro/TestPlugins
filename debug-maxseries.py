#!/usr/bin/env python3
import requests
import re

url = "https://www.maxseries.one/series/assistir-terra-de-pecados-online"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

resp = requests.get(url, headers=headers)
print(f"Status: {resp.status_code}")
print(f"URL final: {resp.url}")

# Salvar HTML
with open("maxseries_debug.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

# Procurar links
patterns = [
    (r'href="([^"]*episodio[^"]*)"', "episodio"),
    (r'href="([^"]*episode[^"]*)"', "episode"),
    (r'data-post="(\d+)"', "data-post"),
    (r'class="[^"]*episode[^"]*"', "episode class"),
]

for pattern, name in patterns:
    matches = re.findall(pattern, resp.text, re.IGNORECASE)
    if matches:
        print(f"\n[{name}]: {matches[:5]}")
