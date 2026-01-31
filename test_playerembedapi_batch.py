#!/usr/bin/env python3
"""
PlayerEmbedAPI v5.0 - Teste em Batch
Testa múltiplas URLs de uma vez

Uso: python test_playerembedapi_batch.py urls.txt
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from test_playerembedapi_v5 import PlayerEmbedAPITester, Colors

def test_single_url(url: str) -> dict:
    """Testa uma única URL"""
    tester = PlayerEmbedAPITester()
    
    # Suprime logs individuais
    tester.log = lambda msg, level=None: None
    
    results = []
    
    # Testar cada estratégia
    strategies = [
        ("API", tester.strategy_api),
        ("ShortIcu", tester.strategy_short_icu),
        ("Regex", tester.strategy_regex),
        ("WebView", tester.strategy_webview),
    ]
    
    for name, strategy_func in strategies:
        try:
            result = strategy_func(url)
            if result:
                results.append({
                    'url': url,
                    'strategy': name,
                    'video_url': result.url,
                    'quality': result.quality,
                    'success': True
                })
                break
        except Exception as e:
            continue
    
    if not results:
        results.append({
            'url': url,
            'strategy': 'None',
            'video_url': None,
            'quality': None,
            'success': False
        })
    
    return results[0]

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_playerembedapi_batch.py <arquivo_com_urls>")
        print("\nFormato do arquivo (uma URL por linha):")
        print("  https://playerembedapi.link/?v=abc123")
        print("  https://playerembedapi.link/?v=def456")
        sys.exit(1)
    
    # Ler URLs
    with open(sys.argv[1], 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print(f"TESTE EM BATCH - {len(urls)} URLs")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    results = []
    start_time = time.time()
    
    # Testar em paralelo (máximo 3 simultâneos)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(test_single_url, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✅" if result['success'] else "❌"
                strategy = result['strategy']
                print(f"{status} {url[:50]:<50} -> {strategy}")
                
            except Exception as e:
                print(f"❌ {url[:50]:<50} -> ERRO: {e}")
                results.append({
                    'url': url,
                    'strategy': 'Error',
                    'video_url': None,
                    'quality': None,
                    'success': False
                })
    
    elapsed = time.time() - start_time
    
    # Estatísticas
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("=" * 70)
    print("ESTATÍSTICAS")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    print(f"Total de URLs: {len(results)}")
    print(f"{Colors.OKGREEN}Sucesso: {successful} ({successful/len(results)*100:.1f}%){Colors.ENDC}")
    print(f"{Colors.FAIL}Falha: {failed} ({failed/len(results)*100:.1f}%){Colors.ENDC}")
    print(f"Tempo total: {elapsed:.2f}s")
    print(f"Tempo médio por URL: {elapsed/len(results):.2f}s")
    
    # Contagem por estratégia
    print(f"\n{Colors.BOLD}Estratégias utilizadas:{Colors.ENDC}")
    strategies = {}
    for r in results:
        strat = r['strategy']
        strategies[strat] = strategies.get(strat, 0) + 1
    
    for strat, count in sorted(strategies.items(), key=lambda x: x[1], reverse=True):
        print(f"  {strat}: {count}")
    
    # URLs que falharam
    if failed > 0:
        print(f"\n{Colors.FAIL}{Colors.BOLD}URLs que falharam:{Colors.ENDC}")
        for r in results:
            if not r['success']:
                print(f"  - {r['url']}")
    
    # Salvar resultados
    output_file = "test_results.json"
    import json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n{Colors.OKCYAN}Resultados salvos em: {output_file}{Colors.ENDC}")

if __name__ == "__main__":
    main()
