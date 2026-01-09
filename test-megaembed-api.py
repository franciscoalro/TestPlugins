#!/usr/bin/env python3
"""
Teste direto da API do MegaEmbed
"""

import requests
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Referer': 'https://megaembed.link/',
    'Origin': 'https://megaembed.link',
}

def test_api():
    # ID do vídeo (do hash #3wnuij)
    video_id = "3wnuij"
    
    api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
    
    print(f"Testando API: {api_url}")
    
    resp = requests.get(api_url, headers=HEADERS, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}")
    print(f"\nResponse:")
    
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
        
        # Salvar resposta
        with open('megaembed_api_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return data
    except:
        print(resp.text[:1000])
        return None

def test_other_ids():
    """Testa outros IDs conhecidos"""
    ids = [
        "3wnuij",  # Terra de Pecados
        "85n51n",  # The Last of Us
        "dqd1uk",  # Casa do Dragão
        "xef8u6",  # Garota Sequestrada
    ]
    
    print("\n" + "="*60)
    print("TESTANDO MÚLTIPLOS IDs")
    print("="*60)
    
    for vid_id in ids:
        api_url = f"https://megaembed.link/api/v1/info?id={vid_id}"
        print(f"\n{vid_id}: ", end="")
        
        try:
            resp = requests.get(api_url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Verificar campos importantes
                if 'url' in data:
                    print(f"✓ URL encontrada: {data['url'][:50]}...")
                elif 'file' in data:
                    print(f"✓ File encontrado: {data['file'][:50]}...")
                elif 'source' in data:
                    print(f"✓ Source encontrado: {data['source'][:50]}...")
                else:
                    print(f"? Campos: {list(data.keys())}")
            else:
                print(f"✗ Status {resp.status_code}")
        except Exception as e:
            print(f"✗ Erro: {e}")

if __name__ == "__main__":
    data = test_api()
    test_other_ids()
