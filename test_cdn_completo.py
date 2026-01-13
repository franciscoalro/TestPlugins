import requests
import time

video_id = "ujxl1l"  # Homem X Bebe
ts = int(time.time())

HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0", "Referer": "https://megaembed.link/"}

# Lista completa de CDNs possiveis
cdns = [
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs", 
    "srcf.marvellaholdings.sbs",
    "sbi6.marvellaholdings.sbs",
    "s6p9.marvellaholdings.sbs",
    # Novos possiveis
    "s1.marvellaholdings.sbs",
    "s2.marvellaholdings.sbs",
    "s3.marvellaholdings.sbs",
    "cdn1.marvellaholdings.sbs",
    "cdn2.marvellaholdings.sbs",
]

# Lista completa de shards
shards = ["x6b", "x7c", "x8d", "x9e", "xa1", "xb2", "xc3", "xd4", "xe5", "xf6"]

print(f"Testando video: {video_id}")
print(f"Timestamp: {ts}")
print(f"CDNs: {len(cdns)}")
print(f"Shards: {len(shards)}")
print(f"Total combinacoes: {len(cdns) * len(shards)}")
print()

found = False
for cdn in cdns:
    if found:
        break
    for shard in shards:
        url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
        try:
            r = requests.get(url, headers=HEADERS, timeout=3)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                print(f"ENCONTRADO: {cdn} / {shard}")
                print(f"URL: {url}")
                print(r.text[:300])
                found = True
                break
            elif r.status_code == 200:
                print(f"200 mas sem M3U8: {cdn}/{shard}")
        except Exception as e:
            pass

if not found:
    print("\nNenhuma combinacao funcionou.")
    print("Este video pode usar CDN diferente ou precisar de WebView.")
