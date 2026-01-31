#!/usr/bin/env python3
"""
Analisador de Logs do CloudStream - PlayerEmbedAPI v5.0
Analisa logs capturados e gera relatório detalhado

Uso: python analyze_logs.py <arquivo_de_log>
"""

import sys
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ExtractionEvent:
    timestamp: str
    strategy: str
    url: str
    success: bool
    duration_ms: int = 0
    error: str = ""

class CloudStreamLogAnalyzer:
    def __init__(self, log_content: str):
        self.log_content = log_content
        self.events: List[ExtractionEvent] = []
        self.stats = {
            'total_extractions': 0,
            'successful': 0,
            'failed': 0,
            'by_strategy': {},
            'avg_duration': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def analyze(self):
        """Analisa o conteúdo do log"""
        self._extract_events()
        self._calculate_stats()
        return self._generate_report()
    
    def _extract_events(self):
        """Extrai eventos de extração do log"""
        lines = self.log_content.split('\n')
        
        current_extraction = None
        start_time = None
        
        for line in lines:
            # Detectar início de extração
            if "PRIORIDADE 1 - PlayerEmbedAPI" in line:
                current_extraction = {"strategy": "v5.0", "success": False}
                start_time = self._extract_timestamp(line)
            
            # Detectar estratégia específica
            elif "Tentando extração via API" in line:
                current_extraction = {"strategy": "API", "success": False}
            elif "Tentando extração via ShortIcu" in line:
                current_extraction = {"strategy": "ShortIcu", "success": False}
            elif "Tentando extração via Regex" in line:
                current_extraction = {"strategy": "Regex", "success": False}
            elif "Tentando extração via WebView" in line:
                current_extraction = {"strategy": "WebView", "success": False}
            
            # Detectar sucesso
            elif "SUCESSO" in line and current_extraction:
                current_extraction["success"] = True
                end_time = self._extract_timestamp(line)
                duration = self._calculate_duration(start_time, end_time) if start_time else 0
                
                self.events.append(ExtractionEvent(
                    timestamp=start_time or "",
                    strategy=current_extraction["strategy"],
                    url="",
                    success=True,
                    duration_ms=duration
                ))
                current_extraction = None
            
            # Detectar erro
            elif ("Falhou" in line or "Erro" in line or "ERROR" in line) and current_extraction:
                error_msg = line.split(":")[-1].strip() if ":" in line else line
                
                self.events.append(ExtractionEvent(
                    timestamp=start_time or "",
                    strategy=current_extraction["strategy"],
                    url="",
                    success=False,
                    error=error_msg
                ))
                current_extraction = None
            
            # Detectar cache
            elif "Cache HIT" in line:
                self.stats['cache_hits'] += 1
            elif "Cache MISS" in line:
                self.stats['cache_misses'] += 1
    
    def _calculate_stats(self):
        """Calcula estatísticas dos eventos"""
        self.stats['total_extractions'] = len(self.events)
        self.stats['successful'] = sum(1 for e in self.events if e.success)
        self.stats['failed'] = sum(1 for e in self.events if not e.success)
        
        # Por estratégia
        for event in self.events:
            strategy = event.strategy
            if strategy not in self.stats['by_strategy']:
                self.stats['by_strategy'][strategy] = {'success': 0, 'failed': 0}
            
            if event.success:
                self.stats['by_strategy'][strategy]['success'] += 1
            else:
                self.stats['by_strategy'][strategy]['failed'] += 1
        
        # Duração média
        durations = [e.duration_ms for e in self.events if e.duration_ms > 0]
        if durations:
            self.stats['avg_duration'] = sum(durations) / len(durations)
    
    def _generate_report(self) -> str:
        """Gera relatório formatado"""
        report = []
        report.append("=" * 60)
        report.append("ANÁLISE DE LOGS - CloudStream PlayerEmbedAPI v5.0")
        report.append("=" * 60)
        report.append("")
        
        # Resumo geral
        report.append("RESUMO GERAL")
        report.append("-" * 60)
        report.append(f"Total de extrações: {self.stats['total_extractions']}")
        report.append(f"[OK] Sucesso: {self.stats['successful']} ({self._percentage(self.stats['successful'])}%)")
        report.append(f"[OK] Falhas: {self.stats['failed']} ({self._percentage(self.stats['failed'])}%)")
        report.append(f"⏱️  Duração média: {self.stats['avg_duration']:.0f}ms")
        report.append("")
        
        # Cache
        report.append("CACHE")
        report.append("-" * 60)
        cache_total = self.stats['cache_hits'] + self.stats['cache_misses']
        if cache_total > 0:
            hit_rate = (self.stats['cache_hits'] / cache_total) * 100
            report.append(f"Cache HIT: {self.stats['cache_hits']} ({hit_rate:.1f}%)")
            report.append(f"Cache MISS: {self.stats['cache_misses']} ({100-hit_rate:.1f}%)")
        else:
            report.append("Sem dados de cache")
        report.append("")
        
        # Por estratégia
        report.append("DESEMPENHO POR ESTRATEGIA")
        report.append("-" * 60)
        for strategy, counts in self.stats['by_strategy'].items():
            total = counts['success'] + counts['failed']
            success_rate = (counts['success'] / total * 100) if total > 0 else 0
            report.append(f"{strategy:12} | Sucesso: {counts['success']:3} | Falhas: {counts['failed']:3} | Taxa: {success_rate:5.1f}%")
        report.append("")
        
        # Detalhes dos eventos
        report.append("EVENTOS DETALHADOS")
        report.append("-" * 60)
        for i, event in enumerate(self.events[:20], 1):  # Primeiros 20
            status = "[OK]" if event.success else "[OK]"
            report.append(f"{i:2}. {status} {event.strategy:12} | {event.duration_ms:4}ms | {event.error[:40] if event.error else 'OK'}")
        
        if len(self.events) > 20:
            report.append(f"    ... e mais {len(self.events) - 20} eventos")
        
        report.append("")
        report.append("=" * 60)
        
        # Recomendações
        report.append("RECOMENDACOES")
        report.append("-" * 60)
        
        if self.stats['failed'] > self.stats['successful']:
            report.append("[AVISO] Muitas falhas detectadas!")
            report.append("   - Verificar conexão de internet")
            report.append("   - Verificar se o site está online")
            report.append("   - Analisar mensagens de erro específicas")
        
        if 'WebView' in self.stats['by_strategy'] and self.stats['by_strategy']['WebView']['success'] > 0:
            report.append("[INFO] WebView sendo usado frequentemente")
            report.append("   - Considere melhorar as estratégias 1-3")
            report.append("   - WebView é mais lento que as outras")
        
        if self.stats['cache_hits'] == 0 and self.stats['cache_misses'] > 0:
            report.append("[INFO] Cache nao esta sendo aproveitado")
            report.append("   - Isso é normal na primeira execução")
            report.append("   - Na segunda execução deve mostrar HITs")
        
        success_rate = self._percentage(self.stats['successful'])
        if success_rate >= 95:
            report.append("[OK] Excelente taxa de sucesso!")
        elif success_rate >= 80:
            report.append("[OK] Boa taxa de sucesso")
        elif success_rate >= 50:
            report.append("[AVISO] Taxa de sucesso moderada")
        else:
            report.append("[ERRO] Taxa de sucesso baixa - necessita atencao")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _extract_timestamp(self, line: str) -> str:
        """Extrai timestamp da linha de log"""
        match = re.match(r'(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})', line)
        return match.group(1) if match else ""
    
    def _calculate_duration(self, start: str, end: str) -> int:
        """Calcula duração entre dois timestamps"""
        try:
            fmt = "%m-%d %H:%M:%S.%f"
            t1 = datetime.strptime(start, fmt)
            t2 = datetime.strptime(end, fmt)
            return int((t2 - t1).total_seconds() * 1000)
        except:
            return 0
    
    def _percentage(self, value: int) -> float:
        """Calcula porcentagem"""
        if self.stats['total_extractions'] == 0:
            return 0.0
        return (value / self.stats['total_extractions']) * 100


def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_logs.py <arquivo_de_log>")
        print("Exemplo: python analyze_logs.py cloudstream_logs.txt")
        sys.exit(1)
    
    log_file = sys.argv[1]
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analyzer = CloudStreamLogAnalyzer(content)
        report = analyzer.analyze()
        
        print(report)
        
        # Salvar relatório
        output_file = log_file.replace('.txt', '_analysis.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[emoji] Relatório salvo em: {output_file}")
        
    except FileNotFoundError:
        print(f"[OK] Arquivo não encontrado: {log_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[OK] Erro: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
