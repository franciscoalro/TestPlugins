import requests
import time

video_id = "ujxl1l"
ts = int(time.time())

# CDN descoberto nas requisicoes reais
cdn = "sqtd.luminairemotion.online"
shard = "is3"

url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"

print(f"Testando CDN descoberto:")
print(f"URL: {url}")
print()

r = requests.get(url, headers={
    "User-Agent": "Mozilla/5.0 Chrome/120.0.0.0",
    "Referer": "https://megaembed.link/"
}, timeout=15)

print(f"Status: {r.status_code}")
print()

if r.status_code == 200:
    print("CONTEUDO:")
    print(r.text)
else:
    print(f"Erro: {r.text[:200]}")
