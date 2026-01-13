#!/usr/bin/env python3
"""
Simula a extração do DoodStream/MyVidPlay
"""

import requests
import re
import time
import random
import string

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

def extract_dood(url, referer):
    """Extrai link de vídeo do DoodStream/MyVidPlay"""
    print(f"\n🔍 Extraindo de: {url}")
    
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": referer
    }
    
    # Passo 1: Obter página do player
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    print(f"Status: {response.status_code}")
    
    # Passo 2: Extrair URL do pass_md5
    pass_md5_match = re.search(r"(/pass_md5/[^'\"]+)", html)
    if not pass_md5_match:
        print("❌ pass_md5 não encontrado")
        return None
    
    pass_md5_path = pass_md5_match.group(1)
    print(f"✅ pass_md5: {pass_md5_path}")
    
    # Determinar domínio base
    if "myvidplay" in url:
        base_domain = "https://myvidplay.com"
    elif "dood" in url:
        # Extrair domínio do dood
        domain_match = re.search(r'(https?://[^/]+)', url)
        base_domain = domain_match.group(1) if domain_match else "https://dood.li"
    else:
        base_domain = "https://dood.li"
    
    pass_md5_url = base_domain + pass_md5_path
    print(f"✅ URL completa: {pass_md5_url}")
    
    # Passo 3: Fazer request para pass_md5
    headers["Referer"] = url
    
    try:
        md5_response = requests.get(pass_md5_url, headers=headers, timeout=15)
        md5_text = md5_response.text
        
        print(f"✅ pass_md5 response: {md5_text[:200]}...")
        
        # Passo 4: Gerar token aleatório
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Passo 5: Construir URL final
        # O formato típico é: {md5_response}{token}?token={token}&expiry={timestamp}
        timestamp = int(time.time() * 1000)
        
        # Verificar se md5_text é uma URL parcial
        if md5_text.startswith("http"):
            final_url = f"{md5_text}{token}?token={token}&expiry={timestamp}"
        else:
            final_url = f"{base_domain}{md5_text}{token}?token={token}&expiry={timestamp}"
        
        print(f"✅ URL final: {final_url}")
        
        # Passo 6: Testar se a URL funciona
        test_headers = {
            "User-Agent": USER_AGENT,
            "Referer": url,
            "Range": "bytes=0-1024"
        }
        
        test_response = requests.get(final_url, headers=test_headers, timeout=15, stream=True)
        print(f"✅ Teste da URL: Status {test_response.status_code}")
        print(f"   Content-Type: {test_response.headers.get('Content-Type', 'N/A')}")
        print(f"   Content-Length: {test_response.headers.get('Content-Length', 'N/A')}")
        
        if test_response.status_code == 200 or test_response.status_code == 206:
            print("✅ URL FUNCIONA!")
            return final_url
        else:
            print("❌ URL não funciona")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("=" * 60)
    print("🔍 TESTE DE EXTRAÇÃO DOODSTREAM/MYVIDPLAY")
    print("=" * 60)
    
    # Testar MyVidPlay
    url = "https://myvidplay.com/e/tilgznkxayrx"
    referer = "https://playerthree.online"
    
    result = extract_dood(url, referer)
    
    if result:
        print(f"\n✅ SUCESSO! Link extraído: {result}")
    else:
        print("\n❌ FALHA na extração")

if __name__ == "__main__":
    main()
