#!/usr/bin/env python3
"""
================================================================================
KALI REQUEST MANIPULATOR - Manipulador de Requisicoes HTTP
Ferramenta tipo Burp Repeater / curl avancado para testes manuais
================================================================================

Funcoes:
- Enviar requisicoes customizadas
- Modificar headers em tempo real
- Testar variacoes de parametros
- Bypass de protecoes
- Replay de requisicoes
- Comparar respostas

Uso: python kali_request_manipulator.py --url https://playerembedapi.link/?v=xxx
"""

import argparse
import json
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

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

class RequestManipulator:
    """Manipulador de requisicoes HTTP"""
    
    def __init__(self):
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.history = []
    
    def send_request(self, method, url, headers=None, params=None, data=None, 
                     cookies=None, allow_redirects=True, timeout=30):
        """Envia requisicao HTTP customizada"""
        
        # Merge headers
        request_headers = dict(self.default_headers)
        if headers:
            request_headers.update(headers)
        
        try:
            print(f"{Colors.CYAN}[*] Enviando {method} para {url[:80]}...{Colors.RESET}")
            
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                cookies=cookies,
                allow_redirects=allow_redirects,
                timeout=timeout,
                verify=False
            )
            
            # Salvar no historico
            self.history.append({
                'method': method,
                'url': url,
                'status': response.status_code,
                'length': len(response.content)
            })
            
            return response
            
        except Exception as e:
            print(f"{Colors.RED}[!] Erro: {str(e)}{Colors.RESET}")
            return None
    
    def print_response(self, response, show_headers=True, show_body=True, max_body=2000):
        """Imprime resposta formatada"""
        if not response:
            return
        
        # Status
        status_color = Colors.GREEN if response.status_code == 200 else Colors.YELLOW if response.status_code < 400 else Colors.RED
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{status_color}[HTTP {response.status_code}] {response.reason}{Colors.RESET}")
        print(f"{Colors.CYAN}URL Final: {response.url}{Colors.RESET}")
        print(f"{Colors.CYAN}Tamanho: {len(response.content)} bytes{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}")
        
        # Headers
        if show_headers:
            print(f"\n{Colors.YELLOW}[Response Headers]{Colors.RESET}")
            for key, value in response.headers.items():
                print(f"    {key}: {value}")
        
        # Body
        if show_body and len(response.content) > 0:
            print(f"\n{Colors.YELLOW}[Response Body]{Colors.RESET}")
            try:
                body = response.text[:max_body]
                print(body)
                if len(response.content) > max_body:
                    print(f"\n... ({len(response.content) - max_body} bytes omitidos)")
            except:
                print(f"{Colors.RED}[Binary content - {len(response.content)} bytes]{Colors.RESET}")
        
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
    
    def test_bypass_headers(self, url):
        """Testa headers de bypass"""
        print(f"{Colors.CYAN}[*] Testando headers de bypass...{Colors.RESET}\n")
        
        bypass_headers = [
            {'X-Forwarded-For': '127.0.0.1'},
            {'X-Real-IP': '127.0.0.1'},
            {'X-Originating-IP': '127.0.0.1'},
            {'X-Remote-IP': '127.0.0.1'},
            {'X-Remote-Addr': '127.0.0.1'},
            {'X-Client-IP': '127.0.0.1'},
            {'X-Host': '127.0.0.1'},
            {'X-Custom-IP-Authorization': '127.0.0.1'},
            {'X-Forwarded-Host': 'localhost'},
            {'X-Forwarded-Server': 'localhost'},
            {'X-HTTP-Host-Override': 'localhost'},
            {'Forwarded': 'for=127.0.0.1;by=127.0.0.1;host=localhost'},
            {'Client-IP': '127.0.0.1'},
            {'True-Client-IP': '127.0.0.1'},
            {'Cluster-Client-IP': '127.0.0.1'},
        ]
        
        results = []
        for headers in bypass_headers:
            response = self.send_request('GET', url, headers=headers)
            if response:
                result = {
                    'headers': headers,
                    'status': response.status_code,
                    'length': len(response.content)
                }
                results.append(result)
                
                status_color = Colors.GREEN if response.status_code == 200 else Colors.RED
                print(f"    {list(headers.keys())[0]}: {status_color}{response.status_code}{Colors.RESET} ({len(response.content)} bytes)")
        
        return results
    
    def test_user_agents(self, url):
        """Testa diferentes User-Agents"""
        print(f"{Colors.CYAN}[*] Testando User-Agents...{Colors.RESET}\n")
        
        user_agents = [
            ('Chrome Win', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            ('Chrome Mac', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),
            ('Firefox', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'),
            ('Safari', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'),
            ('Mobile', 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'),
            ('Bot', 'Googlebot/2.1 (+http://www.google.com/bot.html)'),
            ('Curl', 'curl/7.68.0'),
            ('Wget', 'Wget/1.20.3'),
        ]
        
        results = []
        for name, ua in user_agents:
            response = self.send_request('GET', url, headers={'User-Agent': ua})
            if response:
                results.append({
                    'name': name,
                    'status': response.status_code,
                    'length': len(response.content)
                })
                print(f"    {name}: {response.status_code} ({len(response.content)} bytes)")
        
        return results
    
    def test_http_methods(self, url):
        """Testa diferentes metodos HTTP"""
        print(f"{Colors.CYAN}[*] Testando metodos HTTP...{Colors.RESET}\n")
        
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'TRACE']
        
        results = []
        for method in methods:
            try:
                response = self.send_request(method, url)
                if response:
                    results.append({
                        'method': method,
                        'status': response.status_code
                    })
                    status_color = Colors.GREEN if response.status_code == 200 else Colors.YELLOW if response.status_code != 405 else Colors.RED
                    print(f"    {method}: {status_color}{response.status_code}{Colors.RESET}")
            except:
                print(f"    {method}: {Colors.RED}ERROR{Colors.RESET}")
        
        return results
    
    def extract_video_from_html(self, html):
        """Extrai URLs de video de HTML"""
        import re
        
        patterns = [
            r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
            r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
            r'(https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*)',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'sources\s*:\s*\[\s*\{[^}]*file\s*:\s*["\']([^"\']+)["\']',
        ]
        
        found = []
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match not in found:
                    found.append(match)
        
        return found
    
    def interactive_mode(self, url):
        """Modo interativo"""
        print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                    KALI REQUEST MANIPULATOR - Modo Interativo
================================================================================{Colors.RESET}

Comandos disponiveis:
  get                 - Enviar GET basico
  headers             - Testar headers de bypass
  uas                 - Testar User-Agents
  methods             - Testar metodos HTTP
  custom              - Requisicao customizada
  show <num>          - Mostrar resposta do historico
  replay <num>        - Reenviar requisicao do historico
  extract             - Extrair URLs de video
  quit                - Sair

{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}
        """)
        
        while True:
            try:
                cmd = input(f"\n{Colors.CYAN}[manipulator]{Colors.RESET} > ").strip().lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                
                elif cmd == 'get':
                    response = self.send_request('GET', url)
                    self.print_response(response)
                
                elif cmd == 'headers':
                    self.test_bypass_headers(url)
                
                elif cmd == 'uas':
                    self.test_user_agents(url)
                
                elif cmd == 'methods':
                    self.test_http_methods(url)
                
                elif cmd == 'extract':
                    response = self.send_request('GET', url)
                    if response:
                        videos = self.extract_video_from_html(response.text)
                        if videos:
                            print(f"\n{Colors.GREEN}[+] URLs de video encontradas:{Colors.RESET}")
                            for v in videos[:10]:
                                print(f"    - {v}")
                        else:
                            print(f"{Colors.YELLOW}[!] Nenhuma URL de video encontrada{Colors.RESET}")
                
                elif cmd == 'custom':
                    method = input("Metodo (GET/POST/etc): ").strip().upper() or "GET"
                    custom_url = input(f"URL [{url}]: ").strip() or url
                    
                    headers = {}
                    print("Headers (deixe em branco para terminar):")
                    while True:
                        h = input("  Header (Name: Value): ").strip()
                        if not h:
                            break
                        if ':' in h:
                            k, v = h.split(':', 1)
                            headers[k.strip()] = v.strip()
                    
                    response = self.send_request(method, custom_url, headers=headers)
                    self.print_response(response)
                
                elif cmd == 'history':
                    print(f"\n{Colors.YELLOW}[Historico]{Colors.RESET}")
                    for i, h in enumerate(self.history, 1):
                        print(f"  [{i}] {h['method']} -> {h['status']} ({h['length']} bytes)")
                
                elif cmd.startswith('show '):
                    try:
                        idx = int(cmd.split()[1]) - 1
                        if 0 <= idx < len(self.history):
                            # Reenviar para mostrar
                            h = self.history[idx]
                            response = self.send_request(h['method'], h['url'])
                            self.print_response(response)
                    except:
                        pass
                
                elif cmd.startswith('replay '):
                    try:
                        idx = int(cmd.split()[1]) - 1
                        if 0 <= idx < len(self.history):
                            h = self.history[idx]
                            response = self.send_request(h['method'], h['url'])
                            self.print_response(response)
                    except:
                        pass
                
                else:
                    print(f"{Colors.YELLOW}[!] Comando desconhecido: {cmd}{Colors.RESET}")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[!] Interrompido{Colors.RESET}")
                break
            except Exception as e:
                print(f"{Colors.RED}[!] Erro: {str(e)}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='KALI REQUEST MANIPULATOR - HTTP request manipulation')
    parser.add_argument('--url', '-u', type=str, required=True, help='Target URL')
    parser.add_argument('--method', '-m', type=str, default='GET', help='HTTP method')
    parser.add_argument('--header', '-H', action='append', help='Custom header (Name:Value)')
    parser.add_argument('--data', '-d', type=str, help='POST data')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--test-bypass', '-b', action='store_true', help='Test bypass headers')
    parser.add_argument('--test-uas', action='store_true', help='Test User-Agents')
    parser.add_argument('--extract', '-e', action='store_true', help='Extract video URLs')
    
    args = parser.parse_args()
    
    manipulator = RequestManipulator()
    
    if args.interactive:
        manipulator.interactive_mode(args.url)
    elif args.test_bypass:
        manipulator.test_bypass_headers(args.url)
    elif args.test_uas:
        manipulator.test_user_agents(args.url)
    else:
        # Requisicao simples
        headers = {}
        if args.header:
            for h in args.header:
                if ':' in h:
                    k, v = h.split(':', 1)
                    headers[k.strip()] = v.strip()
        
        response = manipulator.send_request(
            args.method, 
            args.url, 
            headers=headers,
            data=args.data
        )
        
        manipulator.print_response(response)
        
        if args.extract and response:
            videos = manipulator.extract_video_from_html(response.text)
            if videos:
                print(f"\n{Colors.GREEN}[+] URLs de video encontradas:{Colors.RESET}")
                for v in videos[:10]:
                    print(f"    - {v}")

if __name__ == '__main__':
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main()
