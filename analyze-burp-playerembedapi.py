#!/usr/bin/env python3
"""
Analisa arquivo JSON do Burp Suite para encontrar URLs de vídeo do PlayerEmbedAPI
"""

import json
import base64
import re
from urllib.parse import unquote

def decode_base64(encoded):
    """Decodifica string base64"""
    try:
        return base64.b64decode(encoded).decode('utf-8', errors='ignore')
    except:
        return ""

def extract_video_urls(text):
    """Extrai URLs de vídeo do texto"""
    patterns = [
        r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
        r'https?://storage\.googleapis\.com[^\s"\'<>]+',
        r'https?://[^\s"\'<>]*cloudatacdn[^\s"\'<>]+',
        r'https?://[^\s"\'<>]*iamcdn[^\s"\'<>]+',
        r'https?://[^\s"\'<>]*sssrr[^\s"\'<>]+',
    ]
    
    urls = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.update(matches)
    
    return urls

def analyze_burp_json(file_path, max_requests=100):
    """Analisa arquivo JSON do Burp Suite"""
    print(f"🔍 Analisando: {file_path}")
    print(f"⚠️  Limitando a {max_requests} requisições (arquivo muito grande)")
    print()
    
    video_urls = set()
    playerembedapi_requests = []
    
    # Ler arquivo linha por linha (JSON array)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(10_000_000)  # Ler primeiros 10MB
        
        # Tentar parsear como JSON
        try:
            # Encontrar todas as requisições playerembedapi
            matches = re.finditer(r'\{"id":\d+,"host":"playerembedapi\.link"[^}]+\}', content)
            
            for i, match in enumerate(matches):
                if i >= max_requests:
                    break
                    
                try:
                    req = json.loads(match.group())
                    playerembedapi_requests.append(req)
                    
                    # Decodificar raw request
                    if 'raw' in req:
                        decoded = decode_base64(req['raw'])
                        
                        # Extrair URLs de vídeo
                        urls = extract_video_urls(decoded)
                        video_urls.update(urls)
                        
                        # Mostrar info da requisição
                        print(f"📦 Request #{req['id']}")
                        print(f"   Method: {req['method']} {req['path']}")
                        print(f"   Length: {req['length']} bytes")
                        
                        if urls:
                            print(f"   🎯 URLs encontradas: {len(urls)}")
                            for url in urls:
                                print(f"      - {url[:100]}...")
                        print()
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Erro ao parsear JSON: {e}")
    
    # Resumo
    print("=" * 80)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 80)
    print(f"Total de requisições PlayerEmbedAPI analisadas: {len(playerembedapi_requests)}")
    print(f"Total de URLs de vídeo encontradas: {len(video_urls)}")
    print()
    
    if video_urls:
        print("🎯 URLs DE VÍDEO ENCONTRADAS:")
        print()
        for url in sorted(video_urls):
            print(f"  {url}")
            print()
    else:
        print("⚠️  Nenhuma URL de vídeo encontrada nas requisições analisadas")
        print()
        print("💡 Possíveis motivos:")
        print("   1. Vídeos carregados via JavaScript (não aparecem em HTTP)")
        print("   2. URLs encriptadas/ofuscadas")
        print("   3. Requisições de vídeo não capturadas pelo Burp")
        print("   4. Arquivo JSON incompleto ou corrompido")

if __name__ == "__main__":
    file_path = r"C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json"
    analyze_burp_json(file_path, max_requests=50)
