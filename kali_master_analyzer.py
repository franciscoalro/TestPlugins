#!/usr/bin/env python3
"""
================================================================================
KALI MASTER ANALYZER - Suite Completa de Analise
Integracao de todas as ferramentas estilo Kali Linux
================================================================================

Ferramentas integradas:
1. MITM Proxy - Interceptacao de trafego
2. JS Deobfuscator - Analise de JavaScript
3. Param Fuzzer - Fuzzing de parametros
4. Request Manipulator - Manipulacao de requests
5. Session Extractor - Analise de sessoes

Uso: python kali_master_analyzer.py --url https://playerembedapi.link/?v=xxx
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

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

class KaliMasterAnalyzer:
    """Orquestrador master de analise"""
    
    def __init__(self, target_url):
        self.target_url = target_url
        self.results = {}
        self.output_dir = f"kali_analysis_{int(time.time())}"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_full_analysis(self):
        """Executa analise completa"""
        print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                    KALI MASTER ANALYZER
                    Full Security Analysis Suite
================================================================================{Colors.RESET}

Target: {Colors.CYAN}{self.target_url}{Colors.RESET}
Output: {Colors.CYAN}{self.output_dir}/{Colors.RESET}

{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}
        """)
        
        # FASE 1: Analise de Requisicao Basica
        self.phase1_basic_request()
        
        # FASE 2: Analise de JavaScript
        self.phase2_js_analysis()
        
        # FASE 3: Extracao de Sessao
        self.phase3_session_extraction()
        
        # FASE 4: Fuzzing de Parametros
        self.phase4_param_fuzzing()
        
        # FASE 5: Relatorio Final
        self.generate_final_report()
    
    def phase1_basic_request(self):
        """Fase 1: Analise basica de requisicao"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[FASE 1/4] Analise Basica de Requisicao{Colors.RESET}\n")
        
        import requests
        
        try:
            # Requisicao basica
            response = requests.get(
                self.target_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                },
                timeout=30,
                verify=False
            )
            
            self.results['basic'] = {
                'status_code': response.status_code,
                'content_length': len(response.content),
                'content_type': response.headers.get('Content-Type', ''),
                'headers': dict(response.headers),
                'cookies': dict(response.cookies),
            }
            
            print(f"{Colors.GREEN}[+] Status: {response.status_code}{Colors.RESET}")
            print(f"{Colors.GREEN}[+] Tamanho: {len(response.content)} bytes{Colors.RESET}")
            print(f"{Colors.GREEN}[+] Content-Type: {response.headers.get('Content-Type', 'N/A')}{Colors.RESET}")
            
            # Salvar HTML
            html_file = os.path.join(self.output_dir, 'response.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"{Colors.GREEN}[+] HTML salvo: {html_file}{Colors.RESET}")
            
            # Analisar HTML
            self.analyze_html(response.text)
            
        except Exception as e:
            print(f"{Colors.RED}[!] Erro: {str(e)}{Colors.RESET}")
            self.results['basic'] = {'error': str(e)}
    
    def analyze_html(self, html):
        """Analisa conteudo HTML"""
        import re
        
        findings = {
            'forms': [],
            'scripts': [],
            'links': [],
            'inputs': [],
            'meta': {}
        }
        
        # Extrair scripts
        script_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
        findings['scripts'] = re.findall(script_pattern, html)
        
        # Extrair links
        link_pattern = r'href=["\']([^"\']+)["\']'
        links = re.findall(link_pattern, html)
        findings['links'] = [l for l in links if l.startswith('http')]
        
        # Extrair forms
        form_pattern = r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>'
        findings['forms'] = re.findall(form_pattern, html)
        
        # Extrair meta tags
        meta_pattern = r'<meta[^>]+content=["\']([^"\']+)["\'][^>]*>'
        meta_matches = re.findall(meta_pattern, html)
        findings['meta'] = {'count': len(meta_matches)}
        
        # Procurar por dados de video
        video_data = self.extract_video_data(html)
        findings['video_data'] = video_data
        
        self.results['html_analysis'] = findings
        
        print(f"\n{Colors.CYAN}[*] Analise HTML:{Colors.RESET}")
        print(f"    Scripts externos: {len(findings['scripts'])}")
        print(f"    Links externos: {len(findings['links'])}")
        print(f"    Forms: {len(findings['forms'])}")
        
        if video_data:
            print(f"\n{Colors.GREEN}[+] Dados de video encontrados:{Colors.RESET}")
            print(f"    Slug: {video_data.get('slug', 'N/A')}")
            print(f"    MD5 ID: {video_data.get('md5_id', 'N/A')}")
    
    def extract_video_data(self, html):
        """Extrai dados de video do HTML"""
        import base64
        import re
        
        # Procurar campo datas
        match = re.search(r'const\s+datas\s*=\s*"([^"]+)"', html)
        if match:
            datas_b64 = match.group(1)
            
            # Padding
            padding = 4 - len(datas_b64) % 4
            if padding != 4:
                datas_b64 += '=' * padding
            
            try:
                decoded = base64.b64decode(datas_b64)
                decoded_str = decoded.decode('utf-8', errors='replace')
                
                # Extrair campos
                slug = re.search(r'"slug":"([^"]+)"', decoded_str)
                md5_id = re.search(r'"md5_id":(\d+)', decoded_str)
                user_id = re.search(r'"user_id":(\d+)', decoded_str)
                
                return {
                    'slug': slug.group(1) if slug else None,
                    'md5_id': int(md5_id.group(1)) if md5_id else None,
                    'user_id': int(user_id.group(1)) if user_id else None,
                }
            except:
                pass
        
        return None
    
    def phase2_js_analysis(self):
        """Fase 2: Analise de JavaScript"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[FASE 2/4] Analise de JavaScript{Colors.RESET}\n")
        
        js_files = self.results.get('html_analysis', {}).get('scripts', [])
        
        # Filtrar apenas JS relevante
        relevant_js = [js for js in js_files if 'player' in js or 'core' in js or 'bundle' in js]
        
        if not relevant_js:
            print(f"{Colors.YELLOW}[!] Nenhum arquivo JS relevante encontrado{Colors.RESET}")
            return
        
        print(f"{Colors.CYAN}[*] Arquivos JS para analise:{Colors.RESET}")
        for js in relevant_js[:5]:
            print(f"    - {js}")
        
        # Download e analise do core.bundle.js se disponivel
        core_js = [js for js in js_files if 'core.bundle' in js]
        if core_js:
            self.analyze_js_file(core_js[0])
    
    def analyze_js_file(self, url):
        """Download e analise de arquivo JS"""
        import requests
        
        try:
            print(f"\n{Colors.CYAN}[*] Baixando: {url}{Colors.RESET}")
            response = requests.get(url, timeout=30)
            js_code = response.text
            
            # Analise basica
            analysis = {
                'size': len(js_code),
                'has_sotrym': 'SoTrym' in js_code,
                'has_crypto': 'crypto.subtle' in js_code,
                'has_jwplayer': 'jwplayer' in js_code,
            }
            
            self.results['js_analysis'] = analysis
            
            print(f"{Colors.GREEN}[+] Analise JS:{Colors.RESET}")
            print(f"    Tamanho: {analysis['size']:,} bytes")
            print(f"    SoTrym: {'Sim' if analysis['has_sotrym'] else 'Nao'}")
            print(f"    Crypto API: {'Sim' if analysis['has_crypto'] else 'Nao'}")
            print(f"    JWPlayer: {'Sim' if analysis['has_jwplayer'] else 'Nao'}")
            
            # Salvar arquivo
            js_file = os.path.join(self.output_dir, 'core_bundle.js')
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(js_code)
            print(f"{Colors.GREEN}[+] JS salvo: {js_file}{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}[!] Erro ao baixar JS: {str(e)}{Colors.RESET}")
    
    def phase3_session_extraction(self):
        """Fase 3: Extracao de sessao"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[FASE 3/4] Analise de Sessao{Colors.RESET}\n")
        
        cookies = self.results.get('basic', {}).get('cookies', {})
        
        print(f"{Colors.GREEN}[+] Cookies da sessao:{Colors.RESET}")
        if cookies:
            for name, value in cookies.items():
                print(f"    {name}: {value[:50]}...")
        else:
            print(f"    {Colors.YELLOW}Nenhum cookie{Colors.RESET}")
        
        # Headers de seguranca
        headers = self.results.get('basic', {}).get('headers', {})
        security_headers = {
            'X-Frame-Options': headers.get('X-Frame-Options', 'N/A'),
            'X-XSS-Protection': headers.get('X-XSS-Protection', 'N/A'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options', 'N/A'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security', 'N/A'),
            'Content-Security-Policy': headers.get('Content-Security-Policy', 'N/A'),
        }
        
        self.results['security_headers'] = security_headers
        
        print(f"\n{Colors.CYAN}[*] Headers de seguranca:{Colors.RESET}")
        for header, value in security_headers.items():
            color = Colors.GREEN if value != 'N/A' else Colors.RED
            print(f"    {header}: {color}{value}{Colors.RESET}")
    
    def phase4_param_fuzzing(self):
        """Fase 4: Fuzzing de parametros"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}[FASE 4/4] Fuzzing de Parametros{Colors.RESET}\n")
        
        # URLs construidas a partir dos dados
        video_data = self.results.get('html_analysis', {}).get('video_data', {})
        
        if video_data and video_data.get('slug'):
            constructed_urls = [
                f"https://{video_data['slug']}.sssrr.org/sora/{video_data['md5_id']}/",
                f"https://cdn.sssrr.org/sora/{video_data['md5_id']}/",
            ]
            
            print(f"{Colors.GREEN}[+] URLs CDN construidas:{Colors.RESET}")
            for url in constructed_urls:
                print(f"    - {url}")
            
            self.results['constructed_urls'] = constructed_urls
            
            # Testar URLs
            import requests
            
            print(f"\n{Colors.CYAN}[*] Testando URLs...{Colors.RESET}")
            for url in constructed_urls:
                try:
                    resp = requests.head(url, timeout=10, allow_redirects=False, verify=False)
                    status_color = Colors.GREEN if resp.status_code == 200 else Colors.YELLOW if resp.status_code < 400 else Colors.RED
                    print(f"    {url[:60]}... -> {status_color}{resp.status_code}{Colors.RESET}")
                except Exception as e:
                    print(f"    {url[:60]}... -> {Colors.RED}ERROR{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!] Dados insuficientes para construir URLs{Colors.RESET}")
    
    def generate_final_report(self):
        """Gera relatorio final"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}")
        print(f"                            RELATORIO FINAL")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}\n")
        
        # Resumo
        print(f"{Colors.CYAN}Target:{Colors.RESET} {self.target_url}")
        print(f"{Colors.CYAN}Data:{Colors.RESET} {datetime.now().isoformat()}")
        print(f"{Colors.CYAN}Output:{Colors.RESET} {self.output_dir}/")
        
        # Estatisticas
        print(f"\n{Colors.BOLD}Estatisticas:{Colors.RESET}")
        basic = self.results.get('basic', {})
        print(f"    Status HTTP: {basic.get('status_code', 'N/A')}")
        print(f"    Tamanho: {basic.get('content_length', 0):,} bytes")
        print(f"    Cookies: {len(basic.get('cookies', {}))}")
        
        html = self.results.get('html_analysis', {})
        print(f"    Scripts: {len(html.get('scripts', []))}")
        
        video_data = html.get('video_data', {})
        if video_data:
            print(f"\n{Colors.BOLD}Dados de Video:{Colors.RESET}")
            print(f"    Slug: {video_data.get('slug')}")
            print(f"    MD5 ID: {video_data.get('md5_id')}")
            print(f"    User ID: {video_data.get('user_id')}")
        
        # Salvar JSON completo
        report_file = os.path.join(self.output_dir, 'full_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n{Colors.GREEN}[+] Relatorio completo salvo: {report_file}{Colors.RESET}")
        
        # Recomendacoes
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Recomendacoes:{Colors.RESET}")
        
        if video_data and video_data.get('slug'):
            print(f"""
1. Tentar acessar URLs CDN construidas:
   - https://{video_data['slug']}.sssrr.org/sora/{video_data['md5_id']}/
   - Usar headers: Referer={self.target_url}

2. Usar WebView para extracao dinamica:
   - Interceptar requisicoes para sssrr.org
   - Timeout de 30s

3. Analisar core.bundle.js para entender SoTrym()
   - Procurar funcao de decriptacao
   - Extrair algoritmo de criptografia
""")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}\n")

def main():
    parser = argparse.ArgumentParser(description='KALI MASTER ANALYZER - Complete security analysis suite')
    parser.add_argument('--url', '-u', type=str, required=True, help='Target URL')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick mode (basic only)')
    
    args = parser.parse_args()
    
    analyzer = KaliMasterAnalyzer(args.url)
    analyzer.run_full_analysis()

if __name__ == '__main__':
    from urllib3.exceptions import InsecureRequestWarning
    import requests
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main()
