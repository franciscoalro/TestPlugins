#!/usr/bin/env python3
"""
Procura URLs de vídeo no arquivo Burp Suite JSON
"""

import json
import base64
import re

file_path = r"C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json"

print(f"🔍 Procurando URLs de vídeo em {file_path}")
print()

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"📊 Total de requisições: {len(data)}")
print()

# Contadores
playerembedapi_reqs = []
video_urls = set()
googleapis_urls = set()
m3u8_urls = set()
mp4_urls = set()

# Padrões de URL de vídeo
video_patterns = [
    r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
    r'https?://storage\.googleapis\.com[^\s"\'<>]+',
    r'https?://[^\s"\'<>]*cloudatacdn[^\s"\'<>]+',
    r'https?://[^\s"\'<>]*iamcdn[^\s"\'<>]+',
    r'https?://[^\s"\'<>]*sssrr[^\s"\'<>]+',
    r'https?://[^\s"\'<>]*valenium[^\s"\'<>]+',
]

print("🔎 Analisando todas as requisições...")
for i, req in enumerate(data):
    if i % 100 == 0:
        print(f"   Processando {i}/{len(data)}...", end='\r')
    
    host = req.get('host', '')
    path = req.get('path', '')
    url = f"https://{host}{path}" if host else ""
    
    # Procurar PlayerEmbedAPI
    if 'playerembedapi' in host.lower():
        playerembedapi_reqs.append({
            'id': req.get('id'),
            'url': url,
            'method': req.get('method'),
            'length': req.get('length')
        })
    
    # Decodificar raw request e response
    raw_request = ""
    raw_response = ""
    
    if 'raw' in req and req['raw']:
        try:
            raw_request = base64.b64decode(req['raw']).decode('utf-8', errors='ignore')
        except:
            pass
    
    if 'response' in req and req['response'] and 'raw' in req['response']:
        try:
            raw_response = base64.b64decode(req['response']['raw']).decode('utf-8', errors='ignore')
        except:
            pass
    
    # Procurar URLs de vídeo em ambos
    combined_text = raw_request + "\n" + raw_response + "\n" + url
    
    for pattern in video_patterns:
        matches = re.findall(pattern, combined_text, re.IGNORECASE)
        for match in matches:
            # Limpar URL
            clean_url = match.replace('\\/', '/').replace('\\"', '').strip()
            
            # Filtrar URLs inválidas
            if (clean_url.startswith('http') and 
                not clean_url.endswith('.js') and
                'google-analytics' not in clean_url and
                'googletagmanager' not in clean_url and
                'jwplayer' not in clean_url):
                
                video_urls.add(clean_url)
                
                if 'googleapis' in clean_url:
                    googleapis_urls.add(clean_url)
                if '.m3u8' in clean_url:
                    m3u8_urls.add(clean_url)
                if '.mp4' in clean_url:
                    mp4_urls.add(clean_url)

print()
print()
print("=" * 80)
print("📊 RESULTADOS DA ANÁLISE")
print("=" * 80)
print()

print(f"🎯 Requisições PlayerEmbedAPI: {len(playerembedapi_reqs)}")
if playerembedapi_reqs:
    print()
    for req in playerembedapi_reqs[:10]:
        print(f"   #{req['id']}: {req['method']} {req['url']}")
    if len(playerembedapi_reqs) > 10:
        print(f"   ... e mais {len(playerembedapi_reqs) - 10}")
print()

print(f"📺 Total de URLs de vídeo encontradas: {len(video_urls)}")
print(f"   ☁️  Google Storage: {len(googleapis_urls)}")
print(f"   📺 M3U8: {len(m3u8_urls)}")
print(f"   🎬 MP4: {len(mp4_urls)}")
print()

if video_urls:
    print("🎯 URLs DE VÍDEO ENCONTRADAS:")
    print()
    
    # Agrupar por tipo
    if googleapis_urls:
        print("☁️  GOOGLE CLOUD STORAGE:")
        for url in sorted(googleapis_urls)[:5]:
            print(f"   {url}")
        if len(googleapis_urls) > 5:
            print(f"   ... e mais {len(googleapis_urls) - 5}")
        print()
    
    if m3u8_urls:
        print("📺 M3U8 (HLS):")
        for url in sorted(m3u8_urls)[:5]:
            print(f"   {url}")
        if len(m3u8_urls) > 5:
            print(f"   ... e mais {len(m3u8_urls) - 5}")
        print()
    
    if mp4_urls:
        print("🎬 MP4:")
        for url in sorted(mp4_urls)[:5]:
            print(f"   {url}")
        if len(mp4_urls) > 5:
            print(f"   ... e mais {len(mp4_urls) - 5}")
        print()
    
    # Salvar todas as URLs em arquivo
    output_file = "burp_video_urls.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("URLs DE VÍDEO ENCONTRADAS NO BURP SUITE\n")
        f.write("=" * 80 + "\n\n")
        for url in sorted(video_urls):
            f.write(url + "\n")
    
    print(f"💾 Todas as URLs salvas em: {output_file}")
else:
    print("⚠️  Nenhuma URL de vídeo encontrada")
    print()
    print("💡 Isso significa que:")
    print("   1. O vídeo é carregado dinamicamente via JavaScript")
    print("   2. As URLs estão encriptadas/ofuscadas")
    print("   3. O player usa WebRTC ou outra tecnologia não-HTTP")
    print("   4. A captura do Burp não incluiu as requisições de vídeo")
