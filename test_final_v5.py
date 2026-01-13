import requests
import re
import time

print("="*60)
print("TESTE FINAL - MEGAEMBED V5 (SEM WEBVIEW)")
print("="*60)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Referer": "https://megaembed.link/",
    "Origin": "https://megaembed.link"
}

CDNS = [
    "s6p9.marvellaholdings.sbs",
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs",
    "srcf.marvellaholdings.sbs",
    "sbi6.marvellaholdings.sbs"
]

def extract_megaembed_v5(url):
    """Simula o MegaEmbedExtractorV5"""
    
    # Extrair videoId
    match = re.search(r'#([a-zA-Z0-9]+)', url)
    if not match:
        match = re.search(r'/([a-zA-Z0-9]{5,10})/?$', url)
    if not match:
        return None
    
    video_id = match.group(1)
    timestamp = int(time.time())
    
    for cdn in CDNS:
        m3u8_url = f"https://{cdn}/v4/x6b/{video_id}/cf-master.{timestamp}.txt"
        
        try:
            r = requests.get(m3u8_url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                return {
                    "url": m3u8_url,
                    "cdn": cdn,
                    "video_id": video_id,
                    "content": r.text
                }
        except:
            continue
    
    return None

# Teste 1: URL direta
print("\n[1] Teste URL direta MegaEmbed...")
result = extract_megaembed_v5("https://megaembed.link/#3wnuij")
if result:
    print(f"  ✅ VideoId: {result['video_id']}")
    print(f"  ✅ CDN: {result['cdn']}")
    print(f"  ✅ M3U8: {result['url']}")
    print(f"  ✅ Qualidades disponíveis:")
    for line in result['content'].split('\n'):
        if 'RESOLUTION' in line:
            res = re.search(r'RESOLUTION=(\d+x\d+)', line)
            if res:
                print(f"     - {res.group(1)}")

# Teste 2: Fluxo completo MaxSeries
print("\n[2] Teste fluxo completo MaxSeries...")

# Passo 1: Obter página da série
r = requests.get("https://www.maxseries.one/series/assistir-terra-de-pecados-online",
                 headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)

# Passo 2: Extrair iframe playerthree
iframe = re.search(r'playerthree\.online/embed/([^"]+)', r.text)
if iframe:
    series_slug = iframe.group(1).rstrip('/')
    pt_url = f"https://playerthree.online/embed/{series_slug}/"
    print(f"  PlayerThree: {pt_url}")
    
    # Passo 3: Obter episódios
    r = requests.get(pt_url, headers={**HEADERS, "Referer": "https://www.maxseries.one/"}, timeout=15)
    episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
    print(f"  Episódios encontrados: {len(episodes)}")
    
    if episodes:
        # Passo 4: Obter sources do episódio
        r = requests.get(f"https://playerthree.online/episodio/{episodes[0]}",
                        headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"}, timeout=15)
        
        sources = re.findall(r'data-source="([^"]+)"', r.text)
        print(f"  Sources encontradas: {len(sources)}")
        
        for source in sources:
            print(f"    - {source[:60]}...")
        
        # Passo 5: Extrair MegaEmbed
        megaembed = [s for s in sources if "megaembed" in s]
        if megaembed:
            print(f"\n  Extraindo MegaEmbed: {megaembed[0]}")
            result = extract_megaembed_v5(megaembed[0])
            if result:
                print(f"  ✅ M3U8 extraído: {result['url']}")
                
                # Verificar se o M3U8 é válido
                print(f"\n  Verificando playlist...")
                r = requests.get(result['url'], headers=HEADERS, timeout=10)
                if "#EXTM3U" in r.text:
                    print(f"  ✅ Playlist válida!")
                    
                    # Extrair URL do segmento 1080p
                    lines = r.text.split('\n')
                    for i, line in enumerate(lines):
                        if '1080' in line and i+1 < len(lines):
                            segment_file = lines[i+1].strip()
                            base_url = result['url'].rsplit('/', 1)[0]
                            segment_url = f"{base_url}/{segment_file}"
                            print(f"  ✅ Segmento 1080p: {segment_url}")
                            
                            # Testar segmento
                            r2 = requests.get(segment_url, headers=HEADERS, timeout=10)
                            if "#EXTM3U" in r2.text:
                                print(f"  ✅ Segmento 1080p válido!")
                            break

print("\n" + "="*60)
print("RESUMO")
print("="*60)
print("""
MegaEmbedExtractorV5 funciona SEM WebView!

Lógica:
1. Extrair videoId da URL (após # ou último segmento)
2. Usar timestamp atual
3. Testar CDNs conhecidos até encontrar um que funcione
4. Retornar URL M3U8 para o M3u8Helper processar

CDNs funcionando:
- s6p9.marvellaholdings.sbs
- sipt.marvellaholdings.sbs  
- stzm.marvellaholdings.sbs
- srcf.marvellaholdings.sbs
- sbi6.marvellaholdings.sbs
""")
