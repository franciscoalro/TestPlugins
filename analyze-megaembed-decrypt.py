#!/usr/bin/env python3
"""
Análise profunda do MegaEmbed - Decriptação
"""

import requests
import re
import json
from urllib.parse import urljoin

def analyze_megaembed():
    print("🔬 ANÁLISE PROFUNDA MEGAEMBED")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
    })
    
    video_id = "3wnuij"
    base_url = "https://megaembed.link"
    
    # 1. Baixar o JavaScript principal
    print("\n📥 1. Baixando JavaScript principal...")
    
    js_url = f"{base_url}/assets/index-CQ0L9dOW.js"
    try:
        js_response = session.get(js_url, timeout=30)
        js_code = js_response.text
        print(f"✅ JavaScript baixado: {len(js_code)} chars")
        
        # Salvar para análise
        with open('megaembed_index.js', 'w', encoding='utf-8') as f:
            f.write(js_code)
        print("💾 Salvo em: megaembed_index.js")
        
        # Procurar padrões de decriptação
        print("\n🔍 Procurando padrões de decriptação...")
        
        # Padrões comuns de crypto
        crypto_patterns = [
            r'CryptoJS',
            r'AES\.decrypt',
            r'atob\s*\(',
            r'btoa\s*\(',
            r'fromCharCode',
            r'charCodeAt',
            r'decrypt',
            r'decipher',
            r'decode',
            r'xor',
            r'key\s*[=:]',
            r'iv\s*[=:]',
            r'secret',
            r'password'
        ]
        
        for pattern in crypto_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                print(f"   🔑 Encontrado: {pattern} ({len(matches)}x)")
        
        # Procurar URLs de API
        print("\n🔍 Procurando endpoints de API...")
        api_patterns = [
            r'["\']\/api\/[^"\']+["\']',
            r'fetch\s*\(["\'][^"\']+["\']',
            r'axios\.[a-z]+\s*\(["\'][^"\']+["\']',
            r'\.get\s*\(["\'][^"\']+["\']',
            r'\.post\s*\(["\'][^"\']+["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, js_code)
            for match in matches[:5]:
                print(f"   📡 API: {match}")
        
        # Procurar funções de player
        print("\n🔍 Procurando configuração do player...")
        player_patterns = [
            r'file\s*:\s*["\'][^"\']+["\']',
            r'source\s*:\s*["\'][^"\']+["\']',
            r'hls\s*:\s*["\'][^"\']+["\']',
            r'm3u8',
            r'\.mp4',
            r'vidstack',
            r'jwplayer',
            r'videojs'
        ]
        
        for pattern in player_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                print(f"   🎬 Player: {pattern} ({len(matches)}x)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Analisar dados criptografados
    print("\n🔐 2. Analisando dados criptografados...")
    
    api_url = f"{base_url}/api/v1/info?id={video_id}"
    try:
        response = session.get(api_url, headers={
            'Referer': f'{base_url}/#{video_id}',
            'Origin': base_url
        })
        
        encrypted_data = response.text
        print(f"📄 Dados criptografados: {len(encrypted_data)} chars")
        print(f"📄 Primeiros 100 chars: {encrypted_data[:100]}")
        
        # Verificar se é hex
        if all(c in '0123456789abcdef' for c in encrypted_data.lower()):
            print("✅ Formato: HEX string")
            
            # Converter hex para bytes
            try:
                raw_bytes = bytes.fromhex(encrypted_data)
                print(f"📦 Bytes: {len(raw_bytes)}")
                print(f"📦 Primeiros 20 bytes: {raw_bytes[:20]}")
                
                # Tentar decodificar como UTF-8
                try:
                    decoded = raw_bytes.decode('utf-8')
                    print(f"📄 UTF-8: {decoded[:100]}")
                except:
                    print("❌ Não é UTF-8 válido")
                
                # Verificar se parece JSON após XOR com chaves comuns
                common_keys = [video_id, 'megaembed', 'secret', '123456', 'key']
                for key in common_keys:
                    try:
                        key_bytes = key.encode()
                        xored = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(raw_bytes)])
                        decoded = xored.decode('utf-8', errors='ignore')
                        if '{' in decoded[:50] or 'http' in decoded[:100]:
                            print(f"🔑 Possível chave XOR: {key}")
                            print(f"   Resultado: {decoded[:200]}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Erro ao converter hex: {e}")
        else:
            print("❌ Não é hex puro")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Procurar no JS a lógica de decriptação
    print("\n🔍 3. Extraindo lógica de decriptação do JS...")
    
    # Procurar funções que processam a resposta da API
    decrypt_patterns = [
        r'function\s+\w*[Dd]ecrypt\w*\s*\([^)]*\)\s*\{[^}]+\}',
        r'const\s+\w*[Dd]ecrypt\w*\s*=\s*\([^)]*\)\s*=>\s*\{[^}]+\}',
        r'\.then\s*\(\s*\w+\s*=>\s*\{[^}]*decrypt[^}]*\}',
        r'api/v1/info[^}]+\}',
    ]
    
    for pattern in decrypt_patterns:
        matches = re.findall(pattern, js_code, re.DOTALL)
        for match in matches[:3]:
            if len(match) > 50:
                print(f"\n📜 Código encontrado:")
                print(f"   {match[:300]}...")
    
    # 4. Procurar a chave de decriptação
    print("\n🔑 4. Procurando chaves hardcoded...")
    
    key_patterns = [
        r'["\'][a-zA-Z0-9]{16,32}["\']',  # Chaves de 16-32 chars
        r'key\s*[=:]\s*["\'][^"\']+["\']',
        r'secret\s*[=:]\s*["\'][^"\']+["\']',
        r'iv\s*[=:]\s*["\'][^"\']+["\']'
    ]
    
    found_keys = set()
    for pattern in key_patterns:
        matches = re.findall(pattern, js_code)
        for match in matches:
            if len(match) > 10 and len(match) < 100:
                found_keys.add(match)
    
    print(f"   Encontradas {len(found_keys)} possíveis chaves")
    for key in list(found_keys)[:10]:
        print(f"   🔑 {key}")

if __name__ == "__main__":
    analyze_megaembed()
