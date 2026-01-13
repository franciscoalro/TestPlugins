import requests
import re
import json

video_id = "mhfakh"
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}

print(f"Tentando descobrir CDN para videoId: {video_id}")
print("="*60)

# 1. Testar API info
print("\n[1] API /info...")
r = requests.get(f"https://megaembed.link/api/v1/info?id={video_id}", 
                 headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=15)
print(f"    Status: {r.status_code}")
print(f"    Response: {r.text[:300]}")

# 2. Testar API video
print("\n[2] API /video...")
r = requests.get(f"https://megaembed.link/api/v1/video?id={video_id}&w=1920&h=1080&r=playerthree.online",
                 headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=15)
print(f"    Status: {r.status_code}")
print(f"    Response: {r.text[:300]}")

# Se a resposta parece ser um token, tentar API player
if r.status_code == 200 and len(r.text) > 50:
    token = r.text.strip()
    print(f"\n[3] API /player com token...")
    r2 = requests.get(f"https://megaembed.link/api/v1/player?t={token}",
                      headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=15)
    print(f"    Status: {r2.status_code}")
    print(f"    Response: {r2.text[:500]}")
    
    # Procurar URLs no response
    urls = re.findall(r'https?://[^\s"\'<>]+', r2.text)
    if urls:
        print(f"\n    URLs encontradas:")
        for u in urls[:5]:
            print(f"      - {u}")

# 3. Carregar pagina do megaembed e procurar CDN no HTML/JS
print("\n[4] Carregando pagina do MegaEmbed...")
r = requests.get(f"https://megaembed.link/#{video_id}",
                 headers={**HEADERS, "Referer": "https://playerthree.online/"}, timeout=15)
print(f"    Status: {r.status_code}")

# Procurar dominios de CDN no HTML
cdn_patterns = [
    r'https?://([a-z0-9]+\.luminairemotion\.online)',
    r'https?://([a-z0-9]+\.marvellaholdings\.sbs)',
    r'https?://([a-z0-9]+\.[a-z]+\.online)/v4/',
    r'https?://([a-z0-9]+\.[a-z]+\.sbs)/v4/',
]

print("\n    Procurando CDNs no HTML...")
for pattern in cdn_patterns:
    matches = re.findall(pattern, r.text)
    if matches:
        print(f"    Encontrado: {set(matches)}")

# Procurar em scripts externos
scripts = re.findall(r'src="([^"]+\.js[^"]*)"', r.text)
print(f"\n    Scripts encontrados: {len(scripts)}")
for s in scripts[:5]:
    print(f"      - {s}")
