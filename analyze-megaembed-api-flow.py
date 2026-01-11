#!/usr/bin/env python3
"""
Análise do Fluxo API MegaEmbed - Descobrir Como o CDN é Determinado
Baseado no fluxo real observado no navegador
"""

import requests
import re
import json
import time
from urllib.parse import urlparse

def analyze_megaembed_api_flow():
    """Analisa o fluxo completo da API MegaEmbed para descobrir como o CDN é determinado"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    # VideoId do exemplo que funcionou
    video_id = "3wnuij"
    
    print(f"🔍 ANALISANDO FLUXO API MEGAEMBED")
    print(f"VideoId: {video_id}")
    print("=" * 80)
    
    results = {
        "video_id": video_id,
        "api_calls": [],
        "discovered_cdns": [],
        "final_playlist": None
    }
    
    try:
        # Passo 1: API Info (como observado no fluxo)
        print(f"\n📋 PASSO 1: API Info")
        info_url = f"https://megaembed.link/api/v1/info?id={video_id}"
        print(f"🌐 Chamando: {info_url}")
        
        info_response = session.get(
            info_url,
            headers={
                "Referer": "https://megaembed.link/",
                "Accept": "application/json, text/plain, */*"
            }
        )
        
        print(f"📄 Status: {info_response.status_code}")
        print(f"📏 Size: {len(info_response.text)} chars")
        
        if info_response.status_code == 200:
            try:
                info_data = info_response.json()
                print(f"📋 Info keys: {list(info_data.keys())}")
                results["api_calls"].append({
                    "step": "info",
                    "url": info_url,
                    "status": info_response.status_code,
                    "data": info_data
                })
            except:
                print(f"⚠️ Info response não é JSON: {info_response.text[:200]}")
        
        # Passo 2: API Video (como observado no fluxo)
        print(f"\n🎬 PASSO 2: API Video")
        video_url = f"https://megaembed.link/api/v1/video?id={video_id}&w=2144&h=1206&r=playerthree.online"
        print(f"🌐 Chamando: {video_url}")
        
        video_response = session.get(
            video_url,
            headers={
                "Referer": "https://playerthree.online/",
                "Accept": "application/json, text/plain, */*"
            }
        )
        
        print(f"📄 Status: {video_response.status_code}")
        print(f"📏 Size: {len(video_response.text)} chars")
        
        token = None
        if video_response.status_code == 200:
            try:
                video_data = video_response.json()
                print(f"📋 Video keys: {list(video_data.keys())}")
                
                # Procurar por token
                if "token" in video_data:
                    token = video_data["token"]
                    print(f"🔑 Token encontrado: {token[:50]}...")
                
                results["api_calls"].append({
                    "step": "video",
                    "url": video_url,
                    "status": video_response.status_code,
                    "data": video_data
                })
                
            except:
                print(f"⚠️ Video response não é JSON: {video_response.text[:200]}")
                # Pode ser texto criptografado
                if len(video_response.text) > 100:
                    print(f"🔐 Possível resposta criptografada detectada")
                    results["api_calls"].append({
                        "step": "video",
                        "url": video_url,
                        "status": video_response.status_code,
                        "encrypted": True,
                        "data": video_response.text[:200]
                    })
        
        # Passo 3: API Player (se temos token)
        if token:
            print(f"\n🎮 PASSO 3: API Player")
            player_url = f"https://megaembed.link/api/v1/player?t={token}"
            print(f"🌐 Chamando: {player_url}")
            
            player_response = session.get(
                player_url,
                headers={
                    "Referer": "https://megaembed.link/",
                    "Accept": "application/json, text/plain, */*"
                }
            )
            
            print(f"📄 Status: {player_response.status_code}")
            print(f"📏 Size: {len(player_response.text)} chars")
            
            if player_response.status_code == 200:
                try:
                    player_data = player_response.json()
                    print(f"📋 Player keys: {list(player_data.keys())}")
                    
                    # Procurar por URLs de CDN
                    for key, value in player_data.items():
                        if isinstance(value, str) and "marvellaholdings.sbs" in value:
                            print(f"🎯 CDN encontrado no campo '{key}': {value}")
                            results["discovered_cdns"].append({
                                "source": "player_api",
                                "field": key,
                                "url": value
                            })
                    
                    results["api_calls"].append({
                        "step": "player",
                        "url": player_url,
                        "status": player_response.status_code,
                        "data": player_data
                    })
                    
                except:
                    print(f"⚠️ Player response não é JSON: {player_response.text[:200]}")
                    
                    # Procurar padrões de CDN no texto
                    cdn_patterns = [
                        r'https?://[^/\s]+\.marvellaholdings\.sbs[^\s"\']*',
                        r'[a-z0-9]+\.marvellaholdings\.sbs'
                    ]
                    
                    for pattern in cdn_patterns:
                        matches = re.findall(pattern, player_response.text)
                        for match in matches:
                            print(f"🎯 CDN encontrado via regex: {match}")
                            results["discovered_cdns"].append({
                                "source": "player_api_regex",
                                "pattern": pattern,
                                "url": match
                            })
        
        # Passo 4: Tentar construir URL baseada nos CDNs descobertos
        print(f"\n🔨 PASSO 4: Construção Baseada em CDNs Descobertos")
        
        discovered_cdns = [cdn["url"] for cdn in results["discovered_cdns"]]
        if not discovered_cdns:
            # Usar CDNs conhecidos como fallback
            discovered_cdns = [
                "sipt.marvellaholdings.sbs",  # Descoberto no fluxo real
                "stzm.marvellaholdings.sbs",
                "srcf.marvellaholdings.sbs"
            ]
        
        timestamp = int(time.time())
        shards = ["x6b", "x7c", "x8d"]
        
        for cdn_url in discovered_cdns:
            # Extrair apenas o domínio se for URL completa
            if cdn_url.startswith("http"):
                cdn_domain = urlparse(cdn_url).netloc
            else:
                cdn_domain = cdn_url
            
            for shard in shards:
                test_url = f"https://{cdn_domain}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
                
                print(f"🧪 Testando: {test_url}")
                
                try:
                    test_response = session.get(
                        test_url,
                        headers={"Referer": "https://megaembed.link/"},
                        timeout=5
                    )
                    
                    print(f"   📄 Status: {test_response.status_code}")
                    
                    if test_response.status_code == 200 and "#EXTM3U" in test_response.text:
                        print(f"   ✅ SUCESSO! Playlist válida encontrada!")
                        print(f"   📄 Conteúdo: {test_response.text[:200]}...")
                        
                        results["final_playlist"] = {
                            "url": test_url,
                            "cdn": cdn_domain,
                            "shard": shard,
                            "content_preview": test_response.text[:500]
                        }
                        break
                        
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    continue
            
            if results["final_playlist"]:
                break
        
        # Relatório final
        print("\n" + "="*80)
        print("📈 RELATÓRIO FINAL - ANÁLISE API MEGAEMBED")
        print("="*80)
        print(f"VideoId analisado: {video_id}")
        print(f"API calls realizadas: {len(results['api_calls'])}")
        print(f"CDNs descobertos: {len(results['discovered_cdns'])}")
        
        if results["discovered_cdns"]:
            print(f"\n🎯 CDNs Descobertos:")
            for i, cdn in enumerate(results["discovered_cdns"]):
                print(f"   {i+1}. {cdn['url']} (fonte: {cdn['source']})")
        
        if results["final_playlist"]:
            print(f"\n✅ PLAYLIST FINAL ENCONTRADA:")
            print(f"   URL: {results['final_playlist']['url']}")
            print(f"   CDN: {results['final_playlist']['cdn']}")
            print(f"   Shard: {results['final_playlist']['shard']}")
        else:
            print(f"\n❌ Nenhuma playlist válida encontrada")
        
        # Salvar resultados
        with open('megaembed_api_flow_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: megaembed_api_flow_analysis.json")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return None

if __name__ == "__main__":
    print("🧪 ANÁLISE FLUXO API MEGAEMBED - Descobrir CDN Dinâmico")
    print("Baseado no fluxo real observado no navegador")
    print("="*80)
    
    results = analyze_megaembed_api_flow()
    
    if results and results.get("final_playlist"):
        print("\n🎉 SUCESSO! Descobrimos como capturar o CDN dinâmico!")
        print("✅ Esta análise pode ser usada para melhorar o MegaEmbedExtractor")
    else:
        print("\n⚠️ Análise incompleta - mais investigação necessária")