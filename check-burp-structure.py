#!/usr/bin/env python3
"""
Verifica estrutura do arquivo JSON do Burp Suite
"""

import json
import sys

file_path = r"C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json"

print(f"📂 Analisando estrutura: {file_path}")
print()

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ JSON válido!")
    print(f"📊 Total de requisições: {len(data)}")
    print()
    
    if len(data) > 0:
        print("🔍 Estrutura da primeira requisição:")
        print(f"   Keys: {list(data[0].keys())}")
        print()
        
        # Mostrar primeira requisição
        print("📦 Primeira requisição (sample):")
        sample = json.dumps(data[0], indent=2)[:1000]
        print(sample)
        print()
        
        # Procurar requisições playerembedapi
        playerembedapi_count = 0
        googleapis_count = 0
        m3u8_count = 0
        mp4_count = 0
        
        for req in data[:100]:  # Primeiras 100
            url = req.get('url', '') or req.get('path', '') or req.get('host', '')
            
            if 'playerembedapi' in url.lower():
                playerembedapi_count += 1
                print(f"🎯 PlayerEmbedAPI encontrado: {url[:100]}")
            
            if 'googleapis' in url.lower():
                googleapis_count += 1
                print(f"☁️  Google Storage: {url[:100]}")
            
            if '.m3u8' in url.lower():
                m3u8_count += 1
                print(f"📺 M3U8: {url[:100]}")
            
            if '.mp4' in url.lower():
                mp4_count += 1
                print(f"🎬 MP4: {url[:100]}")
        
        print()
        print("📊 RESUMO (primeiras 100 requisições):")
        print(f"   PlayerEmbedAPI: {playerembedapi_count}")
        print(f"   Google Storage: {googleapis_count}")
        print(f"   M3U8: {m3u8_count}")
        print(f"   MP4: {mp4_count}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
