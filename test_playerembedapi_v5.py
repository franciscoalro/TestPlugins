#!/usr/bin/env python3
"""
PlayerEmbedAPI Extractor v5.0 - Python Test Script
Testa as 4 estratégias de extração antes de implementar em Kotlin

Estratégias:
1. API (base64 + AES-CTR)
2. ShortIcu
3. Regex direto no HTML
4. WebView (simulado)

Uso: python test_playerembedapi_v5.py <url>
Exemplo: python test_playerembedapi_v5.py "https://playerembedapi.link/?v=abc123"
"""

import sys
import re
import base64
import hashlib
import json
import time
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configurações
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
TIMEOUT = 15

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

@dataclass
class VideoLink:
    url: str
    quality: str
    source: str
    strategy: str

class PlayerEmbedAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Retry strategy
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.results: List[VideoLink] = []
    
    def log(self, message: str, level: str = "info"):
        """Log com cores"""
        timestamp = time.strftime("%H:%M:%S")
        if level == "success":
            print(f"{Colors.OKGREEN}[{timestamp}] ✅ {message}{Colors.ENDC}")
        elif level == "error":
            print(f"{Colors.FAIL}[{timestamp}] ❌ {message}{Colors.ENDC}")
        elif level == "warning":
            print(f"{Colors.WARNING}[{timestamp}] ⚠️  {message}{Colors.ENDC}")
        elif level == "info":
            print(f"{Colors.OKBLUE}[{timestamp}] ℹ️  {message}{Colors.ENDC}")
        elif level == "header":
            print(f"\n{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    
    def is_valid_video_url(self, url: str) -> bool:
        """Valida se URL é um vídeo válido"""
        if not url.startswith(('http://', 'https://')):
            return False
        
        allowed_domains = [
            'googleapis.com', 'sssrr.org', 'cdn', 'video', 
            'stream', 'media', 'content'
        ]
        
        has_allowed_domain = any(domain in url.lower() for domain in allowed_domains)
        has_video_ext = any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mkv', '.webm'])
        
        return has_allowed_domain or has_video_ext
    
    def detect_quality(self, url: str) -> str:
        """Detecta qualidade a partir da URL"""
        url_lower = url.lower()
        if '2160' in url_lower or '4k' in url_lower:
            return "4K"
        elif '1080' in url_lower:
            return "1080p"
        elif '720' in url_lower:
            return "720p"
        elif '480' in url_lower:
            return "480p"
        elif '360' in url_lower:
            return "360p"
        return "HD"
    
    # ============ ESTRATÉGIA 1: API (base64 + AES-CTR) ============
    
    def strategy_api(self, url: str) -> Optional[VideoLink]:
        """
        Estratégia 1: Extrai dados criptografados do HTML, decodifica base64 e decripta AES-CTR
        """
        self.log("=== ESTRATÉGIA 1: API (base64 + AES-CTR) ===", "header")
        
        try:
            # 1. Obter HTML
            self.log("Obtendo HTML...")
            response = self.session.get(url, timeout=TIMEOUT)
            html = response.text
            self.log(f"HTML recebido: {len(html)} chars")
            
            # 2. Encontrar base64 'datas'
            base64_data = self._find_base64_datas(html)
            if not base64_data:
                self.log("Não encontrou base64 'datas'", "warning")
                return None
            
            self.log(f"Base64 encontrado: {base64_data[:50]}...")
            
            # 3. Decodificar base64
            try:
                decoded_bytes = base64.b64decode(base64_data)
                decoded_str = decoded_bytes.decode('latin-1')
            except Exception as e:
                self.log(f"Erro ao decodificar base64: {e}", "error")
                return None
            
            # 4. Extrair campos
            user_id = self._extract_json_field(decoded_str, 'user_id')
            slug = self._extract_json_field(decoded_str, 'slug')
            md5_id = self._extract_json_field(decoded_str, 'md5_id')
            
            self.log(f"Campos extraídos - user_id: {user_id}, slug: {slug}, md5_id: {md5_id}")
            
            if not all([user_id, slug, md5_id]):
                self.log("Campos obrigatórios faltantes", "warning")
                return None
            
            # 5. Extrair campo 'media' criptografado
            media_match = re.search(r'"media"\s*:\s*"((?:[^"\\]|\\.)*)"', decoded_str)
            if not media_match:
                self.log("Campo 'media' não encontrado", "warning")
                return None
            
            media_escaped = media_match.group(1)
            self.log(f"Media field: {len(media_escaped)} chars")
            
            # 6. Processar escapes JSON
            media_bytes = self._process_json_escapes(media_escaped)
            
            # 7. Decriptar AES-CTR
            decrypted = self._decrypt_aes_ctr(media_bytes, user_id, slug, md5_id)
            if not decrypted:
                self.log("Falha na decriptação AES-CTR", "error")
                return None
            
            # 8. Extrair URLs
            return self._extract_urls_from_decrypted(decrypted, url, "API")
            
        except Exception as e:
            self.log(f"Erro na estratégia API: {e}", "error")
            return None
    
    def _find_base64_datas(self, html: str) -> Optional[str]:
        """Procura base64 'datas' no HTML"""
        patterns = [
            r'const\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"',
            r'var\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"',
            r'let\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"',
            r'datas\s*=\s*"([A-Za-z0-9+/=]{200,})"',
            r'data[=:]\s*"([A-Za-z0-9+/=]{200,})"',
            r'"(eyJ[A-Za-z0-9+/=]{100,})"',
            r'window\.__DATA__\s*=\s*"([A-Za-z0-9+/=]{200,})"',
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, html)
            if match:
                candidate = match.group(1)
                try:
                    base64.b64decode(candidate)
                    self.log(f"Pattern {i+1} funcionou!")
                    return candidate
                except:
                    continue
        return None
    
    def _extract_json_field(self, text: str, field: str) -> Optional[str]:
        """Extrai campo de string JSON-like"""
        patterns = [
            rf'"{field}"\s*:\s*"([^"]+)"',
            rf'"{field}"\s*:\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def _process_json_escapes(self, escaped: str) -> bytes:
        """Processa escapes JSON e retorna bytes"""
        result = bytearray()
        i = 0
        while i < len(escaped):
            if escaped[i] == '\\' and i + 1 < len(escaped):
                next_char = escaped[i + 1]
                if next_char == '"':
                    result.append(0x22)
                    i += 2
                elif next_char == '\\':
                    result.append(0x5C)
                    i += 2
                elif next_char == '/':
                    result.append(0x2F)
                    i += 2
                elif next_char == 'b':
                    result.append(0x08)
                    i += 2
                elif next_char == 'f':
                    result.append(0x0C)
                    i += 2
                elif next_char == 'n':
                    result.append(0x0A)
                    i += 2
                elif next_char == 'r':
                    result.append(0x0D)
                    i += 2
                elif next_char == 't':
                    result.append(0x09)
                    i += 2
                elif next_char == 'u':
                    if i + 5 < len(escaped):
                        hex_val = escaped[i+2:i+6]
                        try:
                            code = int(hex_val, 16)
                            result.append(code & 0xFF)
                        except:
                            result.extend(b'\\u')
                        i += 6
                    else:
                        result.append(ord(escaped[i]))
                        i += 1
                else:
                    result.append(ord(next_char))
                    i += 2
            else:
                result.append(ord(escaped[i]) & 0xFF)
                i += 1
        return bytes(result)
    
    def _decrypt_aes_ctr(self, encrypted: bytes, user_id: str, slug: str, md5_id: str) -> Optional[dict]:
        """Decripta usando AES-CTR"""
        try:
            from Crypto.Cipher import AES
            from Crypto.Util import Counter
            
            # Gerar chave
            pre_key = f"{user_id}:{slug}:{md5_id}"
            md5_hash = hashlib.md5(pre_key.encode()).hexdigest()
            key_bytes = md5_hash.encode('utf-8')
            iv_bytes = key_bytes[:16]
            
            self.log(f"Key MD5: {md5_hash[:16]}... (não logando completo por segurança)")
            
            # AES-CTR
            cipher = AES.new(key_bytes, AES.MODE_CTR, nonce=b'', initial_value=int.from_bytes(iv_bytes, 'big'), 
                           counter=Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big')))
            
            decrypted = cipher.decrypt(encrypted)
            
            # Tentar parse como JSON
            try:
                return json.loads(decrypted.decode('utf-8'))
            except:
                # Tentar sem padding
                return json.loads(decrypted.decode('utf-8', errors='ignore'))
                
        except ImportError:
            self.log("PyCryptodome não instalado. Instale: pip install pycryptodome", "error")
            return None
        except Exception as e:
            self.log(f"Erro na decriptação: {e}", "error")
            return None
    
    def _extract_urls_from_decrypted(self, decrypted: dict, original_url: str, strategy: str) -> Optional[VideoLink]:
        """Extrai URLs do JSON decriptado"""
        
        # Tentar sources[]
        sources = decrypted.get('sources', [])
        for source in sources:
            file_url = source.get('file', '')
            label = source.get('label', 'Auto')
            
            if self.is_valid_video_url(file_url):
                self.log(f"URL encontrada em sources: {file_url[:80]}...", "success")
                return VideoLink(
                    url=file_url,
                    quality=label,
                    source="PlayerEmbedAPI",
                    strategy=strategy
                )
        
        # Tentar HLS
        hls = decrypted.get('hls')
        if hls and self.is_valid_video_url(hls):
            self.log(f"URL HLS encontrada: {hls[:80]}...", "success")
            return VideoLink(
                url=hls,
                quality=self.detect_quality(hls),
                source="PlayerEmbedAPI",
                strategy=f"{strategy}-HLS"
            )
        
        # Tentar MP4
        mp4 = decrypted.get('mp4')
        if mp4 and self.is_valid_video_url(mp4):
            self.log(f"URL MP4 encontrada: {mp4[:80]}...", "success")
            return VideoLink(
                url=mp4,
                quality=self.detect_quality(mp4),
                source="PlayerEmbedAPI",
                strategy=f"{strategy}-MP4"
            )
        
        return None
    
    # ============ ESTRATÉGIA 2: ShortIcu ============
    
    def strategy_short_icu(self, url: str) -> Optional[VideoLink]:
        """
        Estratégia 2: Extrai iframe short.icu e obtém vídeo direto
        """
        self.log("\n=== ESTRATÉGIA 2: ShortIcu ===", "header")
        
        try:
            # 1. Obter HTML do PlayerEmbedAPI
            self.log("Obtendo HTML do PlayerEmbedAPI...")
            response = self.session.get(url, timeout=TIMEOUT)
            html = response.text
            
            # 2. Extrair iframe short.icu
            short_icu_url = self._extract_short_icu_url(html)
            if not short_icu_url:
                self.log("Não encontrou iframe short.icu", "warning")
                return None
            
            self.log(f"ShortIcu URL: {short_icu_url}")
            
            # 3. Acessar short.icu
            self.log("Acessando short.icu...")
            headers = {
                'User-Agent': USER_AGENT,
                'Referer': url,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            short_response = self.session.get(short_icu_url, headers=headers, timeout=TIMEOUT)
            short_html = short_response.text
            
            # 4. Extrair URL do vídeo
            video_url = self._extract_video_url_from_html(short_html)
            if not video_url:
                self.log("Não encontrou vídeo no short.icu", "warning")
                return None
            
            if self.is_valid_video_url(video_url):
                self.log(f"Vídeo encontrado: {video_url[:80]}...", "success")
                return VideoLink(
                    url=video_url,
                    quality=self.detect_quality(video_url),
                    source="PlayerEmbedAPI",
                    strategy="ShortIcu"
                )
            
            return None
            
        except Exception as e:
            self.log(f"Erro na estratégia ShortIcu: {e}", "error")
            return None
    
    def _extract_short_icu_url(self, html: str) -> Optional[str]:
        """Extrai URL do short.icu do HTML"""
        patterns = [
            r'<iframe[^>]+src\s*=\s*"(https://short\.icu/[^"]+)"',
            r'src\s*=\s*"(https://short\.icu/[^"]+)"',
            r'(https://short\.icu/[a-zA-Z0-9]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)
        return None
    
    # ============ ESTRATÉGIA 3: Regex direto no HTML ============
    
    def strategy_regex(self, url: str) -> Optional[VideoLink]:
        """
        Estratégia 3: Extrai URL de vídeo direto via regex no HTML
        """
        self.log("\n=== ESTRATÉGIA 3: Regex direto no HTML ===", "header")
        
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            html = response.text
            
            video_url = self._extract_video_url_from_html(html)
            if video_url and self.is_valid_video_url(video_url):
                self.log(f"Vídeo encontrado via regex: {video_url[:80]}...", "success")
                return VideoLink(
                    url=video_url,
                    quality=self.detect_quality(video_url),
                    source="PlayerEmbedAPI",
                    strategy="Regex"
                )
            
            self.log("Não encontrou vídeo via regex", "warning")
            return None
            
        except Exception as e:
            self.log(f"Erro na estratégia Regex: {e}", "error")
            return None
    
    def _extract_video_url_from_html(self, html: str) -> Optional[str]:
        """Extrai URL de vídeo do HTML usando múltiplos padrões"""
        patterns = [
            # Google Cloud Storage
            r'(https://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*)',
            r'(https://storage\.googleapis\.com/[^"\'<>\s]+)',
            # SSSRR CDN
            r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+\.mp4[^"\'<>\s]*)',
            r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
            r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+)',
            # Genéricos
            r'["\'](https?://[^"\'<>]+\.mp4[^"\'<>]*)["\']',
            r'["\'](https?://[^"\'<>]+\.m3u8[^"\'<>]*)["\']',
            # JWPlayer / VideoJS
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'src\s*:\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                url = match.group(1).replace('\\/', '/')
                return url
        return None
    
    # ============ ESTRATÉGIA 4: WebView (simulado) ============
    
    def strategy_webview(self, url: str) -> Optional[VideoLink]:
        """
        Estratégia 4: Simula WebView com requests especiais
        Na prática, isso seria substituído por um WebView real no Android
        """
        self.log("\n=== ESTRATÉGIA 4: WebView (simulado) ===", "header")
        self.log("Nota: WebView real requer ambiente Android")
        self.log("Simulando com requests avançados...")
        
        try:
            # Headers mais completos (como um navegador)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://maxseries.one/',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = self.session.get(url, headers=headers, timeout=TIMEOUT)
            html = response.text
            
            # Tentar extrair com regex mais agressivo
            video_url = self._extract_video_url_from_html(html)
            if video_url and self.is_valid_video_url(video_url):
                self.log(f"Vídeo encontrado (WebView simulado): {video_url[:80]}...", "success")
                return VideoLink(
                    url=video_url,
                    quality=self.detect_quality(video_url),
                    source="PlayerEmbedAPI",
                    strategy="WebView-Simulated"
                )
            
            self.log("WebView simulado não encontrou vídeo", "warning")
            return None
            
        except Exception as e:
            self.log(f"Erro no WebView simulado: {e}", "error")
            return None
    
    # ============ TESTE PRINCIPAL ============
    
    def test_all_strategies(self, url: str) -> List[VideoLink]:
        """Testa todas as estratégias em ordem"""
        self.log(f"\n{Colors.BOLD}{'='*60}", "header")
        self.log(f"TESTANDO: {url}", "header")
        self.log(f"{'='*60}{Colors.ENDC}\n", "header")
        
        start_time = time.time()
        results = []
        
        # Estratégia 1: API
        result = self.strategy_api(url)
        if result:
            results.append(result)
        
        # Estratégia 2: ShortIcu
        result = self.strategy_short_icu(url)
        if result:
            results.append(result)
        
        # Estratégia 3: Regex
        result = self.strategy_regex(url)
        if result:
            results.append(result)
        
        # Estratégia 4: WebView
        result = self.strategy_webview(url)
        if result:
            results.append(result)
        
        elapsed = time.time() - start_time
        
        # Resumo
        self.log(f"\n{Colors.BOLD}{'='*60}", "header")
        self.log("RESUMO", "header")
        self.log(f"{'='*60}{Colors.ENDC}", "header")
        self.log(f"Tempo total: {elapsed:.2f}s")
        self.log(f"Estratégias bem-sucedidas: {len(results)}")
        
        if results:
            self.log(f"\n{Colors.OKGREEN}Links encontrados:{Colors.ENDC}")
            for i, link in enumerate(results, 1):
                print(f"\n{Colors.OKCYAN}[{i}] Estratégia: {link.strategy}{Colors.ENDC}")
                print(f"    URL: {link.url[:100]}...")
                print(f"    Qualidade: {link.quality}")
        else:
            self.log("\nNenhum link encontrado em nenhuma estratégia", "error")
        
        return results


def main():
    if len(sys.argv) < 2:
        print("Uso: python test_playerembedapi_v5.py <url>")
        print("Exemplo: python test_playerembedapi_v5.py 'https://playerembedapi.link/?v=abc123'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Verificar dependências
    try:
        import requests
    except ImportError:
        print("❌ requests não instalado. Instale: pip install requests")
        sys.exit(1)
    
    try:
        from Crypto.Cipher import AES
    except ImportError:
        print("⚠️  pycryptodome não instalado. Instale: pip install pycryptodome")
        print("   (A estratégia 1 não funcionará sem ele)")
    
    # Executar teste
    tester = PlayerEmbedAPITester()
    tester.test_all_strategies(url)


if __name__ == "__main__":
    main()
