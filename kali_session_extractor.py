#!/usr/bin/env python3
"""
================================================================================
KALI SESSION EXTRACTOR - Extrator de Sessoes e Cookies
Ferramenta para analise e extracao de dados de sessao
================================================================================

Funcoes:
- Extrair cookies de respostas HTTP
- Analisar tokens JWT
- Decodificar sessoes
- Verificar flags de seguranca de cookies
- Replay de sessoes
- Enumeracao de sessoes

Uso: python kali_session_extractor.py --url https://playerembedapi.link/?v=xxx
"""

import argparse
import base64
import hashlib
import hmac
import json
import re
import time
from datetime import datetime
from urllib.parse import unquote

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

class SessionExtractor:
    """Extrator de sessoes e cookies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.extracted_cookies = {}
        self.tokens = []
    
    def extract_from_response(self, response):
        """Extrai informacoes de sessao de uma resposta"""
        result = {
            'cookies': {},
            'headers': {},
            'tokens': [],
            'security_flags': {}
        }
        
        # Extrair cookies
        if response.cookies:
            for cookie in response.cookies:
                result['cookies'][cookie.name] = {
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'secure': cookie.secure,
                    'httponly': cookie.has_nonstandard_attr('HttpOnly'),
                    'samesite': cookie.get_nonstandard_attr('SameSite', 'None'),
                    'expires': cookie.expires
                }
        
        # Extrair cookies de Set-Cookie header
        set_cookie = response.headers.get('Set-Cookie', '')
        if set_cookie:
            result['security_flags']['set_cookie_raw'] = set_cookie
            
            # Analisar flags
            result['security_flags']['has_secure'] = 'Secure' in set_cookie
            result['security_flags']['has_httponly'] = 'HttpOnly' in set_cookie
            result['security_flags']['has_samesite'] = 'SameSite' in set_cookie
        
        # Procurar tokens no corpo
        body = response.text
        
        # JWT tokens
        jwt_pattern = r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'
        jwt_matches = re.findall(jwt_pattern, body)
        for jwt in jwt_matches:
            if jwt not in [t['token'] for t in result['tokens']]:
                result['tokens'].append({
                    'type': 'JWT',
                    'token': jwt,
                    'decoded': self.decode_jwt(jwt)
                })
        
        # API keys
        api_key_patterns = [
            r'["\']?[aA][pP][iI][_-]?[kK][eE][yY]["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'["\']?[kK][eE][yY]["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,})["\']',
        ]
        for pattern in api_key_patterns:
            matches = re.findall(pattern, body)
            for match in matches:
                result['tokens'].append({
                    'type': 'API_KEY',
                    'token': match,
                    'decoded': None
                })
        
        # CSRF tokens
        csrf_pattern = r'["\']?csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']'
        csrf_matches = re.findall(csrf_pattern, body, re.I)
        for csrf in csrf_matches:
            result['tokens'].append({
                'type': 'CSRF',
                'token': csrf,
                'decoded': None
            })
        
        return result
    
    def decode_jwt(self, token):
        """Decodifica token JWT"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Header
            header_padding = 4 - len(parts[0]) % 4
            if header_padding != 4:
                parts[0] += '=' * header_padding
            header = json.loads(base64.urlsafe_b64decode(parts[0]))
            
            # Payload
            payload_padding = 4 - len(parts[1]) % 4
            if payload_padding != 4:
                parts[1] += '=' * payload_padding
            payload = json.loads(base64.urlsafe_b64decode(parts[1]))
            
            return {
                'header': header,
                'payload': payload,
                'signature': parts[2][:20] + '...'
            }
        except:
            return None
    
    def analyze_session(self, url):
        """Analisa sessao de uma URL"""
        print(f"{Colors.CYAN}[*] Analisando sessao: {url}{Colors.RESET}\n")
        
        response = self.session.get(url, timeout=30, verify=False)
        
        result = self.extract_from_response(response)
        
        # Imprimir resultados
        print(f"{Colors.GREEN}[+] Cookies recebidos:{Colors.RESET}")
        if result['cookies']:
            for name, cookie in result['cookies'].items():
                print(f"    {Colors.CYAN}{name}{Colors.RESET}:")
                print(f"      Valor: {cookie['value'][:50]}...")
                print(f"      Dominio: {cookie['domain']}")
                print(f"      Path: {cookie['path']}")
                print(f"      Secure: {cookie['secure']}")
                print(f"      HttpOnly: {cookie['httponly']}")
                print(f"      SameSite: {cookie['samesite']}")
        else:
            print(f"    {Colors.YELLOW}Nenhum cookie{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}[+] Tokens encontrados:{Colors.RESET}")
        if result['tokens']:
            for token in result['tokens']:
                print(f"    Tipo: {token['type']}")
                print(f"    Token: {token['token'][:50]}...")
                if token['decoded']:
                    print(f"    Decodificado: {json.dumps(token['decoded'], indent=2)}")
                print()
        else:
            print(f"    {Colors.YELLOW}Nenhum token{Colors.RESET}")
        
        # Analise de seguranca
        print(f"{Colors.GREEN}[+] Analise de seguranca:{Colors.RESET}")
        flags = result['security_flags']
        
        if flags.get('has_secure'):
            print(f"    {Colors.GREEN}[OK] Cookie usa flag Secure{Colors.RESET}")
        else:
            print(f"    {Colors.RED}[!] Cookie NAO usa flag Secure{Colors.RESET}")
        
        if flags.get('has_httponly'):
            print(f"    {Colors.GREEN}[OK] Cookie usa flag HttpOnly{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}[!] Cookie NAO usa flag HttpOnly (vulneravel a XSS){Colors.RESET}")
        
        if flags.get('has_samesite'):
            print(f"    {Colors.GREEN}[OK] Cookie usa SameSite{Colors.RESET}")
        else:
            print(f"    {Colors.YELLOW}[!] Cookie NAO usa SameSite (vulneravel a CSRF){Colors.RESET}")
        
        return result
    
    def test_session_fixation(self, url):
        """Testa vulnerabilidade de session fixation"""
        print(f"{Colors.CYAN}[*] Testando Session Fixation...{Colors.RESET}\n")
        
        # Primeira requisicao
        session1 = requests.Session()
        resp1 = session1.get(url, timeout=30, verify=False)
        cookies1 = dict(resp1.cookies)
        
        print(f"    Sessao 1: {len(cookies1)} cookies")
        for name, value in cookies1.items():
            print(f"      {name}: {value[:30]}...")
        
        # Segunda requisicao (nova sessao)
        session2 = requests.Session()
        resp2 = session2.get(url, timeout=30, verify=False)
        cookies2 = dict(resp2.cookies)
        
        print(f"\n    Sessao 2: {len(cookies2)} cookies")
        for name, value in cookies2.items():
            print(f"      {name}: {value[:30]}...")
        
        # Comparar
        if cookies1 == cookies2:
            print(f"\n    {Colors.RED}[VULNERAVEL] Cookies identicos - possivel session fixation{Colors.RESET}")
        else:
            print(f"\n    {Colors.GREEN}[OK] Cookies diferentes{Colors.RESET}")
    
    def replay_session(self, url, cookies_dict):
        """Reproduz sessao com cookies especificos"""
        print(f"{Colors.CYAN}[*] Reproduzindo sessao...{Colors.RESET}\n")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        })
        
        # Configurar cookies
        for name, value in cookies_dict.items():
            session.cookies.set(name, value)
            print(f"    Cookie set: {name}={value[:30]}...")
        
        response = session.get(url, timeout=30, verify=False)
        
        print(f"\n    {Colors.GREEN}Status: {response.status_code}{Colors.RESET}")
        print(f"    Tamanho: {len(response.content)} bytes")
        
        return response
    
    def extract_from_browser(self, url):
        """Extrai cookies usando browser (simulado)"""
        print(f"{Colors.CYAN}[*] Extraindo com browser automation...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Requer Playwright/Selenium instalado{Colors.RESET}")
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                page.goto(url)
                page.wait_for_load_state('networkidle')
                
                # Extrair cookies
                cookies = context.cookies()
                
                print(f"{Colors.GREEN}[+] Cookies extraidos: {len(cookies)}{Colors.RESET}")
                for cookie in cookies:
                    print(f"    {cookie['name']}: {cookie['value'][:50]}...")
                
                # Extrair localStorage/sessionStorage
                local_storage = page.evaluate('() => JSON.stringify(localStorage)')
                session_storage = page.evaluate('() => JSON.stringify(sessionStorage)')
                
                if local_storage and local_storage != '{}':
                    print(f"\n{Colors.GREEN}[+] localStorage:{Colors.RESET}")
                    print(f"    {local_storage[:200]}...")
                
                browser.close()
                
                return cookies
                
        except ImportError:
            print(f"{Colors.RED}[!] Playwright nao instalado. Execute: pip install playwright{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}[!] Erro: {str(e)}{Colors.RESET}")
            return None
    
    def brute_force_cookie(self, url, cookie_name, charset='abcdef0123456789', length=32):
        """Tenta adivinhar valor de cookie (demonstracao)"""
        print(f"{Colors.CYAN}[*] Brute force de cookie {cookie_name}...{Colors.RESET}")
        print(f"{Colors.YELLOW}[!] Apenas demonstracao - nao executando{Colors.RESET}")
        print(f"    Charset: {charset}")
        print(f"    Length: {length}")
        print(f"    Combinacoes possiveis: {len(charset) ** length}")

def main():
    parser = argparse.ArgumentParser(description='KALI SESSION EXTRACTOR - Session and cookie analysis')
    parser.add_argument('--url', '-u', type=str, required=True, help='Target URL')
    parser.add_argument('--test-fixation', '-f', action='store_true', help='Test session fixation')
    parser.add_argument('--replay', '-r', type=str, help='Replay session with cookies (JSON file)')
    parser.add_argument('--browser', '-b', action='store_true', help='Extract using browser')
    parser.add_argument('--save', '-s', type=str, help='Save session to file')
    
    args = parser.parse_args()
    
    print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                    KALI SESSION EXTRACTOR - Started
================================================================================{Colors.RESET}
    """)
    
    extractor = SessionExtractor()
    
    if args.browser:
        extractor.extract_from_browser(args.url)
    elif args.test_fixation:
        extractor.test_session_fixation(args.url)
    elif args.replay:
        with open(args.replay, 'r') as f:
            cookies = json.load(f)
        extractor.replay_session(args.url, cookies)
    else:
        result = extractor.analyze_session(args.url)
        
        if args.save:
            with open(args.save, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n{Colors.GREEN}[+] Sessao salva em: {args.save}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}")

if __name__ == '__main__':
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main()
