import requests
import re

print("="*60)
print("TESTE MAXSERIES v59")
print("="*60)

HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) Chrome/120.0.0.0"}

# Teste 1
print("\n[TESTE 1] Pagina principal...")
r = requests.get("https://www.maxseries.one/series", headers=HEADERS, timeout=15)
items = re.findall(r'<article[^>]*class="[^"]*item', r.text)
print(f"  Status: {r.status_code}")
print(f"  Items: {len(items)}")

# Teste 2
print("\n[TESTE 2] Pagina de serie...")
r = requests.get("https://www.maxseries.one/series/assistir-terra-de-pecados-online", headers=HEADERS, timeout=15)
iframe = re.search(r'playerthree\.online/embed/[^"]+', r.text)
pt_url = "https://" + iframe.group(0) if iframe else None
print(f"  Status: {r.status_code}")
print(f"  Playerthree: {pt_url}")

if pt_url:
    # Teste 3
    print("\n[TESTE 3] Playerthree...")
    r = requests.get(pt_url, headers={**HEADERS, "Referer": "https://www.maxseries.one/"}, timeout=15)
    episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
    print(f"  Status: {r.status_code}")
    print(f"  Episodios: {episodes[:5]}")
    
    if episodes:
        # Teste 4
        print("\n[TESTE 4] AJAX episodio...")
        ep_url = f"https://playerthree.online/episodio/{episodes[0]}"
        r = requests.get(ep_url, headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"}, timeout=15)
        sources = re.findall(r'data-source="([^"]+)"', r.text)
        print(f"  Status: {r.status_code}")
        print(f"  Sources encontradas: {len(sources)}")
        for s in sources:
            print(f"    - {s}")

print("\n" + "="*60)
print("Se todas etapas OK, o plugin vai funcionar!")
print("="*60)
