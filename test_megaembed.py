#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MegaEmbed Link Fetcher - Tester Completo em Python
Protótipo avançado para testar extração ANTES de fazer build do plugin Kotlin

Recursos:
- Extração de videoId com múltiplos padrões
- Teste de APIs com retry automático
- Construção de URLs baseada em padrões descobertos
- Cache de respostas para evitar requisições repetidas
- Logging detalhado para arquivo
- Exportação de resultados (JSON/CSV)
- Análise de qualidade do M3U8
- Modo interativo
- Métricas de performance

Uso:
    python test_megaembed.py
    python test_megaembed.py --url "https://megaembed.link/#3wnuij"
    python test_megaembed.py --video-id 3wnuij
    python test_megaembed.py --interactive
    python test_megaembed.py --batch urls.txt
    python test_megaembed.py --verbose

Autor: Para TCC sobre CloudStream Plugin Development
Data: 2026-01-17
"""

import sys
import io

# Configurar UTF-8 para stdout/stderr no Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import re
import json
import time
import argparse
import logging
import hashlib
import os
import pickle
import csv
from typing import Optional, List, Dict, Tuple, Any
from pprint import pprint
from datetime import datetime
from contextlib import contextmanager
from functools import wraps

# ============================================
# CONFIGURAÇÃO DE LOGGING
# ============================================

def setup_logging(log_file: str = None, verbose: bool = False) -> str:
    """Configura logging para console e arquivo"""
    if log_file is None:
        log_file = f"megaembed_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    level = logging.DEBUG if verbose else logging.INFO
    
    # Remover handlers existentes
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return log_file

# ============================================
# CACHE DE RESPOSTAS
# ============================================

class ResponseCache:
    """Cache simples de respostas HTTP para evitar requisições repetidas"""
    
    def __init__(self, cache_dir: str = ".cache", ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # Time to live em segundos
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url: str) -> str:
        """Gera chave única para URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[dict]:
        """Busca resposta no cache"""
        cache_file = os.path.join(self.cache_dir, self._get_cache_key(url))
        
        if os.path.exists(cache_file):
            # Verificar se cache ainda é válido
            if time.time() - os.path.getmtime(cache_file) < self.ttl:
                try:
                    with open(cache_file, 'rb') as f:
                        logging.info(f"💾 Usando cache para: {url[:60]}...")
                        return pickle.load(f)
                except Exception as e:
                    logging.warning(f"Erro ao ler cache: {e}")
        return None
    
    def set(self, url: str, response_data: dict):
        """Salva resposta no cache"""
        cache_file = os.path.join(self.cache_dir, self._get_cache_key(url))
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(response_data, f)
            logging.debug(f"Cache salvo para: {url[:60]}...")
        except Exception as e:
            logging.warning(f"Erro ao salvar cache: {e}")
    
    def clear(self):
        """Limpa todo o cache"""
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                logging.warning(f"Erro ao remover cache {filename}: {e}")
        logging.info("Cache limpo")

# ============================================
# ARMAZENAMENTO DE RESULTADOS
# ============================================

class TestResults:
    """Armazena e exporta resultados dos testes"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, url: str, video_id: str, method: str, 
                   success: bool, playlist_url: str = None, 
                   elapsed_time: float = 0, error: str = None,
                   m3u8_analysis: dict = None):
        """Adiciona resultado de teste"""
        self.results.append({
            "timestamp": datetime.now().isoformat(),
            "input_url": url,
            "video_id": video_id,
            "method": method,  # "api", "api_token", "constructed", "failed"
            "success": success,
            "playlist_url": playlist_url,
            "elapsed_time": elapsed_time,
            "error": error,
            "m3u8_analysis": m3u8_analysis
        })
    
    def export_json(self, filename: str = None):
        """Exporta resultados para JSON"""
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Resultados exportados para: {filename}")
        logging.info(f"Resultados exportados para JSON: {filename}")
    
    def export_csv(self, filename: str = None):
        """Exporta resultados para CSV"""
        if not self.results:
            return
        
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Flatten nested dicts
        flattened_results = []
        for r in self.results:
            flat = {k: v for k, v in r.items() if k != 'm3u8_analysis'}
            if r.get('m3u8_analysis'):
                for k, v in r['m3u8_analysis'].items():
                    flat[f'm3u8_{k}'] = v
            flattened_results.append(flat)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_results:
                writer = csv.DictWriter(f, fieldnames=flattened_results[0].keys())
                writer.writeheader()
                writer.writerows(flattened_results)
        
        print(f"📊 Resultados exportados para: {filename}")
        logging.info(f"Resultados exportados para CSV: {filename}")
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        if not self.results:
            print("\n⚠️ Nenhum resultado para exibir")
            return
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        
        print(f"\n{'='*60}")
        print(f"📊 RESUMO DOS TESTES")
        print(f"{'='*60}")
        print(f"Total de testes: {total}")
        print(f"Sucessos: {successful} ({successful/total*100:.1f}%)")
        print(f"Falhas: {total - successful} ({(total-successful)/total*100:.1f}%)")
        
        # Métodos usados
        methods = {}
        for r in self.results:
            if r["success"]:
                methods[r["method"]] = methods.get(r["method"], 0) + 1
        
        if methods:
            print(f"\nMétodos bem-sucedidos:")
            for method, count in methods.items():
                print(f"  - {method}: {count}")
        
        # Tempo médio
        if total > 0:
            avg_time = sum(r["elapsed_time"] for r in self.results) / total
            print(f"\nTempo médio por teste: {avg_time:.2f}s")
            print(f"Tempo total: {sum(r['elapsed_time'] for r in self.results):.2f}s")
        
        # Erros comuns
        errors = [r["error"] for r in self.results if r.get("error")]
        if errors:
            print(f"\nErros encontrados: {len(errors)}")
            unique_errors = list(set(errors))[:3]
            for error in unique_errors:
                print(f"  - {error[:80]}...")
        
        print(f"{'='*60}\n")

# ============================================
# UTILITÁRIOS
# ============================================

@contextmanager
def measure_time(operation_name: str):
    """Context manager para medir tempo de operação"""
    start = time.time()
    logging.info(f"⏱️ Iniciando: {operation_name}")
    
    try:
        yield
    finally:
        elapsed = time.time() - start
        logging.info(f"⏱️ {operation_name} levou: {elapsed:.2f}s")

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator para retry com backoff exponencial"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logging.error(f"❌ Falhou após {max_retries} tentativas: {e}")
                        raise
                    
                    wait_time = backoff_factor ** attempt
                    logging.warning(f"⚠️ Tentativa {attempt + 1} falhou. Aguardando {wait_time:.1f}s...")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

# ============================================
# CLASSE PRINCIPAL
# ============================================

class MegaEmbedTester:
    """Testa extração de links do MegaEmbed ANTES de fazer build Kotlin"""
    
    USER_AGENT = "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    
    # CDNs conhecidos (descobertos via Burp Suite)
    CDN_DOMAINS = [
        "valenium.shop",
        "spo3.marvellaholdings.sbs",
        "sqtd.luminairemotion.online",
        "stzm.luminairemotion.online",
        "srcf.luminairemotion.online",
        "sipt.marvellaholdings.sbs",
        "stzm.marvellaholdings.sbs",
        "srcf.marvellaholdings.sbs",
        "sbi6.marvellaholdings.sbs",
        "s6p9.marvellaholdings.sbs",
        "sr81.virelodesignagency.cyou"
    ]
    
    # Shards conhecidos
    KNOWN_SHARDS = ["is3", "x6b", "x7c", "x8d", "x9e", "5w3", "xa1", "xb2"]
    
    def __init__(self, use_cache: bool = True, cache_ttl: int = 3600):
        self.cache = ResponseCache(ttl=cache_ttl) if use_cache else None
        self.use_cache = use_cache
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extrai videoId da URL"""
        logging.info(f"\n{'='*60}")
        logging.info(f"🔍 PASSO 1: Extraindo VideoId")
        logging.info(f"{'='*60}")
        logging.info(f"URL: {url}")
        
        patterns = [
            (r"#([a-zA-Z0-9]+)$", "Hash (#)"),
            (r"/embed/([a-zA-Z0-9]+)", "Embed path"),
            (r"/([a-zA-Z0-9]+)/?$", "Direct path"),
            (r"id=([a-zA-Z0-9]+)", "Query param id"),
            (r"v=([a-zA-Z0-9]+)", "Query param v")
        ]
        
        for pattern, name in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logging.info(f"✅ Padrão '{name}' funcionou!")
                logging.info(f"✅ VideoId extraído: {video_id}")
                return video_id
            else:
                logging.debug(f"❌ Padrão '{name}' não funcionou")
        
        logging.error("❌ Nenhum padrão funcionou!")
        return None
    
    @retry_with_backoff(max_retries=3)
    def _make_request(self, url: str, headers: dict) -> requests.Response:
        """Faz requisição HTTP com retry automático"""
        return requests.get(url, headers=headers, timeout=10)
    
    def _decode_hex_response(self, hex_string: str) -> Optional[Dict[str, Any]]:
        """
        Decodifica resposta hexadecimal da API MegaEmbed
        Retorna: dict com informações decodificadas ou None
        """
        try:
            logging.info(f"\n🔓 Tentando decodificar resposta hexadecimal...")
            logging.debug(f"Hex string (primeiros 100 chars): {hex_string[:100]}")
            
            # Converter hex para bytes
            decoded_bytes = bytes.fromhex(hex_string)
            
            # Tentar decodificar como UTF-8
            try:
                decoded_text = decoded_bytes.decode('utf-8')
                logging.info(f"✅ Decodificado como UTF-8")
                logging.debug(f"Texto decodificado: {decoded_text[:200]}")
                
                # Tentar parsear como JSON
                try:
                    json_data = json.loads(decoded_text)
                    logging.info(f"✅ JSON válido encontrado!")
                    logging.debug(json.dumps(json_data, indent=2))
                    return json_data
                except json.JSONDecodeError:
                    logging.debug("Não é JSON, procurando URLs...")
                    
                    # Procurar URLs no texto
                    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                    urls = re.findall(url_pattern, decoded_text)
                    
                    if urls:
                        logging.info(f"✅ {len(urls)} URL(s) encontrada(s) no texto!")
                        for i, url in enumerate(urls, 1):
                            logging.info(f"  [{i}] {url}")
                        
                        # Retornar primeira URL que parece ser M3U8
                        for url in urls:
                            if any(ext in url.lower() for ext in ['.m3u8', '.txt', 'master', 'playlist']):
                                return {"url": url, "source": "decoded_hex"}
                        
                        # Se não encontrou M3U8, retornar primeira URL
                        return {"url": urls[0], "source": "decoded_hex"}
                    
            except UnicodeDecodeError:
                logging.debug("Não é UTF-8 válido")
            
            # Procurar padrões de host/shard diretamente nos bytes
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            
            # Procurar padrões de CDN (domínios completos)
            # Padrões: spo3.marvellaholdings.sbs, valenium.shop, etc
            cdn_patterns = [
                r'([a-z0-9]+\.[a-z]+\.[a-z]+\.[a-z]+)',  # 4 níveis: spo3.marvellaholdings.sbs
                r'([a-z0-9]+\.[a-z]+\.[a-z]+)',          # 3 níveis: valenium.shop
            ]
            
            cdns = []
            for pattern in cdn_patterns:
                matches = re.findall(pattern, decoded_str)
                cdns.extend(matches)
            
            # Filtrar CDNs conhecidos ou que parecem válidos
            valid_cdns = []
            for cdn in cdns:
                # Verificar se tem extensão válida
                if any(cdn.endswith(ext) for ext in ['.shop', '.sbs', '.online', '.cyou', '.xyz', '.com']):
                    valid_cdns.append(cdn)
            
            # Procurar shards (x6b, is3, p3w, etc)
            shard_patterns = [
                r'\b([a-z][0-9][a-z0-9])\b',  # Padrão: letra + número + alfanumérico
                r'\b([a-z]{2}[0-9])\b',        # Padrão: 2 letras + número
            ]
            
            shards = []
            for pattern in shard_patterns:
                matches = re.findall(pattern, decoded_str)
                shards.extend(matches)
            
            # Remover duplicatas
            valid_cdns = list(set(valid_cdns))
            shards = list(set(shards))
            
            if valid_cdns or shards:
                logging.info(f"✅ Padrões encontrados:")
                if valid_cdns:
                    logging.info(f"  CDNs: {valid_cdns}")
                if shards:
                    logging.info(f"  Shards: {shards}")
                
                return {
                    "cdns": valid_cdns,
                    "shards": shards,
                    "source": "pattern_match"
                }
            
        except Exception as e:
            logging.debug(f"Erro ao decodificar hex: {e}")
        
        return None
    
    def test_api_call(self, video_id: str) -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Testa chamada à API do MegaEmbed
        Retorna: (playlist_url, method_used, api_metadata)
        """
        logging.info(f"\n{'='*60}")
        logging.info(f"🌐 PASSO 2: Testando API do MegaEmbed")
        logging.info(f"{'='*60}")
        logging.info(f"VideoId: {video_id}")
        
        headers = {
            "User-Agent": self.USER_AGENT,
            "Referer": "https://megaembed.link/",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://megaembed.link"
        }
        
        api_metadata = {}
        
        # Método 1: API v1
        api_url = f"https://megaembed.link/api/v1/video?id={video_id}"
        logging.info(f"\n📡 Método 1: API v1")
        logging.info(f"URL: {api_url}")
        
        # Verificar cache
        if self.use_cache:
            cached = self.cache.get(api_url)
            if cached:
                data = cached
                logging.info("✅ Usando resposta do cache")
                
                # Processar dados do cache
                result = self._process_api_response(data, headers, api_metadata)
                if result:
                    return (*result, api_metadata)
        
        try:
            logging.info("Fazendo requisição...")
            response = self._make_request(api_url, headers)
            
            logging.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                logging.info("✅ Requisição bem-sucedida!")
                
                # Tentar como JSON primeiro
                try:
                    data = response.json()
                    logging.info(f"\n📄 JSON Response:")
                    logging.debug(json.dumps(data, indent=2))
                    
                    # Salvar no cache
                    if self.use_cache:
                        self.cache.set(api_url, data)
                    
                    # Processar resposta
                    result = self._process_api_response(data, headers, api_metadata)
                    if result:
                        return (*result, api_metadata)
                    
                except json.JSONDecodeError:
                    # Não é JSON, pode ser hex
                    logging.info("⚠️ Resposta não é JSON, tentando decodificar como HEX...")
                    
                    hex_response = response.text.strip()
                    decoded_data = self._decode_hex_response(hex_response)
                    
                    if decoded_data:
                        api_metadata['decoded_from_hex'] = True
                        api_metadata['hex_data'] = decoded_data
                        
                        # Se encontrou URL direta
                        if "url" in decoded_data:
                            logging.info(f"✅ URL ENCONTRADA NA RESPOSTA DECODIFICADA!")
                            return (decoded_data["url"], "api_decoded", api_metadata)
                        
                        # Se encontrou padrões de CDN/shard
                        if "cdns" in decoded_data or "shards" in decoded_data:
                            logging.info(f"✅ Padrões de CDN/Shard encontrados!")
                            # Retornar para usar na construção
                            return (None, None, api_metadata)
                    else:
                        logging.debug(f"Conteúdo hex: {hex_response[:500]}")
            else:
                logging.error(f"❌ Requisição falhou!")
                logging.debug(f"Resposta: {response.text[:500]}")
        
        except Exception as e:
            logging.error(f"❌ Erro na requisição: {e}")
        
        # Método 2: APIs alternativas
        logging.info(f"\n📡 Método 2: APIs Alternativas")
        alternative_apis = [
            f"https://megaembed.link/api/video/{video_id}",
            f"https://megaembed.link/embed/api?id={video_id}",
            f"https://megaembed.xyz/api/v1/video?id={video_id}"
        ]
        
        for api_url in alternative_apis:
            logging.info(f"\n🔄 Tentando: {api_url}")
            
            try:
                response = self._make_request(api_url, headers)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logging.info(f"✅ Resposta JSON recebida")
                        
                        for field in ["url", "file", "source", "playlist", "stream", "video"]:
                            if field in data and isinstance(data[field], str) and data[field].startswith("http"):
                                logging.info(f"✅ LINK ENCONTRADO VIA API ALTERNATIVA!")
                                logging.info(f"URL: {data[field]}")
                                return (data[field], "api_alternative", api_metadata)
                    except:
                        pass
                else:
                    logging.debug(f"❌ Status {response.status_code}")
            
            except Exception as e:
                logging.debug(f"❌ Erro: {e}")
        
        return (None, None, api_metadata)
    
    def _process_api_response(self, data: dict, headers: dict, api_metadata: dict) -> Optional[Tuple[str, str]]:
        """Processa resposta da API e extrai URL do vídeo"""
        # Procurar campos de vídeo
        possible_fields = ["url", "file", "source", "playlist", "stream", "video"]
        logging.info(f"\n🔍 Procurando campos de vídeo...")
        
        for field in possible_fields:
            if field in data:
                value = data[field]
                logging.debug(f"  ✓ Campo '{field}': {value}")
                
                if isinstance(value, str) and value.startswith("http"):
                    logging.info(f"\n✅ LINK DE VÍDEO ENCONTRADO!")
                    logging.info(f"Campo: {field}")
                    logging.info(f"URL: {value}")
                    
                    # Extrair CDN e shard da URL
                    url_match = re.search(r'https?://([^/]+)/v4/([^/]+)/', value)
                    if url_match:
                        api_metadata['cdn_from_url'] = url_match.group(1)
                        api_metadata['shard_from_url'] = url_match.group(2)
                    
                    return (value, "api")
        
        # Verificar se tem token
        if "token" in data:
            logging.info(f"\n🔑 Token encontrado: {data['token']}")
            logging.info("Fazendo segunda chamada com token...")
            
            player_url = f"https://megaembed.link/api/v1/player?t={data['token']}"
            logging.info(f"URL Player API: {player_url}")
            
            try:
                response2 = self._make_request(player_url, headers)
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    logging.info(f"\n📄 Player API Response:")
                    logging.debug(json.dumps(data2, indent=2))
                    
                    for field in possible_fields:
                        if field in data2:
                            value = data2[field]
                            if isinstance(value, str) and value.startswith("http"):
                                logging.info(f"\n✅ LINK VIA TOKEN ENCONTRADO!")
                                logging.info(f"Campo: {field}")
                                logging.info(f"URL: {value}")
                                
                                # Extrair CDN e shard da URL
                                url_match = re.search(r'https?://([^/]+)/v4/([^/]+)/', value)
                                if url_match:
                                    api_metadata['cdn_from_url'] = url_match.group(1)
                                    api_metadata['shard_from_url'] = url_match.group(2)
                                
                                return (value, "api_token")
                else:
                    logging.error(f"❌ Player API falhou: {response2.status_code}")
            except Exception as e:
                logging.error(f"❌ Erro na chamada com token: {e}")
        
        return None
    
    def test_constructed_url(self, video_id: str, api_metadata: dict = None, max_attempts: int = 10) -> Optional[str]:
        """
        Testa construção de URL baseada no padrão
        Prioriza CDN/shard descobertos da API antes de usar lista hardcoded
        """
        logging.info(f"\n{'='*60}")
        logging.info(f"🔨 PASSO 3: Testando Construção de URL")
        logging.info(f"{'='*60}")
        
        timestamp = int(time.time())
        logging.info(f"Timestamp atual: {timestamp}")
        logging.info(f"VideoId: {video_id}")
        
        if api_metadata is None:
            api_metadata = {}
        
        # Priorizar CDN/shard descobertos da API
        priority_cdns = []
        priority_shards = []
        
        # Extrair de URL se disponível
        if 'cdn_from_url' in api_metadata:
            priority_cdns.append(api_metadata['cdn_from_url'])
            logging.info(f"✅ CDN descoberto da API: {api_metadata['cdn_from_url']}")
        
        if 'shard_from_url' in api_metadata:
            priority_shards.append(api_metadata['shard_from_url'])
            logging.info(f"✅ Shard descoberto da API: {api_metadata['shard_from_url']}")
        
        # Extrair de dados decodificados
        if 'hex_data' in api_metadata:
            hex_data = api_metadata['hex_data']
            if 'cdns' in hex_data:
                priority_cdns.extend(hex_data['cdns'])
                logging.info(f"✅ CDNs decodificados: {hex_data['cdns']}")
            if 'shards' in hex_data:
                priority_shards.extend(hex_data['shards'])
                logging.info(f"✅ Shards decodificados: {hex_data['shards']}")
        
        # Remover duplicatas mantendo ordem
        priority_cdns = list(dict.fromkeys(priority_cdns))
        priority_shards = list(dict.fromkeys(priority_shards))
        
        # Combinar com lista conhecida (fallback)
        all_cdns = priority_cdns + [cdn for cdn in self.CDN_DOMAINS if cdn not in priority_cdns]
        all_shards = priority_shards + [shard for shard in self.KNOWN_SHARDS if shard not in priority_shards]
        
        if priority_cdns or priority_shards:
            logging.info(f"\n🎯 MODO INTELIGENTE: Usando dados da API")
            logging.info(f"   CDNs prioritários: {priority_cdns if priority_cdns else 'Nenhum'}")
            logging.info(f"   Shards prioritários: {priority_shards if priority_shards else 'Nenhum'}")
            logging.info(f"   Fallback: Lista conhecida ({len(self.CDN_DOMAINS)} CDNs, {len(self.KNOWN_SHARDS)} shards)")
        else:
            logging.info(f"\n⚠️ MODO FALLBACK: Usando lista hardcoded")
            logging.info(f"   Testando até {max_attempts} combinações...")
        
        logging.info("")
        
        attempts = 0
        
        for cdn in all_cdns:
            for shard in all_shards:
                if attempts >= max_attempts:
                    break
                
                attempts += 1
                url = f"https://{cdn}/v4/{shard}/{video_id}/cf-master.{timestamp}.txt"
                
                # Indicar se é prioritário
                is_priority = cdn in priority_cdns or shard in priority_shards
                priority_marker = "🎯" if is_priority else "🧪"
                
                logging.info(f"{priority_marker} [{attempts}/{max_attempts}] Testando: {cdn}/{shard}")
                
                try:
                    response = requests.get(url, headers={
                        "User-Agent": self.USER_AGENT,
                        "Referer": "https://megaembed.link/"
                    }, timeout=5)
                    
                    if response.status_code == 200:
                        content = response.text[:200]
                        
                        if "#EXTM3U" in response.text:
                            logging.info(f"✅ FUNCIONOU! É um M3U8 válido!")
                            logging.info(f"URL: {url}")
                            logging.info(f"Método: {'API-Guided' if is_priority else 'Brute-Force'}")
                            logging.info(f"\nPrimeiras linhas do M3U8:")
                            logging.info(content)
                            return url
                        else:
                            logging.debug(f"⚠️ Status 200 mas não é M3U8")
                    else:
                        logging.debug(f"❌ Status {response.status_code}")
                
                except Exception as e:
                    logging.debug(f"❌ Erro: {str(e)[:50]}")
            
            if attempts >= max_attempts:
                break
        
        logging.warning(f"\n❌ Nenhuma URL construída funcionou ({attempts} tentativas)")
        return None
    
    @staticmethod
    def analyze_m3u8(url: str) -> Dict[str, Any]:
        """Analisa M3U8 e extrai informações de qualidade"""
        logging.info(f"\n{'='*60}")
        logging.info(f"📊 ANÁLISE DO M3U8")
        logging.info(f"{'='*60}")
        logging.info(f"URL: {url}")
        
        try:
            response = requests.get(url, headers={
                "User-Agent": MegaEmbedTester.USER_AGENT,
                "Referer": "https://megaembed.link/"
            }, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"Status {response.status_code}"}
            
            content = response.text
            
            # Extrair resoluções
            resolutions = re.findall(r'RESOLUTION=(\d+x\d+)', content)
            bandwidths = re.findall(r'BANDWIDTH=(\d+)', content)
            
            # Contar segmentos
            segments = len(re.findall(r'\.ts|\.m4s', content))
            
            # Detectar tipo
            is_master = "EXT-X-STREAM-INF" in content
            is_valid = "#EXTM3U" in content
            
            analysis = {
                "is_valid": is_valid,
                "is_master_playlist": is_master,
                "resolutions": list(set(resolutions)),
                "num_resolutions": len(set(resolutions)),
                "bandwidths_kbps": [int(b)//1000 for b in bandwidths],
                "segments": segments,
                "size_bytes": len(content),
                "has_audio": "TYPE=AUDIO" in content,
                "has_subtitles": "TYPE=SUBTITLES" in content
            }
            
            logging.info(f"\n📊 Resultados da Análise:")
            for key, value in analysis.items():
                logging.info(f"  {key}: {value}")
            
            return analysis
        
        except Exception as e:
            logging.error(f"❌ Erro na análise: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def validate_m3u8(url: str) -> bool:
        """Valida se uma URL é um M3U8 válido"""
        logging.info(f"\n{'='*60}")
        logging.info(f"✅ VALIDAÇÃO FINAL")
        logging.info(f"{'='*60}")
        logging.info(f"URL: {url}")
        
        try:
            response = requests.get(url, headers={
                "User-Agent": MegaEmbedTester.USER_AGENT,
                "Referer": "https://megaembed.link/"
            }, timeout=10)
            
            logging.info(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                is_m3u8 = "#EXTM3U" in content
                has_resolution = "RESOLUTION=" in content
                
                logging.info(f"É M3U8: {is_m3u8}")
                logging.info(f"Tem RESOLUTION: {has_resolution}")
                
                if is_m3u8:
                    logging.info(f"\n✅ M3U8 VÁLIDO!")
                    logging.info(f"\nConteúdo (primeiras 500 chars):")
                    logging.info(content[:500])
                    return True
                else:
                    logging.error(f"❌ Não é um M3U8 válido")
                    return False
            else:
                logging.error(f"❌ Status {response.status_code}")
                return False
        
        except Exception as e:
            logging.error(f"❌ Erro na validação: {e}")
            return False

# ============================================
# FUNÇÕES DE TESTE
# ============================================

def test_complete_flow(url: str, tester: MegaEmbedTester, 
                       max_construct_attempts: int = 10) -> Dict[str, Any]:
    """
    Testa fluxo completo de extração
    Retorna dicionário com resultados
    """
    print("\n" + "="*60)
    print("🚀 TESTE COMPLETO - MegaEmbed Link Fetcher")
    print("="*60)
    print(f"URL de Entrada: {url}")
    print("="*60)
    
    start_time = time.time()
    result = {
        "url": url,
        "video_id": None,
        "method": None,
        "success": False,
        "playlist_url": None,
        "elapsed_time": 0,
        "error": None,
        "m3u8_analysis": None,
        "api_metadata": None
    }
    
    try:
        # Passo 1: Extrair videoId
        with measure_time("Extração de VideoId"):
            video_id = MegaEmbedTester.extract_video_id(url)
        
        if not video_id:
            result["error"] = "Não conseguiu extrair videoId"
            print("\n" + "="*60)
            print("❌ FALHOU: Não conseguiu extrair videoId")
            print("="*60)
            return result
        
        result["video_id"] = video_id
        
        # Passo 2: Testar API
        with measure_time("Teste de API"):
            playlist_url, method, api_metadata = tester.test_api_call(video_id)
        
        result["api_metadata"] = api_metadata
        
        if playlist_url:
            result["playlist_url"] = playlist_url
            result["method"] = method
            result["success"] = True
            
            print("\n" + "="*60)
            print(f"✅ SUCESSO VIA {method.upper()}!")
            print(f"URL Final: {playlist_url}")
            print("="*60)
            
            # Analisar M3U8
            with measure_time("Análise do M3U8"):
                analysis = MegaEmbedTester.analyze_m3u8(playlist_url)
                result["m3u8_analysis"] = analysis
            
            # Validar M3U8
            MegaEmbedTester.validate_m3u8(playlist_url)
            
            return result
        
        # Passo 3: Tentar construção (agora com metadados da API!)
        with measure_time("Construção de URL"):
            playlist_url = tester.test_constructed_url(video_id, api_metadata, max_construct_attempts)
        
        if playlist_url:
            result["playlist_url"] = playlist_url
            result["method"] = "constructed"
            result["success"] = True
            
            print("\n" + "="*60)
            print("✅ SUCESSO VIA CONSTRUÇÃO!")
            print(f"URL Final: {playlist_url}")
            print("="*60)
            
            # Analisar M3U8
            with measure_time("Análise do M3U8"):
                analysis = MegaEmbedTester.analyze_m3u8(playlist_url)
                result["m3u8_analysis"] = analysis
            
            # Validar M3U8
            MegaEmbedTester.validate_m3u8(playlist_url)
            
            return result
        else:
            result["error"] = "Nenhum método funcionou"
            print("\n" + "="*60)
            print("❌ FALHOU: Nenhum método funcionou")
            print("="*60)
            return result
    
    except Exception as e:
        result["error"] = str(e)
        logging.error(f"❌ Erro no teste: {e}")
        return result
    
    finally:
        result["elapsed_time"] = time.time() - start_time

def test_batch(urls_file: str, tester: MegaEmbedTester, 
               results: TestResults, max_construct_attempts: int = 10):
    """Testa múltiplas URLs de um arquivo"""
    print(f"\n{'='*60}")
    print(f"📦 MODO BATCH - Testando múltiplas URLs")
    print(f"{'='*60}")
    print(f"Arquivo: {urls_file}\n")
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"Total de URLs para testar: {len(urls)}\n")
        
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"Teste {i}/{len(urls)}")
            print(f"{'='*60}")
            
            result = test_complete_flow(url, tester, max_construct_attempts)
            
            results.add_result(
                url=result["url"],
                video_id=result["video_id"],
                method=result["method"],
                success=result["success"],
                playlist_url=result["playlist_url"],
                elapsed_time=result["elapsed_time"],
                error=result["error"],
                m3u8_analysis=result["m3u8_analysis"]
            )
            
            # Pequena pausa entre testes
            if i < len(urls):
                time.sleep(1)
        
        print(f"\n{'='*60}")
        print(f"✅ Batch completo!")
        print(f"{'='*60}")
    
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {urls_file}")
        logging.error(f"Arquivo não encontrado: {urls_file}")
    except Exception as e:
        print(f"❌ Erro no batch: {e}")
        logging.error(f"Erro no batch: {e}")

def interactive_mode(tester: MegaEmbedTester, results: TestResults):
    """Modo interativo para testes manuais"""
    print("="*60)
    print("🎮 MODO INTERATIVO")
    print("="*60)
    print("Comandos:")
    print("  - Digite uma URL do MegaEmbed")
    print("  - Digite um videoId direto")
    print("  - 'clear' - Limpa o cache")
    print("  - 'summary' - Mostra resumo dos testes")
    print("  - 'export' - Exporta resultados")
    print("  - 'quit' ou 'exit' - Sair")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Saindo...")
                break
            
            if user_input.lower() == 'clear':
                if tester.use_cache:
                    tester.cache.clear()
                    print("✅ Cache limpo")
                else:
                    print("⚠️ Cache desabilitado")
                continue
            
            if user_input.lower() == 'summary':
                results.print_summary()
                continue
            
            if user_input.lower() == 'export':
                results.export_json()
                results.export_csv()
                continue
            
            # Detectar se é URL ou videoId
            if user_input.startswith("http"):
                result = test_complete_flow(user_input, tester)
                results.add_result(
                    url=result["url"],
                    video_id=result["video_id"],
                    method=result["method"],
                    success=result["success"],
                    playlist_url=result["playlist_url"],
                    elapsed_time=result["elapsed_time"],
                    error=result["error"],
                    m3u8_analysis=result["m3u8_analysis"]
                )
            else:
                # Assumir que é videoId
                print(f"\n🔍 Testando com videoId: {user_input}")
                
                start_time = time.time()
                playlist_url, method, api_metadata = tester.test_api_call(user_input)
                
                if not playlist_url:
                    playlist_url = tester.test_constructed_url(user_input, api_metadata)
                    method = "constructed" if playlist_url else None
                
                elapsed = time.time() - start_time
                
                if playlist_url:
                    analysis = MegaEmbedTester.analyze_m3u8(playlist_url)
                    MegaEmbedTester.validate_m3u8(playlist_url)
                    
                    results.add_result(
                        url=f"videoId:{user_input}",
                        video_id=user_input,
                        method=method,
                        success=True,
                        playlist_url=playlist_url,
                        elapsed_time=elapsed,
                        m3u8_analysis=analysis
                    )
                else:
                    results.add_result(
                        url=f"videoId:{user_input}",
                        video_id=user_input,
                        method=None,
                        success=False,
                        elapsed_time=elapsed,
                        error="Nenhum método funcionou"
                    )
            
            print("\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            logging.error(f"Erro no modo interativo: {e}")

# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="Testa extração de links do MegaEmbed (Protótipo Python para TCC)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python test_megaembed.py
  python test_megaembed.py --url "https://megaembed.link/#3wnuij"
  python test_megaembed.py --video-id 3wnuij
  python test_megaembed.py --interactive
  python test_megaembed.py --batch urls.txt
  python test_megaembed.py --verbose --no-cache
        """
    )
    
    parser.add_argument("--url", type=str, help="URL do MegaEmbed para testar")
    parser.add_argument("--video-id", type=str, help="VideoId direto (pula extração)")
    parser.add_argument("--batch", type=str, help="Arquivo com múltiplas URLs (uma por linha)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interativo")
    parser.add_argument("--max-attempts", type=int, default=10, help="Máximo de tentativas de construção (padrão: 10)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Modo verbose (mais detalhes)")
    parser.add_argument("--no-cache", action="store_true", help="Desabilita cache de respostas")
    parser.add_argument("--cache-ttl", type=int, default=3600, help="Tempo de vida do cache em segundos (padrão: 3600)")
    parser.add_argument("--log-file", type=str, help="Arquivo de log customizado")
    parser.add_argument("--export-json", type=str, help="Exporta resultados para JSON")
    parser.add_argument("--export-csv", type=str, help="Exporta resultados para CSV")
    
    args = parser.parse_args()
    
    # Configurar logging
    log_file = setup_logging(args.log_file, args.verbose)
    print(f"📝 Logs salvos em: {log_file}\n")
    
    # Criar instância do tester
    tester = MegaEmbedTester(
        use_cache=not args.no_cache,
        cache_ttl=args.cache_ttl
    )
    
    # Criar armazenamento de resultados
    results = TestResults()
    
    # Modo interativo
    if args.interactive:
        interactive_mode(tester, results)
        results.print_summary()
        
        if args.export_json:
            results.export_json(args.export_json)
        if args.export_csv:
            results.export_csv(args.export_csv)
        
        return
    
    # Modo batch
    if args.batch:
        test_batch(args.batch, tester, results, args.max_attempts)
        results.print_summary()
        
        if args.export_json:
            results.export_json(args.export_json)
        else:
            results.export_json()
        
        if args.export_csv:
            results.export_csv(args.export_csv)
        else:
            results.export_csv()
        
        return
    
    # Teste com videoId direto
    if args.video_id:
        print(f"Testando com VideoId direto: {args.video_id}\n")
        
        start_time = time.time()
        playlist_url, method, api_metadata = tester.test_api_call(args.video_id)
        
        if not playlist_url:
            playlist_url = tester.test_constructed_url(args.video_id, api_metadata, args.max_attempts)
            method = "constructed" if playlist_url else None
        
        elapsed = time.time() - start_time
        
        if playlist_url:
            analysis = MegaEmbedTester.analyze_m3u8(playlist_url)
            MegaEmbedTester.validate_m3u8(playlist_url)
            
            results.add_result(
                url=f"videoId:{args.video_id}",
                video_id=args.video_id,
                method=method,
                success=True,
                playlist_url=playlist_url,
                elapsed_time=elapsed,
                m3u8_analysis=analysis
            )
        else:
            results.add_result(
                url=f"videoId:{args.video_id}",
                video_id=args.video_id,
                method=None,
                success=False,
                elapsed_time=elapsed,
                error="Nenhum método funcionou"
            )
        
        results.print_summary()
        return
    
    # Teste com URL
    if args.url:
        result = test_complete_flow(args.url, tester, args.max_attempts)
        
        results.add_result(
            url=result["url"],
            video_id=result["video_id"],
            method=result["method"],
            success=result["success"],
            playlist_url=result["playlist_url"],
            elapsed_time=result["elapsed_time"],
            error=result["error"],
            m3u8_analysis=result["m3u8_analysis"]
        )
        
        results.print_summary()
        
        if args.export_json:
            results.export_json(args.export_json)
        if args.export_csv:
            results.export_csv(args.export_csv)
        
        return
    
    # URLs de teste padrão
    test_urls = [
        "https://megaembed.link/#3wnuij",
        "https://megaembed.link/embed/3wnuij",
    ]
    
    print("Nenhuma URL fornecida. Usando URLs de teste padrão:\n")
    
    for test_url in test_urls:
        result = test_complete_flow(test_url, tester, args.max_attempts)
        
        results.add_result(
            url=result["url"],
            video_id=result["video_id"],
            method=result["method"],
            success=result["success"],
            playlist_url=result["playlist_url"],
            elapsed_time=result["elapsed_time"],
            error=result["error"],
            m3u8_analysis=result["m3u8_analysis"]
        )
        
        if result["success"]:
            print(f"\n✅ URL de teste funcionou: {test_url}")
            print(f"✅ Resultado: {result['playlist_url']}")
            break
        
        print("\n")
    
    results.print_summary()
    
    # Exportar resultados automaticamente
    results.export_json()
    results.export_csv()

if __name__ == "__main__":
    main()