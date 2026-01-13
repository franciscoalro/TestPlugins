import requests
import re
import time

print("="*60)
print("TESTE COMPLETO - SERIE NOVA (SEM AJUDA)")
print("="*60)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

# CDNs conhecidos
CDNS = [
    "sqtd.luminairemotion.online",
    "stzm.luminairemotion.online",
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs",
]
SHARDS = ["is3", "x6b", "x7c", "x8d", "x9e"]

# 1. Buscar uma serie aleatoria
print("\n[1] Buscando serie na pagina principal...")
r = requests.get("https://www.maxseries.one/series", headers=HEADERS, timeout=15)
series = list(set(re.findall(r'href="(https://www\.maxseries\.one/series/assistir-[^"]+)"', r.text)))

# Escolher uma que nao seja as ja testadas
for s in series:
    if "terra-de-pecados" not in s and "homem-x-bebe" not in s and "man-vs-baby" not in s:
        serie_url = s
        break

serie_nome = serie_url.split("/")[-1].replace("assistir-", "").replace("-online", "")
print(f"    Serie escolhida: {serie_nome}")
print(f"    URL: {serie_url}")

# 2. Carregar pagina da serie
print("\n[2] Carregando pagina da serie...")
r = requests.get(serie_url, headers=HEADERS, timeout=15)
print(f"    Status: {r.status_code}")

# 3. Extrair iframe playerthree
print("\n[3] Extraindo iframe playerthree...")
iframe = re.search(r'playerthree\.online/embed/([^/"]+)', r.text)
if not iframe:
    print("    ERRO: Playerthree nao encontrado!")
    exit(1)

slug = iframe.group(1)
pt_url = f"https://playerthree.online/embed/{slug}/"
print(f"    Slug: {slug}")
print(f"    URL: {pt_url}")

# 4. Buscar episodios
print("\n[4] Buscando episodios...")
r = requests.get(pt_url, headers={**HEADERS, "Referer": serie_url}, timeout=15)
episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
print(f"    Episodios encontrados: {len(episodes)}")
if episodes:
    print(f"    Primeiro: {episodes[0]}")

if not episodes:
    print("    ERRO: Nenhum episodio!")
    exit(1)

# 5. AJAX do episodio
print("\n[5] Fazendo AJAX do episodio...")
r = requests.get(
    f"https://playerthree.online/episodio/{episodes[0]}",
    headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"},
    timeout=15
)
sources = re.findall(r'data-source="([^"]+)"', r.text)
print(f"    Sources: {len(sources)}")
for s in sources:
    print(f"      - {s}")

# 6. Extrair videoId do MegaEmbed
megaembed = [s for s in sources if "megaembed" in s]
if not megaembed:
    print("\n    AVISO: Sem MegaEmbed, tentando PlayerEmbed...")
    playerembed = [s for s in sources if "playerembed" in s]
    if playerembed:
        print(f"    PlayerEmbed: {playerembed[0]}")
    exit(0)

print(f"\n[6] Extraindo videoId...")
megaembed_url = megaembed[0]
vid_match = re.search(r'#([a-zA-Z0-9]+)$', megaembed_url)
if not vid_match:
    vid_match = re.search(r'/([a-zA-Z0-9]+)/?$', megaembed_url)

if not vid_match:
    print("    ERRO: VideoId nao extraido!")
    exit(1)

video_id = vid_match.group(1)
print(f"    VideoId: {video_id}")

# 7. Testar CDNs
print("\n[7] Testando CDNs...")
ts = int(time.time())
found = False

for cdn in CDNS:
    if found:
        break
    for shard in SHARDS:
        url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
        try:
            r = requests.get(url, headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=5)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                print(f"\n    ✅ ENCONTRADO!")
                print(f"    CDN: {cdn}")
                print(f"    Shard: {shard}")
                print(f"    URL: {url}")
                print(f"\n    M3U8 Content:")
                print(r.text)
                found = True
                break
        except:
            pass

if not found:
    print("    ❌ Nenhum CDN funcionou")
    print("    Pode precisar de WebView ou CDN novo")

# Resumo
print("\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"Serie: {serie_nome}")
print(f"VideoId: {video_id}")
print(f"M3U8 encontrado: {'SIM' if found else 'NAO'}")
print("="*60)
