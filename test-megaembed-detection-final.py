#!/usr/bin/env python3
"""
Teste Final - Verificação da Detecção MegaEmbed
Simula exatamente o fluxo do MaxSeries v47 atualizado
"""

import requests
from bs4 import BeautifulSoup
import re
import json

def test_megaembed_detection():
    """Testa se o MaxSeries v47 consegue detectar fontes MegaEmbed"""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    })
    
    # URLs de teste reais do MaxSeries
    test_urls = [
        "https://www.maxseries.one/episodio/breaking-bad-1x1/",
        "https://www.maxseries.one/episodio/the-walking-dead-1x1/",
        "https://www.maxseries.one/filme/avatar-2009/"
    ]
    
    results = {
        "total_tested": 0,
        "megaembed_found": 0,
        "playerembedapi_found": 0,
        "doodstream_found": 0,
        "sources_by_url": {}
    }
    
    for test_url in test_urls:
        print(f"\n🔍 TESTANDO: {test_url}")
        print("=" * 80)
        
        try:
            # 1. Carregar página principal
            response = session.get(test_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Encontrar iframe
            iframe = soup.find('iframe')
            if not iframe:
                print("❌ Nenhum iframe encontrado")
                continue
                
            iframe_src = iframe.get('src', '')
            if iframe_src.startswith('//'):
                iframe_src = 'https:' + iframe_src
                
            print(f"🖼️ Iframe encontrado: {iframe_src}")
            
            sources_found = []
            
            # 3. NOVO FLUXO - Simular o que o MaxSeries v47 faz
            if 'playerthree' in iframe_src:
                print("🎯 PlayterThree detectado - usando novo fluxo v47")
                
                # Carregar iframe para extrair episode IDs
                iframe_response = session.get(iframe_src, headers={"Referer": test_url})
                
                if iframe_response.status_code == 200:
                    iframe_html = iframe_response.text
                    
                    # Procurar IDs de episódio (como o MaxSeries v47 faz)
                    episode_ids = re.findall(r'data-episode-id["\s]*=["\s]*["\']?(\d+)', iframe_html)
                    
                    print(f"🆔 Episode IDs encontrados: {len(episode_ids)} - {episode_ids[:5]}")
                    
                    # Testar alguns IDs (como o MaxSeries faz)
                    for ep_id in episode_ids[:3]:  # Testar apenas os primeiros 3
                        print(f"\n🧪 Testando Episode ID: {ep_id}")
                        
                        ajax_url = f"https://playerthree.online/episodio/{ep_id}"
                        ajax_response = session.get(
                            ajax_url,
                            headers={
                                "Referer": test_url,
                                "X-Requested-With": "XMLHttpRequest"
                            }
                        )
                        
                        if ajax_response.status_code == 200:
                            ajax_soup = BeautifulSoup(ajax_response.text, 'html.parser')
                            
                            # CRÍTICO: Procurar botões com data-show-player (novo padrão)
                            buttons = ajax_soup.select("button[data-show-player]")
                            print(f"🔘 Botões data-show-player encontrados: {len(buttons)}")
                            
                            for btn in buttons:
                                src = btn.get('data-source', '')
                                player_text = btn.get_text(strip=True)
                                
                                if src.startswith('http') and 'youtube' not in src.lower():
                                    sources_found.append({
                                        'url': src,
                                        'type': get_source_type(src),
                                        'player_text': player_text,
                                        'episode_id': ep_id
                                    })
                                    
                                    print(f"   ✅ {get_source_type(src)}: {src}")
                                    
                                    # Contar por tipo
                                    source_type = get_source_type(src)
                                    if source_type == "MegaEmbed":
                                        results["megaembed_found"] += 1
                                    elif source_type == "PlayerEmbedAPI":
                                        results["playerembedapi_found"] += 1
                                    elif source_type == "DoodStream":
                                        results["doodstream_found"] += 1
                            
                            # Se encontrou fontes, parar de procurar
                            if buttons:
                                break
                    
                    # Fallback: procurar botões data-source (padrão antigo)
                    if not sources_found:
                        print("⚠️ Nenhuma fonte encontrada com data-show-player, tentando data-source...")
                        
                        for ep_id in episode_ids[:3]:
                            ajax_url = f"https://playerthree.online/episodio/{ep_id}"
                            ajax_response = session.get(
                                ajax_url,
                                headers={
                                    "Referer": test_url,
                                    "X-Requested-With": "XMLHttpRequest"
                                }
                            )
                            
                            if ajax_response.status_code == 200:
                                ajax_soup = BeautifulSoup(ajax_response.text, 'html.parser')
                                buttons = ajax_soup.select("button[data-source]")
                                
                                for btn in buttons:
                                    src = btn.get('data-source', '')
                                    if src.startswith('http') and 'youtube' not in src.lower():
                                        sources_found.append({
                                            'url': src,
                                            'type': get_source_type(src),
                                            'player_text': btn.get_text(strip=True),
                                            'episode_id': ep_id
                                        })
                                
                                if buttons:
                                    break
            
            # Salvar resultados
            results["sources_by_url"][test_url] = sources_found
            results["total_tested"] += 1
            
            print(f"\n📊 RESUMO PARA {test_url}:")
            print(f"   Total de fontes: {len(sources_found)}")
            
            for source in sources_found:
                print(f"   - {source['type']}: {source['player_text']}")
            
        except Exception as e:
            print(f"❌ Erro ao testar {test_url}: {e}")
    
    # Relatório final
    print("\n" + "="*80)
    print("📈 RELATÓRIO FINAL - DETECÇÃO DE FONTES")
    print("="*80)
    print(f"URLs testadas: {results['total_tested']}")
    print(f"MegaEmbed encontrados: {results['megaembed_found']}")
    print(f"PlayerEmbedAPI encontrados: {results['playerembedapi_found']}")
    print(f"DoodStream encontrados: {results['doodstream_found']}")
    
    total_sources = results['megaembed_found'] + results['playerembedapi_found'] + results['doodstream_found']
    print(f"Total de fontes: {total_sources}")
    
    if results['megaembed_found'] > 0:
        print("✅ MegaEmbed DETECTADO - Fix funcionando!")
    else:
        print("❌ MegaEmbed NÃO detectado - Problema persiste")
    
    # Salvar resultados detalhados
    with open('megaembed_detection_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: megaembed_detection_results.json")
    
    return results

def get_source_type(url):
    """Identifica o tipo de fonte pela URL"""
    url_lower = url.lower()
    
    if 'megaembed' in url_lower:
        return "MegaEmbed"
    elif 'playerembedapi' in url_lower:
        return "PlayerEmbedAPI"
    elif any(domain in url_lower for domain in ['myvidplay', 'bysebuho', 'g9r6', 'doodstream', 'dood.', 'vidplay']):
        return "DoodStream"
    else:
        return "Other"

if __name__ == "__main__":
    print("🧪 TESTE FINAL - DETECÇÃO MEGAEMBED v47")
    print("Verificando se o fix do MaxSeries está funcionando...")
    print("="*80)
    
    results = test_megaembed_detection()
    
    # Conclusão
    if results['megaembed_found'] > 0:
        print("\n🎉 SUCESSO! O MaxSeries v47 deve conseguir detectar MegaEmbed!")
        print("✅ O problema de 'fonte megaend nao esta sendo raspada' foi resolvido!")
    else:
        print("\n⚠️ ATENÇÃO: MegaEmbed ainda não foi detectado nos testes")
        print("🔧 Pode ser necessário ajustar mais o código de detecção")