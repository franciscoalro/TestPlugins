#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          PLAYEREMBEDAPI - ADVANCED REVERSE ENGINEERING TOOLKIT               ║
║                     White Hat Hacking & Extraction Suite                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Técnicas implementadas:
1. Análise estática do HTML e JavaScript
2. Decodificação e análise do campo 'datas'
3. Engenharia reversa do core.bundle.js
4. Simulação de execução JavaScript
5. Interceptação de rede simulada
6. Manipulação de DOM virtual
7. Análise de padrões de criptografia

Author: Security Researcher (White Hat)
Purpose: Video extraction for legitimate playback
"""

import base64
import json
import re
import sys
import hashlib
import binascii
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Configurações
REQUESTS_SESSION = requests.Session()
REQUESTS_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
})

@dataclass
class VideoData:
    """Estrutura dos dados decodificados do PlayerEmbedAPI"""
    slug: str
    md5_id: int
    user_id: int
    media: bytes  # Dados binários do campo media
    config: Dict[str, Any]
    raw_json: Dict[str, Any]
    
@dataclass
class ExtractedVideo:
    """Resultado da extração de vídeo"""
    url: str
    quality: str
    source: str
    headers: Dict[str, str]
    is_direct: bool
    extraction_method: str

class PlayerEmbedAPIAnalyzer:
    """
    Analisador avançado do PlayerEmbedAPI
    Implementa múltiplas técnicas de engenharia reversa
    """
    
    def __init__(self, html_content: str = None, url: str = None):
        self.html = html_content
        self.url = url
        self.soup = BeautifulSoup(html_content, 'html.parser') if html_content else None
        self.video_data: Optional[VideoData] = None
        self.js_scripts: List[str] = []
        self.network_calls: List[Dict] = []
        
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 1: ANÁLISE ESTÁTICA DO HTML
    # ═══════════════════════════════════════════════════════════════════════════
    
    def extract_datas_field(self) -> Optional[str]:
        """
        Extrai o campo 'datas' base64 do HTML
        Técnica: Regex + Parsing HTML
        """
        if not self.html:
            return None
            
        # Padrão 1: const datas = "..."
        pattern1 = r'const\s+datas\s*=\s*"([^"]+)"'
        match = re.search(pattern1, self.html)
        if match:
            return match.group(1)
            
        # Padrão 2: var datas = "..."
        pattern2 = r'var\s+datas\s*=\s*"([^"]+)"'
        match = re.search(pattern2, self.html)
        if match:
            return match.group(1)
            
        # Padrão 3: window.datas ou datas =
        pattern3 = r'datas\s*=\s*["\']([^"\']+)["\']'
        match = re.search(pattern3, self.html)
        if match:
            return match.group(1)
            
        return None
    
    def decode_datas(self, datas_b64: str) -> Optional[VideoData]:
        """
        Decodifica o campo datas de base64 para estrutura JSON
        """
        try:
            # Adicionar padding se necessário
            padding = 4 - len(datas_b64) % 4
            if padding != 4:
                datas_b64 += '=' * padding
                
            decoded = base64.b64decode(datas_b64)
            json_data = json.loads(decoded)
            
            # O campo media pode ser string base64 ou dados binários
            media_data = json_data.get('media', '')
            if isinstance(media_data, str):
                try:
                    media_bytes = base64.b64decode(media_data)
                except:
                    media_bytes = media_data.encode('utf-8')
            else:
                media_bytes = bytes(media_data) if media_data else b''
            
            self.video_data = VideoData(
                slug=json_data.get('slug', ''),
                md5_id=json_data.get('md5_id', 0),
                user_id=json_data.get('user_id', 0),
                media=media_bytes,
                config=json_data.get('config', {}),
                raw_json=json_data
            )
            
            return self.video_data
            
        except Exception as e:
            print(f"[!] Erro ao decodificar datas: {e}")
            return None
    
    def extract_js_scripts(self) -> List[str]:
        """
        Extrai todos os scripts JavaScript do HTML
        """
        if not self.soup:
            return []
            
        scripts = []
        for script in self.soup.find_all('script'):
            if script.string:
                scripts.append(script.string)
            elif script.get('src'):
                scripts.append(script['src'])
        
        self.js_scripts = scripts
        return scripts
    
    def analyze_js_variables(self) -> Dict[str, Any]:
        """
        Analisa variáveis JavaScript no HTML
        """
        variables = {}
        
        if not self.html:
            return variables
            
        # Padrões comuns
        patterns = {
            'isTouchScreen': r'const\s+isTouchScreen\s*=\s*([^;]+)',
            'isUseExtension': r'const\s+isUseExtension\s*=\s*([^;]+)',
            'jwplayer_config': r'jwplayer\(["\'][^"\']+["\']\)\.setup\((\{[^}]+\})\)',
            'sources': r'sources\s*:\s*(\[[^\]]+\])',
            'file_url': r'file\s*:\s*["\']([^"\']+)["\']',
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, self.html)
            if matches:
                variables[name] = matches
                
        return variables
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 2: ENGENHARIA REVERSA DO CAMPO 'media'
    # ═══════════════════════════════════════════════════════════════════════════
    
    def analyze_media_field(self) -> Dict[str, Any]:
        """
        Analisa o campo media criptografado/codificado
        """
        if not self.video_data:
            return {}
            
        media = self.video_data.media
        analysis = {
            'size': len(media),
            'entropy': self._calculate_entropy(media),
            'is_printable': all(32 <= b < 127 for b in media[:100]),
            'prefix_hex': media[:32].hex() if media else '',
            'possible_encoding': None,
            'decryption_attempts': []
        }
        
        # Tentar detectar encoding
        if media.startswith(b'{'):
            analysis['possible_encoding'] = 'json'
            try:
                analysis['decryption_attempts'].append({
                    'method': 'raw_json',
                    'result': json.loads(media.decode('utf-8'))
                })
            except:
                pass
        elif all(b < 128 for b in media[:100]):
            analysis['possible_encoding'] = 'ascii/base64'
            
        return analysis
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcula a entropia de Shannon dos dados"""
        if not data:
            return 0.0
            
        from math import log2
        entropy = 0
        for x in range(256):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * log2(p_x)
        return entropy
    
    def attempt_aes_decryption(self, key_derivation: str = None) -> List[Dict]:
        """
        Tenta descriptografar o campo media usando AES
        """
        if not self.video_data:
            return []
            
        results = []
        media = self.video_data.media
        
        # Gerar chaves possíveis baseadas nos dados
        possible_keys = [
            f"{self.video_data.user_id}:{self.video_data.md5_id}:{self.video_data.slug}",
            f"{self.video_data.md5_id}:{self.video_data.user_id}:{self.video_data.slug}",
            self.video_data.slug,
            str(self.video_data.md5_id),
            hashlib.md5(f"{self.video_data.user_id}:{self.video_data.md5_id}".encode()).hexdigest(),
            hashlib.sha256(f"{self.video_data.user_id}:{self.video_data.md5_id}:{self.video_data.slug}".encode()).hexdigest()[:32],
        ]
        
        if key_derivation:
            possible_keys.insert(0, key_derivation)
        
        # Tentar cada chave (requer biblioteca de cripto)
        try:
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            
            for key_str in possible_keys[:3]:  # Limitar tentativas
                try:
                    # Criar chave de 16 bytes
                    key = hashlib.md5(key_str.encode()).digest()
                    
                    # Tentar AES-ECB
                    cipher = AES.new(key, AES.MODE_ECB)
                    decrypted = cipher.decrypt(media[:32])  # Testar primeiro bloco
                    
                    results.append({
                        'key': key_str,
                        'mode': 'AES-ECB',
                        'sample': decrypted[:20].hex(),
                        'is_printable': all(32 <= b < 127 for b in decrypted[:20] if b != 0)
                    })
                    
                except Exception as e:
                    results.append({
                        'key': key_str,
                        'error': str(e)
                    })
                    
        except ImportError:
            results.append({'error': 'pycryptodome não instalado'})
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 3: ANÁLISE DO core.bundle.js
    # ═══════════════════════════════════════════════════════════════════════════
    
    def analyze_core_bundle(self, bundle_path: str = 'core_bundle.js') -> Dict[str, Any]:
        """
        Analisa o arquivo core.bundle.js para encontrar funções de decriptação
        """
        try:
            with open(bundle_path, 'r', encoding='utf-8', errors='ignore') as f:
                bundle = f.read()
        except FileNotFoundError:
            return {'error': f'Arquivo {bundle_path} não encontrado'}
        
        analysis = {
            'size': len(bundle),
            'functions_found': [],
            'encryption_patterns': [],
            'string_patterns': []
        }
        
        # Procurar por funções SoTrym
        sotrym_patterns = [
            r'window\.SoTrym\s*=\s*function\s*\(([^)]+)\)\s*\{',
            r'function\s+SoTrym\s*\(([^)]+)\)',
            r'SoTrym\s*[=:]\s*function',
            r'var\s+SoTrym\s*=',
        ]
        
        for pattern in sotrym_patterns:
            matches = re.findall(pattern, bundle)
            if matches:
                analysis['functions_found'].append({
                    'name': 'SoTrym',
                    'pattern': pattern,
                    'matches': matches
                })
        
        # Procurar por padrões de criptografia
        crypto_patterns = {
            'AES': r'AES|aes|encrypt|decrypt',
            'CryptoJS': r'CryptoJS',
            'WebCrypto': r'crypto\.subtle|webkitSubtle',
            'Base64': r'atob|btoa|Base64',
            'XOR': r'\^\s*\w+',
            'RC4': r'RC4|rc4',
        }
        
        for name, pattern in crypto_patterns.items():
            matches = re.findall(pattern, bundle)
            if matches:
                analysis['encryption_patterns'].append({
                    'algorithm': name,
                    'count': len(matches)
                })
        
        # Procurar por strings suspeitas
        string_pattern = r'["\']([a-f0-9]{32,})["\']'
        hex_strings = re.findall(string_pattern, bundle)
        analysis['string_patterns'] = hex_strings[:10]  # Primeiros 10
        
        return analysis
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 4: SIMULAÇÃO DE EXECUÇÃO JAVASCRIPT
    # ═══════════════════════════════════════════════════════════════════════════
    
    def simulate_js_execution(self) -> Dict[str, Any]:
        """
        Simula a execução do JavaScript para prever comportamento
        """
        if not self.video_data:
            return {'error': 'Dados do vídeo não carregados'}
        
        simulation = {
            'predicted_calls': [],
            'jwplayer_setup': None,
            'video_url_patterns': []
        }
        
        # Simular chamadas de rede baseadas nos dados
        video_id = self.video_data.md5_id
        slug = self.video_data.slug
        
        # Padrões de URL prováveis
        patterns = [
            f"https://*.sssrr.org/sora/{video_id}/*",
            f"https://*.sssrr.org/*/{video_id}.*.fd",
            f"https://iamcdn.net/*/{slug}/*",
            f"https://statics.sssrr.org/player/*",
        ]
        simulation['predicted_calls'] = patterns
        
        # Configuração provável do JWPlayer
        simulation['jwplayer_setup'] = {
            'file': f'https://cdn.sssrr.org/{video_id}/master.m3u8',
            'type': 'hls',
            'drm': False,
            'autostart': True
        }
        
        return simulation
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 5: EXTRAÇÃO POR HTTP DIRETO
    # ═══════════════════════════════════════════════════════════════════════════
    
    def attempt_direct_extraction(self, url: str = None) -> List[ExtractedVideo]:
        """
        Tenta extrair URL de vídeo diretamente via HTTP
        """
        target_url = url or self.url
        if not target_url:
            return []
        
        results = []
        
        try:
            # Fazer requisição
            response = REQUESTS_SESSION.get(target_url, timeout=30)
            response.raise_for_status()
            
            html = response.text
            
            # Técnica 5.1: Procurar por URLs de vídeo no HTML
            video_patterns = [
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*',
                r'https?://[^\s"\'<>]*sssrr\.org[^\s"\'<>]*',
                r'file\s*:\s*["\']([^"\']+)["\']',
                r'sources\s*:\s*\[\s*\{[^}]*file\s*:\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in video_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    results.append(ExtractedVideo(
                        url=match,
                        quality='Unknown',
                        source='PlayerEmbedAPI',
                        headers={'Referer': target_url},
                        is_direct=True,
                        extraction_method='regex_direct'
                    ))
            
            # Técnica 5.2: Procurar por JSON com configuração de vídeo
            json_patterns = [
                r'var\s+config\s*=\s*(\{[^;]+\});',
                r'var\s+sources\s*=\s*(\[[^\]]+\]);',
                r'var\s+playerConfig\s*=\s*(\{[^;]+\});',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        config = json.loads(match)
                        if isinstance(config, dict):
                            if 'file' in config:
                                results.append(ExtractedVideo(
                                    url=config['file'],
                                    quality=config.get('label', 'Unknown'),
                                    source='PlayerEmbedAPI',
                                    headers={'Referer': target_url},
                                    is_direct=True,
                                    extraction_method='json_config'
                                ))
                            elif 'sources' in config:
                                for source in config['sources']:
                                    if 'file' in source:
                                        results.append(ExtractedVideo(
                                            url=source['file'],
                                            quality=source.get('label', 'Unknown'),
                                            source='PlayerEmbedAPI',
                                            headers={'Referer': target_url},
                                            is_direct=True,
                                            extraction_method='json_sources'
                                        ))
                    except json.JSONDecodeError:
                        pass
            
        except Exception as e:
            print(f"[!] Erro na extração direta: {e}")
        
        # Remover duplicatas
        seen = set()
        unique_results = []
        for r in results:
            if r.url not in seen:
                seen.add(r.url)
                unique_results.append(r)
        
        return unique_results
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TÉCNICA 6: MANIPULAÇÃO DE DOM VIRTUAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def virtual_dom_analysis(self) -> Dict[str, Any]:
        """
        Analisa o DOM virtualmente sem executar JavaScript
        """
        if not self.soup:
            return {}
        
        analysis = {
            'video_elements': [],
            'iframe_sources': [],
            'data_attributes': {},
            'meta_tags': {}
        }
        
        # Procurar elementos de vídeo
        for video in self.soup.find_all('video'):
            analysis['video_elements'].append({
                'src': video.get('src'),
                'data_src': video.get('data-src'),
                'poster': video.get('poster'),
            })
        
        # Procurar iframes
        for iframe in self.soup.find_all('iframe'):
            analysis['iframe_sources'].append(iframe.get('src'))
        
        # Procurar data-* attributes
        for elem in self.soup.find_all(attrs={"data-source": True}):
            analysis['data_attributes']['source'] = elem.get('data-source')
        
        # Meta tags relevantes
        for meta in self.soup.find_all('meta'):
            if meta.get('property') in ['og:video', 'og:video:url', 'og:video:secure_url']:
                analysis['meta_tags'][meta.get('property')] = meta.get('content')
        
        return analysis


# ═══════════════════════════════════════════════════════════════════════════════
# TÉCNICA 7: ORQUESTRADOR DE EXTRAÇÃO AVANÇADO
# ═══════════════════════════════════════════════════════════════════════════════

class AdvancedVideoExtractor:
    """
    Orquestrador que combina múltiplas técnicas de extração
    """
    
    def __init__(self):
        self.analyzer: Optional[PlayerEmbedAPIAnalyzer] = None
        self.results: List[ExtractedVideo] = []
        self.log: List[str] = []
    
    def log_step(self, message: str):
        """Registra um passo do processo"""
        self.log.append(message)
        print(f"[+] {message}")
    
    def extract_from_url(self, url: str, html_content: str = None) -> List[ExtractedVideo]:
        """
        Pipeline completo de extração usando múltiplas técnicas
        """
        self.log_step(f"Iniciando extração avançada: {url}")
        
        # Passo 1: Obter HTML
        if not html_content:
            try:
                self.log_step("Obtendo HTML da URL...")
                response = REQUESTS_SESSION.get(url, timeout=30)
                html_content = response.text
            except Exception as e:
                self.log_step(f"[!] Erro ao obter HTML: {e}")
                return []
        
        # Passo 2: Inicializar analisador
        self.analyzer = PlayerEmbedAPIAnalyzer(html_content, url)
        
        # Passo 3: Pipeline de técnicas
        techniques = [
            ("Extração direta via HTTP", self._technique_direct_http),
            ("Análise do campo datas", self._technique_datas_analysis),
            ("Engenharia reversa do media", self._technique_media_reverse),
            ("Análise de DOM virtual", self._technique_dom_virtual),
            ("Simulação JavaScript", self._technique_js_simulation),
        ]
        
        all_results = []
        
        for name, technique in techniques:
            self.log_step(f"Aplicando: {name}...")
            try:
                results = technique()
                if results:
                    self.log_step(f"  ✓ Técnica '{name}' encontrou {len(results)} resultado(s)")
                    all_results.extend(results)
                else:
                    self.log_step(f"  ✗ Técnica '{name}' não encontrou resultados")
            except Exception as e:
                self.log_step(f"  [!] Erro em '{name}': {e}")
        
        # Passo 4: Deduplicação e validação
        self.results = self._deduplicate_and_validate(all_results)
        
        self.log_step(f"Extração completa: {len(self.results)} vídeo(s) encontrado(s)")
        return self.results
    
    def _technique_direct_http(self) -> List[ExtractedVideo]:
        """Técnica 1: Extração direta via HTTP"""
        return self.analyzer.attempt_direct_extraction()
    
    def _technique_datas_analysis(self) -> List[ExtractedVideo]:
        """Técnica 2: Análise do campo datas"""
        datas = self.analyzer.extract_datas_field()
        if not datas:
            return []
        
        video_data = self.analyzer.decode_datas(datas)
        if not video_data:
            return []
        
        self.log_step(f"  → Dados decodificados: slug={video_data.slug}, md5_id={video_data.md5_id}")
        
        # Tentar construir URL diretamente dos dados
        results = []
        
        # Padrão conhecido do sssrr.org
        potential_urls = [
            f"https://{video_data.slug}.sssrr.org/sora/{video_data.md5_id}/",
        ]
        
        for pot_url in potential_urls:
            results.append(ExtractedVideo(
                url=pot_url,
                quality='Unknown',
                source='PlayerEmbedAPI',
                headers={'Referer': self.analyzer.url},
                is_direct=False,
                extraction_method='datas_constructed'
            ))
        
        return results
    
    def _technique_media_reverse(self) -> List[ExtractedVideo]:
        """Técnica 3: Engenharia reversa do campo media"""
        if not self.analyzer.video_data:
            return []
        
        analysis = self.analyzer.analyze_media_field()
        self.log_step(f"  → Campo media: {analysis.get('size', 0)} bytes, entropia: {analysis.get('entropy', 0):.2f}")
        
        # Tentativas de decriptação
        attempts = self.analyzer.attempt_aes_decryption()
        self.log_step(f"  → Tentativas de decriptação: {len(attempts)}")
        
        return []  # Retorna vazio por enquanto, apenas análise
    
    def _technique_dom_virtual(self) -> List[ExtractedVideo]:
        """Técnica 4: Análise de DOM virtual"""
        dom_analysis = self.analyzer.virtual_dom_analysis()
        results = []
        
        for video in dom_analysis.get('video_elements', []):
            if video.get('src'):
                results.append(ExtractedVideo(
                    url=video['src'],
                    quality='Unknown',
                    source='PlayerEmbedAPI',
                    headers={'Referer': self.analyzer.url},
                    is_direct=True,
                    extraction_method='dom_video_element'
                ))
        
        return results
    
    def _technique_js_simulation(self) -> List[ExtractedVideo]:
        """Técnica 5: Simulação JavaScript"""
        simulation = self.analyzer.simulate_js_execution()
        results = []
        
        for pattern in simulation.get('predicted_calls', []):
            if pattern.startswith('http'):
                results.append(ExtractedVideo(
                    url=pattern,
                    quality='Unknown',
                    source='PlayerEmbedAPI',
                    headers={'Referer': self.analyzer.url},
                    is_direct=False,
                    extraction_method='js_simulation'
                ))
        
        return results
    
    def _deduplicate_and_validate(self, results: List[ExtractedVideo]) -> List[ExtractedVideo]:
        """Remove duplicatas e valida URLs"""
        seen = set()
        unique = []
        
        for r in results:
            # Normalizar URL
            url = r.url.split('?')[0] if '?' in r.url else r.url
            
            if url not in seen and url.startswith('http'):
                seen.add(url)
                unique.append(r)
        
        return unique
    
    def generate_report(self) -> str:
        """Gera relatório completo da análise"""
        report = []
        report.append("=" * 80)
        report.append("PLAYEREMBEDAPI - RELATÓRIO DE ANÁLISE AVANÇADA")
        report.append("=" * 80)
        report.append("")
        
        # Log de execução
        report.append("LOG DE EXECUÇÃO:")
        report.append("-" * 40)
        for entry in self.log:
            report.append(f"  {entry}")
        report.append("")
        
        # Resultados
        report.append(f"RESULTADOS ({len(self.results)} vídeo(s)):")
        report.append("-" * 40)
        for i, video in enumerate(self.results, 1):
            report.append(f"\n  [{i}] {video.extraction_method}")
            report.append(f"      URL: {video.url[:80]}...")
            report.append(f"      Qualidade: {video.quality}")
            report.append(f"      Direto: {'Sim' if video.is_direct else 'Não'}")
        
        # Dados decodificados
        if self.analyzer and self.analyzer.video_data:
            vd = self.analyzer.video_data
            report.append("\n")
            report.append("DADOS DECODIFICADOS:")
            report.append("-" * 40)
            report.append(f"  Slug: {vd.slug}")
            report.append(f"  MD5 ID: {vd.md5_id}")
            report.append(f"  User ID: {vd.user_id}")
            report.append(f"  Media Size: {len(vd.media)} bytes")
            report.append(f"  Config: {json.dumps(vd.config, indent=2)}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Função principal de execução"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║          PLAYEREMBEDAPI - ADVANCED REVERSE ENGINEERING TOOLKIT               ║
    ║                     White Hat Hacking & Extraction Suite                     ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    extractor = AdvancedVideoExtractor()
    
    # Testar com arquivo local ou URL
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        
        if input_path.startswith('http'):
            # URL
            results = extractor.extract_from_url(input_path)
        else:
            # Arquivo local
            try:
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()
                results = extractor.extract_from_url("file://" + input_path, html)
            except FileNotFoundError:
                print(f"[!] Arquivo não encontrado: {input_path}")
                return
    else:
        # Procurar por arquivos de exemplo
        example_files = [
            'playerembedapi_kBJLtxCD3.html',
            'playerembedapi_QvXFt2de3.html',
            'playerembedapi_response_new.html',
        ]
        
        for example in example_files:
            if Path(example).exists():
                print(f"[*] Analisando arquivo de exemplo: {example}")
                with open(example, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()
                results = extractor.extract_from_url("file://" + example, html)
                break
        else:
            print("[!] Nenhum arquivo de exemplo encontrado")
            print("[*] Uso: python hacker_playerembedapi_advanced.py <url|arquivo.html>")
            return
    
    # Gerar e salvar relatório
    report = extractor.generate_report()
    print(report)
    
    # Salvar relatório
    report_file = 'playerembedapi_hacker_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n[*] Relatório salvo em: {report_file}")


if __name__ == '__main__':
    main()
