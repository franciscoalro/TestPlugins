import requests
import time

# Dados da captura do usuario
video_id = "ujxl1l"
ts = int(time.time())

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0",
    "Referer": "https://megaembed.link/"
}

# CDN e shard da captura
cdn = "sqtd.luminairemotion.online"
shard = "is3"

url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"

print(f"Testando URL baseada na captura:")
print(f"URL: {url}")
print()

r = requests.get(url, headers=HEADERS, timeout=15)
print(f"Status: {r.status_code}")

if r.status_code == 200 and "#EXTM3U" in r.text:
    print("\n✅ FUNCIONA!")
    print("\nM3U8:")
    print(r.text)
else:
    print(f"\n❌ Falhou: {r.text[:200]}")
