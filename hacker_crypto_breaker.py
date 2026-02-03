#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAYEREMBEDAPI - CRYPTO BREAKER & JS REVERSE ENGINEER           ║
║                    Advanced Cryptanalysis & Deobfuscation                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Técnicas de criptoanálise:
1. Análise de entropia e padrões
2. Ataques de força bruta em chaves derivadas
3. Análise de modo de operação (ECB, CBC, CTR, GCM)
4. Padding oracle detection
5. Known-plaintext attacks
6. Deobfuscação de JavaScript
7. String decryption
"""

import base64
import binascii
import hashlib
import json
import re
import struct
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any
from pathlib import Path
from math import log2

# Tentar importar bibliotecas criptográficas
try:
    from Crypto.Cipher import AES, DES, DES3, Blowfish
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Util.strxor import strxor
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("[!] pycryptodome não instalado. Instale com: pip install pycryptodome")


@dataclass
class CryptoAnalysis:
    """Resultado da análise criptográfica"""
    algorithm: str
    confidence: float  # 0-1
    key: Optional[bytes]
    decrypted_sample: Optional[bytes]
    full_decrypted: Optional[bytes]
    method: str


@dataclass
class JSStructure:
    """Estrutura de código JavaScript analisado"""
    functions: List[Dict]
    variables: Dict[str, Any]
    strings: List[str]
    obfuscation_type: str
    encryption_calls: List[Dict]


class EntropyAnalyzer:
    """Analisador de entropia para detectar criptografia"""
    
    @staticmethod
    def calculate(data: bytes) -> float:
        """Calcula entropia de Shannon"""
        if not data:
            return 0.0
        
        entropy = 0.0
        length = len(data)
        
        for byte_val in range(256):
            count = data.count(byte_val)
            if count > 0:
                freq = count / length
                entropy -= freq * log2(freq)
        
        return entropy
    
    @staticmethod
    def analyze_blocks(data: bytes, block_size: int = 16) -> Dict:
        """Analisa entropia por blocos"""
        blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]
        entropies = [EntropyAnalyzer.calculate(b) for b in blocks if len(b) == block_size]
        
        return {
            'block_entropies': entropies,
            'avg_entropy': sum(entropies) / len(entropies) if entropies else 0,
            'max_entropy': max(entropies) if entropies else 0,
            'min_entropy': min(entropies) if entropies else 0,
            'uniform': all(abs(e - entropies[0]) < 0.1 for e in entropies) if entropies else False
        }
    
    @staticmethod
    def detect_encryption(data: bytes) -> Dict:
        """Detecta se os dados parecem criptografados"""
        entropy = EntropyAnalyzer.calculate(data)
        block_analysis = EntropyAnalyzer.analyze_blocks(data)
        
        # Entropia alta (>7.5) sugere criptografia ou compressão
        is_high_entropy = entropy > 7.5
        
        # Blocos uniformes sugerem ECB
        likely_ecb = block_analysis['uniform'] and len(set(block_analysis['block_entropies'])) < 3
        
        return {
            'entropy': entropy,
            'is_likely_encrypted': is_high_entropy,
            'likely_mode': 'ECB' if likely_ecb else 'CBC/CTR/GCM',
            'block_analysis': block_analysis
        }


class KeyDeriver:
    """Deriva chaves de múltiplas fontes"""
    
    @staticmethod
    def derive_all_keys(video_data: Dict) -> List[Tuple[str, bytes]]:
        """Gera todas as chaves possíveis baseadas nos dados"""
        keys = []
        
        slug = video_data.get('slug', '')
        md5_id = str(video_data.get('md5_id', ''))
        user_id = str(video_data.get('user_id', ''))
        
        # Combinações diretas
        combinations = [
            f"{user_id}:{md5_id}:{slug}",
            f"{md5_id}:{user_id}:{slug}",
            f"{slug}:{md5_id}:{user_id}",
            f"{user_id}{md5_id}{slug}",
            f"{md5_id}{user_id}{slug}",
            slug,
            md5_id,
            user_id,
            f"{slug}{md5_id}",
            f"{md5_id}{slug}",
        ]
        
        for combo in combinations:
            # MD5
            keys.append((f"md5:{combo}", hashlib.md5(combo.encode()).digest()))
            # SHA1
            keys.append((f"sha1:{combo}", hashlib.sha1(combo.encode()).digest()[:16]))
            # SHA256
            keys.append((f"sha256:{combo}", hashlib.sha256(combo.encode()).digest()[:16]))
            # Raw
            keys.append((f"raw:{combo}", combo.encode()[:16].ljust(16, b'\x00')))
        
        return keys


class AESBreaker:
    """Tenta quebrar criptografia AES"""
    
    MODES = ['ECB', 'CBC', 'CTR', 'CFB', 'OFB']
    
    def __init__(self):
        self.results: List[CryptoAnalysis] = []
    
    def attempt_decrypt(self, ciphertext: bytes, keys: List[Tuple[str, bytes]], 
                       iv: bytes = None) -> List[CryptoAnalysis]:
        """Tenta descriptografar com múltiplas chaves e modos"""
        
        if not CRYPTO_AVAILABLE:
            return []
        
        for key_name, key in keys:
            for mode_name in self.MODES:
                try:
                    result = self._try_mode(ciphertext, key, mode_name, iv)
                    if result:
                        self.results.append(result)
                except Exception as e:
                    pass
        
        # Ordenar por confiança
        self.results.sort(key=lambda x: x.confidence, reverse=True)
        return self.results
    
    def _try_mode(self, ciphertext: bytes, key: bytes, mode: str, 
                  iv: bytes = None) -> Optional[CryptoAnalysis]:
        """Tenta um modo específico"""
        
        # Ajustar tamanho da chave
        if len(key) not in [16, 24, 32]:
            key = key[:16].ljust(16, b'\x00')
        
        # IV padrão se não fornecido
        if iv is None:
            iv = b'\x00' * 16
        
        try:
            if mode == 'ECB':
                cipher = AES.new(key, AES.MODE_ECB)
            elif mode == 'CBC':
                cipher = AES.new(key, AES.MODE_CBC, iv)
            elif mode == 'CTR':
                cipher = AES.new(key, AES.MODE_CTR, nonce=b'')
            elif mode == 'CFB':
                cipher = AES.new(key, AES.MODE_CFB, iv)
            elif mode == 'OFB':
                cipher = AES.new(key, AES.MODE_OFB, iv)
            else:
                return None
            
            decrypted = cipher.decrypt(ciphertext)
            
            # Verificar se é texto legível
            confidence = self._calculate_confidence(decrypted)
            
            if confidence > 0.3:  # Threshold mínimo
                return CryptoAnalysis(
                    algorithm=f"AES-{len(key)*8}-{mode}",
                    confidence=confidence,
                    key=key,
                    decrypted_sample=decrypted[:100],
                    full_decrypted=decrypted if confidence > 0.7 else None,
                    method=f"key={key.hex()[:20]}..."
                )
        except:
            pass
        
        return None
    
    def _calculate_confidence(self, data: bytes) -> float:
        """Calcula confiança baseada em características do texto"""
        if not data:
            return 0.0
        
        # Verificar se é JSON
        try:
            json.loads(data.decode('utf-8'))
            return 1.0
        except:
            pass
        
        # Verificar se é URL
        try:
            text = data.decode('utf-8')
            if text.startswith('http') or '.m3u8' in text or '.mp4' in text:
                return 0.95
        except:
            pass
        
        # Verificar caracteres imprimíveis
        printable = sum(1 for b in data if 32 <= b < 127 or b in [9, 10, 13])
        ratio = printable / len(data)
        
        # Penalizar entropia muito alta (dados ainda criptografados)
        entropy = EntropyAnalyzer.calculate(data)
        
        if ratio > 0.9 and entropy < 6.0:
            return ratio * 0.8
        elif ratio > 0.7:
            return ratio * 0.5
        else:
            return ratio * 0.2


class JSDeobfuscator:
    """Deobfuscador de JavaScript"""
    
    def __init__(self, js_code: str):
        self.code = js_code
        self.structure = JSStructure(
            functions=[],
            variables={},
            strings=[],
            obfuscation_type='unknown',
            encryption_calls=[]
        )
    
    def analyze(self) -> JSStructure:
        """Analisa o código JavaScript"""
        
        # Detectar tipo de obfuscação
        self._detect_obfuscation()
        
        # Extrair strings
        self._extract_strings()
        
        # Extrair funções
        self._extract_functions()
        
        # Procurar por chamadas de criptografia
        self._find_crypto_calls()
        
        return self.structure
    
    def _detect_obfuscation(self):
        """Detecta o tipo de obfuscação"""
        
        patterns = {
            'obfuscator.io': r'var _0x[a-f0-9]+',
            'javascript-obfuscator': r'_0x[\w$]+',
            'packer': r'eval\(function\(p,a,c,k,e,',
            'aaencode': r'ﾟωﾟﾉ',
            'jjencode': r"\$=~\[\]",
        }
        
        for name, pattern in patterns.items():
            if re.search(pattern, self.code):
                self.structure.obfuscation_type = name
                return
    
    def _extract_strings(self):
        """Extrai strings do código"""
        
        # Strings entre aspas
        patterns = [
            r'"([^"\\]*(?:\\.[^"\\]*)*)"',
            r"'([^'\\]*(?:\\.[^'\\]*)*)'",
            r'`([^`\\]*(?:\\.[^`\\]*)*)`',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.code)
            self.structure.strings.extend(matches)
    
    def _extract_functions(self):
        """Extrai funções do código"""
        
        # Padrões de função
        patterns = [
            r'function\s+(\w+)\s*\(([^)]*)\)\s*\{',
            r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)\s*\{',
            r'(\w+)\s*:\s*function\s*\(([^)]*)\)\s*\{',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.code)
            for name, params in matches:
                self.structure.functions.append({
                    'name': name,
                    'params': params.split(',') if params else [],
                })
    
    def _find_crypto_calls(self):
        """Procura por chamadas de criptografia"""
        
        crypto_patterns = {
            'crypto.subtle.decrypt': r'crypto\.subtle\.decrypt\s*\(([^)]+)\)',
            'crypto.subtle.encrypt': r'crypto\.subtle\.encrypt\s*\(([^)]+)\)',
            'AES': r'AES|aes\.\w+',
            'CryptoJS': r'CryptoJS\.(\w+)',
            'atob': r'atob\s*\(([^)]+)\)',
            'btoa': r'btoa\s*\(([^)]+)\)',
        }
        
        for name, pattern in crypto_patterns.items():
            matches = re.findall(pattern, self.code)
            if matches:
                self.structure.encryption_calls.append({
                    'algorithm': name,
                    'matches': matches
                })
    
    def unpack_packer(self) -> Optional[str]:
        """Desempacota código empacotado (P.A.C.K.E.R.)"""
        
        packer_pattern = r"eval\(function\(p,a,c,k,e,([dr])\)(.*?)\)"
        match = re.search(packer_pattern, self.code)
        
        if match:
            # Implementação básica do unpacker
            try:
                # Extrair componentes
                payload = match.group(2)
                # Aqui você implementaria a lógica completa de unpacking
                # Por simplicidade, retornamos indicativo
                return f"[Packer detected - manual unpacking required]"
            except:
                pass
        
        return None
    
    def beautify_simple(self) -> str:
        """Formatação simples do código"""
        
        # Adicionar novas linhas após ;
        code = re.sub(r';', ';\n', self.code)
        
        # Adicionar novas linhas após {
        code = re.sub(r'\{', '{\n', code)
        
        # Adicionar novas linhas antes de }
        code = re.sub(r'\}', '\n}', code)
        
        # Indentação básica
        lines = code.split('\n')
        indented = []
        indent = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.endswith('}'):
                indent = max(0, indent - 1)
            
            indented.append('  ' * indent + stripped)
            
            if stripped.endswith('{'):
                indent += 1
        
        return '\n'.join(indented)


class PlayerEmbedAPICryptoAnalyzer:
    """
    Analisador específico para criptografia do PlayerEmbedAPI
    """
    
    def __init__(self, html_content: str = None, json_data: Dict = None):
        self.html = html_content
        self.json_data = json_data or {}
        self.media_data: Optional[bytes] = None
        self.analysis_results: List[CryptoAnalysis] = []
    
    def load_from_html(self, html: str):
        """Carrega dados de HTML"""
        self.html = html
        
        # Extrair datas
        pattern = r'const\s+datas\s*=\s*"([^"]+)"'
        match = re.search(pattern, html)
        
        if match:
            datas_b64 = match.group(1)
            # Padding
            padding = 4 - len(datas_b64) % 4
            if padding != 4:
                datas_b64 += '=' * padding
            
            decoded = base64.b64decode(datas_b64)
            self.json_data = json.loads(decoded)
            
            media_str = self.json_data.get('media', '')
            if isinstance(media_str, str):
                try:
                    self.media_data = base64.b64decode(media_str)
                except:
                    self.media_data = media_str.encode('utf-8')
            else:
                self.media_data = bytes(media_str) if media_str else b''
    
    def full_analysis(self) -> Dict:
        """Executa análise completa"""
        
        results = {
            'input_data': self.json_data,
            'media_size': len(self.media_data) if self.media_data else 0,
            'entropy_analysis': None,
            'decryption_attempts': [],
            'js_analysis': None,
            'recommended_approach': None
        }
        
        if not self.media_data:
            return results
        
        # Análise de entropia
        results['entropy_analysis'] = EntropyAnalyzer.detect_encryption(self.media_data)
        
        # Se dados parecem criptografados, tentar quebrar
        if results['entropy_analysis']['is_likely_encrypted']:
            print(f"[*] Dados parecem criptografados (entropia: {results['entropy_analysis']['entropy']:.2f})")
            
            # Gerar chaves
            keys = KeyDeriver.derive_all_keys(self.json_data)
            print(f"[*] Geradas {len(keys)} chaves para teste")
            
            # Tentar AES
            breaker = AESBreaker()
            attempts = breaker.attempt_decrypt(self.media_data, keys[:20])  # Limitar
            
            results['decryption_attempts'] = [
                {
                    'algorithm': a.algorithm,
                    'confidence': a.confidence,
                    'sample': a.decrypted_sample.hex() if a.decrypted_sample else None,
                    'method': a.method
                }
                for a in attempts[:5]  # Top 5
            ]
            
            if attempts and attempts[0].confidence > 0.7:
                results['recommended_approach'] = {
                    'method': 'decryption',
                    'algorithm': attempts[0].algorithm,
                    'confidence': attempts[0].confidence
                }
            else:
                results['recommended_approach'] = {
                    'method': 'browser_automation',
                    'reason': 'Decryption failed or confidence too low'
                }
        else:
            results['recommended_approach'] = {
                'method': 'direct_extraction',
                'reason': 'Data does not appear to be encrypted'
            }
        
        return results
    
    def analyze_js_bundle(self, bundle_path: str) -> Dict:
        """Analisa o bundle JavaScript"""
        
        try:
            with open(bundle_path, 'r', encoding='utf-8', errors='ignore') as f:
                js_code = f.read()
        except FileNotFoundError:
            return {'error': 'Bundle não encontrado'}
        
        deobf = JSDeobfuscator(js_code)
        structure = deobf.analyze()
        
        # Procurar especificamente por SoTrym
        sotrym_matches = re.findall(r'SoTrym[\s=:]+function\s*\(([^)]+)\)\s*\{([^}]+)\}', js_code, re.DOTALL)
        
        return {
            'obfuscation_type': structure.obfuscation_type,
            'total_functions': len(structure.functions),
            'total_strings': len(structure.strings),
            'encryption_calls': structure.encryption_calls,
            'sotrym_found': len(sotrym_matches) > 0,
            'sotrym_params': sotrym_matches[0][0] if sotrym_matches else None,
            'sample_strings': structure.strings[:20]
        }


def main():
    """Função principal"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║              PLAYEREMBEDAPI - CRYPTO BREAKER & JS REVERSE ENGINEER           ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    
    analyzer = PlayerEmbedAPICryptoAnalyzer()
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        
        if input_path.startswith('http'):
            # Download HTML
            import requests
            print(f"[*] Baixando: {input_path}")
            resp = requests.get(input_path, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            analyzer.load_from_html(resp.text)
        else:
            # Arquivo local
            print(f"[*] Carregando: {input_path}")
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                analyzer.load_from_html(f.read())
    else:
        # Procurar arquivo de exemplo
        examples = [
            'playerembedapi_kBJLtxCD3.html',
            'playerembedapi_QvXFt2de3.html',
        ]
        
        for ex in examples:
            if Path(ex).exists():
                print(f"[*] Usando exemplo: {ex}")
                with open(ex, 'r', encoding='utf-8', errors='ignore') as f:
                    analyzer.load_from_html(f.read())
                break
        else:
            print("[!] Nenhum arquivo de exemplo encontrado")
            print("Uso: python hacker_crypto_breaker.py <url|arquivo.html>")
            return
    
    # Executar análise
    print("\n[*] Executando análise criptográfica completa...")
    results = analyzer.full_analysis()
    
    # Exibir resultados
    print("\n" + "="*60)
    print("RESULTADOS DA ANÁLISE")
    print("="*60)
    
    print(f"\nDados de entrada:")
    print(f"  Slug: {results['input_data'].get('slug')}")
    print(f"  MD5 ID: {results['input_data'].get('md5_id')}")
    print(f"  User ID: {results['input_data'].get('user_id')}")
    print(f"  Tamanho do media: {results['media_size']} bytes")
    
    if results['entropy_analysis']:
        print(f"\nAnálise de entropia:")
        print(f"  Entropia: {results['entropy_analysis']['entropy']:.2f}/8.0")
        print(f"  Provavelmente criptografado: {results['entropy_analysis']['is_likely_encrypted']}")
        print(f"  Modo provável: {results['entropy_analysis']['likely_mode']}")
    
    if results['decryption_attempts']:
        print(f"\nTentativas de decriptação (top 5):")
        for i, attempt in enumerate(results['decryption_attempts'][:5], 1):
            print(f"  [{i}] {attempt['algorithm']}")
            print(f"      Confiança: {attempt['confidence']:.2%}")
            print(f"      Amostra: {attempt['sample'][:50] if attempt['sample'] else 'N/A'}...")
    
    print(f"\nAbordagem recomendada:")
    rec = results['recommended_approach']
    print(f"  Método: {rec['method']}")
    if 'reason' in rec:
        print(f"  Razão: {rec['reason']}")
    if 'algorithm' in rec:
        print(f"  Algoritmo: {rec['algorithm']}")
        print(f"  Confiança: {rec['confidence']:.2%}")
    
    # Analisar JS bundle se disponível
    bundle_path = 'core_bundle.js'
    if Path(bundle_path).exists():
        print(f"\n[*] Analisando bundle JavaScript...")
        js_analysis = analyzer.analyze_js_bundle(bundle_path)
        
        print(f"\nAnálise do JavaScript:")
        print(f"  Tipo de obfuscação: {js_analysis.get('obfuscation_type', 'N/A')}")
        print(f"  Funções encontradas: {js_analysis.get('total_functions', 0)}")
        print(f"  Strings encontradas: {js_analysis.get('total_strings', 0)}")
        print(f"  SoTrym encontrado: {js_analysis.get('sotrym_found', False)}")
        
        if js_analysis.get('encryption_calls'):
            print(f"\n  Chamadas de criptografia:")
            for call in js_analysis['encryption_calls']:
                print(f"    - {call['algorithm']}: {len(call['matches'])} ocorrências")
    
    # Salvar relatório
    report_file = 'crypto_analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n[*] Relatório completo salvo em: {report_file}")


if __name__ == '__main__':
    main()
