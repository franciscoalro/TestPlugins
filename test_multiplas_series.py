import requests
import re
import time

HEADERS = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}
cdns = ["sipt.marvellaholdings.sbs", "stzm.marvellaholdings.sbs", "srcf.marvellaholdings.sbs", "sbi6.marvellaholdings.sbs"]
shards = ["x6b", "x7c", "x8d", "x9e"]

def test_video(video_id):
    ts = int(time.time())
    for cdn in cdns:
        for shard in shards:
            url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{ts}.txt"
            try:
                r = requests.get(url, headers={**HEADERS, "Referer": "https://megaembed.link/"}, timeout=3)
                if r.status_code == 200 and "#EXTM3U" in r.text:
                    return f"{cdn}/{shard}"
            except:
                pass
    return None

def get_video_id(series_url):
    try:
        r = requests.get(series_url, headers=HEADERS, timeout=10)
        iframe = re.search(r'playerthree\.online/embed/([^/"]+)', r.text)
        if not iframe:
            return None, None
        
        slug = iframe.group(1)
        pt_url = f"https://playerthree.online/embed/{slug}/"
        
        r = requests.get(pt_url, headers={**HEADERS, "Referer": series_url}, timeout=10)
        episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
        if not episodes:
            return None, None
        
        r = requests.get(f"https://playerthree.online/episodio/{episodes[0]}", 
                        headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"}, timeout=10)
        sources = re.findall(r'data-source="([^"]+)"', r.text)
        
        megaembed = [s for s in sources if "megaembed" in s]
        if not megaembed:
            return None, sources
        
        vid = re.search(r'#([a-zA-Z0-9]+)$', megaembed[0])
        if vid:
            return vid.group(1), sources
        return None, sources
    except Exception as e:
        return None, str(e)

# Buscar series
print("Buscando series para testar...")
r = requests.get("https://www.maxseries.one/series", headers=HEADERS, timeout=15)
series = list(set(re.findall(r'href="(https://www\.maxseries\.one/series/assistir-[^"]+)"', r.text)))[:15]

print(f"\nTestando {len(series)} series:\n")
print(f"{'Serie':<40} {'VideoId':<10} {'CDN Direto':<25} {'Sources'}")
print("-"*100)

results = {"direto": 0, "webview": 0, "sem_megaembed": 0, "erro": 0}

for s in series:
    nome = s.split("/")[-1].replace("assistir-", "").replace("-online", "")[:38]
    video_id, sources = get_video_id(s)
    
    if video_id:
        cdn_result = test_video(video_id)
        if cdn_result:
            print(f"{nome:<40} {video_id:<10} {cdn_result:<25} MegaEmbed")
            results["direto"] += 1
        else:
            print(f"{nome:<40} {video_id:<10} {'WebView necessario':<25} MegaEmbed")
            results["webview"] += 1
    elif sources and isinstance(sources, list):
        other = [s.split("/")[-1][:20] for s in sources if "megaembed" not in s]
        print(f"{nome:<40} {'N/A':<10} {'N/A':<25} {other}")
        results["sem_megaembed"] += 1
    else:
        print(f"{nome:<40} {'ERRO':<10} {'N/A':<25} {sources}")
        results["erro"] += 1

print("\n" + "="*100)
print(f"RESUMO: Direto={results['direto']} | WebView={results['webview']} | Sem MegaEmbed={results['sem_megaembed']} | Erro={results['erro']}")
print("="*100)
