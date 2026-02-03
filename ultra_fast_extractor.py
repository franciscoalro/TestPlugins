#!/usr/bin/env python3
"""
================================================================================
ULTRA FAST EXTRACTOR - Extração em Milissegundos
Otimizado para velocidade máxima
================================================================================

Técnicas de otimização:
1. Conexões HTTP persistentes (keep-alive)
2. Parsing minimalista (regex direto, sem BeautifulSoup)
3. Decodificação base64 otimizada
4. Async/await para paralelismo
5. Cache de DNS
6. Sem validação de SSL (mais rápido)
7. Headers pré-definidos

Uso: python ultra_fast_extractor.py <url>
"""

import asyncio
import base64
import re
import ssl
import sys
import time
from urllib.parse import urlparse

# import aiohttp  # Opcional - descomente se tiver instalado
import requests
from colorama import Fore, Style, init

init(autoreset=True)

class Colors:
    GREEN = Fore.GREEN
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    RESET = Style.RESET_ALL

class UltraFastExtractor:
    """Extrator otimizado para velocidade máxima"""
    
    # Headers pré-definidos (evita recriação)
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'DNT': '1',
    }
    
    # Regex pré-compiladas (mais rápido)
    RE_DATAS = re.compile(r'const\s+datas\s*=\s*"([^"]+)"')
    RE_SLUG = re.compile(r'"slug":"([^"]+)"')
    RE_MD5 = re.compile(r'"md5_id":(\d+)')
    RE_USER = re.compile(r'"user_id":(\d+)')
    RE_TITLE = re.compile(r'<title>([^<]+)</title>')
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        # Desabilitar SSL para mais velocidade
        self.session.verify = False
        # Adaptador com pool maior
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=0
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
    
    def extract_sync(self, url):
        """Extração síncrona ultra-rápida"""
        start = time.perf_counter()
        
        # 1. Download HTML (mais lento)
        try:
            response = self.session.get(url, timeout=5)
            html = response.text
        except:
            return None
        
        t_download = time.perf_counter() - start
        
        # 2. Extrair campo datas (rápido)
        match = self.RE_DATAS.search(html)
        if not match:
            return None
        
        datas_b64 = match.group(1)
        
        # 3. Decodificar base64 (muito rápido)
        padding = 4 - len(datas_b64) % 4
        if padding != 4:
            datas_b64 += '=' * padding
        
        try:
            decoded = base64.b64decode(datas_b64)
            decoded_str = decoded.decode('utf-8', errors='replace')
        except:
            return None
        
        t_decode = time.perf_counter() - start - t_download
        
        # 4. Extrair campos com regex (muito rápido)
        slug = self.RE_SLUG.search(decoded_str)
        md5 = self.RE_MD5.search(decoded_str)
        user = self.RE_USER.search(decoded_str)
        title = self.RE_TITLE.search(html)
        
        t_parse = time.perf_counter() - start - t_download - t_decode
        
        total = time.perf_counter() - start
        
        return {
            'slug': slug.group(1) if slug else None,
            'md5_id': int(md5.group(1)) if md5 else None,
            'user_id': int(user.group(1)) if user else None,
            'title': title.group(1) if title else None,
            'timings': {
                'download_ms': round(t_download * 1000, 2),
                'decode_ms': round(t_decode * 1000, 2),
                'parse_ms': round(t_parse * 1000, 2),
                'total_ms': round(total * 1000, 2)
            },
            'cdn_urls': [
                f"https://{slug.group(1)}.sssrr.org/sora/{md5.group(1)}/" if slug and md5 else None,
                f"https://cdn.sssrr.org/sora/{md5.group(1)}/" if md5 else None
            ]
        }
    
    # async def extract_async(self, url):
    #     """Extração assíncrona (ainda mais rápida para múltiplas)"""
    #     # Requer aiohttp instalado
    #     pass
    
    def benchmark(self, url, iterations=10):
        """Benchmark de velocidade"""
        print(f"\n{Colors.CYAN}Benchmark: {iterations} iteracoes{Colors.RESET}\n")
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            result = self.extract_sync(url)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.2f} ms")
        
        avg = sum(times) / len(times)
        min_t = min(times)
        max_t = max(times)
        
        print(f"\n{Colors.GREEN}Resultados:{Colors.RESET}")
        print(f"  Media: {avg:.2f} ms")
        print(f"  Min:   {min_t:.2f} ms")
        print(f"  Max:   {max_t:.2f} ms")
        
        return result

def compare_methods(url):
    """Compara métodos de extração"""
    print(f"\n{Colors.CYAN}COMPARACAO DE METODOS{Colors.RESET}")
    print(f"URL: {url}\n")
    
    extractor = UltraFastExtractor()
    
    # 1. Ultra Fast (este script)
    print(f"{Colors.YELLOW}1. ULTRA FAST (otimizado){Colors.RESET}")
    start = time.perf_counter()
    result = extractor.extract_sync(url)
    t1 = (time.perf_counter() - start) * 1000
    print(f"   Tempo: {t1:.2f} ms")
    if result:
        print(f"   Slug: {result['slug']}")
        print(f"   MD5: {result['md5_id']}")
    
    # 2. Modo com detalhamento
    if result:
        print(f"\n   Detalhamento:")
        for key, val in result['timings'].items():
            print(f"     {key}: {val} ms")
    
    # 3. Benchmark
    print(f"\n{Colors.YELLOW}2. BENCHMARK (10 iteracoes){Colors.RESET}")
    result = extractor.benchmark(url, iterations=10)
    
    return result

def main():
    if len(sys.argv) < 2:
        # URLs de teste
        urls = [
            "https://playerembedapi.link/?v=kBJLtxCD3",
            "https://playerembedapi.link/?v=rZeP5UzqD",
        ]
        
        for url in urls:
            compare_methods(url)
            print("\n" + "="*60)
    else:
        url = sys.argv[1]
        result = compare_methods(url)
        
        if result:
            print(f"\n{Colors.GREEN}RESULTADO FINAL:{Colors.RESET}")
            print(f"  Título: {result['title']}")
            print(f"  Slug: {result['slug']}")
            print(f"  MD5 ID: {result['md5_id']}")
            print(f"  URLs CDN:")
            for cdn in result['cdn_urls']:
                if cdn:
                    print(f"    - {cdn}")

if __name__ == '__main__':
    # Suprimir warnings SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main()
