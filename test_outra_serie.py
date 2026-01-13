import requests
import re
import time

print("="*60)
print("TESTE COM OUTRA SERIE")
print("="*60)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

# Buscar uma serie diferente na pagina principal
print("\n[1] Buscando series disponiveis...")
r = requests.get("https://www.maxseries.one/series", headers=HEADERS, timeout=15)

# Extrair links de series
series_links = re.findall(r'href="(https://www\.maxseries\.one/series/[^"]+)"', r.text)
series_links = list(set(series_links))[:10]  # Pegar 10 unicas

print(f"  Series encontradas: {len(series_links)}")
for s in series_links[:5]:
    print(f"    - {s.split('/')[-1]}")

# Testar uma serie diferente de Terra de Pecados
test_series = None
for link in series_links:
    if "terra-de-pecados" not in link and "garota-sequestrada" not in link:
        test_series = link
        break

if not test_series:
    test_series = series_links[0]

print(f"\n[2] Testando: {test_series}")
r = requests.get(test_series, headers=HEADERS, timeout=15)

# Extrair playerthree
iframe = re.search(r'playerthree\.online/embed/([^/"]+)', r.text)
if not iframe:
    print("  ERRO: Playerthree nao encontrado")
    exit(1)

slug = iframe.group(1)
pt_url = f"https://playerthree.online/embed/{slug}/"
print(f"  Playerthree: {pt_url}")

# Buscar episodios
print("\n[3] Buscando episodios...")
r = requests.get(pt_url, headers={**HEADERS, "Referer": test_series}, timeout=15)
episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
print(f"  Episodios: {episodes[:5]}")

if not episodes:
    print("  ERRO: Nenhum episodio encontrado")
    exit(1)

# AJAX do episodio
print(f"\n[4] AJAX episodio {episodes[0]}...")
r = requests.get(
    f"https://playerthree.online/episodio/{episodes[0]}",
    headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"},
    timeout=15
)
sources = re.findall(r'data-source="([^"]+)"', r.text)
print(f"  Sources: {sources}")

# Pegar megaembed
megaembed = [s for s in sources if "megaembed" in s]
if not megaembed:
    print("  AVISO: MegaEmbed nao encontrado, tentando playerembed...")
    exit(0)

megaembed_url = megaembed[0]
video_id = re.search(r'#([a-zA-Z0-9]+)$', megaembed_url)
if not video_id:
    video_id = re.search(r'/([a-zA-Z0-9]+)/?$', megaembed_url)

if not video_id:
    print("  ERRO: VideoId nao extraido")
    exit(1)

video_id = video_id.group(1)
print(f"\n[5] VideoId: {video_id}")

# Testar CDNs
print("\n[6] Testando CDNs...")
cdns = ["sipt.marvellaholdings.sbs", "stzm.marvellaholdings.sbs", "srcf.marvellaholdings.sbs"]
shards = ["x6b", "x7c", "x8d", "x9e"]
ts = int(time.time())

found = False
for cdn in cdns:
    if found:
        break
    for shard in shards:
        url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
        try:
            r = requests.get(url, headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=5)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                print(f"\n  ENCONTRADO!")
                print(f"  URL: {url}")
                print(f"  CDN: {cdn}")
                print(f"  Shard: {shard}")
                print(f"\n  M3U8 Content:")
                print(r.text)
                found = True
                break
        except:
            pass

if not found:
    print("  Nenhum CDN direto funcionou para este video")
    print("  (Pode precisar de WebView ou CDN diferente)")

print("\n" + "="*60)
print("TESTE CONCLUIDO")
print("="*60)
