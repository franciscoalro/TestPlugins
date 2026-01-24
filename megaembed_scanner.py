import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
VIDEO_ID = "xez5rx"  # ID conhecido de um vídeo (A Casa do Dragão)
# Se não funcionar, troque por um ID recente que você saiba que existe no site

# Base Domains (Adicione novos que encontrar no F12)
DOMAINS = [
    "valenium.shop",
    "marvellaholdings.sbs",
    "luminairemotion.online",
    "virelodesignagency.cyou",
    "fcloud.store"
]

# Potential Subdomains (Wordlist de Brute Force)
SUBDOMAINS = [
    "sskt", "soq6", "spo3", "sbi6", "s6p9", "stzm", "srcf", "sipt", "sqtd", "sr81",
    "cdn", "www", "img", "data", "video", "stream",
    # Generated variations
    "sbi7", "sbi8", "spo4", "spo5", "srcf2", "stzm2" 
]

# Shards / Clusters
SHARDS = [
    "is3", "is9", "x6b", "x7c", "x8d", "x9e", "5w3", "xa1", "xb2",
    "p3w", "z83", "z2e", "c7s", "b1t", "h0z", "b8z", "k8v", "r8c"
]

# --- SCANNER LOGIC ---

def check_combination(sub, domain, shard, video_id):
    timestamp = int(time.time())
    # O arquivo cf-master.xxxx.txt é o que valida o link
    url = f"https://{sub}.{domain}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
    
    try:
        # Usamos HEAD para ser mais rápido (não baixa o corpo)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://megaembed.link/"
        }
        response = requests.head(url, headers=headers, timeout=2)
        
        if response.status_code == 200:
            return (True, url, f"{sub}.{domain}", shard)
        else:
            return (False, url, None, None)
            
    except Exception as e:
        return (False, url, None, None)

def main():
    print(f"🚀 Iniciando MegaEmbed CDN Scanner")
    print(f"🎯 Video ID: {VIDEO_ID}")
    print(f"📦 Domínios: {len(DOMAINS)}")
    print(f"🔤 Subdomínios: {len(SUBDOMAINS)}")
    print(f"💎 Shards: {len(SHARDS)}")
    
    total_combinations = len(DOMAINS) * len(SUBDOMAINS) * len(SHARDS)
    print(f"🔄 Total de combinações a testar: {total_combinations}")
    print("-" * 50)

    found_cdns = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for domain in DOMAINS:
            for sub in SUBDOMAINS:
                for shard in SHARDS:
                    futures.append(executor.submit(check_combination, sub, domain, shard, VIDEO_ID))
        
        processed = 0
        for future in as_completed(futures):
            processed += 1
            success, url, cdn, shard = future.result()
            
            # Progress bar simples
            if processed % 100 == 0:
                print(f"⏳ Processado: {processed}/{total_combinations}", end="\r")

            if success:
                print(f"\n✅ SUCESSO ENCONTRADO!")
                print(f"🔗 URL: {url}")
                print(f"📡 CDN: {cdn}")
                print(f"💎 Shard: {shard}")
                found_cdns.append(f'"{cdn}"')
                print("-" * 50)
    
    print("\n\n🏁 Scan finalizado.")
    if found_cdns:
        print("📋 Adicione estes CDNs ao arquivo MegaEmbedLinkFetcher.kt:")
        print(f"CDN_DOMAINS = listOf(\n    {', '.join(set(found_cdns))}\n)")
    else:
        print("❌ Nenhum CDN ativo encontrado para este ID.")

if __name__ == "__main__":
    main()
