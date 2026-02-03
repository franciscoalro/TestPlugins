#!/usr/bin/env python3
"""
================================================================================
KALI PARAM FUZZER - Fuzzing de Parametros HTTP
Ferramenta tipo wfuzz / ffuf para descoberta de parametros e endpoints
================================================================================

Funcoes:
- Fuzzing de parametros GET/POST
- Descoberta de endpoints ocultos
- Teste de variacoes de URL
- Bypass de restricoes
- Enumeracao de subdominios

Uso: python kali_param_fuzzer.py --url "https://playerembedapi.link/?v=FUZZ"
"""

import argparse
import asyncio
import json
import random
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests
from colorama import Fore, Style, init

init(autoreset=True)

class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT

class ParamFuzzer:
    """Fuzzer de parametros HTTP"""
    
    def __init__(self, base_url, threads=10, delay=0, timeout=10):
        self.base_url = base_url
        self.threads = threads
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
        })
        self.results = []
        self.baseline_status = None
        self.baseline_length = None
    
    def set_baseline(self):
        """Define baseline para comparacao"""
        try:
            # Fazer requisicao com parametro aleatorio
            random_param = ''.join(random.choices(string.ascii_lowercase, k=10))
            test_url = self.base_url.replace('FUZZ', random_param)
            
            response = self.session.get(test_url, timeout=self.timeout, allow_redirects=False)
            self.baseline_status = response.status_code
            self.baseline_length = len(response.content)
            
            print(f"{Colors.CYAN}[*] Baseline: Status={self.baseline_status}, Length={self.baseline_length}{Colors.RESET}\n")
            
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Erro ao definir baseline: {e}{Colors.RESET}")
    
    def fuzz_param(self, payload):
        """Fuzz um unico parametro"""
        try:
            time.sleep(self.delay)
            
            url = self.base_url.replace('FUZZ', str(payload))
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            
            result = {
                'payload': payload,
                'url': url,
                'status': response.status_code,
                'length': len(response.content),
                'headers': dict(response.headers),
                'interesting': False
            }
            
            # Verificar se eh interessante
            if response.status_code != self.baseline_status:
                result['interesting'] = True
                result['reason'] = f"Status diferente ({response.status_code} vs {self.baseline_status})"
            elif abs(len(response.content) - self.baseline_length) > 100:
                result['interesting'] = True
                result['reason'] = f"Tamanho diferente ({len(response.content)} vs {self.baseline_length})"
            
            # Verificar conteudo
            content = response.text.lower()
            if any(err in content for err in ['error', 'exception', 'sql', 'syntax']):
                result['interesting'] = True
                result['reason'] = "Possivel erro/vulnerabilidade"
            
            if any(ok in content for ok in ['video', 'player', 'source', 'm3u8', 'mp4']):
                result['interesting'] = True
                result['reason'] = "Conteudo de video detectado"
            
            return result
            
        except requests.exceptions.Timeout:
            return {'payload': payload, 'error': 'Timeout', 'interesting': False}
        except Exception as e:
            return {'payload': payload, 'error': str(e), 'interesting': False}
    
    def run_fuzz(self, wordlist):
        """Executa fuzzing com wordlist"""
        print(f"{Colors.CYAN}[*] Iniciando fuzzing com {len(wordlist)} payloads...{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Threads: {self.threads}, Delay: {self.delay}s{Colors.RESET}\n")
        
        interesting_results = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.fuzz_param, payload): payload for payload in wordlist}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                self.results.append(result)
                
                # Progresso
                if completed % 10 == 0 or completed == len(wordlist):
                    print(f"{Colors.CYAN}[*] Progresso: {completed}/{len(wordlist)}{Colors.RESET}", end='\r')
                
                # Mostrar resultados interessantes
                if result.get('interesting'):
                    interesting_results.append(result)
                    print(f"\n{Colors.GREEN}[FOUND] Payload: {result['payload']}{Colors.RESET}")
                    print(f"        Status: {result['status']}, Length: {result['length']}")
                    print(f"        Reason: {result['reason']}")
        
        print(f"\n{Colors.GREEN}[+] Fuzzing completo. {len(interesting_results)} resultados interessantes.{Colors.RESET}")
        return interesting_results
    
    def generate_video_id_payloads(self):
        """Gera payloads especificos para IDs de video"""
        payloads = []
        
        # IDs numericos
        payloads.extend([
            '1', '2', '3', '10', '100', '1000',
            '999999', '000000',
        ])
        
        # IDs alfanumericos (tipo PlayerEmbedAPI)
        payloads.extend([
            'kBJLtxCD3',  # ID conhecido
            'abc123def4',
            'test123',
            'video123',
        ])
        
        # Caracteres especiais
        payloads.extend([
            "'", '"', '<', '>', ';', '&', '|',
            '$(whoami)', '${jndi:ldap://x}',  # Teste basico de injecao
        ])
        
        # Bypass
        payloads.extend([
            '../', '..\\', '%2e%2e%2f', '%252e%252e%252f',
            'null', 'undefined', 'none', 'false', 'true',
        ])
        
        return payloads
    
    def generate_endpoint_payloads(self):
        """Gera payloads para descoberta de endpoints"""
        endpoints = [
            'api', 'sora', 'future', 'video', 'player',
            'stream', 'source', 'embed', 'play',
            'admin', 'config', 'settings',
            'test', 'dev', 'debug',
            'v1', 'v2', 'api/v1', 'api/v2',
        ]
        
        extensions = ['', '.json', '.php', '.html', '.txt', '.xml']
        
        payloads = []
        for endpoint in endpoints:
            for ext in extensions:
                payloads.append(f"{endpoint}{ext}")
        
        return payloads
    
    def test_param_variations(self, param_name, base_value):
        """Testa variacoes de um parametro"""
        variations = [
            base_value,
            base_value.upper(),
            base_value.lower(),
            base_value[::-1],  # Reverso
            base_value + '1',
            base_value + '0',
            '0' + base_value,
            base_value.replace('0', 'O'),
            base_value.replace('1', 'l'),
        ]
        
        # Adicionar caracteres especiais
        special_chars = ['%20', '+', '%00', '%0d%0a', '%2f', '%5c']
        for char in special_chars:
            variations.append(base_value + char)
        
        results = []
        for var in variations:
            url = self.base_url.replace(f'{param_name}=FUZZ', f'{param_name}={var}')
            result = self.fuzz_param(var)
            results.append(result)
            
            if result.get('interesting'):
                print(f"{Colors.GREEN}[INTERESTING] {param_name}={var} -> {result['status']}{Colors.RESET}")
        
        return results
    
    def analyze_response_differences(self):
        """Analisa diferencas nas respostas"""
        status_codes = {}
        lengths = {}
        
        for r in self.results:
            if 'error' in r:
                continue
            
            status = r['status']
            length = r['length']
            
            status_codes[status] = status_codes.get(status, 0) + 1
            
            # Agrupar tamanhos similares
            length_key = (length // 100) * 100
            lengths[length_key] = lengths.get(length_key, 0) + 1
        
        print(f"\n{Colors.CYAN}[*] Distribuicao de Status Codes:{Colors.RESET}")
        for status, count in sorted(status_codes.items()):
            color = Colors.GREEN if status == 200 else Colors.YELLOW if status == 302 else Colors.RED
            print(f"    {color}HTTP {status}: {count} respostas{Colors.RESET}")
        
        return status_codes, lengths
    
    def save_report(self, filename=None):
        """Salva relatorio"""
        if not filename:
            filename = f"fuzz_report_{int(time.time())}.json"
        
        report = {
            'target_url': self.base_url,
            'total_requests': len(self.results),
            'interesting_results': [r for r in self.results if r.get('interesting')],
            'all_results': self.results,
            'baseline': {
                'status': self.baseline_status,
                'length': self.baseline_length
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}[+] Relatorio salvo: {filename}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='KALI PARAM FUZZER - Parameter fuzzing tool')
    parser.add_argument('--url', '-u', type=str, required=True, help='Target URL with FUZZ keyword')
    parser.add_argument('--wordlist', '-w', type=str, help='Wordlist file')
    parser.add_argument('--threads', '-t', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('--delay', '-d', type=float, default=0, help='Delay between requests (seconds)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout (seconds)')
    parser.add_argument('--mode', '-m', choices=['video', 'endpoint', 'param'], 
                       default='video', help='Fuzzing mode')
    
    args = parser.parse_args()
    
    print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                        KALI PARAM FUZZER - Started
================================================================================{Colors.RESET}
    """)
    
    # Inicializar fuzzer
    fuzzer = ParamFuzzer(args.url, threads=args.threads, delay=args.delay, timeout=args.timeout)
    
    # Definir baseline
    fuzzer.set_baseline()
    
    # Carregar wordlist
    if args.wordlist:
        with open(args.wordlist, 'r') as f:
            wordlist = [line.strip() for line in f if line.strip()]
    else:
        # Usar wordlist padrao baseada no modo
        if args.mode == 'video':
            wordlist = fuzzer.generate_video_id_payloads()
        elif args.mode == 'endpoint':
            wordlist = fuzzer.generate_endpoint_payloads()
        else:
            wordlist = ['test', 'admin', 'root', '1', '0', 'null']
    
    print(f"{Colors.CYAN}[*] Wordlist carregada: {len(wordlist)} payloads{Colors.RESET}\n")
    
    # Executar fuzzing
    interesting = fuzzer.run_fuzz(wordlist)
    
    # Analise
    print(f"\n{Colors.CYAN}[*] Analisando resultados...{Colors.RESET}")
    fuzzer.analyze_response_differences()
    
    # Salvar relatorio
    fuzzer.save_report()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}")

if __name__ == '__main__':
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main()
