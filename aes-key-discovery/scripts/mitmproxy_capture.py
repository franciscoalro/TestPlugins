#!/usr/bin/env python3

"""
Script para mitmproxy - Captura requisições crypto
Uso: mitmproxy -s mitmproxy_capture.py
"""

import json
import re
from mitmproxy import http

class CryptoCapture:
    def __init__(self):
        self.output_file = "output/mitmproxy_crypto.txt"
        self.js_files = []
        
    def response(self, flow: http.HTTPFlow) -> None:
        """Intercepta respostas HTTP"""
        
        url = flow.request.pretty_url
        content_type = flow.response.headers.get("content-type", "")
        
        # Capturar JavaScript
        if ".js" in url or "javascript" in content_type:
            self.save_js(flow)
        
        # Capturar respostas com crypto
        if flow.response.content:
            content = flow.response.get_text(strict=False)
            if content and self.has_crypto_content(content):
                self.save_crypto_response(flow, content)
    
    def save_js(self, flow: http.HTTPFlow):
        """Salva arquivos JavaScript"""
        filename = flow.request.path.split('/')[-1]
        if not filename:
            filename = "index.js"
        
        filepath = f"output/js_{filename}"
        
        try:
            with open(filepath, "wb") as f:
                f.write(flow.response.content)
            print(f"[+] JavaScript salvo: {filepath}")
            self.js_files.append(filepath)
        except Exception as e:
            print(f"[-] Erro ao salvar JS: {e}")
    
    def has_crypto_content(self, content: str) -> bool:
        """Verifica se o conteúdo tem referências crypto"""
        keywords = [
            "crypto", "AES", "importKey", "decrypt", "encrypt",
            "user_id", "slug", "md5_id", "key", "secret", "token"
        ]
        
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in keywords)
    
    def save_crypto_response(self, flow: http.HTTPFlow, content: str):
        """Salva respostas com conteúdo crypto"""
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"URL: {flow.request.pretty_url}\n")
                f.write(f"Method: {flow.request.method}\n")
                f.write(f"Status: {flow.response.status_code}\n")
                f.write("-" * 80 + "\n")
                f.write("Headers:\n")
                for key, value in flow.response.headers.items():
                    f.write(f"  {key}: {value}\n")
                f.write("-" * 80 + "\n")
                f.write("Content (primeiros 2000 chars):\n")
                f.write(content[:2000])
                f.write("\n")
                
                # Procurar padrões específicos
                self.extract_patterns(f, content)
                
            print(f"[+] Crypto response capturada: {flow.request.pretty_url}")
        except Exception as e:
            print(f"[-] Erro ao salvar crypto response: {e}")
    
    def extract_patterns(self, file, content: str):
        """Extrai padrões específicos do conteúdo"""
        file.write("-" * 80 + "\n")
        file.write("Padrões encontrados:\n")
        
        # Procurar por chaves hexadecimais
        hex_keys = re.findall(r'[0-9a-fA-F]{32,}', content)
        if hex_keys:
            file.write(f"  • Hex keys: {hex_keys[:5]}\n")
        
        # Procurar por JSON com 'key'
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                if isinstance(data, dict):
                    for key in ['key', 'secret', 'token', 'aes_key', 'encryption_key']:
                        if key in data:
                            file.write(f"  • JSON.{key}: {data[key]}\n")
        except:
            pass
        
        # Procurar por user_id, slug, md5_id
        for param in ['user_id', 'slug', 'md5_id']:
            matches = re.findall(rf'{param}["\']?\s*[:=]\s*["\']?([^"\'\\s,}}]+)', content)
            if matches:
                file.write(f"  • {param}: {matches[:3]}\n")

addons = [CryptoCapture()]
