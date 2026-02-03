#!/usr/bin/env python3
"""
================================================================================
KALI MITM PROXY - Interceptador de Trafego HTTP/HTTPS
Ferramenta tipo Burp Suite / OWASP ZAP para analise de requisicoes
================================================================================

Funcoes:
- Interceptar requests/responses
- Modificar headers em tempo real
- Extrair URLs de video
- Salvar sessao para analise
- Replay de requisicoes

Uso: python kali_mitm_proxy.py --target playerembedapi.link
"""

import argparse
import json
import re
import ssl
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs, urlencode
import http.client as http_client

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

class RequestResponse:
    """Representa um par request/response interceptado"""
    def __init__(self):
        self.id = int(time.time() * 1000)
        self.timestamp = datetime.now().isoformat()
        self.method = ""
        self.url = ""
        self.path = ""
        self.headers_request = {}
        self.headers_response = {}
        self.body_request = ""
        self.body_response = ""
        self.status_code = 0
        self.content_type = ""
        self.size = 0
        self.is_video = False
        self.is_api = False

class MITMProxyHandler(BaseHTTPRequestHandler):
    """Handler do proxy MITM"""
    
    # Lista global de requests capturados
    captured_requests = []
    target_domain = ""
    intercept_mode = True
    modify_headers = {}
    
    def log_message(self, format, *args):
        # Silenciar logs do servidor
        pass
    
    def do_GET(self):
        self.handle_request("GET")
    
    def do_POST(self):
        self.handle_request("POST")
    
    def do_OPTIONS(self):
        self.handle_request("OPTIONS")
    
    def handle_request(self, method):
        """Processa a requisicao interceptada"""
        
        # Parse da URL
        parsed = urlparse(self.path)
        target_url = self.path
        
        # Se nao for URL completa, usar headers
        if not parsed.scheme:
            host = self.headers.get('Host', self.target_domain)
            target_url = f"https://{host}{self.path}"
        
        # Criar objeto de captura
        capture = RequestResponse()
        capture.method = method
        capture.url = target_url
        capture.path = parsed.path
        
        print(f"\n{Colors.CYAN}[{'INTERCEPTED' if self.intercept_mode else 'PASSING'}] {method} {target_url[:80]}...{Colors.RESET}")
        
        # Ler body se existir
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            capture.body_request = self.rfile.read(content_length).decode('utf-8', errors='ignore')
        
        # Copiar headers
        for header, value in self.headers.items():
            capture.headers_request[header] = value
        
        # Aplicar modificacoes de headers
        headers = dict(self.headers)
        for key, value in self.modify_headers.items():
            headers[key] = value
            print(f"{Colors.YELLOW}[MODIFIED] {key}: {value}{Colors.RESET}")
        
        # Headers padrao para bypass
        headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        headers.setdefault('Accept', '*/*')
        headers.setdefault('Accept-Language', 'pt-BR,pt;q=0.9,en;q=0.8')
        headers.setdefault('Accept-Encoding', 'gzip, deflate, br')
        headers.setdefault('DNT', '1')
        headers.setdefault('Connection', 'keep-alive')
        
        try:
            # Fazer requisicao real
            response = requests.request(
                method=method,
                url=target_url,
                headers=headers,
                data=capture.body_request if capture.body_request else None,
                timeout=30,
                allow_redirects=True,
                verify=False  # Ignorar SSL para MITM
            )
            
            # Capturar response
            capture.status_code = response.status_code
            capture.headers_response = dict(response.headers)
            capture.body_response = response.text
            capture.size = len(response.content)
            capture.content_type = response.headers.get('Content-Type', '')
            
            # Detectar se eh video
            video_patterns = [r'\.m3u8', r'\.mp4', r'video/', r'sssrr\.org']
            if any(re.search(p, target_url, re.I) for p in video_patterns):
                capture.is_video = True
                print(f"{Colors.GREEN}[VIDEO DETECTED] {target_url}{Colors.RESET}")
            
            # Detectar se eh API
            api_patterns = [r'/api/', r'/sora/', r'\.json', r'future']
            if any(re.search(p, target_url, re.I) for p in api_patterns):
                capture.is_api = True
                print(f"{Colors.MAGENTA}[API DETECTED] {target_url}{Colors.RESET}")
            
            # Salvar captura
            self.captured_requests.append(capture)
            
            # Extrair URLs de video do response
            if 'text/html' in capture.content_type or 'application/javascript' in capture.content_type:
                self.extract_video_urls(capture.body_response, target_url)
            
            # Enviar response ao cliente
            self.send_response(response.status_code)
            
            # Filtrar headers problematicos
            skip_headers = ['transfer-encoding', 'content-encoding', 'content-length', 'connection']
            for header, value in response.headers.items():
                if header.lower() not in skip_headers:
                    try:
                        self.send_header(header, value)
                    except:
                        pass
            
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"{Colors.RED}[ERROR] {str(e)}{Colors.RESET}")
            self.send_error(502, f"Proxy Error: {str(e)}")
    
    def extract_video_urls(self, content, source_url):
        """Extrai URLs de video do conteudo"""
        patterns = [
            r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
            r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)',
            r'(https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*)',
        ]
        
        found = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match not in found:
                    found.add(match)
                    print(f"{Colors.GREEN}[EXTRACTED] {match[:80]}...{Colors.RESET}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP multithread"""
    allow_reuse_address = True
    daemon_threads = True

class KaliMITMProxy:
    """Proxy MITM principal"""
    
    def __init__(self, port=8080, target=""):
        self.port = port
        self.target = target
        self.server = None
        self.running = False
        self.captured_requests = []
    
    def start(self):
        """Inicia o proxy"""
        MITMProxyHandler.target_domain = self.target
        
        self.server = ThreadedHTTPServer(('0.0.0.0', self.port), MITMProxyHandler)
        self.running = True
        
        print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                        KALI MITM PROXY - Started
================================================================================{Colors.RESET}

Proxy listening on: {Colors.CYAN}http://127.0.0.1:{self.port}{Colors.RESET}
Target domain: {Colors.YELLOW}{self.target or "Any"}{Colors.RESET}

Configure your browser to use: 127.0.0.1:{self.port}
Or use: curl -x http://127.0.0.1:{self.port} <url>

Commands:
  - Press Ctrl+C to stop
  - Requests will be intercepted automatically

{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}
        """)
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Para o proxy"""
        self.running = False
        if self.server:
            self.server.shutdown()
        
        print(f"\n{Colors.YELLOW}[*] Proxy stopped{Colors.RESET}")
        self.save_session()
    
    def save_session(self):
        """Salva sessao capturada"""
        if not MITMProxyHandler.captured_requests:
            print(f"{Colors.YELLOW}[!] No requests captured{Colors.RESET}")
            return
        
        filename = f"mitm_session_{int(time.time())}.json"
        
        session_data = []
        for req in MITMProxyHandler.captured_requests:
            session_data.append({
                'id': req.id,
                'timestamp': req.timestamp,
                'method': req.method,
                'url': req.url,
                'path': req.path,
                'status_code': req.status_code,
                'content_type': req.content_type,
                'size': req.size,
                'is_video': req.is_video,
                'is_api': req.is_api,
                'headers_request': req.headers_request,
                'headers_response': req.headers_response,
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.GREEN}[+] Session saved: {filename} ({len(session_data)} requests){Colors.RESET}")
        
        # Gerar relatorio de videos
        videos = [r for r in MITMProxyHandler.captured_requests if r.is_video]
        if videos:
            print(f"\n{Colors.GREEN}[+] Videos found: {len(videos)}{Colors.RESET}")
            for v in videos:
                print(f"    - {v.url}")

def main():
    parser = argparse.ArgumentParser(description='KALI MITM PROXY - Intercept HTTP/HTTPS traffic')
    parser.add_argument('--port', '-p', type=int, default=8080, help='Proxy port (default: 8080)')
    parser.add_argument('--target', '-t', type=str, default='', help='Target domain to intercept')
    parser.add_argument('--modify-header', '-m', action='append', help='Modify header (format: "Name:Value")')
    
    args = parser.parse_args()
    
    # Processar modificacoes de headers
    modify_headers = {}
    if args.modify_header:
        for header in args.modify_header:
            if ':' in header:
                key, value = header.split(':', 1)
                modify_headers[key.strip()] = value.strip()
    
    MITMProxyHandler.modify_headers = modify_headers
    
    proxy = KaliMITMProxy(port=args.port, target=args.target)
    proxy.start()

if __name__ == '__main__':
    # Desabilitar warnings SSL
    from urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    main()
