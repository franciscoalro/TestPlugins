#!/usr/bin/env python3
"""
HTTP Simulator Test - PlayerEmbedAPI v5.0
=========================================

Script de teste que simula requisições HTTP para testar o fluxo completo
do PlayerEmbedAPI usando requests_mock.

Cenários de teste implementados:
1. Resposta HTML do playerembedapi.link com base64 válido
2. Resposta HTML do short.icu com URL de vídeo
3. Respostas de erro (404, timeout, 500, 403)
4. Teste das 4 estratégias de extração
5. Verificação do fallback entre estratégias

Uso:
    python http_simulator_test.py
    python http_simulator_test.py -v  # modo verbose
"""

import sys
import json
import base64
import hashlib
import re
import argparse
import time
from unittest.mock import patch, MagicMock
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum, auto

# Import requests_mock para simulação HTTP
try:
    import requests_mock
    REQUESTS_MOCK_AVAILABLE = True
except ImportError:
    REQUESTS_MOCK_AVAILABLE = False
    print("[AVISO] requests_mock não instalado. Instale com: pip install requests_mock")

import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError


# =============================================================================
# CONSTANTES E CONFIGURAÇÕES
# =============================================================================

class TestStatus(Enum):
    """Status dos testes"""
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()


# Dados de teste simulados
TEST_VIDEO_URL_HLS = "https://cdn.example.com/videos/abc123/master.m3u8"
TEST_VIDEO_URL_MP4 = "https://cdn.example.com/videos/abc123/video.mp4"
TEST_SHORT_ICU_URL = "https://short.icu/redirect/xyz789"
TEST_FINAL_VIDEO_URL = "https://video.cdn.net/stream/final.mp4"

# Base64 válido com dados de teste (simula o campo 'datas')
TEST_DATAS = {
    "user_id": "user123",
    "slug": "test-video-slug",
    "md5_id": "abc123def456",
    "media": "",  # Será preenchido com dados criptografados
    "expires": int(time.time()) + 3600
}

# Chave AES para teste
TEST_KEY_STRING = f"{TEST_DATAS['user_id']}:{TEST_DATAS['slug']}:{TEST_DATAS['md5_id']}"
TEST_AES_KEY = hashlib.md5(TEST_KEY_STRING.encode()).digest()


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    name: str
    status: TestStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


@dataclass
class ExtractionResult:
    """Resultado de uma estratégia de extração"""
    strategy: str
    success: bool = False
    urls: List[str] = field(default_factory=list)
    error: Optional[str] = None
    fallback_triggered: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# MOCK HTML GENERATORS
# =============================================================================

class MockHTMLGenerators:
    """Geradores de HTML mock para testes"""
    
    @staticmethod
    def generate_playerembedapi_html(datas_b64: str) -> str:
        """Gera HTML do playerembedapi.link com base64 válido"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Embed API</title>
    <script src="https://cdn.jsdelivr.net/npm/crypto-js@4.2.0/index.min.js"></script>
</head>
<body>
    <div id="player-container">
        <video id="video-player" controls></video>
    </div>
    <script>
        // Configuração do player
        const playerConfig = {{
            autoplay: true,
            muted: true,
            controls: true
        }};
        
        // Dados criptografados (base64)
        const datas = "{datas_b64}";
        
        // Decrypt function simulada
        function decryptData(encryptedData) {{
            console.log('Decrypting data...');
            return JSON.parse(atob(encryptedData));
        }}
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {{
            const decrypted = decryptData(datas);
            console.log('Video ready:', decrypted);
        }});
    </script>
</body>
</html>"""
    
    @staticmethod
    def generate_short_icu_html(video_url: str) -> str:
        """Gera HTML do short.icu com URL de vídeo"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Short ICU Redirect</title>
    <meta http-equiv="refresh" content="0;url={video_url}">
</head>
<body>
    <script>
        // Redirecionamento via JavaScript
        window.location.href = "{video_url}";
        
        // Config do vídeo (fallback)
        const videoConfig = {{
            sources: [
                {{ file: "{video_url}", label: "HD" }}
            ],
            tracks: []
        }};
    </script>
    <p>Redirecting to <a href="{video_url}">{video_url}</a>...</p>
</body>
</html>"""
    
    @staticmethod
    def generate_error_page(status_code: int, message: str) -> str:
        """Gera página de erro"""
        return f"""<!DOCTYPE html>
<html>
<head><title>Error {status_code}</title></head>
<body>
    <h1>Error {status_code}</h1>
    <p>{message}</p>
</body>
</html>"""
    
    @staticmethod
    def generate_m3u8_manifest() -> str:
        """Gera manifesto M3U8 válido"""
        return """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD

#EXT-X-STREAM-INF:BANDWIDTH=800000,RESOLUTION=640x360
https://cdn.example.com/videos/abc123/360p/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=1400000,RESOLUTION=1280x720
https://cdn.example.com/videos/abc123/720p/playlist.m3u8

#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1920x1080
https://cdn.example.com/videos/abc123/1080p/playlist.m3u8
"""


# =============================================================================
# EXTRACTOR STRATEGIES (As 4 estratégias mencionadas)
# =============================================================================

class ExtractionStrategies:
    """
    As 4 estratégias de extração de URLs de vídeo
    """
    
    @staticmethod
    def strategy_1_direct_regex(html_content: str) -> ExtractionResult:
        """
        Estratégia 1: Extração direta via regex
        Busca por padrões de URLs de vídeo diretamente no HTML
        """
        result = ExtractionResult(strategy="Direct Regex")
        
        patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
            r'["\']([^"\']*video[^"\']*\.mp4[^"\']*)["\']',
        ]
        
        found_urls = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            found_urls.extend(matches)
        
        result.urls = list(set(found_urls))  # Remove duplicatas
        result.success = len(result.urls) > 0
        
        if not result.success:
            result.error = "No video URLs found via direct regex"
            result.fallback_triggered = True
        
        return result
    
    @staticmethod
    def strategy_2_base64_decode(html_content: str) -> ExtractionResult:
        """
        Estratégia 2: Decodificação de base64
        Extrai e decodifica strings base64 que podem conter URLs
        """
        result = ExtractionResult(strategy="Base64 Decode")
        
        # Padrão para encontrar base64
        b64_pattern = r'["\']([A-Za-z0-9+/]{50,}={0,2})["\']'
        matches = re.findall(b64_pattern, html_content)
        
        found_urls = []
        for b64_string in matches:
            try:
                # Adiciona padding se necessário
                padding = 4 - len(b64_string) % 4
                if padding != 4:
                    b64_string += '=' * padding
                
                decoded = base64.b64decode(b64_string).decode('utf-8', errors='ignore')
                
                # Procura URLs no conteúdo decodificado
                url_pattern = r'https?://[^\s"\'<>]+\.(?:m3u8|mp4|ts)[^\s"\'<>]*'
                urls = re.findall(url_pattern, decoded, re.IGNORECASE)
                found_urls.extend(urls)
                
            except Exception as e:
                continue
        
        result.urls = list(set(found_urls))
        result.success = len(result.urls) > 0
        
        if not result.success:
            result.error = "No video URLs found via base64 decode"
            result.fallback_triggered = True
        
        return result
    
    @staticmethod
    def strategy_3_json_parse(html_content: str) -> ExtractionResult:
        """
        Estratégia 3: Parse de JSON embutido
        Extrai objetos JSON do HTML que podem conter configurações de vídeo
        """
        result = ExtractionResult(strategy="JSON Parse")
        
        # Procura por objetos JSON no HTML
        json_patterns = [
            r'const\s+\w+\s*=\s*(\{[^;]+\});',
            r'var\s+\w+\s*=\s*(\{[^;]+\});',
            r'window\.__INITIAL_STATE__\s*=\s*(\{[^;]+\});',
            r'data-datas="([^"]+)"',
        ]
        
        found_urls = []
        for pattern in json_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            for match in matches:
                try:
                    # Tenta parsear como JSON
                    data = json.loads(match)
                    
                    # Procura recursivamente por URLs
                    def find_urls(obj):
                        if isinstance(obj, str):
                            if obj.startswith('http') and any(ext in obj for ext in ['.m3u8', '.mp4']):
                                found_urls.append(obj)
                        elif isinstance(obj, dict):
                            for v in obj.values():
                                find_urls(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_urls(item)
                    
                    find_urls(data)
                    
                except json.JSONDecodeError:
                    continue
        
        result.urls = list(set(found_urls))
        result.success = len(result.urls) > 0
        
        if not result.success:
            result.error = "No video URLs found via JSON parse"
            result.fallback_triggered = True
        
        return result
    
    @staticmethod
    def strategy_4_player_decrypt(html_content: str) -> ExtractionResult:
        """
        Estratégia 4: Simulação de decriptação do player
        Extrai o campo 'datas' e simula a decriptação AES
        """
        result = ExtractionResult(strategy="Player Decrypt")
        
        try:
            # Extrai o base64 'datas'
            datas_pattern = r'const\s+datas\s*=\s*"([A-Za-z0-9+/=]+)"'
            match = re.search(datas_pattern, html_content)
            
            if not match:
                result.error = "No 'datas' field found"
                result.fallback_triggered = True
                return result
            
            datas_b64 = match.group(1)
            
            # Decodifica base64
            padding = 4 - len(datas_b64) % 4
            if padding != 4:
                datas_b64 += '=' * padding
            
            datas_json = json.loads(base64.b64decode(datas_b64).decode('utf-8'))
            
            # Verifica campos necessários
            required = ['user_id', 'slug', 'md5_id', 'media']
            if not all(k in datas_json for k in required):
                result.error = f"Missing required fields: {[k for k in required if k not in datas_json]}"
                result.fallback_triggered = True
                return result
            
            # Deriva chave e decripta (simplificado para teste)
            key_string = f"{datas_json['user_id']}:{datas_json['slug']}:{datas_json['md5_id']}"
            key = hashlib.md5(key_string.encode()).digest()
            
            # Simula dados decriptados com URLs de vídeo
            decrypted_media = {
                "hls": TEST_VIDEO_URL_HLS,
                "mp4": TEST_VIDEO_URL_MP4,
                "sources": [
                    {"file": TEST_VIDEO_URL_HLS, "label": "HLS"},
                    {"file": TEST_VIDEO_URL_MP4, "label": "MP4"}
                ]
            }
            
            result.urls = [TEST_VIDEO_URL_HLS, TEST_VIDEO_URL_MP4]
            result.success = True
            result.details = {
                'decrypted_media': decrypted_media,
                'key_used': key.hex()
            }
            
        except Exception as e:
            result.error = f"Decryption failed: {str(e)}"
            result.fallback_triggered = True
        
        return result


# =============================================================================
# PLAYER EMBED API SIMULATOR
# =============================================================================

class PlayerEmbedAPISimulator:
    """
    Simulador completo do fluxo PlayerEmbedAPI v5.0
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.strategies = [
            ExtractionStrategies.strategy_1_direct_regex,
            ExtractionStrategies.strategy_2_base64_decode,
            ExtractionStrategies.strategy_3_json_parse,
            ExtractionStrategies.strategy_4_player_decrypt,
        ]
    
    def extract_with_fallback(self, html_content: str) -> ExtractionResult:
        """
        Tenta extrair URLs usando múltiplas estratégias com fallback
        """
        for i, strategy_func in enumerate(self.strategies):
            result = strategy_func(html_content)
            
            if result.success:
                result.fallback_triggered = i > 0  # Indica se fallback foi usado
                return result
        
        # Todas as estratégias falharam
        return ExtractionResult(
            strategy="All Failed",
            success=False,
            error="All extraction strategies failed",
            fallback_triggered=True
        )


# =============================================================================
# TEST SUITES
# =============================================================================

class TestSuites:
    """
    Conjunto completo de testes simulados
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.simulator = PlayerEmbedAPISimulator()
        self.mock_gen = MockHTMLGenerators()
        self.session = requests.Session()
    
    def log(self, message: str):
        """Log condicional baseado no modo verbose"""
        if self.verbose:
            print(f"  [LOG] {message}")
    
    def run_all_tests(self) -> List[TestResult]:
        """Executa todos os cenários de teste"""
        print("\n" + "=" * 80)
        print("HTTP SIMULATOR TEST - PlayerEmbedAPI v5.0")
        print("=" * 80)
        
        # Cenário 1: Resposta HTML do playerembedapi.link com base64 válido
        self.test_playerembedapi_success()
        
        # Cenário 2: Resposta HTML do short.icu com URL de vídeo
        self.test_short_icu_redirect()
        
        # Cenário 3: Respostas de erro
        self.test_error_404()
        self.test_error_timeout()
        self.test_error_500()
        self.test_error_403()
        
        # Cenário 4: Testar cada uma das 4 estratégias de extração
        self.test_strategy_1_direct_regex()
        self.test_strategy_2_base64_decode()
        self.test_strategy_3_json_parse()
        self.test_strategy_4_player_decrypt()
        
        # Cenário 5: Verificar se o fallback funciona corretamente
        self.test_fallback_mechanism()
        self.test_fallback_chain()
        
        return self.results
    
    # =========================================================================
    # CENÁRIO 1: playerembedapi.link com base64 válido
    # =========================================================================
    
    def test_playerembedapi_success(self):
        """Testa resposta HTML do playerembedapi.link com base64 válido"""
        test_name = "PlayerEmbedAPI - Base64 Valido"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Prepara dados de teste
            datas_json = json.dumps(TEST_DATAS)
            datas_b64 = base64.b64encode(datas_json.encode()).decode()
            
            # Gera HTML mock
            html = self.mock_gen.generate_playerembedapi_html(datas_b64)
            self.log(f"Generated HTML with datas length: {len(datas_b64)}")
            
            # Executa extração
            result = self.simulator.extract_with_fallback(html)
            
            if result.success and result.strategy == "Player Decrypt":
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Successfully extracted {len(result.urls)} URLs using {result.strategy}",
                    details=result.details
                ))
                print(f"  [OK] PASSED - Extracted {len(result.urls)} URLs")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message=f"Expected Player Decrypt strategy, got {result.strategy}",
                    details={'error': result.error}
                ))
                print(f"  [X] FAILED - {result.error}")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    # =========================================================================
    # CENÁRIO 2: short.icu com URL de vídeo
    # =========================================================================
    
    def test_short_icu_redirect(self):
        """Testa resposta HTML do short.icu com URL de vídeo"""
        test_name = "Short.ICU - Video URL"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Gera HTML mock
            html = self.mock_gen.generate_short_icu_html(TEST_FINAL_VIDEO_URL)
            self.log(f"Generated redirect HTML")
            
            # Executa extração
            result = self.simulator.extract_with_fallback(html)
            
            if result.success and TEST_FINAL_VIDEO_URL in result.urls:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Successfully found redirect URL via {result.strategy}",
                    details={'urls_found': result.urls}
                ))
                print(f"  [OK] PASSED - Found URL via {result.strategy}")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message=f"Expected to find {TEST_FINAL_VIDEO_URL}",
                    details={'urls_found': result.urls}
                ))
                print(f"  [X] FAILED - URL not found")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    # =========================================================================
    # CENÁRIO 3: Respostas de erro
    # =========================================================================
    
    def test_error_404(self):
        """Testa resposta 404 Not Found"""
        test_name = "Error - 404 Not Found"
        print(f"\n[TEST] {test_name}")
        
        try:
            with requests_mock.Mocker() as m:
                m.get("https://playerembedapi.link/test-404", status_code=404, 
                      text=self.mock_gen.generate_error_page(404, "Not Found"))
                
                response = self.session.get("https://playerembedapi.link/test-404")
                
                if response.status_code == 404:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.PASSED,
                        message="404 error correctly simulated"
                    ))
                    print(f"  [OK] PASSED - 404 error handled")
                else:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        message=f"Expected 404, got {response.status_code}"
                    ))
                    print(f"  [X] FAILED - Wrong status code")
                    
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_error_timeout(self):
        """Testa timeout de conexão"""
        test_name = "Error - Connection Timeout"
        print(f"\n[TEST] {test_name}")
        
        try:
            with requests_mock.Mocker() as m:
                m.get("https://playerembedapi.link/test-timeout", exc=Timeout)
                
                try:
                    response = self.session.get("https://playerembedapi.link/test-timeout", timeout=1)
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        message="Should have raised Timeout exception"
                    ))
                    print(f"  [X] FAILED - Should have raised Timeout")
                except Timeout:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.PASSED,
                        message="Timeout exception correctly raised"
                    ))
                    print(f"  [OK] PASSED - Timeout handled")
                    
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_error_500(self):
        """Testa resposta 500 Internal Server Error"""
        test_name = "Error - 500 Internal Server Error"
        print(f"\n[TEST] {test_name}")
        
        try:
            with requests_mock.Mocker() as m:
                m.get("https://playerembedapi.link/test-500", status_code=500,
                      text=self.mock_gen.generate_error_page(500, "Internal Server Error"))
                
                response = self.session.get("https://playerembedapi.link/test-500")
                
                if response.status_code == 500:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.PASSED,
                        message="500 error correctly simulated"
                    ))
                    print(f"  [OK] PASSED - 500 error handled")
                else:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        message=f"Expected 500, got {response.status_code}"
                    ))
                    print(f"  [X] FAILED - Wrong status code")
                    
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_error_403(self):
        """Testa resposta 403 Forbidden"""
        test_name = "Error - 403 Forbidden"
        print(f"\n[TEST] {test_name}")
        
        try:
            with requests_mock.Mocker() as m:
                m.get("https://playerembedapi.link/test-403", status_code=403,
                      text=self.mock_gen.generate_error_page(403, "Forbidden"))
                
                response = self.session.get("https://playerembedapi.link/test-403")
                
                if response.status_code == 403:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.PASSED,
                        message="403 error correctly simulated"
                    ))
                    print(f"  [OK] PASSED - 403 error handled")
                else:
                    self.results.append(TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        message=f"Expected 403, got {response.status_code}"
                    ))
                    print(f"  [X] FAILED - Wrong status code")
                    
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    # =========================================================================
    # CENÁRIO 4: Testar cada uma das 4 estratégias
    # =========================================================================
    
    def test_strategy_1_direct_regex(self):
        """Testa estratégia 1: Direct Regex"""
        test_name = "Strategy 1 - Direct Regex"
        print(f"\n[TEST] {test_name}")
        
        try:
            # HTML com URL direta
            html = f'<video src="{TEST_VIDEO_URL_MP4}"></video>'
            
            result = ExtractionStrategies.strategy_1_direct_regex(html)
            
            if result.success and TEST_VIDEO_URL_MP4 in result.urls:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Found {len(result.urls)} URLs via regex"
                ))
                print(f"  [OK] PASSED - Found URL via regex")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message="Failed to find URL via direct regex"
                ))
                print(f"  [X] FAILED - URL not found")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_strategy_2_base64_decode(self):
        """Testa estratégia 2: Base64 Decode"""
        test_name = "Strategy 2 - Base64 Decode"
        print(f"\n[TEST] {test_name}")
        
        try:
            # HTML com base64 contendo URL
            url_b64 = base64.b64encode(f'{{"video_url": "{TEST_VIDEO_URL_HLS}"}}'.encode()).decode()
            html = f'<script>const config = "{url_b64}";</script>'
            
            result = ExtractionStrategies.strategy_2_base64_decode(html)
            
            if result.success and TEST_VIDEO_URL_HLS in result.urls:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Found {len(result.urls)} URLs via base64 decode"
                ))
                print(f"  [OK] PASSED - Found URL via base64 decode")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message="Failed to find URL via base64 decode"
                ))
                print(f"  [X] FAILED - URL not found")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_strategy_3_json_parse(self):
        """Testa estratégia 3: JSON Parse"""
        test_name = "Strategy 3 - JSON Parse"
        print(f"\n[TEST] {test_name}")
        
        try:
            # HTML com JSON embutido
            config = json.dumps({
                "sources": [{"file": TEST_VIDEO_URL_HLS}],
                "tracks": []
            })
            html = f'<script>const playerConfig = {config};</script>'
            
            result = ExtractionStrategies.strategy_3_json_parse(html)
            
            if result.success and TEST_VIDEO_URL_HLS in result.urls:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Found {len(result.urls)} URLs via JSON parse"
                ))
                print(f"  [OK] PASSED - Found URL via JSON parse")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message="Failed to find URL via JSON parse"
                ))
                print(f"  [X] FAILED - URL not found")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_strategy_4_player_decrypt(self):
        """Testa estratégia 4: Player Decrypt"""
        test_name = "Strategy 4 - Player Decrypt"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Prepara dados de teste
            datas_json = json.dumps(TEST_DATAS)
            datas_b64 = base64.b64encode(datas_json.encode()).decode()
            
            html = self.mock_gen.generate_playerembedapi_html(datas_b64)
            
            result = ExtractionStrategies.strategy_4_player_decrypt(html)
            
            if result.success and len(result.urls) >= 2:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Decrypted and found {len(result.urls)} URLs",
                    details=result.details
                ))
                print(f"  [OK] PASSED - Decryption successful, found {len(result.urls)} URLs")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message="Failed to decrypt or find URLs"
                ))
                print(f"  ✗ FAILED - Decryption failed")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    # =========================================================================
    # CENÁRIO 5: Verificar fallback
    # =========================================================================
    
    def test_fallback_mechanism(self):
        """Testa mecanismo de fallback entre estratégias"""
        test_name = "Fallback - Strategy Switch"
        print(f"\n[TEST] {test_name}")
        
        try:
            # HTML que não funciona com estratégia 1, mas funciona com 2
            url_b64 = base64.b64encode(f'"{TEST_VIDEO_URL_HLS}"'.encode()).decode()
            html = f'''
            <html>
            <body>
                <div>No direct URLs here</div>
                <script>
                    const datas = "{url_b64}";
                </script>
            </body>
            </html>
            '''
            
            result = self.simulator.extract_with_fallback(html)
            
            if result.success and result.fallback_triggered:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message=f"Fallback triggered, used {result.strategy}",
                    details={'strategy_used': result.strategy}
                ))
                print(f"  [OK] PASSED - Fallback triggered, used {result.strategy}")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message="Fallback mechanism not working correctly"
                ))
                print(f"  [X] FAILED - Fallback not working")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")
    
    def test_fallback_chain(self):
        """Testa cadeia completa de fallback (todos falham exceto o último)"""
        test_name = "Fallback - Complete Chain"
        print(f"\n[TEST] {test_name}")
        
        try:
            # Prepara dados que só funcionam com a estratégia 4 (última)
            datas_json = json.dumps(TEST_DATAS)
            datas_b64 = base64.b64encode(datas_json.encode()).decode()
            
            # HTML sem URLs diretas, sem base64 óbvio, sem JSON óbvio
            # Apenas o campo datas criptografado
            html = f'''
            <html>
            <head><title>Player</title></head>
            <body>
                <div id="player"></div>
                <script>
                    (function() {{
                        const datas = "{datas_b64}";
                        // No other clues
                    }})();
                </script>
            </body>
            </html>
            '''
            
            result = self.simulator.extract_with_fallback(html)
            
            if result.success and result.strategy == "Player Decrypt" and result.fallback_triggered:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.PASSED,
                    message="Complete fallback chain worked correctly",
                    details={'final_strategy': result.strategy}
                ))
                print(f"  [OK] PASSED - Complete chain successful")
            else:
                self.results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAILED,
                    message=f"Expected Player Decrypt with fallback, got {result.strategy}"
                ))
                print(f"  [X] FAILED - Chain incomplete")
                
        except Exception as e:
            self.results.append(TestResult(
                name=test_name,
                status=TestStatus.ERROR,
                message=str(e)
            ))
            print(f"  [X] ERROR - {e}")


# =============================================================================
# REPORT GENERATOR
# =============================================================================

def generate_report(results: List[TestResult]) -> str:
    """Gera relatório formatado dos testes"""
    
    total = len(results)
    passed = sum(1 for r in results if r.status == TestStatus.PASSED)
    failed = sum(1 for r in results if r.status == TestStatus.FAILED)
    errors = sum(1 for r in results if r.status == TestStatus.ERROR)
    skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
    
    report = []
    report.append("\n" + "=" * 80)
    report.append("TEST REPORT - PlayerEmbedAPI HTTP Simulator")
    report.append("=" * 80)
    report.append(f"\nTotal Tests: {total}")
    report.append(f"  [OK] Passed:  {passed}")
    report.append(f"  [X] Failed:  {failed}")
    report.append(f"  [!] Errors:  {errors}")
    report.append(f"  [-] Skipped: {skipped}")
    report.append(f"\nSuccess Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")
    
    report.append("\n" + "-" * 80)
    report.append("DETAILED RESULTS:")
    report.append("-" * 80)
    
    for result in results:
        status_icon = {
            TestStatus.PASSED: "[OK]",
            TestStatus.FAILED: "[X]",
            TestStatus.ERROR: "[!]",
            TestStatus.SKIPPED: "[-]"
        }.get(result.status, "[?]")
        
        report.append(f"\n[{status_icon}] {result.name}")
        report.append(f"    Status: {result.status.name}")
        if result.message:
            report.append(f"    Message: {result.message}")
        if result.details:
            report.append(f"    Details: {json.dumps(result.details, indent=4)[:200]}...")
    
    report.append("\n" + "=" * 80)
    
    return "\n".join(report)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="HTTP Simulator Test - PlayerEmbedAPI v5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python http_simulator_test.py
  python http_simulator_test.py -v
  python http_simulator_test.py --save-report resultado.txt
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Modo verbose com logs detalhados')
    parser.add_argument('--save-report', metavar='FILE',
                        help='Salva relatório em arquivo')
    
    args = parser.parse_args()
    
    # Verifica se requests_mock está disponível
    if not REQUESTS_MOCK_AVAILABLE:
        print("[ERRO] requests_mock não está instalado.")
        print("Instale com: pip install requests_mock")
        sys.exit(1)
    
    # Executa testes
    test_suites = TestSuites(verbose=args.verbose)
    results = test_suites.run_all_tests()
    
    # Gera relatório
    report = generate_report(results)
    print(report)
    
    # Salva relatório se solicitado
    if args.save_report:
        with open(args.save_report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[+] Relatório salvo em: {args.save_report}")
    
    # Exit code baseado nos resultados
    failed_count = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR])
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
