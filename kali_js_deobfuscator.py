#!/usr/bin/env python3
"""
================================================================================
KALI JS DEOBFUSCATOR - Analisador e Deobfuscador de JavaScript
Ferramenta tipo JSDetox / de4js para analise de codigo ofuscado
================================================================================

Funcoes:
- Detectar tipo de ofuscacao
- Deobfuscar codigo P.A.C.K.E.R.
- Extrair strings ofuscadas
- Analisar funcoes de criptografia
- Reconstruir codigo legivel
- Encontrar endpoints de API

Uso: python kali_js_deobfuscator.py --file core.bundle.js
"""

import argparse
import base64
import json
import re
import sys
from pathlib import Path
from colorama import Fore, Style, init
from urllib.parse import urlparse

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

class JSDeobfuscator:
    """Deobfuscador de JavaScript"""
    
    def __init__(self, js_code):
        self.code = js_code
        self.original_code = js_code
        self.obfuscation_type = None
        self.strings = []
        self.functions = []
        self.endpoints = []
        self.crypto_calls = []
        self.variables = {}
    
    def analyze(self):
        """Executa analise completa"""
        print(f"{Colors.CYAN}[*] Analisando codigo JavaScript...{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Tamanho: {len(self.code)} caracteres{Colors.RESET}\n")
        
        # 1. Detectar tipo de ofuscacao
        self.detect_obfuscation()
        
        # 2. Extrair strings
        self.extract_strings()
        
        # 3. Extrair funcoes
        self.extract_functions()
        
        # 4. Procurar chamadas de criptografia
        self.find_crypto_calls()
        
        # 5. Extrair URLs/endpoints
        self.extract_endpoints()
        
        # 6. Analisar variaveis globais
        self.analyze_variables()
        
        return self.generate_report()
    
    def detect_obfuscation(self):
        """Detecta o tipo de ofuscacao"""
        patterns = {
            'P.A.C.K.E.R.': r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*[dr]\s*\)',
            'Javascript Obfuscator': r'var _0x[a-f0-9]+\s*=',
            'Obfuscator.io': r'var _0x\w+\s*=\s*\[',
            'JJEncode': r'\$=~\[\]',
            'AAEncode': r'ﾟωﾟﾉ',
            'URL Encoded': r'%[0-9A-Fa-f]{2}',
            'Hex Encoded': r'\\x[0-9A-Fa-f]{2}',
            'Unicode Escape': r'\\u[0-9A-Fa-f]{4}',
            'Base64': r'[A-Za-z0-9+/]{100,}={0,2}',
        }
        
        detected = []
        for name, pattern in patterns.items():
            if re.search(pattern, self.code):
                detected.append(name)
        
        self.obfuscation_type = detected if detected else ['None or Unknown']
        
        print(f"{Colors.GREEN}[+] Tipo de ofuscacao detectada:{Colors.RESET}")
        for dtype in self.obfuscation_type:
            print(f"    - {dtype}")
        print()
    
    def unpack_packer(self):
        """Desempacota codigo P.A.C.K.E.R."""
        packer_pattern = r'eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,\s*([dr])\s*\)\s*\{([^}]+)\}\s*\(\s*([^)]+)\)\s*\)'
        match = re.search(packer_pattern, self.code, re.DOTALL)
        
        if match:
            print(f"{Colors.YELLOW}[*] Desempacotando P.A.C.K.E.R...{Colors.RESET}")
            try:
                # Extrair parametros
                p = match.group(3).strip().strip("'")
                # Implementacao simplificada - em caso real seria mais complexo
                return f"[P.A.C.K.E.R. detected - manual unpacking required]\nParams: {p[:100]}..."
            except:
                pass
        return None
    
    def extract_strings(self):
        """Extrai strings do codigo"""
        # Strings entre aspas
        patterns = [
            (r'"([^"\\]*(?:\\.[^"\\]*)*)"', 'double'),
            (r"'([^'\\]*(?:\\.[^'\\]*)*)'", 'single'),
            (r'`([^`\\]*(?:\\.[^`\\]*)*)`', 'template'),
        ]
        
        for pattern, quote_type in patterns:
            matches = re.findall(pattern, self.code)
            for match in matches:
                if len(match) > 5:  # Ignorar strings muito curtas
                    self.strings.append({
                        'value': match,
                        'type': quote_type,
                        'length': len(match)
                    })
        
        # Ordenar por tamanho (maiores primeiro - provavelmente mais importantes)
        self.strings.sort(key=lambda x: x['length'], reverse=True)
        
        print(f"{Colors.GREEN}[+] Strings extraidas: {len(self.strings)}{Colors.RESET}")
        
        # Mostrar strings suspeitas
        suspicious = [s for s in self.strings if self.is_suspicious_string(s['value'])]
        if suspicious:
            print(f"{Colors.YELLOW}[+] Strings suspeitas:{Colors.RESET}")
            for s in suspicious[:10]:
                print(f"    [{s['type']}] {s['value'][:80]}...")
        print()
    
    def is_suspicious_string(self, s):
        """Verifica se string eh suspeita (URLs, tokens, etc)"""
        patterns = [
            r'https?://',
            r'[a-f0-9]{32}',  # MD5
            r'[A-Za-z0-9+/]{40,}={0,2}',  # Base64
            r'api[_/]',
            r'key[_/]',
            r'token',
            r'encrypt',
            r'decrypt',
        ]
        return any(re.search(p, s, re.I) for p in patterns)
    
    def extract_functions(self):
        """Extrai definicoes de funcoes"""
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)\s*\{',
            r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)\s*\{',
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)\s*\{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
            r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.code)
            for match in matches:
                if isinstance(match, tuple):
                    name, params = match[0], match[1] if len(match) > 1 else ''
                else:
                    name, params = match, ''
                self.functions.append({
                    'name': name,
                    'params': params,
                    'suspicious': self.is_suspicious_function(name)
                })
        
        print(f"{Colors.GREEN}[+] Funcoes encontradas: {len(self.functions)}{Colors.RESET}")
        
        # Mostrar funcoes suspeitas
        suspicious = [f for f in self.functions if f['suspicious']]
        if suspicious:
            print(f"{Colors.YELLOW}[+] Funcoes suspeitas:{Colors.RESET}")
            for f in suspicious[:15]:
                print(f"    - {f['name']}({f['params']})")
        print()
    
    def is_suspicious_function(self, name):
        """Verifica se nome de funcao eh suspeito"""
        suspicious = [
            'encrypt', 'decrypt', 'crypto', 'aes', 'xor', 'hash',
            'decode', 'encode', 'parse', 'stringify', 'unpack',
            'obfuscate', 'deobfuscate', 'eval', 'exec',
            'sotrym', 'player', 'video', 'source', 'stream',
            'api', 'request', 'fetch', 'ajax', 'xhr',
            'key', 'token', 'auth', 'sign', 'verify'
        ]
        return any(s in name.lower() for s in suspicious)
    
    def find_crypto_calls(self):
        """Procura por chamadas de criptografia"""
        patterns = {
            'crypto.subtle.decrypt': r'crypto\.subtle\.decrypt\s*\(([^)]+)\)',
            'crypto.subtle.encrypt': r'crypto\.subtle\.encrypt\s*\(([^)]+)\)',
            'crypto.subtle.importKey': r'crypto\.subtle\.importKey\s*\(([^)]+)\)',
            'AES.decrypt': r'AES\.decrypt\s*\(([^)]+)\)',
            'AES.encrypt': r'AES\.encrypt\s*\(([^)]+)\)',
            'CryptoJS': r'CryptoJS\.(\w+)\s*\(([^)]+)\)',
            'atob': r'atob\s*\(([^)]+)\)',
            'btoa': r'btoa\s*\(([^)]+)\)',
            'JSON.parse': r'JSON\.parse\s*\(([^)]+)\)',
            'JSON.stringify': r'JSON\.stringify\s*\(([^)]+)\)',
        }
        
        for algo, pattern in patterns.items():
            matches = re.findall(pattern, self.code)
            if matches:
                self.crypto_calls.append({
                    'algorithm': algo,
                    'matches': matches[:5],  # Limitar
                    'count': len(matches)
                })
        
        print(f"{Colors.GREEN}[+] Chamadas de criptografia: {len(self.crypto_calls)} tipos{Colors.RESET}")
        for call in self.crypto_calls:
            print(f"    - {call['algorithm']}: {call['count']} ocorrencias")
        print()
    
    def extract_endpoints(self):
        """Extrai endpoints de API"""
        # Padroes de URL em strings
        url_pattern = r'(https?://[^\s"\'<>]+)'
        
        for s in self.strings:
            url_match = re.search(url_pattern, s['value'])
            if url_match:
                url = url_match.group(1)
                parsed = urlparse(url)
                if parsed.netloc and parsed.path:
                    self.endpoints.append({
                        'url': url,
                        'domain': parsed.netloc,
                        'path': parsed.path
                    })
        
        # Tambem procurar em todo o codigo
        all_urls = re.findall(url_pattern, self.code)
        for url in all_urls:
            if url not in [e['url'] for e in self.endpoints]:
                parsed = urlparse(url)
                if parsed.netloc:
                    self.endpoints.append({
                        'url': url,
                        'domain': parsed.netloc,
                        'path': parsed.path
                    })
        
        # Remover duplicatas
        seen = set()
        unique = []
        for e in self.endpoints:
            if e['url'] not in seen:
                seen.add(e['url'])
                unique.append(e)
        self.endpoints = unique
        
        print(f"{Colors.GREEN}[+] Endpoints encontrados: {len(self.endpoints)}{Colors.RESET}")
        
        # Agrupar por dominio
        by_domain = {}
        for e in self.endpoints:
            domain = e['domain']
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(e['path'])
        
        for domain, paths in by_domain.items():
            print(f"    {Colors.CYAN}{domain}{Colors.RESET}")
            for path in paths[:5]:
                print(f"      {path}")
        print()
    
    def analyze_variables(self):
        """Analisa variaveis globais"""
        # Procurar por variaveis importantes
        patterns = {
            'api_url': r'(api[_-]?url|api[_-]?endpoint)\s*=\s*["\']([^"\']+)["\']',
            'base_url': r'(base[_-]?url|base[_-]?path)\s*=\s*["\']([^"\']+)["\']',
            'config': r'(config|configuration)\s*=\s*(\{[^}]+\})',
            'key': r'(api[_-]?key|secret[_-]?key)\s*=\s*["\']([^"\']+)["\']',
        }
        
        for var_name, pattern in patterns.items():
            matches = re.findall(pattern, self.code, re.I)
            if matches:
                self.variables[var_name] = matches[:3]
        
        if self.variables:
            print(f"{Colors.GREEN}[+] Variaveis importantes:{Colors.RESET}")
            for var, values in self.variables.items():
                print(f"    - {var}: {len(values)} ocorrencias")
            print()
    
    def find_sotrym_function(self):
        """Procura especificamente pela funcao SoTrym"""
        patterns = [
            r'window\.SoTrym\s*=\s*function\s*\(([^)]+)\)\s*\{([^}]+)\}',
            r'function\s+SoTrym\s*\(([^)]+)\)\s*\{([^}]+)\}',
            r'var\s+SoTrym\s*=\s*function\s*\(([^)]+)\)',
            r'SoTrym\s*:\s*function\s*\(([^)]+)\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.code, re.DOTALL)
            if match:
                return {
                    'params': match.group(1),
                    'body': match.group(2) if len(match.groups()) > 1 else None
                }
        return None
    
    def generate_report(self):
        """Gera relatorio da analise"""
        report = {
            'obfuscation_type': self.obfuscation_type,
            'statistics': {
                'code_size': len(self.code),
                'strings_count': len(self.strings),
                'functions_count': len(self.functions),
                'endpoints_count': len(self.endpoints),
                'crypto_calls_count': sum(c['count'] for c in self.crypto_calls),
            },
            'suspicious_functions': [f['name'] for f in self.functions if f['suspicious']][:20],
            'suspicious_strings': [s['value'] for s in self.strings if self.is_suspicious_string(s['value'])][:20],
            'endpoints': [{'url': e['url'], 'domain': e['domain']} for e in self.endpoints[:20]],
            'crypto_calls': self.crypto_calls,
            'variables': self.variables,
        }
        
        # Verificar SoTrym especificamente
        sotrym = self.find_sotrym_function()
        report['sotrym_found'] = sotrym is not None
        if sotrym:
            report['sotrym_params'] = sotrym['params']
            report['sotrym_body_preview'] = sotrym['body'][:500] if sotrym['body'] else None
        
        return report
    
    def beautify(self):
        """Tenta formatar o codigo de forma legivel"""
        # Substituir strings ofuscadas
        code = self.code
        
        # Hex escape sequences
        code = re.sub(r'\\x([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), code)
        
        # Unicode escape sequences
        code = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), code)
        
        # Adicionar quebras de linha
        code = re.sub(r';', ';\n', code)
        code = re.sub(r'\{', '{\n', code)
        code = re.sub(r'\}', '\n}', code)
        
        return code

def main():
    parser = argparse.ArgumentParser(description='KALI JS DEOBFUSCATOR - Analyze obfuscated JavaScript')
    parser.add_argument('--file', '-f', type=str, help='JavaScript file to analyze')
    parser.add_argument('--output', '-o', type=str, help='Output file for report')
    parser.add_argument('--beautify', '-b', action='store_true', help='Beautify and save code')
    
    args = parser.parse_args()
    
    print(f"""
{Colors.BOLD}{Colors.GREEN}================================================================================
                    KALI JS DEOBFUSCATOR - Started
================================================================================{Colors.RESET}
    """)
    
    # Ler arquivo
    if args.file:
        with open(args.file, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
    else:
        # Tentar arquivo padrao
        default_file = 'core_bundle.js'
        if Path(default_file).exists():
            print(f"{Colors.YELLOW}[*] Usando arquivo padrao: {default_file}{Colors.RESET}\n")
            with open(default_file, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
        else:
            print(f"{Colors.RED}[!] Arquivo nao especificado. Use --file{Colors.RESET}")
            sys.exit(1)
    
    # Analisar
    deobf = JSDeobfuscator(code)
    report = deobf.analyze()
    
    # Imprimir resumo
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}")
    print(f"                            RESUMO DA ANALISE")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.RESET}\n")
    
    print(f"Tipo de ofuscacao: {', '.join(report['obfuscation_type'])}")
    print(f"Tamanho do codigo: {report['statistics']['code_size']:,} caracteres")
    print(f"Strings: {report['statistics']['strings_count']}")
    print(f"Funcoes: {report['statistics']['functions_count']}")
    print(f"Endpoints: {report['statistics']['endpoints_count']}")
    print(f"Chamadas crypto: {report['statistics']['crypto_calls_count']}")
    print(f"SoTrym encontrado: {'Sim' if report['sotrym_found'] else 'Nao'}")
    
    if report['sotrym_found']:
        print(f"{Colors.GREEN}[+] SoTrym params: {report['sotrym_params']}{Colors.RESET}")
    
    # Salvar relatorio
    output_file = args.output or f"js_analysis_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.GREEN}[+] Relatorio salvo: {output_file}{Colors.RESET}")
    
    # Beautify se solicitado
    if args.beautify:
        beautified = deobf.beautify()
        beautify_file = output_file.replace('.json', '_beautified.js')
        with open(beautify_file, 'w', encoding='utf-8') as f:
            f.write(beautified)
        print(f"{Colors.GREEN}[+] Codigo formatado: {beautify_file}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}================================================================================{Colors.RESET}")

if __name__ == '__main__':
    import time
    main()
