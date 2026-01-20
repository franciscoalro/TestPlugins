#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa o fluxo completo das requisições PlayerEmbedAPI
"""

import json
import base64
import re
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

file_path = r"C:\Users\KYTHOURS\Desktop\logsburpsuit\2026-01-18-162104_json_requests.json"

print("ANALISE DETALHADA DO FLUXO PLAYEREMBEDAPI")
print("=" * 80)
print()

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtrar requisições PlayerEmbedAPI
playerembedapi_reqs = []
for req in data:
    host = req.get('host', '')
    if 'playerembedapi' in host.lower():
        playerembedapi_reqs.append(req)

print(f"Total de requisicoes PlayerEmbedAPI: {len(playerembedapi_reqs)}")
print()

# Analisar cada requisição
for i, req in enumerate(playerembedapi_reqs, 1):
    print(f"{'=' * 80}")
    print(f"REQUISICAO #{i} (ID: {req.get('id')})")
    print(f"{'=' * 80}")
    print(f"URL: {req.get('method')} https://{req.get('host')}{req.get('path')}")
    print(f"Tamanho: {req.get('length')} bytes")
    print(f"TLS: {req.get('is_tls')}")
    print()
    
    # Decodificar request
    if 'raw' in req and req['raw']:
        try:
            raw_request = base64.b64decode(req['raw']).decode('utf-8', errors='ignore')
            print("REQUEST HEADERS:")
            headers = raw_request.split('\r\n\r\n')[0].split('\r\n')
            for header in headers[:15]:  # Primeiros 15 headers
                print(f"   {header}")
            print()
        except Exception as e:
            print(f"   Erro ao decodificar request: {e}")
    
    # Decodificar response
    if 'response' in req and req['response']:
        response = req['response']
        status = response.get('status_code', 'N/A')
        print(f"RESPONSE: {status}")
        
        if 'raw' in response and response['raw']:
            try:
                raw_response = base64.b64decode(response['raw']).decode('utf-8', errors='ignore')
                
                # Separar headers e body
                parts = raw_response.split('\r\n\r\n', 1)
                if len(parts) > 0:
                    print("   HEADERS:")
                    headers = parts[0].split('\r\n')
                    for header in headers[:10]:
                        print(f"      {header}")
                    print()
                
                if len(parts) > 1:
                    body = parts[1]
                    print(f"   BODY SIZE: {len(body)} chars")
                    
                    # Procurar URLs de vídeo no body
                    video_patterns = [
                        r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
                        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                        r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]+',
                        r'https?://[^\s"\'<>]*googleapis[^\s"\'<>]+',
                    ]
                    
                    found_videos = set()
                    for pattern in video_patterns:
                        matches = re.findall(pattern, body, re.IGNORECASE)
                        for match in matches:
                            clean = match.replace('\\/', '/').replace('\\"', '').strip()
                            if clean.startswith('http') and not clean.endswith('.js'):
                                found_videos.add(clean)
                    
                    if found_videos:
                        print()
                        print("   VIDEO URLs ENCONTRADAS NO BODY:")
                        for url in sorted(found_videos):
                            print(f"      {url}")
                    
                    # Mostrar snippet do HTML
                    if '<html' in body.lower() or '<!doctype' in body.lower():
                        print()
                        print("   HTML SNIPPET (primeiros 500 chars):")
                        print("   " + "-" * 76)
                        snippet = body[:500].replace('\n', '\n   ')
                        print(f"   {snippet}")
                        print("   " + "-" * 76)
                        
                        # Procurar scripts importantes
                        script_patterns = [
                            r'<script[^>]*src=["\']([^"\']+)["\']',
                            r'var\s+(\w+)\s*=\s*["\']https?://[^"\']+["\']',
                            r'file\s*:\s*["\']([^"\']+)["\']',
                            r'source\s*:\s*["\']([^"\']+)["\']',
                        ]
                        
                        print()
                        print("   SCRIPTS E VARIAVEIS:")
                        for pattern in script_patterns:
                            matches = re.findall(pattern, body[:5000], re.IGNORECASE)
                            for match in matches[:3]:
                                print(f"      {match}")
                    
            except Exception as e:
                print(f"   Erro ao decodificar response: {e}")
    
    print()

print()
print("=" * 80)
print("CONCLUSOES")
print("=" * 80)
print()
print("PlayerEmbedAPI usa CDN sssrr.org para hospedar videos")
print("URLs encontradas no formato: https://*.sssrr.org/sora/{id}/{base64}")
print("Tambem encontrado: https://*.sssrr.org/{path}/{hash}.{id}.{quality}.fd")
print()
print("PADROES DE URL IDENTIFICADOS:")
print("   1. https://*.sssrr.org/sora/{video_id}/{base64_token}")
print("   2. https://*.sssrr.org/{path}/{hash}.{video_id}.{quality}.fd")
print("   3. https://*.sssrr.org/future")
print()
print("RECOMENDACAO:")
print("   Atualizar regex do WebView para capturar URLs sssrr.org")
print("   Regex sugerido: (?i)sssrr\\.org/(?:sora/|\\d+/)")
