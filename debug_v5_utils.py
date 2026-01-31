#!/usr/bin/env python3
"""
================================================================================
PlayerEmbedAPI v5.0 - Debug Utilities
================================================================================
Utilitários para debug do PlayerEmbedAPI Extractor v5.0 no projeto brcloudstream.

Funções principais:
1. Extrair e decodificar base64 'datas' manualmente
2. Simular a decriptação AES-CTR
3. Validar URLs de vídeo
4. Comparar resultados entre Python e Kotlin
5. Gerar logs detalhados para análise

Uso:
    from debug_v5_utils import PlayerEmbedDebugUtils
    
    # Debug completo de uma URL
    debug = PlayerEmbedDebugUtils()
    result = debug.full_debug("https://playerembedapi.link/?v=ABC123")
    
    # Ou usar via linha de comando:
    python debug_v5_utils.py <url>

Autor: Debug Tools for brcloudstream
Versão: 1.0.0 (Compatível com PlayerEmbedAPI v5.0)
================================================================================
"""

import sys
import re
import base64
import hashlib
import json
import time
import logging
from typing import Optional, List, Dict, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path

# Configuração de logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('PlayerEmbedDebug')

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

    @classmethod
    def disable(cls):
        """Desabilita cores (para output em arquivo)"""
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, '')


@dataclass
class DebugResult:
    """Resultado de uma operação de debug"""
    success: bool
    operation: str
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DecryptionResult:
    """Resultado da decriptação"""
    success: bool
    user_id: Optional[str] = None
    slug: Optional[str] = None
    md5_id: Optional[str] = None
    pre_key: Optional[str] = None
    key_md5: Optional[str] = None
    decrypted_json: Optional[dict] = None
    video_urls: List[Dict] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.video_urls is None:
            self.video_urls = []


@dataclass
class VideoLink:
    """Link de vídeo encontrado"""
    url: str
    quality: str
    source: str
    strategy: str
    is_valid: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)


class PlayerEmbedDebugUtils:
    """
    Utilitários de debug para PlayerEmbedAPI v5.0
    """
    
    # Constantes do v5.0
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"
    MAIN_URL = "https://playerembedapi.link"
    
    # Padrões base64 'datas' (compilados)
    BASE64_PATTERNS = [
        re.compile(r'const\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'var\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'let\s+datas\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'datas\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'data[=:]\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'"(eyJ[A-Za-z0-9+/=]{100,})"'),
        re.compile(r'window\.__DATA__\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
        re.compile(r'encryptedData\s*=\s*"([A-Za-z0-9+/=]{200,})"'),
    ]
    
    # Padrões de URL de vídeo
    VIDEO_URL_PATTERNS = [
        # Google Cloud Storage
        re.compile(r'(https://storage\.googleapis\.com/[^"\'<>\s]+\.mp4[^"\'<>\s]*)'),
        re.compile(r'(https://storage\.googleapis\.com/[^"\'<>\s]+)'),
        # SSSRR CDN
        re.compile(r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+\.mp4[^"\'<>\s]*)'),
        re.compile(r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+\.m3u8[^"\'<>\s]*)'),
        re.compile(r'(https?://[^/]*sssrr\.org/[^"\'<>\s]+)'),
        # Players genéricos
        re.compile(r'["\'](https?://[^"\'<>]+\.mp4[^"\'<>]*)["\']'),
        re.compile(r'["\'](https?://[^"\'<>]+\.m3u8[^"\'<>]*)["\']'),
        re.compile(r'["\'](https?://[^"\'<>]+\.mkv[^"\'<>]*)["\']'),
        re.compile(r'["\'](https?://[^"\'<>]+\.webm[^"\'<>]*)["\']'),
        # JWPlayer / VideoJS
        re.compile(r'file\s*:\s*["\']([^"\']+)["\']'),
        re.compile(r'src\s*:\s*["\']([^"\']+)["\']'),
    ]
    
    # Regex para extração de campos JSON
    USER_ID_PATTERN = re.compile(r'"user_id"\s*:\s*(\d+)')
    SLUG_PATTERN = re.compile(r'"slug"\s*:\s*"([^"]+)"')
    MD5_ID_PATTERN = re.compile(r'"md5_id"\s*:\s*(\d+)')
    MEDIA_PATTERN = re.compile(r'"media"\s*:\s*"((?:[^"\\]|\\.)*)"')
    
    # Domínios permitidos
    ALLOWED_VIDEO_DOMAINS = [
        'googleapis.com', 'sssrr.org', 'cdn', 'video',
        'stream', 'media', 'content'
    ]
    
    def __init__(self, use_colors: bool = True, log_file: Optional[str] = None):
        """
        Inicializa o utilitário de debug
        
        Args:
            use_colors: Se True, usa cores no terminal
            log_file: Se fornecido, salva logs neste arquivo
        """
        self.use_colors = use_colors
        if not use_colors:
            Colors.disable()
        
        self.log_file = log_file
        self.session = self._create_session()
        self.results: List[DebugResult] = []
        
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(message)s'
            ))
            logger.addHandler(file_handler)
    
    def _create_session(self):
        """Cria sessão HTTP configurada"""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            })
            
            # Retry strategy
            retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            return session
        except ImportError:
            logger.error("❌ requests não instalado. Instale: pip install requests")
            return None
    
    # =============================================================================
    # FUNÇÃO 1: Extrair e Decodificar Base64 'datas'
    # =============================================================================
    
    def extract_base64_datas(self, html: str) -> DebugResult:
        """
        Extrai e decodifica base64 'datas' do HTML
        
        Args:
            html: HTML da página do PlayerEmbedAPI
            
        Returns:
            DebugResult com os dados decodificados ou erro
        """
        start_time = time.time()
        operation = "extract_base64_datas"
        
        self._print_header("🔍 EXTRAINDO BASE64 'datas'")
        logger.info(f"HTML recebido: {len(html)} caracteres")
        
        for i, pattern in enumerate(self.BASE64_PATTERNS, 1):
            match = pattern.search(html)
            if match:
                candidate = match.group(1)
                try:
                    # Tentar decodificar
                    decoded_bytes = base64.b64decode(candidate)
                    decoded_str = decoded_bytes.decode('latin-1')
                    
                    duration = (time.time() - start_time) * 1000
                    
                    result = {
                        'pattern_used': i,
                        'base64_raw': candidate[:100] + "..." if len(candidate) > 100 else candidate,
                        'base64_length': len(candidate),
                        'decoded_bytes': len(decoded_bytes),
                        'decoded_preview': decoded_str[:200] + "..." if len(decoded_str) > 200 else decoded_str,
                        'decoded_full': decoded_str
                    }
                    
                    self._print_success(f"Base64 encontrado com pattern {i}")
                    logger.info(f"Base64 length: {len(candidate)}, Decoded: {len(decoded_str)} chars")
                    
                    debug_result = DebugResult(
                        success=True,
                        operation=operation,
                        data=result,
                        duration_ms=duration
                    )
                    self.results.append(debug_result)
                    return debug_result
                    
                except Exception as e:
                    logger.warning(f"Pattern {i} encontrou match mas base64 inválido: {e}")
                    continue
        
        duration = (time.time() - start_time) * 1000
        error_msg = "Nenhum base64 'datas' válido encontrado"
        self._print_error(error_msg)
        
        debug_result = DebugResult(
            success=False,
            operation=operation,
            error=error_msg,
            duration_ms=duration
        )
        self.results.append(debug_result)
        return debug_result
    
    def decode_base64_manual(self, b64_string: str) -> DebugResult:
        """
        Decodifica base64 manualmente com logs detalhados
        
        Args:
            b64_string: String base64 para decodificar
            
        Returns:
            DebugResult com dados decodificados
        """
        start_time = time.time()
        operation = "decode_base64_manual"
        
        self._print_header("🔐 DECODIFICAÇÃO BASE64 MANUAL")
        logger.info(f"Input: {b64_string[:50]}... ({len(b64_string)} chars)")
        
        try:
            # Validar caracteres base64
            valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
            invalid_chars = set(b64_string) - valid_chars
            if invalid_chars:
                logger.warning(f"Caracteres inválidos encontrados: {invalid_chars}")
            
            # Padding
            padding_needed = 4 - (len(b64_string) % 4) if len(b64_string) % 4 else 0
            logger.info(f"Padding necessário: {padding_needed}")
            
            # Decodificar
            decoded_bytes = base64.b64decode(b64_string)
            
            # Tentar diferentes encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            decoded_variants = {}
            
            for enc in encodings:
                try:
                    decoded_variants[enc] = decoded_bytes.decode(enc)
                    logger.info(f"✅ Decodificado com {enc}: {len(decoded_variants[enc])} chars")
                except Exception as e:
                    decoded_variants[enc] = f"<erro: {e}>"
            
            duration = (time.time() - start_time) * 1000
            
            result = {
                'input_length': len(b64_string),
                'output_bytes': len(decoded_bytes),
                'decoded_variants': decoded_variants,
                'hex_preview': decoded_bytes[:50].hex()
            }
            
            debug_result = DebugResult(
                success=True,
                operation=operation,
                data=result,
                duration_ms=duration
            )
            self.results.append(debug_result)
            return debug_result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            error_msg = f"Erro na decodificação: {str(e)}"
            self._print_error(error_msg)
            
            debug_result = DebugResult(
                success=False,
                operation=operation,
                error=error_msg,
                duration_ms=duration
            )
            self.results.append(debug_result)
            return debug_result
    
    # =============================================================================
    # FUNÇÃO 2: Simular Decriptação AES-CTR
    # =============================================================================
    
    def simulate_aes_ctr_decryption(
        self, 
        encrypted_bytes: bytes, 
        user_id: str, 
        slug: str, 
        md5_id: str,
        verbose: bool = True
    ) -> DecryptionResult:
        """
        Simula a decriptação AES-CTR do PlayerEmbedAPI v5.0
        
        Lógica (match com Kotlin LinkDecryptor.decryptPlayerEmbedMedia):
        1. PreKey = userId + ":" + slug + ":" + md5Id
        2. Hash = MD5(PreKey) (hex string, 32 chars)
        3. KeyBytes = Hash.toByteArray(UTF-8) (32 bytes)
        4. IV = KeyBytes[0..15] (primeiros 16 bytes)
        5. AES/CTR/NoPadding
        
        Args:
            encrypted_bytes: Bytes criptografados (campo 'media')
            user_id: ID do usuário
            slug: Slug do vídeo
            md5_id: ID MD5
            verbose: Se True, imprime logs detalhados
            
        Returns:
            DecryptionResult com resultado da decriptação
        """
        if verbose:
            self._print_header("🔓 SIMULAÇÃO AES-CTR DECRYPTION")
        
        logger.info(f"Input: {len(encrypted_bytes)} bytes")
        logger.info(f"user_id={user_id}, slug={slug}, md5_id={md5_id}")
        
        try:
            from Crypto.Cipher import AES
            from Crypto.Util import Counter
            
            # Passo 1: PreKey
            pre_key = f"{user_id}:{slug}:{md5_id}"
            if verbose:
                logger.info(f"Step 1 - PreKey: {pre_key}")
            
            # Passo 2: MD5 Hash
            md5_hash = hashlib.md5(pre_key.encode('utf-8')).hexdigest()
            if verbose:
                logger.info(f"Step 2 - MD5 Hash: {md5_hash[:16]}... (32 chars)")
            
            # Passo 3: KeyBytes
            key_bytes = md5_hash.encode('utf-8')
            if verbose:
                logger.info(f"Step 3 - KeyBytes: {len(key_bytes)} bytes")
            
            # Passo 4: IV
            iv_bytes = key_bytes[:16]
            if verbose:
                logger.info(f"Step 4 - IV: {iv_bytes.hex()[:32]}...")
            
            # Passo 5: AES-CTR Decrypt
            cipher = AES.new(
                key_bytes, 
                AES.MODE_CTR, 
                nonce=b'', 
                initial_value=int.from_bytes(iv_bytes, 'big'),
                counter=Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big'))
            )
            
            decrypted_bytes = cipher.decrypt(encrypted_bytes)
            
            # Tentar parse JSON
            decrypted_str = decrypted_bytes.decode('utf-8', errors='ignore')
            if verbose:
                logger.info(f"Decrypted: {decrypted_str[:100]}...")
            
            try:
                decrypted_json = json.loads(decrypted_str)
                if verbose:
                    self._print_success("Decriptação bem-sucedida!")
                    logger.info(f"JSON válido com {len(decrypted_json)} campos")
            except json.JSONDecodeError:
                decrypted_json = None
                if verbose:
                    logger.warning("Decriptação OK mas JSON inválido")
            
            # Extrair URLs de vídeo
            video_urls = self._extract_video_urls_from_json(decrypted_json) if decrypted_json else []
            
            return DecryptionResult(
                success=True,
                user_id=user_id,
                slug=slug,
                md5_id=md5_id,
                pre_key=pre_key,
                key_md5=md5_hash,
                decrypted_json=decrypted_json,
                video_urls=video_urls
            )
            
        except ImportError:
            error_msg = "PyCryptodome não instalado. Execute: pip install pycryptodome"
            self._print_error(error_msg)
            return DecryptionResult(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Erro na decriptação: {str(e)}"
            logger.exception("Erro detalhado:")
            return DecryptionResult(success=False, error=error_msg)
    
    def decrypt_from_base64(self, base64_data: str) -> DecryptionResult:
        """
        Pipeline completo: base64 -> JSON -> extrair campos -> AES-CTR -> resultado
        
        Args:
            base64_data: String base64 com os dados criptografados
            
        Returns:
            DecryptionResult com o resultado completo
        """
        self._print_header("🔄 PIPELINE COMPLETO: Base64 → AES-CTR")
        
        # 1. Decodificar base64
        decode_result = self.decode_base64_manual(base64_data)
        if not decode_result.success:
            return DecryptionResult(success=False, error=f"Base64 decode falhou: {decode_result.error}")
        
        decoded_str = decode_result.data['decoded_variants']['latin-1']
        
        # 2. Extrair campos
        user_id = self.USER_ID_PATTERN.search(decoded_str)
        slug = self.SLUG_PATTERN.search(decoded_str)
        md5_id = self.MD5_ID_PATTERN.search(decoded_str)
        media = self.MEDIA_PATTERN.search(decoded_str)
        
        if not all([user_id, slug, md5_id, media]):
            missing = []
            if not user_id: missing.append('user_id')
            if not slug: missing.append('slug')
            if not md5_id: missing.append('md5_id')
            if not media: missing.append('media')
            return DecryptionResult(success=False, error=f"Campos faltantes: {missing}")
        
        logger.info(f"Campos extraídos: user_id={user_id.group(1)}, slug={slug.group(1)}, md5_id={md5_id.group(1)}")
        
        # 3. Processar escapes JSON do media
        media_escaped = media.group(1)
        media_bytes = self._process_json_escapes(media_escaped)
        logger.info(f"Media bytes: {len(media_bytes)} bytes")
        
        # 4. Decriptar
        return self.simulate_aes_ctr_decryption(
            media_bytes,
            user_id.group(1),
            slug.group(1),
            md5_id.group(1)
        )
    
    def _process_json_escapes(self, escaped: str) -> bytes:
        """Processa escapes JSON e retorna bytes (match com Kotlin)"""
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
    
    def _extract_video_urls_from_json(self, json_data: dict) -> List[Dict]:
        """Extrai URLs de vídeo do JSON decriptado"""
        urls = []
        
        # Sources array
        sources = json_data.get('sources', [])
        for source in sources:
            file_url = source.get('file', '')
            label = source.get('label', 'Auto')
            if file_url and self.is_valid_video_url(file_url):
                urls.append({
                    'url': file_url,
                    'quality': label,
                    'type': source.get('type', 'unknown'),
                    'source': 'sources[]'
                })
        
        # HLS
        hls = json_data.get('hls')
        if hls and self.is_valid_video_url(hls):
            urls.append({
                'url': hls,
                'quality': self.detect_quality(hls),
                'type': 'hls',
                'source': 'hls field'
            })
        
        # MP4
        mp4 = json_data.get('mp4')
        if mp4 and self.is_valid_video_url(mp4):
            urls.append({
                'url': mp4,
                'quality': self.detect_quality(mp4),
                'type': 'mp4',
                'source': 'mp4 field'
            })
        
        return urls
    
    # =============================================================================
    # FUNÇÃO 3: Validar URLs de Vídeo
    # =============================================================================
    
    def is_valid_video_url(self, url: str) -> bool:
        """
        Valida se uma URL é um vídeo válido (match com v5.0)
        
        Args:
            url: URL para validar
            
        Returns:
            True se válido, False caso contrário
        """
        if not url or not isinstance(url, str):
            return False
        
        # Deve começar com http
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Verificar domínios permitidos
        has_allowed_domain = any(
            domain in url.lower() 
            for domain in self.ALLOWED_VIDEO_DOMAINS
        )
        
        # Verificar extensões de vídeo
        has_video_ext = any(
            ext in url.lower() 
            for ext in ['.mp4', '.m3u8', '.mkv', '.webm', '/video', '/stream']
        )
        
        return has_allowed_domain or has_video_ext
    
    def validate_video_url(self, url: str, test_access: bool = False) -> DebugResult:
        """
        Validação completa de URL de vídeo
        
        Args:
            url: URL para validar
            test_access: Se True, testa acessar a URL
            
        Returns:
            DebugResult com detalhes da validação
        """
        start_time = time.time()
        operation = "validate_video_url"
        
        self._print_header(f"✅ VALIDANDO URL: {url[:60]}...")
        
        checks = {
            'is_string': isinstance(url, str),
            'not_empty': bool(url),
            'starts_with_http': url.startswith(('http://', 'https://')) if isinstance(url, str) else False,
            'has_allowed_domain': any(d in url.lower() for d in self.ALLOWED_VIDEO_DOMAINS) if isinstance(url, str) else False,
            'has_video_extension': any(ext in url.lower() for ext in ['.mp4', '.m3u8', '.mkv', '.webm']) if isinstance(url, str) else False,
        }
        
        is_valid = all([
            checks['is_string'],
            checks['not_empty'],
            checks['starts_with_http'],
            checks['has_allowed_domain'] or checks['has_video_extension']
        ])
        
        result = {
            'url': url,
            'checks': checks,
            'is_valid': is_valid,
            'quality_detected': self.detect_quality(url) if is_valid else None,
            'parsed_url': urlparse(url)._asdict() if is_valid else None
        }
        
        # Testar acesso se solicitado
        if test_access and is_valid and self.session:
            try:
                logger.info("Testando acesso à URL...")
                response = self.session.head(url, timeout=10, allow_redirects=True)
                result['access_test'] = {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('Content-Type', 'unknown'),
                    'content_length': response.headers.get('Content-Length', 'unknown'),
                    'accessible': response.status_code == 200
                }
                if response.status_code == 200:
                    self._print_success("URL acessível!")
                else:
                    self._print_warning(f"URL retornou status {response.status_code}")
            except Exception as e:
                result['access_test'] = {'error': str(e), 'accessible': False}
                self._print_error(f"Erro ao testar acesso: {e}")
        
        duration = (time.time() - start_time) * 1000
        
        if is_valid:
            self._print_success(f"URL válida! Qualidade: {result['quality_detected']}")
        else:
            failed = [k for k, v in checks.items() if not v]
            self._print_error(f"URL inválida. Falhou em: {failed}")
        
        debug_result = DebugResult(
            success=is_valid,
            operation=operation,
            data=result,
            duration_ms=duration
        )
        self.results.append(debug_result)
        return debug_result
    
    def detect_quality(self, url: str) -> str:
        """Detecta qualidade da URL"""
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
    
    # =============================================================================
    # FUNÇÃO 4: Comparar Python vs Kotlin
    # =============================================================================
    
    def compare_python_kotlin(self, operation: str, **kwargs) -> DebugResult:
        """
        Compara implementação Python vs Kotlin equivalente
        
        Args:
            operation: Operação a comparar ('base64', 'aes', 'regex', 'json')
            **kwargs: Argumentos específicos da operação
            
        Returns:
            DebugResult com comparação lado a lado
        """
        start_time = time.time()
        
        self._print_header(f"🔄 COMPARAÇÃO PYTHON vs KOTLIN: {operation.upper()}")
        
        comparisons = {
            'base64': self._compare_base64,
            'aes': self._compare_aes,
            'regex': self._compare_regex,
            'json': self._compare_json,
            'http': self._compare_http,
            'validation': self._compare_validation
        }
        
        if operation not in comparisons:
            return DebugResult(
                success=False,
                operation="compare_python_kotlin",
                error=f"Operação '{operation}' não suportada. Use: {list(comparisons.keys())}"
            )
        
        result = comparisons[operation](**kwargs)
        duration = (time.time() - start_time) * 1000
        
        debug_result = DebugResult(
            success=True,
            operation=f"compare_{operation}",
            data=result,
            duration_ms=duration
        )
        self.results.append(debug_result)
        return debug_result
    
    def _compare_base64(self, b64_string: str) -> dict:
        """Compara decodificação base64"""
        python_code = f"""
# PYTHON
import base64
decoded = base64.b64decode("{b64_string[:30]}...")
text = decoded.decode('utf-8')"""
        
        kotlin_code = f"""
// KOTLIN
import android.util.Base64
val decoded = Base64.decode("{b64_string[:30]}...", Base64.DEFAULT)
val text = String(decoded, Charsets.UTF_8)"""
        
        # Executar Python
        try:
            decoded = base64.b64decode(b64_string)
            python_result = f"✅ {len(decoded)} bytes decodificados"
        except Exception as e:
            python_result = f"❌ Erro: {e}"
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Resultado: {python_result}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Resultado Kotlin: Mesmo resultado esperado{Colors.ENDC}")
        
        return {
            'python_code': python_code,
            'kotlin_code': kotlin_code,
            'python_result': python_result,
            'notes': 'Kotlin usa android.util.Base64 em vez do módulo base64 do Python'
        }
    
    def _compare_aes(self, encrypted: bytes, user_id: str, slug: str, md5_id: str) -> dict:
        """Compara decriptação AES-CTR"""
        python_code = f"""
# PYTHON
from Crypto.Cipher import AES
from Crypto.Util import Counter
import hashlib

pre_key = f"{{user_id}}:{{slug}}:{{md5_id}}"
md5_hash = hashlib.md5(pre_key.encode()).hexdigest()
key_bytes = md5_hash.encode('utf-8')
iv_bytes = key_bytes[:16]

cipher = AES.new(key_bytes, AES.MODE_CTR, 
                 nonce=b'', 
                 initial_value=int.from_bytes(iv_bytes, 'big'),
                 counter=Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big')))
decrypted = cipher.decrypt(encrypted_bytes)"""
        
        kotlin_code = f"""
// KOTLIN (LinkDecryptor.decryptPlayerEmbedMedia)
val preKey = "$userId:$slug:$md5Id"
val md5Hash = md5(preKey)  // hex string, 32 chars
val keyBytes = md5Hash.toByteArray(Charsets.UTF_8)  // 32 bytes
val ivBytes = keyBytes.copyOfRange(0, 16)  // primeiros 16 bytes

val algorithm = "AES/CTR/NoPadding"
val cipher = Cipher.getInstance(algorithm)
cipher.init(Cipher.DECRYPT_MODE, 
            SecretKeySpec(keyBytes, "AES"), 
            IvParameterSpec(ivBytes))
val decrypted = cipher.doFinal(encryptedBytes)"""
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        
        # Notas importantes
        print(f"\n{Colors.BOLD}⚠️  NOTAS IMPORTANTES:{Colors.ENDC}")
        print("   1. Kotlin usa javax.crypto (built-in do Android)")
        print("   2. Python precisa do PyCryptodome: pip install pycryptodome")
        print("   3. Ambos usam AES/CTR/NoPadding")
        print("   4. IV em Kotlin é gerado dos primeiros 16 bytes da chave MD5")
        
        return {
            'python_code': python_code,
            'kotlin_code': kotlin_code,
            'key_differences': [
                'Kotlin: javax.crypto (built-in)',
                'Python: PyCryptodome (instalação necessária)',
                'Ambos: AES/CTR/NoPadding',
                'IV: primeiros 16 bytes do MD5 hash'
            ]
        }
    
    def _compare_regex(self, pattern: str, text: str) -> dict:
        """Compara regex"""
        python_code = f"""
# PYTHON
import re
pattern = r"{pattern}"
match = re.search(pattern, text)
if match:
    valor = match.group(1)"""
        
        kotlin_code = f"""
// KOTLIN
val pattern = Regex(\"{pattern}\")
val match = pattern.find(text)
val valor = match?.groupValues?.get(1)"""
        
        # Testar Python
        import re
        match = re.search(pattern, text)
        python_result = match.group(1) if match else "Não encontrado"
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Resultado Python: {python_result}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Resultado Kotlin esperado: {python_result}{Colors.ENDC}")
        
        return {
            'python_code': python_code,
            'kotlin_code': kotlin_code,
            'python_result': python_result,
            'notes': 'Kotlin usa Regex() em vez de re.compile()'
        }
    
    def _compare_json(self, json_str: str) -> dict:
        """Compara parsing JSON"""
        python_code = """
# PYTHON
import json
data = json.loads(json_str)
valor = data['chave']"""
        
        kotlin_code = """
// KOTLIN
val mapper = JsonHelper.mapper  // ObjectMapper
val data = mapper.readTree(json_str)
val valor = data.get("chave").asText()"""
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Nota:{Colors.ENDC} Kotlin usa Jackson (ObjectMapper) para JSON")
        
        return {'python_code': python_code, 'kotlin_code': kotlin_code}
    
    def _compare_http(self, url: str) -> dict:
        """Compara requisição HTTP"""
        python_code = f"""
# PYTHON
import requests
response = requests.get("{url}", headers=headers, timeout=15)
html = response.text
status = response.status_code"""
        
        kotlin_code = f"""
// KOTLIN (CloudStream)
val response = app.get(
    url = "{url}",
    headers = mapOf("User-Agent" to USER_AGENT)
)
val html = response.text
val status = response.code"""
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        
        return {'python_code': python_code, 'kotlin_code': kotlin_code}
    
    def _compare_validation(self, url: str) -> dict:
        """Compara validação de URL"""
        python_code = """
# PYTHON
def is_valid_video_url(url: str) -> bool:
    if not url.startswith(('http://', 'https://')):
        return False
    allowed = ['googleapis.com', 'sssrr.org', 'cdn', 
               'video', 'stream', 'media']
    has_domain = any(d in url.lower() for d in allowed)
    has_ext = any(ext in url.lower() 
                  for ext in ['.mp4', '.m3u8', '.mkv'])
    return has_domain or has_ext"""
        
        kotlin_code = """
// KOTLIN
private fun isValidVideoUrl(url: String): Boolean {
    if (!url.startsWith("http")) return false
    val allowed = listOf("googleapis.com", "sssrr.org", 
                         "cdn", "video", "stream", "media")
    val hasDomain = allowed.any { url.contains(it, true) }
    val hasExt = listOf(".mp4", ".m3u8", ".mkv")
                 .any { url.contains(it, true) }
    return hasDomain || hasExt
}"""
        
        print(f"\n{Colors.OKCYAN}{python_code}{Colors.ENDC}")
        print(f"\n{Colors.WARNING}{kotlin_code}{Colors.ENDC}")
        
        return {'python_code': python_code, 'kotlin_code': kotlin_code}
    
    # =============================================================================
    # FUNÇÃO 5: Gerar Logs Detalhados
    # =============================================================================
    
    def generate_debug_report(self, output_file: Optional[str] = None) -> str:
        """
        Gera relatório detalhado de debug
        
        Args:
            output_file: Se fornecido, salva relatório neste arquivo
            
        Returns:
            String com o relatório
        """
        report = []
        report.append("=" * 80)
        report.append("PLAYEREMBEDAPI v5.0 - DEBUG REPORT")
        report.append("=" * 80)
        report.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de operações: {len(self.results)}")
        report.append("")
        
        # Resumo por operação
        report.append("-" * 80)
        report.append("RESUMO DAS OPERAÇÕES")
        report.append("-" * 80)
        
        for result in self.results:
            status = "✅" if result.success else "❌"
            report.append(f"{status} {result.operation}")
            report.append(f"   Duração: {result.duration_ms:.2f}ms")
            if result.error:
                report.append(f"   Erro: {result.error}")
            report.append("")
        
        # Estatísticas
        successes = sum(1 for r in self.results if r.success)
        failures = len(self.results) - successes
        total_time = sum(r.duration_ms for r in self.results)
        
        report.append("-" * 80)
        report.append("ESTATÍSTICAS")
        report.append("-" * 80)
        report.append(f"Sucessos: {successes}")
        report.append(f"Falhas: {failures}")
        report.append(f"Tempo total: {total_time:.2f}ms")
        report.append(f"Tempo médio: {total_time/len(self.results):.2f}ms" if self.results else "N/A")
        report.append("")
        
        # Detalhes completos
        report.append("-" * 80)
        report.append("DETALHES COMPLETOS")
        report.append("-" * 80)
        
        for i, result in enumerate(self.results, 1):
            report.append(f"\n[{i}] {result.operation}")
            report.append(f"    Timestamp: {result.timestamp}")
            report.append(f"    Sucesso: {result.success}")
            report.append(f"    Duração: {result.duration_ms:.2f}ms")
            if result.data:
                report.append(f"    Dados: {json.dumps(result.data, indent=2, default=str)[:500]}")
            if result.error:
                report.append(f"    Erro: {result.error}")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        report_str = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_str)
            print(f"\n📄 Relatório salvo em: {output_file}")
        
        return report_str
    
    def save_session_log(self, filename: str = None) -> str:
        """Salva log completo da sessão"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"debug_v5_session_{timestamp}.log"
        
        filepath = Path(filename)
        self.generate_debug_report(str(filepath))
        return str(filepath)
    
    # =============================================================================
    # DEBUG COMPLETO
    # =============================================================================
    
    def full_debug(self, url: str, save_report: bool = True) -> Dict:
        """
        Executa debug completo de uma URL do PlayerEmbedAPI
        
        Args:
            url: URL do PlayerEmbedAPI
            save_report: Se True, salva relatório em arquivo
            
        Returns:
            Dict com todos os resultados
        """
        self._print_header(f"🚀 DEBUG COMPLETO: PlayerEmbedAPI v5.0")
        print(f"URL: {url}")
        print(f"Iniciado em: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        overall_start = time.time()
        
        if not self.session:
            print("❌ Sessão HTTP não disponível")
            return {'success': False, 'error': 'No HTTP session'}
        
        try:
            # 1. Obter HTML
            print("\n📡 [1/5] Obtendo HTML...")
            response = self.session.get(url, timeout=15)
            html = response.text
            print(f"    Status: {response.status_code}")
            print(f"    Tamanho: {len(html)} caracteres")
            
            # 2. Extrair base64
            print("\n🔍 [2/5] Extraindo base64 'datas'...")
            base64_result = self.extract_base64_datas(html)
            
            if not base64_result.success:
                print("    ⚠️  Base64 não encontrado, tentando regex direto...")
                video_url = None
                for pattern in self.VIDEO_URL_PATTERNS:
                    match = pattern.search(html)
                    if match:
                        video_url = match.group(1).replace('\\/', '/')
                        break
                
                if video_url:
                    print(f"    ✅ URL encontrada via regex: {video_url[:60]}...")
                    self.validate_video_url(video_url, test_access=False)
                else:
                    print("    ❌ Nenhuma URL de vídeo encontrada")
                
                return {
                    'success': bool(video_url),
                    'url': url,
                    'video_url': video_url,
                    'strategy': 'regex_fallback'
                }
            
            # 3. Decriptar
            print("\n🔓 [3/5] Decriptando dados...")
            base64_data = base64_result.data['base64_raw']
            decrypt_result = self.decrypt_from_base64(base64_data)
            
            if not decrypt_result.success:
                print(f"    ❌ Falha na decriptação: {decrypt_result.error}")
                return {
                    'success': False,
                    'url': url,
                    'error': decrypt_result.error
                }
            
            print(f"    ✅ Decriptação bem-sucedida!")
            print(f"    JSON: {json.dumps(decrypt_result.decrypted_json, indent=2)[:200]}...")
            
            # 4. Validar URLs
            print("\n✅ [4/5] Validando URLs de vídeo...")
            valid_urls = []
            for video in decrypt_result.video_urls:
                validation = self.validate_video_url(video['url'], test_access=False)
                if validation.success:
                    valid_urls.append(video)
            
            print(f"    {len(valid_urls)} URLs válidas encontradas")
            
            # 5. Comparação Python vs Kotlin
            print("\n🔄 [5/5] Comparação Python vs Kotlin...")
            self.compare_python_kotlin('aes')
            
            # Resultado final
            overall_time = (time.time() - overall_start) * 1000
            
            result = {
                'success': len(valid_urls) > 0,
                'url': url,
                'duration_ms': overall_time,
                'base64_extracted': base64_result.success,
                'decryption': {
                    'success': decrypt_result.success,
                    'user_id': decrypt_result.user_id,
                    'slug': decrypt_result.slug,
                    'md5_id': decrypt_result.md5_id,
                    'video_count': len(decrypt_result.video_urls)
                },
                'video_urls': valid_urls,
                'all_results': [r.to_dict() for r in self.results]
            }
            
            # Salvar relatório
            if save_report:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = f"debug_v5_report_{timestamp}.log"
                self.save_session_log(report_file)
            
            return result
            
        except Exception as e:
            logger.exception("Erro durante debug completo:")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
    
    # =============================================================================
    # HELPERS DE OUTPUT
    # =============================================================================
    
    def _print_header(self, text: str):
        """Imprime header formatado"""
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKCYAN}{text}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
    
    def _print_success(self, text: str):
        """Imprime mensagem de sucesso"""
        print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")
        logger.info(text)
    
    def _print_error(self, text: str):
        """Imprime mensagem de erro"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")
        logger.error(text)
    
    def _print_warning(self, text: str):
        """Imprime mensagem de aviso"""
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")
        logger.warning(text)


# =============================================================================
# FUNÇÕES AUXILIARES (STANDALONE)
# =============================================================================

def quick_decode_base64(b64_string: str) -> Optional[str]:
    """Decodifica base64 rapidamente"""
    try:
        return base64.b64decode(b64_string).decode('latin-1')
    except Exception as e:
        print(f"Erro: {e}")
        return None

def quick_decrypt_aes(encrypted_hex: str, user_id: str, slug: str, md5_id: str) -> Optional[dict]:
    """Decripta AES-CTR rapidamente a partir de hex string"""
    try:
        from Crypto.Cipher import AES
        from Crypto.Util import Counter
        
        encrypted = bytes.fromhex(encrypted_hex)
        pre_key = f"{user_id}:{slug}:{md5_id}"
        md5_hash = hashlib.md5(pre_key.encode()).hexdigest()
        key_bytes = md5_hash.encode('utf-8')
        iv_bytes = key_bytes[:16]
        
        cipher = AES.new(
            key_bytes, 
            AES.MODE_CTR, 
            nonce=b'', 
            initial_value=int.from_bytes(iv_bytes, 'big'),
            counter=Counter.new(128, initial_value=int.from_bytes(iv_bytes, 'big'))
        )
        
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"Erro: {e}")
        return None

def validate_url(url: str) -> bool:
    """Valida URL de vídeo rapidamente"""
    debug = PlayerEmbedDebugUtils(use_colors=False)
    return debug.is_valid_video_url(url)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Função principal para uso via linha de comando"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Debug Utilities para PlayerEmbedAPI v5.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    # Debug completo de uma URL
    python debug_v5_utils.py "https://playerembedapi.link/?v=ABC123"
    
    # Apenas decodificar base64
    python debug_v5_utils.py --decode-base64 "eyJ0ZXN0IjogdHJ1ZX0="
    
    # Validar URL
    python debug_v5_utils.py --validate-url "https://storage.googleapis.com/..."
    
    # Comparar Python vs Kotlin
    python debug_v5_utils.py --compare aes
        """
    )
    
    parser.add_argument('url', nargs='?', help='URL do PlayerEmbedAPI para debug')
    parser.add_argument('--decode-base64', metavar='B64', help='Decodificar string base64')
    parser.add_argument('--decrypt-aes', metavar='HEX', help='Decriptar hex com AES-CTR')
    parser.add_argument('--user-id', help='User ID para decriptação AES')
    parser.add_argument('--slug', help='Slug para decriptação AES')
    parser.add_argument('--md5-id', help='MD5 ID para decriptação AES')
    parser.add_argument('--validate-url', metavar='URL', help='Validar URL de vídeo')
    parser.add_argument('--test-access', action='store_true', help='Testar acesso à URL')
    parser.add_argument('--compare', choices=['base64', 'aes', 'regex', 'json', 'http', 'validation'],
                       help='Comparar Python vs Kotlin')
    parser.add_argument('--no-color', action='store_true', help='Desabilitar cores no output')
    parser.add_argument('--save-report', action='store_true', help='Salvar relatório em arquivo')
    parser.add_argument('--log-file', help='Arquivo de log adicional')
    
    args = parser.parse_args()
    
    use_colors = not args.no_color
    
    # Inicializar debug utils
    debug = PlayerEmbedDebugUtils(use_colors=use_colors, log_file=args.log_file)
    
    # Executar comando solicitado
    if args.decode_base64:
        result = debug.decode_base64_manual(args.decode_base64)
        print(json.dumps(result.to_dict(), indent=2, default=str))
        
    elif args.decrypt_aes and args.user_id and args.slug and args.md5_id:
        encrypted = bytes.fromhex(args.decrypt_aes)
        result = debug.simulate_aes_ctr_decryption(
            encrypted, args.user_id, args.slug, args.md5_id
        )
        print(json.dumps(result.__dict__, indent=2, default=str))
        
    elif args.validate_url:
        result = debug.validate_video_url(args.validate_url, test_access=args.test_access)
        print(json.dumps(result.to_dict(), indent=2, default=str))
        
    elif args.compare:
        # Parâmetros adicionais para comparação
        kwargs = {}
        if args.compare == 'base64':
            kwargs['b64_string'] = args.decode_base64 or "eyJ0ZXN0IjogdHJ1ZX0="
        elif args.compare == 'aes':
            if args.decrypt_aes:
                kwargs['encrypted'] = bytes.fromhex(args.decrypt_aes)
                kwargs['user_id'] = args.user_id or "123"
                kwargs['slug'] = args.slug or "test"
                kwargs['md5_id'] = args.md5_id or "456"
        elif args.compare == 'regex':
            kwargs['pattern'] = r'"user_id"\s*:\s*(\d+)'
            kwargs['text'] = '{"user_id": 123, "slug": "test"}'
        elif args.compare == 'json':
            kwargs['json_str'] = '{"test": true, "value": 123}'
        elif args.compare == 'http':
            kwargs['url'] = args.url or "https://playerembedapi.link"
        elif args.compare == 'validation':
            kwargs['url'] = args.validate_url or "https://storage.googleapis.com/test.mp4"
            
        result = debug.compare_python_kotlin(args.compare, **kwargs)
        
    elif args.url:
        # Debug completo
        result = debug.full_debug(args.url, save_report=args.save_report)
        print("\n" + "=" * 80)
        print("RESULTADO FINAL:")
        print("=" * 80)
        print(json.dumps(result, indent=2, default=str))
        
    else:
        parser.print_help()
        print("\n" + "=" * 80)
        print("EXEMPLOS RÁPIDOS:")
        print("=" * 80)
        print("""
1. Debug completo:
   python debug_v5_utils.py "https://playerembedapi.link/?v=ABC123"

2. Decodificar base64:
   python debug_v5_utils.py --decode-base64 "eyJ0ZXN0IjogdHJ1ZX0="

3. Validar URL:
   python debug_v5_utils.py --validate-url "https://storage.googleapis.com/video.mp4" --test-access

4. Comparar implementações:
   python debug_v5_utils.py --compare aes
        """)


if __name__ == "__main__":
    main()
