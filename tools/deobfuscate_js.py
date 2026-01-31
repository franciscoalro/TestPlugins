#!/usr/bin/env python3
"""
JavaScript Deobfuscator - MaxSeries Reverse Engineering
Extracts and deobfuscates JavaScript from streaming sites

Usage:
    python deobfuscate_js.py https://playerembedapi.link
"""

import requests
import re
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_js_from_page(url):
    """Extract all JavaScript from a page"""
    print(f"[1] Fetching page: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    scripts = []
    
    # Inline scripts
    for script in soup.find_all('script'):
        if script.string and len(script.string.strip()) > 50:
            scripts.append(('inline', script.string))
    
    # External scripts
    for script in soup.find_all('script', src=True):
        src = script['src']
        if not src.startswith('http'):
            src = urljoin(url, src)
        
        try:
            print(f"  Downloading: {src[:60]}...")
            js_content = requests.get(src, headers=headers).text
            scripts.append((src, js_content))
        except Exception as e:
            print(f"  Failed: {e}")
    
    return scripts

def find_crypto_functions(js_code):
    """Identify cryptography functions in JavaScript"""
    patterns = {
        'Web Crypto API': r'crypto\.subtle\.(encrypt|decrypt|importKey)',
        'CryptoJS': r'CryptoJS\.(AES|DES|TripleDES|Rabbit|RC4)',
        'Base64': r'(atob|btoa)\s*\(',
        'Byte Manipulation': r'\.charCodeAt\s*\(',
        'JWPlayer Setup': r'jwplayer\([^)]+\)\.setup\s*\(',
        'Fetch API': r'fetch\s*\([^)]+\)',
        'XMLHttpRequest': r'new\s+XMLHttpRequest\s*\(',
    }
    
    findings = {}
    for name, pattern in patterns.items():
        matches = re.findall(f'.{{0,80}}{pattern}.{{0,80}}', js_code, re.IGNORECASE)
        if matches:
            findings[name] = matches[:3]  # Limit to 3 examples
    
    return findings

def extract_jwplayer_config(js_code):
    """Extract JWPlayer configuration"""
    # Pattern: jwplayer('player').setup({...})
    pattern = r'jwplayer\([^)]+\)\.setup\s*\((\{[^}]+\})\)'
    matches = re.findall(pattern, js_code, re.DOTALL)
    
    configs = []
    for match in matches:
        # Try to extract file/sources
        file_match = re.search(r'["\']file["\']\s*:\s*["\']([^"\']+)["\']', match)
        if file_match:
            configs.append({'type': 'file', 'url': file_match.group(1)})
        
        sources_match = re.search(r'["\']sources["\']\s*:\s*\[([^\]]+)\]', match)
        if sources_match:
            configs.append({'type': 'sources', 'data': sources_match.group(1)})
    
    return configs

def main():
    if len(sys.argv) < 2:
        print("Usage: python deobfuscate_js.py <URL>")
        print("Example: python deobfuscate_js.py https://playerembedapi.link")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Extract scripts
    scripts = extract_js_from_page(url)
    print(f"\n[2] Found {len(scripts)} scripts\n")
    
    # Analyze each script
    for i, (source, code) in enumerate(scripts):
        print(f"{'='*70}")
        print(f"[3] Script {i+1}: {source[:60]}...")
        print(f"    Size: {len(code)} bytes")
        
        # Find crypto functions
        crypto_funcs = find_crypto_functions(code)
        
        if crypto_funcs:
            print(f"\n    [CRYPTO DETECTED]")
            for func_type, examples in crypto_funcs.items():
                print(f"      • {func_type}: {len(examples)} occurrences")
                for example in examples[:1]:  # Show first example
                    print(f"        → {example[:60]}...")
        
        # Extract JWPlayer configs
        jwplayer_configs = extract_jwplayer_config(code)
        if jwplayer_configs:
            print(f"\n    [JWPLAYER CONFIG FOUND]")
            for config in jwplayer_configs:
                print(f"      • Type: {config['type']}")
                if config['type'] == 'file':
                    print(f"        URL: {config['url']}")
        
        # Save interesting scripts
        if crypto_funcs or jwplayer_configs:
            filename = f'extracted_script_{i}.js'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"\n    [SAVED] {filename}")
        
        print()
    
    print(f"{'='*70}")
    print("[DONE] Analysis complete")

if __name__ == '__main__':
    main()
