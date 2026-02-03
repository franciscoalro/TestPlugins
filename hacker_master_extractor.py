#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              PLAYEREMBEDAPI - MASTER EXTRACTION SYSTEM                       ║
║           Integração Completa de Técnicas de Engenharia Reversa              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Sistema mestre que integra todas as técnicas:
1. Análise estática e dinâmica
2. Criptoanálise avançada  
3. Interceptação de rede
4. Manipulação de DOM
5. Extração multi-camadas

Este é o sistema definitivo para extração de vídeo do PlayerEmbedAPI.
"""

import asyncio
import base64
import hashlib
import json
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# Importar nossos módulos
from hacker_playerembedapi_advanced import (
    PlayerEmbedAPIAnalyzer, AdvancedVideoExtractor, 
    VideoData, ExtractedVideo
)


@dataclass
class ExtractionReport:
    """Relatório completo de extração"""
    target_url: str
    extraction_time: float
    techniques_applied: List[str]
    results: List[ExtractedVideo]
    crypto_analysis: Dict[str, Any]
    network_analysis: Dict[str, Any]
    js_analysis: Dict[str, Any]
    recommendations: List[str]
    final_video_url: Optional[str] = None
    is_playable: bool = False
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'target_url': self.target_url,
            'extraction_time': self.extraction_time,
            'techniques_applied': self.techniques_applied,
            'results': [
                {
                    'url': r.url,
                    'quality': r.quality,
                    'source': r.source,
                    'headers': r.headers,
                    'is_direct': r.is_direct,
                    'extraction_method': r.extraction_method
                }
                for r in self.results
            ],
            'crypto_analysis': self.crypto_analysis,
            'network_analysis': self.network_analysis,
            'js_analysis': self.js_analysis,
            'recommendations': self.recommendations,
            'final_video_url': self.final_video_url,
            'is_playable': self.is_playable
        }


class MasterPlayerEmbedAPIExtractor:
    """
    Extrator mestre que orquestra todas as técnicas
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        self.log: List[str] = []
    
    def log_msg(self, msg: str, level: str = "INFO"):
        """Registra mensagem"""
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {msg}"
        self.log.append(formatted)
        print(formatted)
    
    async def extract(self, url: str, use_browser: bool = True) -> ExtractionReport:
        """
        Executa extração completa
        
        Args:
            url: URL do playerembedapi
            use_browser: Se deve usar automatização de browser
        """
        start_time = time.time()
        techniques = []
        all_results = []
        
        self.log_msg(f"Iniciando extração mestre: {url}")
        self.log_msg("=" * 60)
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 1: ANÁLISE ESTÁTICA
        # ═══════════════════════════════════════════════════════════════════════
        
        self.log_msg("FASE 1: Análise Estática", "PHASE")
        
        # Obter HTML
        try:
            response = self.session.get(url, timeout=30)
            html = response.text
            self.log_msg(f"HTML obtido: {len(html)} bytes")
        except Exception as e:
            self.log_msg(f"Falha ao obter HTML: {e}", "ERROR")
            return self._create_error_report(url, str(e))
        
        # Inicializar analisador
        analyzer = PlayerEmbedAPIAnalyzer(html, url)
        
        # Extrair campo datas
        datas = analyzer.extract_datas_field()
        if datas:
            self.log_msg(f"Campo datas encontrado: {len(datas)} caracteres")
            video_data = analyzer.decode_datas(datas)
            if video_data:
                self.log_msg(f"Dados decodificados: slug={video_data.slug}, md5_id={video_data.md5_id}")
        
        # Análise de DOM
        dom_analysis = analyzer.virtual_dom_analysis()
        self.log_msg(f"Elementos de vídeo encontrados: {len(dom_analysis.get('video_elements', []))}")
        
        techniques.append("static_analysis")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 2: EXTRAÇÃO HTTP DIRETA
        # ═══════════════════════════════════════════════════════════════════════
        
        self.log_msg("FASE 2: Extração HTTP Direta", "PHASE")
        
        http_results = analyzer.attempt_direct_extraction(url)
        if http_results:
            self.log_msg(f"Encontrados {len(http_results)} vídeo(s) via HTTP direto")
            all_results.extend(http_results)
        else:
            self.log_msg("Nenhum vídeo encontrado via HTTP direto", "WARN")
        
        techniques.append("direct_http")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 3: ANÁLISE CRIPTOGRÁFICA
        # ═══════════════════════════════════════════════════════════════════════
        
        self.log_msg("FASE 3: Análise Criptográfica", "PHASE")
        
        crypto_analysis = {}
        if analyzer.video_data and analyzer.video_data.media:
            from hacker_crypto_breaker import EntropyAnalyzer, KeyDeriver, AESBreaker
            
            media = analyzer.video_data.media
            entropy_analysis = EntropyAnalyzer.detect_encryption(media)
            crypto_analysis['entropy'] = entropy_analysis
            
            self.log_msg(f"Entropia do campo media: {entropy_analysis['entropy']:.2f}")
            self.log_msg(f"Provavelmente criptografado: {entropy_analysis['is_likely_encrypted']}")
            
            if entropy_analysis['is_likely_encrypted']:
                # Tentar quebrar
                keys = KeyDeriver.derive_all_keys(analyzer.video_data.raw_json)
                self.log_msg(f"Testando {len(keys[:10])} chaves derivadas...")
                
                breaker = AESBreaker()
                attempts = breaker.attempt_decrypt(media, keys[:10])
                
                if attempts:
                    best = attempts[0]
                    self.log_msg(f"Melhor tentativa: {best.algorithm} (confiança: {best.confidence:.2%})")
                    crypto_analysis['best_attempt'] = {
                        'algorithm': best.algorithm,
                        'confidence': best.confidence,
                        'sample': best.decrypted_sample.hex() if best.decrypted_sample else None
                    }
        
        techniques.append("crypto_analysis")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 4: ANÁLISE JAVASCRIPT
        # ═══════════════════════════════════════════════════════════════════════
        
        self.log_msg("FASE 4: Análise JavaScript", "PHASE")
        
        js_analysis = {}
        js_scripts = analyzer.extract_js_variables()
        js_analysis['variables_found'] = list(js_scripts.keys())
        
        # Procurar por JWPlayer config
        jwplayer_patterns = [
            r'jwplayer\(["\'][^"\']+["\']\)\.setup\((\{[^}]+\})',
            r'file\s*:\s*["\']([^"\']+)["\']',
            r'sources\s*:\s*(\[[^\]]+\])',
        ]
        
        for pattern in jwplayer_patterns:
            matches = re.findall(pattern, html)
            if matches:
                js_analysis[f'pattern_{pattern[:20]}'] = len(matches)
        
        self.log_msg(f"Variáveis JS encontradas: {len(js_analysis['variables_found'])}")
        
        techniques.append("js_analysis")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 5: AUTOMATIZAÇÃO DE BROWSER (se habilitado)
        # ═══════════════════════════════════════════════════════════════════════
        
        network_analysis = {}
        
        if use_browser and not all_results:
            self.log_msg("FASE 5: Automação de Browser", "PHASE")
            
            try:
                from hacker_network_interceptor import PlaywrightInterceptor
                
                interceptor = PlaywrightInterceptor()
                await interceptor.launch(headless=True)
                
                videos = await interceptor.extract_video(url, wait_time=12)
                
                if videos:
                    self.log_msg(f"Browser interceptou {len(videos)} vídeo(s)")
                    for v in videos:
                        all_results.append(ExtractedVideo(
                            url=v.url,
                            quality=v.quality,
                            source='PlayerEmbedAPI',
                            headers=v.headers,
                            is_direct=True,
                            extraction_method=f'browser_{v.intercepted_from}'
                        ))
                
                network_analysis['total_calls'] = len(interceptor.network_calls)
                network_analysis['video_calls'] = len([c for c in interceptor.network_calls if c.is_video()])
                
                await interceptor.close()
                techniques.append("browser_automation")
                
            except Exception as e:
                self.log_msg(f"Erro no browser automation: {e}", "ERROR")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 6: CONSTRUÇÃO DE URL (fallback)
        # ═══════════════════════════════════════════════════════════════════════
        
        if not all_results and analyzer.video_data:
            self.log_msg("FASE 6: Construção de URL via Dados", "PHASE")
            
            vd = analyzer.video_data
            constructed_urls = [
                f"https://{vd.slug}.sssrr.org/sora/{vd.md5_id}/",
                f"https://cdn.sssrr.org/sora/{vd.md5_id}/",
                f"https://{vd.slug}.sssrr.org/future",
            ]
            
            for url_constructed in constructed_urls:
                all_results.append(ExtractedVideo(
                    url=url_constructed,
                    quality='Unknown',
                    source='PlayerEmbedAPI',
                    headers={'Referer': url},
                    is_direct=False,
                    extraction_method='url_construction'
                ))
            
            self.log_msg(f"Construídas {len(constructed_urls)} URLs potenciais")
            techniques.append("url_construction")
        
        # ═══════════════════════════════════════════════════════════════════════
        # FASE 7: VALIDAÇÃO E RECOMENDAÇÕES
        # ═══════════════════════════════════════════════════════════════════════
        
        self.log_msg("FASE 7: Validação e Recomendações", "PHASE")
        
        # Deduplicar resultados
        seen = set()
        unique_results = []
        for r in all_results:
            url_clean = r.url.split('?')[0]
            if url_clean not in seen:
                seen.add(url_clean)
                unique_results.append(r)
        
        recommendations = []
        final_url = None
        is_playable = False
        
        if unique_results:
            # Ordenar por preferência
            preferred = sorted(unique_results, key=lambda x: (
                0 if '.m3u8' in x.url else 1,
                0 if x.is_direct else 1,
                0 if 'browser' in x.extraction_method else 1
            ))
            
            final_url = preferred[0].url
            
            # Verificar se URL é diretamente jogável
            if preferred[0].is_direct and ('.m3u8' in final_url or '.mp4' in final_url):
                is_playable = True
                recommendations.append("URL pronta para reprodução")
            else:
                recommendations.append("URL requer validação adicional")
            
            if any('sssrr.org' in r.url for r in unique_results):
                recommendations.append("Usar headers: Referer=https://playerembedapi.link/")
        else:
            recommendations.append("Nenhuma URL encontrada - requer análise manual")
        
        # Se criptografia detectada, recomendar browser
        if crypto_analysis.get('entropy', {}).get('is_likely_encrypted'):
            recommendations.append("Dados criptografados detectados - usar WebView recomendado")
        
        # ═══════════════════════════════════════════════════════════════════════
        # GERAR RELATÓRIO
        # ═══════════════════════════════════════════════════════════════════════
        
        extraction_time = time.time() - start_time
        
        report = ExtractionReport(
            target_url=url,
            extraction_time=extraction_time,
            techniques_applied=techniques,
            results=unique_results,
            crypto_analysis=crypto_analysis,
            network_analysis=network_analysis,
            js_analysis=js_analysis,
            recommendations=recommendations,
            final_video_url=final_url,
            is_playable=is_playable
        )
        
        self.log_msg("=" * 60)
        self.log_msg(f"Extração completa em {extraction_time:.2f}s")
        self.log_msg(f"Resultados: {len(unique_results)} vídeo(s) único(s)")
        
        return report
    
    def _create_error_report(self, url: str, error: str) -> ExtractionReport:
        """Cria relatório de erro"""
        return ExtractionReport(
            target_url=url,
            extraction_time=0,
            techniques_applied=[],
            results=[],
            crypto_analysis={'error': error},
            network_analysis={},
            js_analysis={},
            recommendations=[f"Erro: {error}"],
            final_video_url=None,
            is_playable=False
        )
    
    def save_report(self, report: ExtractionReport, filename: str = None):
        """Salva relatório em arquivo"""
        if filename is None:
            timestamp = int(time.time())
            filename = f"extraction_report_{timestamp}.json"
        
        data = report.to_dict()
        data['extraction_log'] = self.log
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.log_msg(f"Relatório salvo em: {filename}")
        return filename


def print_final_summary(report: ExtractionReport):
    """Imprime resumo final formatado"""
    print("\n" + "=" * 70)
    print("RESUMO FINAL DA EXTRAÇÃO")
    print("=" * 70)
    
    print(f"\n🎯 URL Alvo: {report.target_url}")
    print(f"⏱️  Tempo: {report.extraction_time:.2f} segundos")
    print(f"🔧 Técnicas: {', '.join(report.techniques_applied)}")
    
    print(f"\n📊 Resultados ({len(report.results)} encontrados):")
    for i, r in enumerate(report.results, 1):
        icon = "✅" if r.is_direct else "⚠️"
        print(f"   {icon} [{i}] {r.extraction_method}")
        print(f"      URL: {r.url[:70]}...")
        print(f"      Qualidade: {r.quality}")
    
    if report.final_video_url:
        print(f"\n🎬 URL Final Recomendada:")
        print(f"   {report.final_video_url}")
        
        if report.is_playable:
            print("\n   ✅ Esta URL deve ser reproduzível diretamente")
            print("   Headers necessários:")
            print('   {')
            print('     "Referer": "https://playerembedapi.link/",')
            print('     "Origin": "https://playerembedapi.link",')
            print('     "User-Agent": "Mozilla/5.0..."')
            print('   }')
    
    if report.recommendations:
        print(f"\n💡 Recomendações:")
        for rec in report.recommendations:
            print(f"   • {rec}")
    
    print("\n" + "=" * 70)


async def main():
    """Função principal"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║              PLAYEREMBEDAPI - MASTER EXTRACTION SYSTEM                       ║
    ║                    White Hat Security Research Tool                          ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    
    AVISO: Esta ferramenta é destinada apenas para pesquisa de segurança legítima
    e extração de conteúdo para uso pessoal. Respeite os termos de serviço.
    """)
    
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python hacker_master_extractor.py <url> [--no-browser]")
        print("\nExemplos:")
        print("  python hacker_master_extractor.py https://playerembedapi.link/?v=xxx")
        print("  python hacker_master_extractor.py https://playerembedapi.link/?v=xxx --no-browser")
        
        # Testar com arquivo local
        test_files = [
            'playerembedapi_kBJLtxCD3.html',
            'playerembedapi_QvXFt2de3.html',
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"\n[*] Testando com arquivo local: {test_file}")
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html = f.read()
                
                extractor = MasterPlayerEmbedAPIExtractor()
                
                # Simular extração
                analyzer = PlayerEmbedAPIAnalyzer(html, f"file://{test_file}")
                datas = analyzer.extract_datas_field()
                
                if datas:
                    video_data = analyzer.decode_datas(datas)
                    if video_data:
                        print(f"\n[✓] Dados extraídos com sucesso:")
                        print(f"    Slug: {video_data.slug}")
                        print(f"    MD5 ID: {video_data.md5_id}")
                        print(f"    User ID: {video_data.user_id}")
                        print(f"    Media Size: {len(video_data.media)} bytes")
                        
                        # URLs construídas
                        print(f"\n[→] URLs potenciais:")
                        print(f"    https://{video_data.slug}.sssrr.org/sora/{video_data.md5_id}/")
                        print(f"    https://cdn.sssrr.org/sora/{video_data.md5_id}/")
                
                return
        
        return
    
    url = sys.argv[1]
    use_browser = '--no-browser' not in sys.argv
    
    extractor = MasterPlayerEmbedAPIExtractor()
    report = await extractor.extract(url, use_browser=use_browser)
    
    print_final_summary(report)
    
    # Salvar relatório
    filename = extractor.save_report(report)
    
    # Se tiver resultado, criar arquivo de importação para VLC/players
    if report.final_video_url:
        m3u_content = f"""#EXTM3U
#EXTINF:-1,PlayerEmbedAPI Video
{report.final_video_url}
"""
        m3u_file = filename.replace('.json', '.m3u')
        with open(m3u_file, 'w', encoding='utf-8') as f:
            f.write(m3u_content)
        print(f"\n[✓] Playlist M3U salva em: {m3u_file}")
        print("    Esta playlist pode ser aberta no VLC, MPV, Kodi, etc.")


if __name__ == '__main__':
    asyncio.run(main())
