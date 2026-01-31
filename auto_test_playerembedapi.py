#!/usr/bin/env python3
"""
PlayerEmbedAPI v5.0 - Teste Automático Completo
===============================================
Script de teste automatizado sem interação humana para validar:
1. Extração de base64
2. Decriptação AES-CTR
3. Validação de URLs de vídeo
4. Detecção de qualidade
5. Processamento de JSON escapes

Autor: Test Suite Automático
Data: 2026-01-31
"""

import base64
import hashlib
import json
import re
import sys
import time
import unittest
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# ============================================================================
# MOCK DATA - Dados fictícios mas realistas para testes
# ============================================================================

MOCK_USER_ID = "482120"
MOCK_SLUG = "yhRExEdvKy"
MOCK_MD5_ID = "27648163"

# Mock JSON de configuração (estrutura realista do PlayerEmbedAPI)
MOCK_CONFIG_JSON = {
    "user_id": MOCK_USER_ID,
    "slug": MOCK_SLUG,
    "md5_id": MOCK_MD5_ID,
    "version": "5.0.0",
    "timestamp": int(time.time()),
    "expires": int(time.time()) + 3600,
    "media": ""  # Será preenchido com dados criptografados
}

# Mock Media JSON (estrutura de streams)
MOCK_MEDIA_JSON = {
    "hls": "https://cdn.iamcdn.net/hls/playlist_480p.m3u8",
    "mp4": [
        "https://cdn.iamcdn.net/videos/480p.mp4",
        "https://cdn.iamcdn.net/videos/720p.mp4",
        "https://cdn.iamcdn.net/videos/1080p.mp4"
    ],
    "sources": [
        {"file": "https://cdn.iamcdn.net/hls/master.m3u8", "label": "Auto", "type": "hls"},
        {"file": "https://cdn.iamcdn.net/videos/480p.mp4", "label": "480p", "type": "mp4"},
        {"file": "https://cdn.iamcdn.net/videos/720p.mp4", "label": "720p", "type": "mp4"},
        {"file": "https://cdn.iamcdn.net/videos/1080p.mp4", "label": "1080p", "type": "mp4"}
    ],
    "tracks": [],
    "drm": None
}

# Mock HTML com diferentes variações de base64
MOCK_HTML_VARIANTS = [
    # Variante 1: const datas
    '''<script>
    const datas = "{BASE64_DATA}";
    console.log("PlayerEmbedAPI v5.0");
    </script>''',
    # Variante 2: var datas
    '''<script>
    var datas = "{BASE64_DATA}";
    initPlayer(datas);
    </script>''',
    # Variante 3: let datas
    '''<script>
    let datas = "{BASE64_DATA}";
    </script>''',
    # Variante 4: atributo data
    '''<div id="player" data-datas="{BASE64_DATA}"></div>''',
    # Variante 5: JSON inline
    '''<script>window.__INITIAL_STATE__ = {{"datas": "{BASE64_DATA}"}};</script>''',
]

# Mock chave AES (32 bytes) - derivada de MD5
MOCK_AES_KEY = hashlib.md5(f"{MOCK_USER_ID}:{MOCK_SLUG}:{MOCK_MD5_ID}".encode()).hexdigest().encode('utf-8')
MOCK_AES_IV = MOCK_AES_KEY[:16]

# URLs de vídeo válidas para teste
VALID_VIDEO_URLS = [
    ("https://cdn.iamcdn.net/hls/playlist.m3u8", "hls", "480p"),
    ("https://cdn.iamcdn.net/hls/master_720p.m3u8", "hls", "720p"),
    ("https://cdn.iamcdn.net/hls/master_1080p.m3u8", "hls", "1080p"),
    ("https://cdn.iamcdn.net/videos/movie_480p.mp4", "mp4", "480p"),
    ("https://cdn.iamcdn.net/videos/movie_720p.mp4", "mp4", "720p"),
    ("https://cdn.iamcdn.net/videos/movie_1080p.mp4", "mp4", "1080p"),
    ("https://stream.example.com/live/stream.m3u8", "hls", "live"),
]

# URLs inválidas para teste de validação
INVALID_URLS = [
    "not-a-url",
    "ftp://invalid.protocol.com/file.mp4",
    "https://no-video-extension.com/file.txt",
    "",
    "   ",
    "javascript:void(0)",
    "data:text/plain;base64,SGVsbG8=",
]

# Strings com escapes JSON para teste
JSON_ESCAPE_TEST_CASES = [
    # (input, expected_output)
    ('{"url": "https://example.com/video.mp4"}', {"url": "https://example.com/video.mp4"}),
    ('{"title": "Episode \\"The Beginning\\""}', {"title": 'Episode "The Beginning"'}),
    ('{"path": "C:\\\\Users\\\\Video\\\\file.mp4"}', {"path": "C:\\Users\\Video\\file.mp4"}),
    ('{"unicode": "\\u0048\\u0065\\u006c\\u006c\\u006f"}', {"unicode": "Hello"}),
    ('{"special": "line1\\nline2\\ttabbed"}', {"special": "line1\nline2\ttabbed"}),
    ('{"backslash": "test\\\\value"}', {"backslash": "test\\value"}),
    ('{"null": null, "bool": true}', {"null": None, "bool": True}),
]


# ============================================================================
# CLASSES AUXILIARES
# ============================================================================

@dataclass
class TestResult:
    """Representa o resultado de um teste individual."""
    name: str
    category: str
    passed: bool
    message: str = ""
    duration_ms: float = 0.0
    details: Dict = field(default_factory=dict)


@dataclass
class QualityInfo:
    """Representa informações de qualidade detectadas."""
    resolution: str
    bandwidth: Optional[int]
    height: int
    width: int
    label: str


class Colors:
    """Cores para output no terminal."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


# ============================================================================
# MÓDULOS DE TESTE
# ============================================================================

class Base64ExtractorTester:
    """Testa extração de base64 de diferentes variações de HTML/JS."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.patterns = [
            r'const\s+datas\s*=\s*"([A-Za-z0-9+/=]+)"',
            r'var\s+datas\s*=\s*"([A-Za-z0-9+/=]+)"',
            r'let\s+datas\s*=\s*"([A-Za-z0-9+/=]+)"',
            r'datas\s*=\s*"([A-Za-z0-9+/=]+)"',
            r'"datas":\s*"([A-Za-z0-9+/=]+)"',
            r'data-datas="([A-Za-z0-9+/=]+)"',
        ]
    
    def extract_datas(self, html_content: str) -> Optional[str]:
        """Extrai o base64 'datas' do conteúdo HTML."""
        for pattern in self.patterns:
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
        
        # Fallback: procura por qualquer base64 grande
        script_pattern = re.search(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        if script_pattern:
            base64_matches = re.findall(r'["\']([A-Za-z0-9+/]{100,}={0,2})["\']', html_content)
            for b64 in base64_matches:
                try:
                    decoded = base64.b64decode(b64)
                    if decoded.startswith(b'{') or decoded.startswith(b'['):
                        json.loads(decoded)
                        return b64
                except:
                    continue
        return None
    
    def run_tests(self) -> List[TestResult]:
        """Executa todos os testes de extração de base64."""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TESTES: Extração de Base64{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Prepara dados de teste
        test_data = json.dumps(MOCK_CONFIG_JSON).encode('utf-8')
        base64_data = base64.b64encode(test_data).decode('utf-8')
        
        test_cases = [
            ("const datas", MOCK_HTML_VARIANTS[0].format(BASE64_DATA=base64_data)),
            ("var datas", MOCK_HTML_VARIANTS[1].format(BASE64_DATA=base64_data)),
            ("let datas", MOCK_HTML_VARIANTS[2].format(BASE64_DATA=base64_data)),
            ("data-datas attr", MOCK_HTML_VARIANTS[3].format(BASE64_DATA=base64_data)),
            ("JSON inline", MOCK_HTML_VARIANTS[4].format(BASE64_DATA=base64_data)),
            ("base64 com padding", f'const datas = "{base64_data}";'),
            ("base64 sem padding", f'const datas = "{base64_data.rstrip("=")}";'),
        ]
        
        for test_name, html_content in test_cases:
            start = time.time()
            try:
                result = self.extract_datas(html_content)
                duration = (time.time() - start) * 1000
                
                if result:
                    # Verifica se decodifica corretamente
                    decoded = base64.b64decode(result + '=' * (4 - len(result) % 4) if len(result) % 4 else result)
                    parsed = json.loads(decoded)
                    
                    if parsed.get('user_id') == MOCK_USER_ID:
                        self.results.append(TestResult(
                            name=f"Extract: {test_name}",
                            category="Base64 Extraction",
                            passed=True,
                            message=f"Extraído com sucesso: {len(result)} caracteres",
                            duration_ms=duration,
                            details={"extracted_length": len(result)}
                        ))
                    else:
                        self.results.append(TestResult(
                            name=f"Extract: {test_name}",
                            category="Base64 Extraction",
                            passed=False,
                            message="Dados decodificados não correspondem",
                            duration_ms=duration
                        ))
                else:
                    self.results.append(TestResult(
                        name=f"Extract: {test_name}",
                        category="Base64 Extraction",
                        passed=False,
                        message="Não foi possível extrair base64",
                        duration_ms=duration
                    ))
            except Exception as e:
                duration = (time.time() - start) * 1000
                self.results.append(TestResult(
                    name=f"Extract: {test_name}",
                    category="Base64 Extraction",
                    passed=False,
                    message=f"Erro: {str(e)}",
                    duration_ms=duration
                ))
        
        # Teste de base64 inválido
        start = time.time()
        try:
            invalid_b64 = "!!!Invalid_Base64!!!"
            base64.b64decode(invalid_b64)
            self.results.append(TestResult(
                name="Invalid base64 handling",
                category="Base64 Extraction",
                passed=False,
                message="Deveria ter lançado exceção para base64 inválido",
                duration_ms=(time.time() - start) * 1000
            ))
        except Exception:
            self.results.append(TestResult(
                name="Invalid base64 handling",
                category="Base64 Extraction",
                passed=True,
                message="Exceção corretamente lançada para base64 inválido",
                duration_ms=(time.time() - start) * 1000
            ))
        
        return self.results


class AESCTRTester:
    """Testa decriptação AES-CTR com chaves conhecidas."""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def derive_key(self, user_id: str, slug: str, md5_id: str) -> Tuple[bytes, bytes]:
        """Deriva chave e IV usando MD5."""
        key_string = f"{user_id}:{slug}:{md5_id}"
        md5_hash = hashlib.md5(key_string.encode('utf-8')).hexdigest()
        key_bytes = md5_hash.encode('utf-8')
        iv_bytes = key_bytes[:16]
        return key_bytes, iv_bytes
    
    def mock_decrypt_aes_ctr(self, encrypted_data: bytes, key: bytes, iv: bytes) -> str:
        """Mock de decriptação AES-CTR (simula sem dependência externa)."""
        # Para testes, usamos XOR simples como mock do CTR
        # Em produção, usar pycryptodome
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            key_byte = key[i % len(key)]
            iv_byte = iv[i % len(iv)]
            result.append(byte ^ key_byte ^ iv_byte)
        return result.decode('utf-8', errors='ignore')
    
    def run_tests(self) -> List[TestResult]:
        """Executa todos os testes de decriptação AES-CTR."""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TESTES: Decriptação AES-CTR{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Teste 1: Derivação de chave
        start = time.time()
        try:
            key, iv = self.derive_key(MOCK_USER_ID, MOCK_SLUG, MOCK_MD5_ID)
            duration = (time.time() - start) * 1000
            
            if len(key) == 32 and len(iv) == 16:
                self.results.append(TestResult(
                    name="Key derivation MD5",
                    category="AES-CTR Decryption",
                    passed=True,
                    message=f"Chave: {len(key)} bytes, IV: {len(iv)} bytes",
                    duration_ms=duration,
                    details={"key_hex": key.hex(), "iv_hex": iv.hex()}
                ))
            else:
                self.results.append(TestResult(
                    name="Key derivation MD5",
                    category="AES-CTR Decryption",
                    passed=False,
                    message=f"Tamanhos incorretos - Key: {len(key)}, IV: {len(iv)}",
                    duration_ms=duration
                ))
        except Exception as e:
            self.results.append(TestResult(
                name="Key derivation MD5",
                category="AES-CTR Decryption",
                passed=False,
                message=f"Erro: {str(e)}",
                duration_ms=(time.time() - start) * 1000
            ))
        
        # Teste 2: Verificação de derivação consistente
        start = time.time()
        key1, iv1 = self.derive_key("123", "test", "456")
        key2, iv2 = self.derive_key("123", "test", "456")
        duration = (time.time() - start) * 1000
        
        if key1 == key2 and iv1 == iv2:
            self.results.append(TestResult(
                name="Consistent key derivation",
                category="AES-CTR Decryption",
                passed=True,
                message="Derivação é determinística",
                duration_ms=duration
            ))
        else:
            self.results.append(TestResult(
                name="Consistent key derivation",
                category="AES-CTR Decryption",
                passed=False,
                message="Derivação não é determinística!",
                duration_ms=duration
            ))
        
        # Teste 3: Tamanhos de chave com diferentes inputs
        test_cases = [
            ("1", "a", "1"),
            ("123456789", "test-slug-long", "999999999"),
            ("user_12345", "my-video-title", "md5_hash_123"),
        ]
        
        for uid, slug, mid in test_cases:
            start = time.time()
            key, iv = self.derive_key(uid, slug, mid)
            duration = (time.time() - start) * 1000
            
            if len(key) == 32 and len(iv) == 16:
                self.results.append(TestResult(
                    name=f"Key size with inputs: {uid[:5]}...",
                    category="AES-CTR Decryption",
                    passed=True,
                    message=f"Key: {len(key)} bytes, IV: {len(iv)} bytes",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name=f"Key size with inputs: {uid[:5]}...",
                    category="AES-CTR Decryption",
                    passed=False,
                    message=f"Tamanhos incorretos",
                    duration_ms=duration
                ))
        
        # Teste 4: Mock de decriptação
        start = time.time()
        try:
            test_plaintext = json.dumps(MOCK_MEDIA_JSON)
            key, iv = self.derive_key(MOCK_USER_ID, MOCK_SLUG, MOCK_MD5_ID)
            
            # Cria dados "criptografados" (mock)
            encrypted = bytearray()
            for i, char in enumerate(test_plaintext.encode('utf-8')):
                key_byte = key[i % len(key)]
                iv_byte = iv[i % len(iv)]
                encrypted.append(char ^ key_byte ^ iv_byte)
            
            # Decripta
            decrypted = self.mock_decrypt_aes_ctr(bytes(encrypted), key, iv)
            duration = (time.time() - start) * 1000
            
            if "hls" in decrypted and "cdn.iamcdn.net" in decrypted:
                self.results.append(TestResult(
                    name="Mock AES-CTR decrypt",
                    category="AES-CTR Decryption",
                    passed=True,
                    message="Decriptação simulada bem-sucedida",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name="Mock AES-CTR decrypt",
                    category="AES-CTR Decryption",
                    passed=False,
                    message="Dados decriptados não correspondem",
                    duration_ms=duration
                ))
        except Exception as e:
            self.results.append(TestResult(
                name="Mock AES-CTR decrypt",
                category="AES-CTR Decryption",
                passed=False,
                message=f"Erro: {str(e)}",
                duration_ms=(time.time() - start) * 1000
            ))
        
        return self.results


class URLValidatorTester:
    """Testa validação de URLs de vídeo."""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def validate_video_url(self, url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Valida uma URL de vídeo.
        Retorna: (is_valid, message, video_type)
        """
        if not url or not isinstance(url, str):
            return False, "URL vazia ou inválida", None
        
        url = url.strip()
        if not url:
            return False, "URL vazia após trim", None
        
        # Verifica protocolo
        if not url.startswith(('http://', 'https://')):
            return False, "Protocolo inválido", None
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "Hostname ausente", None
        except Exception as e:
            return False, f"Parse error: {e}", None
        
        # Detecta tipo de vídeo pela extensão
        url_lower = url.lower()
        if '.m3u8' in url_lower:
            return True, "URL HLS válida", "hls"
        elif '.mpd' in url_lower:
            return True, "URL DASH válida", "dash"
        elif any(ext in url_lower for ext in ['.mp4', '.webm', '.mkv', '.avi', '.mov']):
            return True, "URL Progressive válida", "progressive"
        elif '.ts' in url_lower:
            return True, "URL TS segment válida", "segment"
        
        return False, "Extensão de vídeo não reconhecida", None
    
    def run_tests(self) -> List[TestResult]:
        """Executa todos os testes de validação de URL."""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TESTES: Validação de URLs de Vídeo{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Testes com URLs válidas
        for url, expected_type, quality in VALID_VIDEO_URLS:
            start = time.time()
            is_valid, message, detected_type = self.validate_video_url(url)
            duration = (time.time() - start) * 1000
            
            # Considera mp4 e progressive como equivalentes
            type_match = detected_type == expected_type or (
                expected_type == "mp4" and detected_type == "progressive"
            )
            if is_valid and type_match:
                self.results.append(TestResult(
                    name=f"Valid URL: {quality} {expected_type}",
                    category="URL Validation",
                    passed=True,
                    message=f"{message} ({detected_type})",
                    duration_ms=duration,
                    details={"url": url[:50], "type": detected_type}
                ))
            else:
                self.results.append(TestResult(
                    name=f"Valid URL: {quality} {expected_type}",
                    category="URL Validation",
                    passed=False,
                    message=f"Esperado {expected_type}, got {detected_type}: {message}",
                    duration_ms=duration
                ))
        
        # Testes com URLs inválidas
        for url in INVALID_URLS:
            start = time.time()
            is_valid, message, detected_type = self.validate_video_url(url)
            duration = (time.time() - start) * 1000
            
            if not is_valid:
                self.results.append(TestResult(
                    name=f"Invalid URL rejected: {url[:30] if url else 'empty'}...",
                    category="URL Validation",
                    passed=True,
                    message=f"Corretamente rejeitada: {message}",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name=f"Invalid URL rejected: {url[:30] if url else 'empty'}...",
                    category="URL Validation",
                    passed=False,
                    message=f"URL inválida foi aceita!",
                    duration_ms=duration
                ))
        
        # Teste de detecção de CDN específicos
        cdn_patterns = [
            ("https://cdn.iamcdn.net/video.mp4", "iamcdn"),
            ("https://ssu5.valenium.shop/stream.m3u8", "valenium"),
            ("https://playerembedapi.link/video.m3u8", "playerembed"),
        ]
        
        for url, cdn_name in cdn_patterns:
            start = time.time()
            is_valid, message, detected_type = self.validate_video_url(url)
            duration = (time.time() - start) * 1000
            
            if is_valid:
                self.results.append(TestResult(
                    name=f"CDN detection: {cdn_name}",
                    category="URL Validation",
                    passed=True,
                    message=f"CDN {cdn_name} reconhecida ({detected_type})",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name=f"CDN detection: {cdn_name}",
                    category="URL Validation",
                    passed=False,
                    message=f"Não reconheceu URL da CDN {cdn_name}",
                    duration_ms=duration
                ))
        
        return self.results


class QualityDetectorTester:
    """Testa detecção de qualidade de vídeo."""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def detect_quality(self, url: str) -> QualityInfo:
        """Detecta qualidade da URL do vídeo."""
        url_lower = url.lower()
        
        # Padrões de resolução na URL (ordem importa - mais específicos primeiro)
        patterns = [
            (r'[/_-](\d{3,4})x(\d{3,4})[/_\.]', "dimensions"),
            (r'[/_-](\d{3,4})p[/_\.]', "label"),
            (r'res[=_](\d{3,4})p?', "resolution"),
            (r'quality[=/](\d{3,4})', "quality"),
        ]
        
        resolution = "Unknown"
        height = 0
        width = 0
        
        for pattern, ptype in patterns:
            match = re.search(pattern, url_lower)
            if match:
                if ptype == "label":
                    height = int(match.group(1))
                    resolution = f"{height}p"
                    width = int(height * 16 / 9)  # Assumindo 16:9
                elif ptype == "dimensions":
                    width = int(match.group(1))
                    height = int(match.group(2))
                    resolution = f"{height}p"
                elif ptype in ("resolution", "quality"):
                    height = int(match.group(1))
                    resolution = f"{height}p"
                break
        
        # Estimativa de bandwidth
        bandwidth_map = {
            240: 400000, 360: 800000, 480: 1400000,
            720: 2800000, 1080: 5800000, 1440: 10000000, 2160: 20000000
        }
        bandwidth = bandwidth_map.get(height)
        
        return QualityInfo(
            resolution=resolution,
            bandwidth=bandwidth,
            height=height,
            width=width,
            label=f"{resolution} ({width}x{height})" if width else resolution
        )
    
    def run_tests(self) -> List[TestResult]:
        """Executa todos os testes de detecção de qualidade."""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TESTES: Detecção de Qualidade{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        test_cases = [
            ("https://cdn.com/video_240p.mp4", "240p", 240, 426),
            ("https://cdn.com/video_360p.mp4", "360p", 360, 640),
            ("https://cdn.com/video_480p.mp4", "480p", 480, 854),
            ("https://cdn.com/video_720p.mp4", "720p", 720, 1280),
            ("https://cdn.com/video_1080p.mp4", "1080p", 1080, 1920),
            ("https://cdn.com/video_1920x1080.mp4", "1080p", 1080, 1920),
            ("https://cdn.com/video_1280x720.mp4", "720p", 720, 1280),
            ("https://cdn.com/video-res=1080.mp4", "1080p", 1080, 1920),
            ("https://cdn.com/video/quality/720/stream.m3u8", "720p", 720, 1280),
            ("https://cdn.com/video.mp4", "Unknown", 0, 0),  # Sem info de qualidade
        ]
        
        for url, expected_res, expected_height, expected_width in test_cases:
            start = time.time()
            quality = self.detect_quality(url)
            duration = (time.time() - start) * 1000
            
            if quality.resolution == expected_res:
                self.results.append(TestResult(
                    name=f"Quality detect: {expected_res}",
                    category="Quality Detection",
                    passed=True,
                    message=f"Detectado: {quality.label}, Bandwidth: {quality.bandwidth}",
                    duration_ms=duration,
                    details={"resolution": quality.resolution, "bandwidth": quality.bandwidth}
                ))
            else:
                self.results.append(TestResult(
                    name=f"Quality detect: {expected_res}",
                    category="Quality Detection",
                    passed=False,
                    message=f"Esperado {expected_res}, obtido {quality.resolution}",
                    duration_ms=duration
                ))
        
        # Teste de ordenação de qualidades
        start = time.time()
        urls = [
            "https://cdn.com/video_480p.mp4",
            "https://cdn.com/video_1080p.mp4",
            "https://cdn.com/video_720p.mp4",
            "https://cdn.com/video_360p.mp4",
        ]
        qualities = [(url, self.detect_quality(url)) for url in urls]
        sorted_qualities = sorted(qualities, key=lambda x: x[1].height, reverse=True)
        duration = (time.time() - start) * 1000
        
        expected_order = ["1080p", "720p", "480p", "360p"]
        actual_order = [q.resolution for _, q in sorted_qualities]
        
        if actual_order == expected_order:
            self.results.append(TestResult(
                name="Quality sorting",
                category="Quality Detection",
                passed=True,
                message=f"Ordenação correta: {' > '.join(actual_order)}",
                duration_ms=duration
            ))
        else:
            self.results.append(TestResult(
                name="Quality sorting",
                category="Quality Detection",
                passed=False,
                message=f"Esperado {expected_order}, obtido {actual_order}",
                duration_ms=duration
            ))
        
        return self.results


class JSONEscapeTester:
    """Testa processamento de JSON escapes."""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def parse_json_safe(self, json_str: str) -> Tuple[bool, Any, str]:
        """Parse seguro de JSON com tratamento de escapes."""
        try:
            # Tenta parse direto
            result = json.loads(json_str)
            return True, result, "Parse direto bem-sucedido"
        except json.JSONDecodeError as e:
            # Tenta corrigir escapes duplos
            try:
                fixed = json_str.replace('\\"', '"').replace('\\\\', '\\')
                result = json.loads(fixed)
                return True, result, "Parse com correção de escapes"
            except:
                return False, None, f"Erro de parse: {e}"
    
    def extract_json_from_js(self, js_code: str) -> List[Dict]:
        """Extrai objetos JSON de código JavaScript."""
        results = []
        
        # Procura por objetos JSON
        patterns = [
            r'JSON\.parse\s*\(\s*["\'](.+?)["\']\s*\)',
            r'[{]\s*["\']\w+["\']\s*:\s*["\'][^}]+[}]',
            r'["\']({[^}]+})["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_code, re.DOTALL)
            for match in matches:
                try:
                    # Tenta parse
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]
                    parsed = json.loads(match)
                    results.append(parsed)
                except:
                    pass
        
        return results
    
    def run_tests(self) -> List[TestResult]:
        """Executa todos os testes de processamento de JSON escapes."""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}TESTES: Processamento de JSON Escapes{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Testes de parse de JSON com escapes
        for i, (input_str, expected) in enumerate(JSON_ESCAPE_TEST_CASES):
            start = time.time()
            success, result, message = self.parse_json_safe(input_str)
            duration = (time.time() - start) * 1000
            
            test_name = f"JSON escape case {i+1}"
            
            if success and result == expected:
                self.results.append(TestResult(
                    name=test_name,
                    category="JSON Escapes",
                    passed=True,
                    message=f"Parse correto: {message}",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name=test_name,
                    category="JSON Escapes",
                    passed=False,
                    message=f"Esperado {expected}, obtido {result}: {message}",
                    duration_ms=duration
                ))
        
        # Teste de extração de JSON de JS
        js_test_cases = [
            ('const data = JSON.parse(\'{"url": "test.mp4"}\');', {"url": "test.mp4"}),
            ('var x = \'{"hls": "stream.m3u8", "quality": 720}\';', {"hls": "stream.m3u8", "quality": 720}),
        ]
        
        for i, (js_code, expected) in enumerate(js_test_cases):
            start = time.time()
            results = self.extract_json_from_js(js_code)
            duration = (time.time() - start) * 1000
            
            test_name = f"JSON from JS extraction {i+1}"
            
            if results and any(r == expected for r in results):
                self.results.append(TestResult(
                    name=test_name,
                    category="JSON Escapes",
                    passed=True,
                    message=f"Extraído corretamente: {results[0]}",
                    duration_ms=duration
                ))
            else:
                self.results.append(TestResult(
                    name=test_name,
                    category="JSON Escapes",
                    passed=False,
                    message=f"Não extraiu JSON esperado. Encontrado: {results}",
                    duration_ms=duration
                ))
        
        # Teste de serialização/deserialização
        start = time.time()
        test_obj = {
            "url": "https://cdn.com/video.mp4",
            "title": 'Episode "The Beginning"',
            "path": "C:\\Users\\Video\\file.mp4",
            "nested": {"key": "value with \"quotes\""}
        }
        
        serialized = json.dumps(test_obj)
        deserialized = json.loads(serialized)
        duration = (time.time() - start) * 1000
        
        if deserialized == test_obj:
            self.results.append(TestResult(
                name="JSON round-trip serialization",
                category="JSON Escapes",
                passed=True,
                message="Serialização e desserialização corretas",
                duration_ms=duration
            ))
        else:
            self.results.append(TestResult(
                name="JSON round-trip serialization",
                category="JSON Escapes",
                passed=False,
                message="Dados alterados após round-trip",
                duration_ms=duration
            ))
        
        return self.results


# ============================================================================
# RELATÓRIO DE TESTES
# ============================================================================

class TestReporter:
    """Gera relatório de testes formatado."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_results(self, results: List[TestResult]):
        """Adiciona resultados de teste."""
        self.results.extend(results)
    
    def start(self):
        """Marca início dos testes."""
        self.start_time = time.time()
    
    def finish(self):
        """Marca fim dos testes."""
        self.end_time = time.time()
    
    def generate_report(self) -> str:
        """Gera relatório completo em formato de string."""
        lines = []
        lines.append("=" * 80)
        lines.append(" " * 25 + "RELATÓRIO DE TESTES - PlayerEmbedAPI v5.0")
        lines.append("=" * 80)
        lines.append(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duração Total: {(self.end_time - self.start_time)*1000:.2f} ms")
        lines.append("")
        
        # Agrupa por categoria
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = []
            categories[r.category].append(r)
        
        # Estatísticas
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        lines.append("-" * 80)
        lines.append("RESUMO")
        lines.append("-" * 80)
        lines.append(f"  Total de Testes: {total}")
        lines.append(f"  {Colors.GREEN}Passaram: {passed}{Colors.END}")
        lines.append(f"  {Colors.RED}Falharam: {failed}{Colors.END}")
        lines.append(f"  Taxa de Sucesso: {(passed/total*100):.1f}%")
        lines.append("")
        
        # Detalhes por categoria
        for category, results in categories.items():
            cat_passed = sum(1 for r in results if r.passed)
            cat_total = len(results)
            
            lines.append("-" * 80)
            lines.append(f"CATEGORIA: {category} ({cat_passed}/{cat_total} passaram)")
            lines.append("-" * 80)
            
            for r in results:
                status = f"{Colors.GREEN}[PASS]{Colors.END}" if r.passed else f"{Colors.RED}[FAIL]{Colors.END}"
                lines.append(f"  {status} {r.name}")
                lines.append(f"         {r.message}")
                lines.append(f"         ({r.duration_ms:.2f} ms)")
                if r.details:
                    for k, v in r.details.items():
                        lines.append(f"         {k}: {v}")
                lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def print_summary(self):
        """Imprime resumo no console."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}RESUMO FINAL{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"Total de testes: {total}")
        print(f"{Colors.GREEN}Passaram: {passed}{Colors.END}")
        print(f"{Colors.RED}Falharam: {failed}{Colors.END}")
        print(f"Taxa de sucesso: {(passed/total*100):.1f}%")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}[OK] TODOS OS TESTES PASSARAM!{Colors.END}")
        else:
            print(f"{Colors.YELLOW}[AVISO] ALGUNS TESTES FALHARAM{Colors.END}")
        
        print("")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def run_all_tests() -> Tuple[int, int, int]:
    """
    Executa todos os testes e retorna estatísticas.
    
    Returns:
        Tuple de (total, passed, failed)
    """
    print(f"\n{Colors.HEADER}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}  PlayerEmbedAPI v5.0 - Suite de Testes Automáticos{Colors.END}")
    print(f"{Colors.HEADER}{'='*60}{Colors.END}")
    
    reporter = TestReporter()
    reporter.start()
    
    # Executa testes de cada módulo
    testers = [
        Base64ExtractorTester(),
        AESCTRTester(),
        URLValidatorTester(),
        QualityDetectorTester(),
        JSONEscapeTester(),
    ]
    
    for tester in testers:
        try:
            results = tester.run_tests()
            reporter.add_results(results)
        except Exception as e:
            print(f"{Colors.RED}Erro ao executar testes: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
    
    reporter.finish()
    
    # Imprime relatório detalhado
    report = reporter.generate_report()
    print(report)
    
    # Imprime resumo
    reporter.print_summary()
    
    # Salva relatório em arquivo
    report_path = "test_report_playerembedapi.txt"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            # Remove códigos ANSI para o arquivo
            clean_report = re.sub(r'\033\[[0-9;]*m', '', report)
            f.write(clean_report)
        print(f"Relatório salvo em: {report_path}")
    except Exception as e:
        print(f"Não foi possível salvar relatório: {e}")
    
    passed = sum(1 for r in reporter.results if r.passed)
    failed = sum(1 for r in reporter.results if not r.passed)
    return len(reporter.results), passed, failed


def main():
    """Função principal."""
    total, passed, failed = run_all_tests()
    
    # Retorna código de saída apropriado
    if failed == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
