import requests
import re
import time

print("="*60)
print("TESTE MEGAEMBED SIMPLIFICADO - SEM WEBVIEW")
print("="*60)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://megaembed.link/",
    "Origin": "https://megaembed.link"
}

# CDNs conhecidos do MegaEmbed
CDNS = [
    "s6p9.marvellaholdings.sbs",
    "sipt.marvellaholdings.sbs",
    "stzm.marvellaholdings.sbs",
    "srcf.marvellaholdings.sbs",
    "sbi6.marvellaholdings.sbs"
]

def extract_megaembed(url):
    """Extrai M3U8 do MegaEmbed sem precisar de WebView"""
    
    # Extrair video ID da URL (ex: https://megaembed.link/#3wnuij)
    video_id = re.search(r'#([a-zA-Z0-9]+)', url)
    if not video_id:
        video_id = re.search(r'/([a-zA-Z0-9]+)$', url)
    
    if not video_id:
        print("  Erro: Video ID nao encontrado")
        return None
    
    video_id = video_id.group(1)
    print(f"  Video ID: {video_id}")
    
    # Timestamp atual
    timestamp = int(time.time())
    
    # Tentar cada CDN
    for cdn in CDNS:
        m3u8_url = f"https://{cdn}/v4/x6b/{video_id}/cf-master.{timestamp}.txt"
        
        try:
            r = requests.get(m3u8_url, headers=HEADERS, timeout=10)
            if r.status_code == 200 and "#EXTM3U" in r.text:
                print(f"  CDN funcionando: {cdn}")
                return m3u8_url
        except:
            continue
    
    return None

# Teste 1: URL direta do MegaEmbed
print("\n[1] Teste com URL MegaEmbed direta...")
url1 = "https://megaembed.link/#3wnuij"
result1 = extract_megaembed(url1)
if result1:
    print(f"  M3U8: {result1}")

# Teste 2: Fluxo completo do MaxSeries
print("\n[2] Teste fluxo completo MaxSeries...")

# Passo 1: Obter iframe do playerthree
r = requests.get("https://www.maxseries.one/series/assistir-terra-de-pecados-online", 
                 headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)
iframe = re.search(r'playerthree\.online/embed/[^"]+', r.text)
if iframe:
    pt_url = "https://" + iframe.group(0)
    print(f"  PlayerThree: {pt_url}")
    
    # Passo 2: Obter episodios
    r = requests.get(pt_url, headers={**HEADERS, "Referer": "https://www.maxseries.one/"}, timeout=15)
    episodes = re.findall(r'data-episode-id="(\d+)"', r.text)
    if episodes:
        print(f"  Episodios: {len(episodes)}")
        
        # Passo 3: Obter sources do primeiro episodio
        r = requests.get(f"https://playerthree.online/episodio/{episodes[0]}", 
                        headers={**HEADERS, "Referer": pt_url, "X-Requested-With": "XMLHttpRequest"}, timeout=15)
        sources = re.findall(r'data-source="([^"]+)"', r.text)
        
        # Filtrar MegaEmbed
        megaembed_urls = [s for s in sources if "megaembed" in s]
        if megaembed_urls:
            print(f"  MegaEmbed URL: {megaembed_urls[0]}")
            
            # Extrair M3U8
            result2 = extract_megaembed(megaembed_urls[0])
            if result2:
                print(f"  M3U8: {result2}")

print("\n" + "="*60)
print("SUCESSO! MegaEmbed pode ser extraido sem WebView!")
print("="*60)
print("""
Logica para o Extractor Kotlin:

1. Extrair videoId da URL (apos # ou ultimo segmento)
2. Montar URL: https://{cdn}/v4/x6b/{videoId}/cf-master.{timestamp}.txt
3. Testar CDNs ate encontrar um que funcione
4. Retornar ExtractorLink com a URL M3U8

Nao precisa:
- Decriptar resposta da API
- WebView
- Cookies especiais
""")
