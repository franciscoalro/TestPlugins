#!/usr/bin/env python3
"""
Testa se o token do MegaEmbed é simplesmente o ID
"""

import requests
import json

def test_megaembed_token(video_id):
    """Testa diferentes variações de token"""
    
    base_url = "https://megaembed.link"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, */*',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Referer': f'https://megaembed.link/#{video_id}',
        'Origin': 'https://megaembed.link'
    }
    
    print(f"\n🧪 TESTANDO TOKENS PARA: {video_id}")
    print("=" * 80)
    
    # Variações de token para testar
    token_variations = [
        ("ID simples", video_id),
        ("ID com #", f"#{video_id}"),
        ("ID decoded", video_id),
        ("ID uppercase", video_id.upper()),
        ("ID lowercase", video_id.lower()),
    ]
    
    for name, token in token_variations:
        print(f"\n📡 Testando: {name} = '{token}'")
        
        try:
            url = f"{base_url}/api/v1/player?t={token}"
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                content = response.text
                
                # Tentar parsear como JSON
                try:
                    data = json.loads(content)
                    print(f"   📦 JSON: {json.dumps(data, indent=2)[:300]}")
                    
                    # Verificar se tem erro
                    if 'error' not in data:
                        print(f"   ✅ SUCESSO! Token válido!")
                        return token, data
                    else:
                        print(f"   ❌ Erro: {data.get('error')}")
                except:
                    # Não é JSON, pode ser m3u8 ou URL
                    if '#EXTM3U' in content:
                        print(f"   ✅ M3U8 DIRETO!")
                        return token, content
                    elif content.startswith('http'):
                        print(f"   ✅ URL: {content[:100]}")
                        return token, content
                    else:
                        print(f"   📄 Conteúdo: {content[:100]}")
        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return None, None

def test_with_cookies(video_id):
    """Testa com cookies/sessão"""
    
    print(f"\n🍪 TESTANDO COM SESSÃO/COOKIES")
    print("=" * 80)
    
    session = requests.Session()
    
    # 1. Primeiro, carregar a página principal para obter cookies
    print("\n1️⃣ Carregando página principal...")
    try:
        page_url = f"https://megaembed.link/#{video_id}"
        response = session.get(page_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        print(f"   Status: {response.status_code}")
        print(f"   Cookies: {len(session.cookies)} cookie(s)")
        for cookie in session.cookies:
            print(f"      - {cookie.name} = {cookie.value[:50]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Agora tentar a API com os cookies
    print("\n2️⃣ Tentando API com cookies...")
    try:
        api_url = f"https://megaembed.link/api/v1/player?t={video_id}"
        response = session.get(api_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, */*',
            'Referer': f'https://megaembed.link/#{video_id}',
        })
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.text)
                print(f"   📦 JSON: {json.dumps(data, indent=2)[:300]}")
                
                if 'error' not in data:
                    print(f"   ✅ SUCESSO COM COOKIES!")
                    return data
            except:
                print(f"   📄 Resposta: {response.text[:200]}")
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return None

# Testar com o ID do Burp Suite
video_id = "xez5rx"

# Teste 1: Variações simples
token, result = test_megaembed_token(video_id)

if not result:
    # Teste 2: Com cookies
    result = test_with_cookies(video_id)

if result:
    print("\n" + "=" * 80)
    print("✅ ENCONTRAMOS A SOLUÇÃO!")
    print("=" * 80)
    if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        print(result[:500])
else:
    print("\n" + "=" * 80)
    print("❌ Nenhum método funcionou")
    print("💡 MegaEmbed realmente precisa de WebView ou análise mais profunda do JS")
    print("=" * 80)
