import requests
import time

video_id = "mhfakh"
ts = int(time.time())
HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0", "Referer": "https://megaembed.link/"}

# CDNs mais provaveis baseados nos padroes descobertos
cdns = [
    "sqtd.luminairemotion.online",
    "stzm.luminairemotion.online", 
    "srcf.luminairemotion.online",
    "sipt.luminairemotion.online",
    "sqtd.marvellaholdings.sbs",
    "sipt.marvellaholdings.sbs",
]

shards = ["is3", "x6b", "is1", "is2"]

print(f"Teste rapido - VideoId: {video_id}")

for cdn in cdns:
    for shard in shards:
        url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
        try:
            r = requests.get(url, headers=HEADERS, timeout=3)
            if r.status_code == 200:
                print(f"200: {cdn}/{shard}")
                if "#EXTM3U" in r.text:
                    print(f"  -> M3U8 VALIDO!")
                    print(r.text[:200])
        except Exception as e:
            pass

print("\nConcluido")
