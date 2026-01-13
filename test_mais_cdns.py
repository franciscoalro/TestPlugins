import requests
import time
import itertools

video_id = "mhfakh"
ts = int(time.time())
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0", "Referer": "https://megaembed.link/"}

# Lista expandida de CDNs possiveis
cdn_prefixes = ["sqtd", "stzm", "srcf", "sbi6", "s6p9", "sipt", "s1", "s2", "s3", "cdn", "cdn1", "cdn2", "vod", "stream"]
cdn_domains = ["luminairemotion.online", "marvellaholdings.sbs"]

# Gerar todas combinacoes
cdns = [f"{p}.{d}" for p, d in itertools.product(cdn_prefixes, cdn_domains)]

# Shards expandidos
shards = ["is3", "x6b", "x7c", "x8d", "x9e", "xa1", "xb2", "is1", "is2", "is4"]

print(f"Testando {len(cdns)} CDNs x {len(shards)} shards = {len(cdns)*len(shards)} combinacoes")
print(f"VideoId: {video_id}")
print(f"Timestamp: {ts}")
print()

found = False
tested = 0

for cdn in cdns:
    if found:
        break
    for shard in shards:
        tested += 1
        url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
        try:
            r = requests.get(url, headers=HEADERS, timeout=3)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                print(f"\n✅ ENCONTRADO apos {tested} tentativas!")
                print(f"CDN: {cdn}")
                print(f"Shard: {shard}")
                print(f"URL: {url}")
                print(f"\nM3U8:")
                print(r.text)
                found = True
                break
        except:
            pass

if not found:
    print(f"\n❌ Nenhuma das {tested} combinacoes funcionou")
    print("Este video provavelmente usa um CDN diferente")
    print("que so pode ser descoberto via WebView/JavaScript")
