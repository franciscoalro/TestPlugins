import requests
import time

print("="*60)
print("TESTE M3U8 ENCONTRADO")
print("="*60)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://megaembed.link/",
    "Origin": "https://megaembed.link"
}

# URL encontrada no elemento video
video_id = "3wnuij"
cdn = "s6p9.marvellaholdings.sbs"
timestamp_found = 1767386783  # timestamp da URL encontrada

print(f"\nVideo ID: {video_id}")
print(f"CDN: {cdn}")
print(f"Timestamp encontrado: {timestamp_found}")

# Testar a URL original
print("\n[1] Testando URL original...")
url = f"https://{cdn}/v4/x6b/{video_id}/cf-master.{timestamp_found}.txt"
print(f"  URL: {url}")

r = requests.get(url, headers=HEADERS, timeout=15)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    print(f"  Conteudo:\n{r.text[:1000]}")

# Testar com timestamp atual
print("\n[2] Testando com timestamp atual...")
current_ts = int(time.time())
url2 = f"https://{cdn}/v4/x6b/{video_id}/cf-master.{current_ts}.txt"
print(f"  URL: {url2}")
print(f"  Timestamp atual: {current_ts}")

r2 = requests.get(url2, headers=HEADERS, timeout=15)
print(f"  Status: {r2.status_code}")
if r2.status_code == 200:
    print(f"  Conteudo:\n{r2.text[:500]}")

# Testar outros CDNs com mesmo padrão
print("\n[3] Testando outros CDNs conhecidos...")
cdns = [
    "s6p9.marvellaholdings.sbs",
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs",
    "srcf.marvellaholdings.sbs",
    "sbi6.marvellaholdings.sbs"
]

for cdn_test in cdns:
    url_test = f"https://{cdn_test}/v4/x6b/{video_id}/cf-master.{current_ts}.txt"
    try:
        r = requests.get(url_test, headers=HEADERS, timeout=5)
        status = "OK" if r.status_code == 200 else r.status_code
        has_m3u8 = "#EXTM3U" in r.text if r.status_code == 200 else False
        print(f"  {cdn_test}: {status} {'[M3U8]' if has_m3u8 else ''}")
        if has_m3u8:
            print(f"    Preview: {r.text[:200]}")
    except Exception as e:
        print(f"  {cdn_test}: Erro - {e}")

print("\n" + "="*60)
print("CONCLUSAO")
print("="*60)
print("""
Padrao da URL M3U8:
  https://{cdn}/v4/x6b/{videoId}/cf-master.{timestamp}.txt

O timestamp parece ser:
  - Gerado pelo servidor na resposta da API
  - Ou calculado pelo JS baseado em alguma logica

Para o CloudStream:
  - WebViewResolver carrega a pagina
  - Intercepta URLs que contem 'cf-master' ou '.m3u8'
  - Extrai a URL do <source> ou das requisicoes de rede
""")
