import requests
import time

HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0", "Referer": "https://megaembed.link/"}

# CDNs atualizados
cdns = [
    "sqtd.luminairemotion.online",  # NOVO
    "stzm.luminairemotion.online",  # NOVO
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs",
]
shards = ["is3", "x6b", "x7c", "x8d"]

def test_video(video_id, nome):
    ts = int(time.time())
    print(f"\n{'='*50}")
    print(f"Testando: {nome} (videoId: {video_id})")
    print(f"{'='*50}")
    
    for cdn in cdns:
        for shard in shards:
            url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
            try:
                r = requests.get(url, headers=HEADERS, timeout=5)
                if r.status_code == 200 and "#EXTM3U" in r.text:
                    print(f"✅ ENCONTRADO!")
                    print(f"   CDN: {cdn}")
                    print(f"   Shard: {shard}")
                    print(f"   URL: {url}")
                    
                    # Mostrar qualidades
                    if "1920x1080" in r.text:
                        print(f"   Qualidades: 720p, 1080p")
                    elif "1280x720" in r.text:
                        print(f"   Qualidades: 720p")
                    return True
            except:
                pass
    
    print(f"❌ Nenhum CDN funcionou")
    return False

# Testar as duas series
print("TESTE DE AMBAS AS SERIES")
print("="*50)

# Serie 1: Terra de Pecados
result1 = test_video("3wnuij", "Terra de Pecados")

# Serie 2: Homem X Bebe  
result2 = test_video("ujxl1l", "Homem X Bebe")

print("\n" + "="*50)
print("RESUMO")
print("="*50)
print(f"Terra de Pecados: {'✅ OK' if result1 else '❌ FALHOU'}")
print(f"Homem X Bebe: {'✅ OK' if result2 else '❌ FALHOU'}")

if result1 and result2:
    print("\n🎉 AMBAS FUNCIONAM! O extractor está pronto!")
