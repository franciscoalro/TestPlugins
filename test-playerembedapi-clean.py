#!/usr/bin/env python3
"""
Teste limpo do PlayerEmbedAPI - sem emojis
"""

import requests
import re

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def main():
    url = "https://playerembedapi.link/?v=4PHWs34H0"
    referer = "https://playerthree.online"
    
    print(f"Analisando: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": referer
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"Tamanho: {len(html)} chars")
        
        if response.status_code == 200:
            print("[OK] Site respondeu corretamente (status 200)")
        else:
            print(f"[AVISO] Status diferente de 200: {response.status_code}")
        
        # Procurar padrões de URL de video
        print("\nProcurando URLs de video...")
        
        patterns = [
            (r'src\s*=\s*["\']([^"\']*storage\.googleapis\.com[^"\']+)["\']', "storage.googleapis.com"),
            (r'src\s*=\s*["\']([^"\']+\.mp4[^"\']*)["\']', ".mp4"),
            (r'src\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']', ".m3u8"),
            (r'"file"\s*:\s*"([^"]+)"', "file JSON"),
            (r"'file'\s*:\s*'([^']+)'", "file JS"),
            (r'source\s*:\s*["\']([^"\']+)["\']', "source"),
            (r'video\.src\s*=\s*["\']([^"\']+)["\']', "video.src"),
            (r'videoUrl\s*=\s*["\']([^"\']+)["\']', "videoUrl"),
            (r'playbackUrl\s*=\s*["\']([^"\']+)["\']', "playbackUrl"),
            (r'https://[^"\'<>\s]+\.mp4', "URL direta mp4"),
            (r'https://[^"\'<>\s]+\.m3u8', "URL direta m3u8"),
            (r'https://storage\.googleapis\.com/[^"\'<>\s]+', "GCS URL"),
        ]
        
        found = []
        for pattern, name in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"\n[ENCONTRADO] Padrao '{name}':")
                for m in matches[:5]:
                    print(f"   {m[:100]}...")
                    if m not in found:
                        found.append(m)
        
        print(f"\n--- RESULTADO ---")
        print(f"Total de URLs de video encontradas: {len(found)}")
        
        if len(found) > 0:
            print("[SUCESSO] URLs de video foram encontradas!")
            for i, url in enumerate(found[:5], 1):
                print(f"  {i}. {url[:80]}...")
        else:
            print("[FALHA] Nenhuma URL de video encontrada")
        
        # Procurar elementos video
        print("\nProcurando elementos <video>...")
        videos = re.findall(r'<video[^>]*>.*?</video>', html, re.DOTALL | re.IGNORECASE)
        print(f"Encontrados {len(videos)} elementos video")
        for v in videos[:3]:
            print(f"  {v[:200]}")
        
        # Procurar elementos source
        print("\nProcurando elementos <source>...")
        sources = re.findall(r'<source[^>]+>', html, re.IGNORECASE)
        print(f"Encontrados {len(sources)} elementos source")
        for s in sources[:5]:
            print(f"  {s}")
        
        # Procurar scripts
        print("\nAnalisando scripts...")
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        print(f"Encontrados {len(scripts)} scripts")
        
        for i, script in enumerate(scripts):
            if len(script) > 200 and ("src" in script.lower() or "url" in script.lower() or "file" in script.lower()):
                print(f"\n[Script {i+1} - {len(script)} chars]")
                # Procurar variaveis interessantes
                print(script[:800])
                print("...")
                break
        
        # Conclusao
        print("\n" + "="*60)
        print("CONCLUSAO:")
        print("="*60)
        print(f"1. Status HTTP: {response.status_code} {'(OK)' if response.status_code == 200 else '(FALHA)'}")
        print(f"2. URLs de video encontradas: {len(found)} {'(OK)' if len(found) > 0 else '(FALHA)'}")
        print(f"3. Elementos <video>: {len(videos)}")
        print(f"4. Elementos <source>: {len(sources)}")
        
        if response.status_code == 200 and len(found) > 0:
            print("\n[RESULTADO FINAL] O extractor DEVE FUNCIONAR no CloudStream")
        elif response.status_code == 200:
            print("\n[RESULTADO FINAL] O site responde mas padroes precisam ser atualizados")
        else:
            print("\n[RESULTADO FINAL] O extractor NAO vai funcionar - problema de acesso")
            
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
