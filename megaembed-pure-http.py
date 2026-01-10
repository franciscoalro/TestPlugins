#!/usr/bin/env python3
"""
MegaEmbed Pure HTTP Extractor
Replica a lógica do JavaScript em Python puro - sem browser

Fluxo:
1. Baixar o JavaScript principal
2. Extrair a lógica de descriptografia AES
3. Chamar API /api/v1/info
4. Descriptografar resposta
5. Obter URL do vídeo
"""

import requests
import re
import json
import hashlib
import base64
from urllib.parse import urlparse

# Crypto
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import binascii

class MegaEmbedExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        })
        self.js_code = None
        self.decrypt_key = None
        self.decrypt_iv = None
    
    def extract(self, url):
        """Extrai URL do vídeo do MegaEmbed"""
        print(f"\n[*] Extraindo: {url}")
        
        # Extrair ID do hash
        video_id = self._extract_id(url)
        if not video_id:
            print("[!] ID não encontrado na URL")
            return None
        
        print(f"[+] Video ID: {video_id}")
        
        # Baixar página principal para obter cookies e JS
        base_url = f"https://megaembed.link/"
        self.session.get(base_url, headers={"Referer": url})
        
        # Baixar e analisar JavaScript
        if not self._analyze_javascript():
            print("[!] Falha ao analisar JavaScript")
            return None
        
        # Chamar API
        api_url = f"https://megaembed.link/api/v1/info?id={video_id}"
        print(f"[*] Chamando API: {api_url}")
        
        resp = self.session.get(api_url, headers={
            "Referer": "https://megaembed.link/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
        
        if resp.status_code != 200:
            print(f"[!] API retornou: {resp.status_code}")
            return None
        
        encrypted_data = resp.text.strip()
        print(f"[+] Dados criptografados: {encrypted_data[:50]}...")
        
        # Descriptografar
        decrypted = self._decrypt_response(encrypted_data)
        if decrypted:
            print(f"[+] Descriptografado: {decrypted[:200]}...")
            return self._parse_video_url(decrypted)
        
        return None

    def _extract_id(self, url):
        """Extrai ID do vídeo da URL"""
        # megaembed.link/#ID ou megaembed.link/?v=ID
        if "#" in url:
            return url.split("#")[-1]
        parsed = urlparse(url)
        if parsed.fragment:
            return parsed.fragment
        # Query param
        import urllib.parse
        params = urllib.parse.parse_qs(parsed.query)
        return params.get("v", [None])[0] or params.get("id", [None])[0]
    
    def _analyze_javascript(self):
        """Baixa e analisa o JavaScript para extrair lógica de crypto"""
        print("[*] Analisando JavaScript...")
        
        # Baixar página principal
        resp = self.session.get("https://megaembed.link/")
        html = resp.text
        
        # Encontrar arquivo JS principal
        js_pattern = r'/assets/index-[A-Za-z0-9_-]+\.js'
        js_matches = re.findall(js_pattern, html)
        
        if not js_matches:
            print("[!] JavaScript não encontrado")
            return False
        
        js_url = f"https://megaembed.link{js_matches[0]}"
        print(f"[+] JS URL: {js_url}")
        
        # Baixar JS
        js_resp = self.session.get(js_url)
        self.js_code = js_resp.text
        
        # Analisar padrões de crypto
        return self._extract_crypto_logic()
    
    def _extract_crypto_logic(self):
        """Extrai a lógica de descriptografia do JavaScript"""
        js = self.js_code
        
        # Procurar padrões de AES
        # Comum: CryptoJS.AES.decrypt ou crypto.subtle
        
        # Padrão 1: Chave hardcoded
        key_patterns = [
            r'key\s*[=:]\s*["\']([a-fA-F0-9]{32,64})["\']',
            r'secretKey\s*[=:]\s*["\']([^"\']+)["\']',
            r'aesKey\s*[=:]\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in key_patterns:
            match = re.search(pattern, js)
            if match:
                self.decrypt_key = match.group(1)
                print(f"[+] Chave encontrada: {self.decrypt_key[:20]}...")
                break
        
        # Padrão 2: IV hardcoded
        iv_patterns = [
            r'iv\s*[=:]\s*["\']([a-fA-F0-9]{32})["\']',
            r'initVector\s*[=:]\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in iv_patterns:
            match = re.search(pattern, js)
            if match:
                self.decrypt_iv = match.group(1)
                print(f"[+] IV encontrado: {self.decrypt_iv}")
                break
        
        # Padrão 3: Derivação de chave do hostname
        if not self.decrypt_key:
            # Muitos sites usam hostname como base da chave
            hostname = "megaembed.link"
            
            # Tentar várias derivações
            self.key_candidates = [
                hashlib.sha256(hostname.encode()).digest(),
                hashlib.md5(hostname.encode()).digest(),
                hashlib.sha256(hostname.encode()).hexdigest()[:32].encode(),
                (hostname * 3)[:32].encode(),
                (hostname * 3)[:16].encode(),
            ]
            print(f"[*] Usando {len(self.key_candidates)} candidatos de chave")
        
        return True
    
    def _decrypt_response(self, encrypted_hex):
        """Tenta descriptografar a resposta da API"""
        
        # Converter hex para bytes
        try:
            encrypted = binascii.unhexlify(encrypted_hex)
        except:
            print("[!] Dados não são hex válido")
            # Tentar base64
            try:
                encrypted = base64.b64decode(encrypted_hex)
            except:
                return None
        
        print(f"[*] Dados binários: {len(encrypted)} bytes")
        
        # Se temos chave específica
        if self.decrypt_key:
            key = self.decrypt_key.encode() if isinstance(self.decrypt_key, str) else self.decrypt_key
            if len(key) > 32:
                key = binascii.unhexlify(key) if len(key) == 64 else key[:32]
            return self._try_decrypt(encrypted, key)
        
        # Tentar candidatos
        for i, key in enumerate(self.key_candidates):
            result = self._try_decrypt(encrypted, key)
            if result:
                print(f"[+] Chave {i+1} funcionou!")
                return result
        
        # Tentar com IV nos primeiros 16 bytes
        print("[*] Tentando com IV embutido...")
        iv = encrypted[:16]
        ciphertext = encrypted[16:]
        
        for i, key in enumerate(self.key_candidates):
            result = self._try_decrypt_with_iv(ciphertext, key, iv)
            if result:
                print(f"[+] Chave {i+1} com IV embutido funcionou!")
                return result
        
        return None

    def _try_decrypt(self, encrypted, key):
        """Tenta descriptografar com AES-CBC, IV = primeiros 16 bytes"""
        try:
            if len(key) not in [16, 24, 32]:
                key = key[:32] if len(key) > 32 else key.ljust(32, b'\0')
            
            iv = encrypted[:16]
            ciphertext = encrypted[16:]
            
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            # Verificar se é texto válido
            text = decrypted.decode('utf-8')
            if self._is_valid_json_or_url(text):
                return text
        except Exception as e:
            pass
        return None
    
    def _try_decrypt_with_iv(self, ciphertext, key, iv):
        """Tenta descriptografar com IV específico"""
        try:
            if len(key) not in [16, 24, 32]:
                key = key[:32] if len(key) > 32 else key.ljust(32, b'\0')
            
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
            
            text = decrypted.decode('utf-8')
            if self._is_valid_json_or_url(text):
                return text
        except:
            pass
        return None
    
    def _is_valid_json_or_url(self, text):
        """Verifica se o texto descriptografado é válido"""
        text = text.strip()
        # JSON
        if text.startswith('{') or text.startswith('['):
            try:
                json.loads(text)
                return True
            except:
                pass
        # URL
        if 'http' in text or '.m3u8' in text or '.mp4' in text:
            return True
        # Texto legível
        if text.isprintable() and len(text) > 10:
            return True
        return False
    
    def _parse_video_url(self, decrypted):
        """Extrai URL do vídeo do texto descriptografado"""
        # Tentar JSON
        try:
            data = json.loads(decrypted)
            # Procurar campos comuns
            for key in ['url', 'file', 'source', 'src', 'stream', 'video', 'hls', 'mp4']:
                if key in data:
                    return data[key]
            # Procurar recursivamente
            return self._find_url_in_dict(data)
        except:
            pass
        
        # Procurar URL diretamente no texto
        url_pattern = r'https?://[^\s"\'<>]+\.(?:m3u8|mp4|ts)[^\s"\'<>]*'
        matches = re.findall(url_pattern, decrypted)
        if matches:
            return matches[0]
        
        return decrypted
    
    def _find_url_in_dict(self, obj):
        """Procura URL recursivamente em dict/list"""
        if isinstance(obj, str):
            if 'http' in obj and ('.m3u8' in obj or '.mp4' in obj):
                return obj
        elif isinstance(obj, dict):
            for v in obj.values():
                result = self._find_url_in_dict(v)
                if result:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = self._find_url_in_dict(item)
                if result:
                    return result
        return None


def main():
    print("="*70)
    print("MEGAEMBED PURE HTTP EXTRACTOR")
    print("="*70)
    
    # URL de teste
    test_url = "https://megaembed.link/#Yzg0NjI0NjI="
    
    extractor = MegaEmbedExtractor()
    video_url = extractor.extract(test_url)
    
    if video_url:
        print(f"\n{'='*70}")
        print(f"[+] URL DO VÍDEO: {video_url}")
        print(f"{'='*70}")
        
        # Testar se URL funciona
        print("\n[*] Testando URL...")
        resp = requests.head(video_url, allow_redirects=True, timeout=10)
        print(f"[+] Status: {resp.status_code}")
        print(f"[+] Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    else:
        print("\n[!] Não foi possível extrair URL do vídeo")
        print("[!] A criptografia do MegaEmbed pode usar chaves dinâmicas")


if __name__ == "__main__":
    main()
