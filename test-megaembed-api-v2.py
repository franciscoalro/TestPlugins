#!/usr/bin/env python3
"""
Teste MegaEmbed API v2 - Baseado na Descoberta dos Links
Testa a nova lógica de extração baseada no padrão descoberto:
https://stzm.marvellaholdings.sbs/v4/x6b/3wnuij/cf-master.1767386783.txt
"""

import requests
import re
import json
import time
from urllib.parse import urlparse

def test_megaembed_api():
    """Testa a API do MegaEmbed com diferentes abordagens"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    # URLs de teste reais do MegaEmbed
    test_urls = [
        "https://megaembed.link/#3wnuij",  # The Walking Dead exemplo
        "https://megaembed.link/#iln1cp",  # Outro exemplo
    ]
    
    results = {
        "tests": [],
        "successful_extractions": 0,
        "total_tests": 0
    }
    
    for test_url in test_urls:
        print(f"\n🔍 TESTANDO: {test_url}")
        print("=" * 80)
        
        # Extrair videoId
        video_id = extract_video_id(test_url)
        if not video_id:
            print("❌ Não foi possível extrair videoId")
            continue
            
        print(f"🆔 VideoId extraído: {video_id}")
        
        test_result = {
            "url": test_url,
            "video_id": video_id,
            "methods": {}
        }
        
        # Método 1: API v1 do MegaEmbed
        print(f"\n🔄 Método 1: API v1")
        api_result = test_api_v1(session, video_id)
        test_result["methods"]["api_v1"] = api_result
        
        if api_result["success"]:
            print(f"✅ API v1 funcionou: {api_result['url']}")
            results["successful_extractions"] += 1
        else:
            print(f"❌ API v1 falhou: {api_result['error']}")
        
        # Método 2: APIs alternativas
        print(f"\n🔄 Método 2: APIs alternativas")
        alt_result = test_alternative_apis(session, video_id)
        test_result["methods"]["alternative_apis"] = alt_result
        
        if alt_result["success"]:
            print(f"✅ API alternativa funcionou: {alt_result['url']}")
            results["successful_extractions"] += 1
        else:
            print(f"❌ APIs alternativas falharam: {alt_result['error']}")
        
        # Método 3: Construção baseada no padrão
        print(f"\n🔄 Método 3: Construção baseada no padrão")
        pattern_result = test_pattern_construction(session, video_id)
        test_result["methods"]["pattern_construction"] = pattern_result
        
        if pattern_result["success"]:
            print(f"✅ Construção por padrão funcionou: {pattern_result['url']}")
            results["successful_extractions"] += 1
        else:
            print(f"❌ Construção por padrão falhou: {pattern_result['error']}")
        
        results["tests"].append(test_result)
        results["total_tests"] += 1
    
    # Relatório final
    print("\n" + "="*80)
    print("📈 RELATÓRIO FINAL - TESTE MEGAEMBED API v2")
    print("="*80)
    print(f"URLs testadas: {results['total_tests']}")
    print(f"Extrações bem-sucedidas: {results['successful_extractions']}")
    print(f"Taxa de sucesso: {(results['successful_extractions'] / max(results['total_tests'] * 3, 1)) * 100:.1f}%")
    
    # Salvar resultados
    with open('megaembed_api_v2_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: megaembed_api_v2_results.json")
    
    return results

def extract_video_id(url):
    """Extrai o videoId da URL do MegaEmbed"""
    patterns = [
        r'#([a-zA-Z0-9]+)$',           # #3wnuij
        r'/embed/([a-zA-Z0-9]+)',      # /embed/3wnuij
        r'/([a-zA-Z0-9]+)/?$',         # /3wnuij
        r'id=([a-zA-Z0-9]+)',          # ?id=3wnuij
        r'v=([a-zA-Z0-9]+)'            # ?v=3wnuij
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def test_api_v1(session, video_id):
    """Testa a API v1 do MegaEmbed"""
    try:
        api_url = f"https://megaembed.link/api/v1/video?id={video_id}"
        print(f"   🌐 Chamando: {api_url}")
        
        response = session.get(
            api_url,
            headers={
                "Referer": "https://megaembed.link/",
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest"
            }
        )
        
        print(f"   📄 Status: {response.status_code}")
        print(f"   📏 Size: {len(response.text)} chars")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   📋 JSON keys: {list(data.keys())}")
                
                # Procurar campos com URLs
                possible_fields = ["url", "file", "source", "playlist", "stream", "video"]
                for field in possible_fields:
                    if field in data:
                        url = data[field]
                        if url and isinstance(url, str) and url.startswith('http'):
                            print(f"   ✅ URL encontrada no campo '{field}': {url}")
                            return {"success": True, "url": url, "method": f"api_v1_{field}"}
                
                # Se tem token, tentar segunda chamada
                if "token" in data:
                    token = data["token"]
                    print(f"   🔑 Token encontrado: {token[:20]}...")
                    
                    player_url = f"https://megaembed.link/api/v1/player?t={token}"
                    player_response = session.get(
                        player_url,
                        headers={
                            "Referer": "https://megaembed.link/",
                            "Accept": "application/json, text/plain, */*"
                        }
                    )
                    
                    if player_response.status_code == 200:
                        try:
                            player_data = player_response.json()
                            print(f"   📋 Player JSON keys: {list(player_data.keys())}")
                            
                            for field in possible_fields:
                                if field in player_data:
                                    url = player_data[field]
                                    if url and isinstance(url, str) and url.startswith('http'):
                                        print(f"   ✅ URL encontrada via token no campo '{field}': {url}")
                                        return {"success": True, "url": url, "method": f"api_v1_token_{field}"}
                        except:
                            print(f"   ⚠️ Player response não é JSON: {player_response.text[:100]}")
                
                return {"success": False, "error": "Nenhum campo de URL encontrado", "data": data}
                
            except json.JSONDecodeError:
                print(f"   ⚠️ Response não é JSON: {response.text[:200]}")
                return {"success": False, "error": "Response não é JSON", "response": response.text[:200]}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}", "response": response.text[:200]}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def test_alternative_apis(session, video_id):
    """Testa APIs alternativas do MegaEmbed"""
    alternative_apis = [
        f"https://megaembed.link/api/video/{video_id}",
        f"https://megaembed.link/embed/api?id={video_id}",
        f"https://megaembed.xyz/api/v1/video?id={video_id}",
        f"https://megaembed.to/api/v1/video?id={video_id}"
    ]
    
    for api_url in alternative_apis:
        try:
            print(f"   🌐 Tentando: {api_url}")
            
            response = session.get(
                api_url,
                headers={"Referer": "https://megaembed.link/"},
                timeout=10
            )
            
            print(f"   📄 Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📋 JSON keys: {list(data.keys())}")
                    
                    possible_fields = ["url", "file", "source", "playlist", "stream", "video"]
                    for field in possible_fields:
                        if field in data:
                            url = data[field]
                            if url and isinstance(url, str) and url.startswith('http'):
                                print(f"   ✅ URL encontrada: {url}")
                                return {"success": True, "url": url, "method": f"alt_api_{field}"}
                                
                except json.JSONDecodeError:
                    # Pode ser texto puro
                    if response.text.startswith('http'):
                        print(f"   ✅ URL direta encontrada: {response.text}")
                        return {"success": True, "url": response.text.strip(), "method": "alt_api_direct"}
                        
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue
    
    return {"success": False, "error": "Todas as APIs alternativas falharam"}

def test_pattern_construction(session, video_id):
    """Testa construção baseada no padrão descoberto"""
    # CDNs conhecidos (baseado na descoberta)
    cdn_domains = [
        "stzm.marvellaholdings.sbs",
        "srcf.marvellaholdings.sbs", 
        "sbi6.marvellaholdings.sbs",
        "s6p9.marvellaholdings.sbs"
    ]
    
    # Shards possíveis (baseado na análise)
    possible_shards = ["x6b", "x7c", "x8d", "x9e", "xa1", "xb2"]
    
    # Usar timestamp atual como aproximação
    timestamp = int(time.time())
    
    for cdn in cdn_domains:
        for shard in possible_shards:
            constructed_url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
            
            try:
                print(f"   🧪 Testando: {constructed_url}")
                
                response = session.get(
                    constructed_url,
                    headers={"Referer": "https://megaembed.link/"},
                    timeout=5
                )
                
                print(f"   📄 Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text
                    if "#EXTM3U" in content or "RESOLUTION=" in content:
                        print(f"   ✅ Playlist válida encontrada!")
                        print(f"   📄 Conteúdo: {content[:200]}...")
                        return {"success": True, "url": constructed_url, "method": "pattern_construction"}
                        
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
    
    return {"success": False, "error": "Nenhuma URL construída funcionou"}

if __name__ == "__main__":
    print("🧪 TESTE MEGAEMBED API v2 - Baseado na Descoberta dos Links")
    print("Testando nova lógica de extração...")
    print("="*80)
    
    results = test_megaembed_api()
    
    if results["successful_extractions"] > 0:
        print("\n🎉 SUCESSO! Pelo menos um método funcionou!")
        print("✅ A nova lógica MegaEmbed pode ser implementada no CloudStream")
    else:
        print("\n⚠️ ATENÇÃO: Nenhum método funcionou nos testes")
        print("🔧 Pode ser necessário ajustar a implementação")