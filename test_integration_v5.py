#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
TESTE DE INTEGRAÇÃO - PlayerEmbedAPI v5.0
Projeto: brcloudstream (MaxSeries Provider)
Versão: 1.0.0
Data: 31/01/2026
===============================================================================

Este script realiza testes de integração para verificar:
1. Compilação sintática dos arquivos Kotlin
2. Dependências entre os novos arquivos V5
3. Atualização correta do MaxSeriesProvider.kt
4. Configuração do build.gradle.kts
5. Geração de relatório de status

Uso:
    python test_integration_v5.py
    python test_integration_v5.py --verbose
    python test_integration_v5.py --report-format json

===============================================================================
"""

import os
import re
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum


class Status(Enum):
    """Status dos testes"""
    PASS = "[PASS]"
    FAIL = "[FAIL]"
    WARN = "[WARN]"
    INFO = "[INFO]"
    SKIP = "[SKIP]"


@dataclass
class TestResult:
    """Resultado de um teste individual"""
    name: str
    status: Status
    message: str = ""
    details: List[str] = field(default_factory=list)
    line_number: Optional[int] = None
    file_path: Optional[str] = None


@dataclass
class IntegrationReport:
    """Relatório completo de integração"""
    timestamp: str
    project_path: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    results: List[TestResult] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)


class KotlinSyntaxChecker:
    """Verificador sintático básico para arquivos Kotlin"""
    
    # Padrões de erros comuns em Kotlin
    ERROR_PATTERNS = {
        'unmatched_brace': re.compile(r'^[^{}]*\{[^{}]*$'),
        'unmatched_parenthesis': re.compile(r'^[^()]*\([^()]*$'),
        'unmatched_bracket': re.compile(r'^[^\[\]]*\[[^\[\]]*$'),
        'incomplete_string': re.compile(r'"[^"]*$'),
        'incomplete_multiline_string': re.compile(r'"""[^"]*$'),
    }
    
    # Palavras-chave obrigatórias para classes/extractors
    REQUIRED_KEYWORDS = ['package', 'import', 'class', 'fun']
    
    def __init__(self, file_path: str, content: str):
        self.file_path = file_path
        self.content = content
        self.lines = content.split('\n')
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
    
    def check_balance(self) -> bool:
        """Verifica balanceamento de chaves, parênteses e colchetes"""
        stack = []
        line_num = 0
        
        for line in self.lines:
            line_num += 1
            # Ignorar strings e comentários para contagem
            clean_line = self._remove_strings_and_comments(line)
            
            for char in clean_line:
                if char in '({[':
                    stack.append((char, line_num))
                elif char in ')}]':
                    if not stack:
                        self.errors.append((line_num, f"Caractere de fechamento '{char}' sem abertura correspondente"))
                        return False
                    last_char, last_line = stack.pop()
                    expected_open = {'}': '{', ')': '(', ']': '['}[char]
                    if last_char != expected_open:
                        self.errors.append((line_num, f"Caractere de fechamento '{char}' não corresponde à abertura '{last_char}' (linha {last_line})"))
                        return False
        
        if stack:
            for char, line_num in stack:
                self.errors.append((line_num, f"Caractere de abertura '{char}' não fechado"))
            return False
        
        return True
    
    def _remove_strings_and_comments(self, line: str) -> str:
        """Remove strings e comentários da linha para análise"""
        result = []
        i = 0
        in_string = False
        string_char = None
        
        while i < len(line):
            if not in_string:
                if line[i:i+2] == '//':
                    break  # Comentário de linha, ignorar resto
                elif line[i:i+2] == '/*':
                    # Comentário de bloco - simplificado
                    if '*/' in line[i:]:
                        i = line.find('*/', i) + 2
                        continue
                elif line[i] in '"\'':
                    in_string = True
                    string_char = line[i]
                    i += 1
                    continue
                else:
                    result.append(line[i])
            else:
                if line[i] == '\\' and i + 1 < len(line):
                    i += 2  # Escape sequence
                    continue
                elif line[i] == string_char:
                    in_string = False
                    string_char = None
            i += 1
        
        return ''.join(result)
    
    def check_imports(self) -> bool:
        """Verifica se os imports estão corretos"""
        import_pattern = re.compile(r'^import\s+([\w.]+)')
        imports = []
        
        for line_num, line in enumerate(self.lines, 1):
            match = import_pattern.match(line.strip())
            if match:
                import_path = match.group(1)
                imports.append((line_num, import_path))
                # Verificar imports potencialmente problemáticos
                if '..' in import_path or import_path.startswith('.'):
                    self.warnings.append((line_num, f"Import suspeito: {import_path}"))
        
        return len(imports) > 0 or 'package' not in self.content
    
    def check_class_structure(self) -> bool:
        """Verifica estrutura básica da classe"""
        has_package = bool(re.search(r'^package\s+', self.content, re.MULTILINE))
        has_class = bool(re.search(r'\bclass\s+\w+', self.content))
        has_object = bool(re.search(r'\bobject\s+\w+', self.content))
        has_interface = bool(re.search(r'\binterface\s+\w+', self.content))
        
        if not has_package:
            self.errors.append((1, "Arquivo não possui declaração de package"))
        
        if not (has_class or has_object or has_interface):
            self.errors.append((1, "Arquivo não possui class, object ou interface"))
        
        return has_package and (has_class or has_object or has_interface)
    
    def check_common_mistakes(self) -> None:
        """Verifica erros comuns em Kotlin"""
        for line_num, line in enumerate(self.lines, 1):
            stripped = line.strip()
            
            # Verificar ponto-e-vírgula desnecessário (não é erro, mas é warning)
            if stripped.endswith(';') and not stripped.startswith('for'):
                self.warnings.append((line_num, "Ponto-e-vírgula desnecessário em Kotlin"))
            
            # Verificar null safety básica
            if '!!' in line and '!!!' not in line:
                self.warnings.append((line_num, "Uso de operador !! (not-null assertion) - pode causar NPE"))
            
            # Verificar TODOs não resolvidos
            if 'TODO(' in line or 'TODO:' in line:
                self.warnings.append((line_num, "TODO encontrado - verificar se precisa ser implementado"))
            
            # Verificar prints (deveria usar Log)
            if 'println(' in line:
                self.warnings.append((line_num, "Uso de println - considerar usar Log.d/i/w/e"))
    
    def run_all_checks(self) -> Tuple[bool, List[str], List[str]]:
        """Executa todas as verificações e retorna resultado"""
        self.check_balance()
        self.check_imports()
        self.check_class_structure()
        self.check_common_mistakes()
        
        is_valid = len(self.errors) == 0
        error_msgs = [f"Linha {line}: {msg}" for line, msg in self.errors]
        warning_msgs = [f"Linha {line}: {msg}" for line, msg in self.warnings]
        
        return is_valid, error_msgs, warning_msgs


class PlayerEmbedAPIV5IntegrationTester:
    """Testador de integração específico para PlayerEmbedAPI v5.0"""
    
    def __init__(self, project_path: str, verbose: bool = False):
        self.project_path = Path(project_path)
        self.verbose = verbose
        self.report = IntegrationReport(
            timestamp=datetime.now().isoformat(),
            project_path=str(self.project_path)
        )
        
        # Arquivos importantes
        self.v5_extractor = self.project_path / "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorV5.kt"
        self.v5_webview = self.project_path / "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIWebViewExtractorV5.kt"
        self.provider = self.project_path / "MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt"
        self.build_gradle = self.project_path / "MaxSeries/build.gradle.kts"
        
        # Dependências esperadas
        self.expected_utils = [
            "LinkDecryptor",
            "QualityDetector", 
            "VideoUrlCache",
            "JsonHelper"
        ]
        
        self.results: List[TestResult] = []
    
    def log(self, message: str):
        """Log condicional baseado em verbose"""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def add_result(self, name: str, status: Status, message: str = "", details: List[str] = None, line_number: int = None, file_path: str = None):
        """Adiciona resultado ao relatório"""
        result = TestResult(
            name=name,
            status=status,
            message=message,
            details=details or [],
            line_number=line_number,
            file_path=file_path
        )
        self.results.append(result)
        
        # Atualizar contadores
        self.report.total_tests += 1
        if status == Status.PASS:
            self.report.passed += 1
        elif status == Status.FAIL:
            self.report.failed += 1
        elif status == Status.WARN:
            self.report.warnings += 1
        
        # Print imediato
        status_icon = status.value
        print(f"{status_icon} {name}", flush=True)
        if message:
            print(f"   {message}")
        if details:
            for detail in details[:5]:  # Limitar a 5 detalhes
                print(f"   -> {detail}")
        print()
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Lê conteúdo de um arquivo"""
        try:
            if not file_path.exists():
                return None
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.log(f"Erro ao ler {file_path}: {e}")
            return None
    
    # =========================================================================
    # TESTE 1: Verificação de Sintaxe Kotlin
    # =========================================================================
    def test_kotlin_syntax(self):
        """Testa sintaxe dos arquivos Kotlin V5"""
        print("\n" + "="*70)
        print("TESTE 1: VERIFICAÇÃO DE SINTAXE KOTLIN")
        print("="*70 + "\n")
        
        files_to_check = [
            ("PlayerEmbedAPIExtractorV5", self.v5_extractor),
            ("PlayerEmbedAPIWebViewExtractorV5", self.v5_webview),
            ("MaxSeriesProvider", self.provider),
        ]
        
        for name, file_path in files_to_check:
            self.log(f"Verificando sintaxe de {name}...")
            
            content = self.read_file(file_path)
            if content is None:
                self.add_result(
                    f"Sintaxe: {name}",
                    Status.FAIL,
                    f"Arquivo não encontrado: {file_path}"
                )
                continue
            
            checker = KotlinSyntaxChecker(str(file_path), content)
            is_valid, errors, warnings = checker.run_all_checks()
            
            if is_valid and len(warnings) == 0:
                self.add_result(
                    f"Sintaxe: {name}",
                    Status.PASS,
                    f"Arquivo sintaticamente correto ({len(content)} caracteres)"
                )
            elif is_valid:
                self.add_result(
                    f"Sintaxe: {name}",
                    Status.WARN,
                    f"Sintaxe OK, mas há {len(warnings)} avisos",
                    warnings[:10]
                )
            else:
                self.add_result(
                    f"Sintaxe: {name}",
                    Status.FAIL,
                    f"Encontrados {len(errors)} erros de sintaxe",
                    errors[:10]
                )
    
    # =========================================================================
    # TESTE 2: Verificação de Dependências V5
    # =========================================================================
    def test_v5_dependencies(self):
        """Testa dependências entre os arquivos V5"""
        print("\n" + "="*70)
        print("TESTE 2: VERIFICAÇÃO DE DEPENDÊNCIAS V5")
        print("="*70 + "\n")
        
        # Verificar se PlayerEmbedAPIExtractorV5 importa WebViewExtractorV5
        v5_content = self.read_file(self.v5_extractor)
        if v5_content:
            has_webview_import = "PlayerEmbedAPIWebViewExtractorV5" in v5_content
            
            if has_webview_import:
                self.add_result(
                    "Dependência: V5 -> WebViewV5",
                    Status.PASS,
                    "PlayerEmbedAPIExtractorV5 referencia PlayerEmbedAPIWebViewExtractorV5"
                )
            else:
                self.add_result(
                    "Dependência: V5 -> WebViewV5",
                    Status.WARN,
                    "PlayerEmbedAPIExtractorV5 não referencia diretamente WebViewV5"
                )
        
        # Verificar imports de utilitários
        for util in self.expected_utils:
            util_file = self.project_path / f"MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/utils/{util}.kt"
            util_exists = util_file.exists()
            
            # Verificar se é importado pelo V5
            imported_in_v5 = util in v5_content if v5_content else False
            
            status = Status.PASS if util_exists else Status.FAIL
            msg = f"Utilitário {util}: {'encontrado' if util_exists else 'NÃO ENCONTRADO'}"
            if util_exists and imported_in_v5:
                msg += " e importado em V5"
            
            self.add_result(
                f"Dependência: Utils/{util}",
                status,
                msg
            )
        
        # Verificar estrutura de dados necessária
        if v5_content:
            has_extractor_api = "ExtractorApi" in v5_content
            has_geturl = "getUrl" in v5_content
            has_extractor_link = "ExtractorLink" in v5_content
            
            checks = [
                ("Herança ExtractorApi", has_extractor_api),
                ("Método getUrl", has_geturl),
                ("Uso de ExtractorLink", has_extractor_link),
            ]
            
            for check_name, check_passed in checks:
                self.add_result(
                    f"Estrutura V5: {check_name}",
                    Status.PASS if check_passed else Status.FAIL,
                    f"{'Encontrado' if check_passed else 'NÃO encontrado'} em PlayerEmbedAPIExtractorV5"
                )
    
    # =========================================================================
    # TESTE 3: Verificação do MaxSeriesProvider.kt
    # =========================================================================
    def test_provider_integration(self):
        """Testa se MaxSeriesProvider.kt está corretamente atualizado"""
        print("\n" + "="*70)
        print("TESTE 3: VERIFICAÇÃO DO MaxSeriesProvider.kt")
        print("="*70 + "\n")
        
        provider_content = self.read_file(self.provider)
        if not provider_content:
            self.add_result(
                "Provider: Arquivo",
                Status.FAIL,
                "MaxSeriesProvider.kt não encontrado"
            )
            return
        
        # Verificar import do V5
        has_v5_import = "PlayerEmbedAPIExtractorV5" in provider_content
        self.add_result(
            "Provider: Import V5",
            Status.PASS if has_v5_import else Status.FAIL,
            f"Import de PlayerEmbedAPIExtractorV5 {'encontrado' if has_v5_import else 'NÃO encontrado'}"
        )
        
        # Verificar uso do V5 em extractSourcesParallel
        has_v5_usage = "PlayerEmbedAPIExtractorV5()" in provider_content
        self.add_result(
            "Provider: Uso do V5",
            Status.PASS if has_v5_usage else Status.FAIL,
            f"Instanciação de PlayerEmbedAPIExtractorV5 {'encontrada' if has_v5_usage else 'NÃO encontrada'}"
        )
        
        # Verificar prioridade do V5 (deve ser prioridade 1)
        v5_priority_match = re.search(r'PRIORIDADE\s*1.*PlayerEmbedAPI', provider_content, re.IGNORECASE)
        has_priority_comment = v5_priority_match is not None
        
        self.add_result(
            "Provider: Prioridade V5",
            Status.PASS if has_priority_comment else Status.INFO,
            f"Comentário de prioridade 1 para V5 {'encontrado' if has_priority_comment else 'não encontrado (pode estar implícito)'}"
        )
        
        # Verificar versão do provider
        version_match = re.search(r'Provider\s+v(\d+)', provider_content)
        if version_match:
            version = version_match.group(1)
            self.add_result(
                "Provider: Versão",
                Status.INFO,
                f"Versão do provider detectada: v{version}"
            )
        
        # Verificar nome do provider
        name_match = re.search(r'name\s*=\s*"MaxSeries\s+v?(\d+)"', provider_content)
        if name_match:
            name_version = name_match.group(1)
            self.add_result(
                "Provider: Nome",
                Status.PASS,
                f"Nome do provider: 'MaxSeries v{name_version}'"
            )
        
        # Verificar outros extractors suportados
        other_extractors = [
            "MegaEmbedExtractorV8",
            "MegaEmbedExtractorV9",
            "PlayerThreeBloggerExtractor",
            "MyVidPlayExtractor",
            "DoodStreamExtractor",
            "StreamtapeExtractor",
            "MixdropExtractor",
            "FilemoonExtractor"
        ]
        
        found_extractors = []
        for extractor in other_extractors:
            if extractor in provider_content:
                found_extractors.append(extractor)
        
        self.add_result(
            "Provider: Extractors Suportados",
            Status.PASS,
            f"{len(found_extractors)} extractors encontrados",
            found_extractors
        )
    
    # =========================================================================
    # TESTE 4: Verificação do build.gradle.kts
    # =========================================================================
    def test_build_gradle(self):
        """Testa configuração do build.gradle.kts"""
        print("\n" + "="*70)
        print("TESTE 4: VERIFICAÇÃO DO build.gradle.kts")
        print("="*70 + "\n")
        
        gradle_content = self.read_file(self.build_gradle)
        if not gradle_content:
            self.add_result(
                "Gradle: Arquivo",
                Status.FAIL,
                "build.gradle.kts não encontrado"
            )
            return
        
        # Verificar versão
        version_match = re.search(r'version\s*=\s*(\d+)', gradle_content)
        if version_match:
            version = version_match.group(1)
            self.add_result(
                "Gradle: Versão",
                Status.PASS,
                f"Versão configurada: {version}"
            )
        else:
            self.add_result(
                "Gradle: Versão",
                Status.WARN,
                "Versão não encontrada no formato esperado"
            )
        
        # Verificar bloco cloudstream
        has_cloudstream = 'cloudstream {' in gradle_content
        self.add_result(
            "Gradle: Bloco cloudstream",
            Status.PASS if has_cloudstream else Status.FAIL,
            f"Bloco cloudstream {'encontrado' if has_cloudstream else 'NÃO encontrado'}"
        )
        
        # Verificar descrição
        desc_match = re.search(r'description\s*=\s*"([^"]+)"', gradle_content)
        if desc_match:
            description = desc_match.group(1)
            has_v5_in_desc = 'v5' in description.lower() or '5.0' in description
            self.add_result(
                "Gradle: Descrição",
                Status.PASS if has_v5_in_desc else Status.INFO,
                f"Descrição: '{description}' {'(contém referência V5)' if has_v5_in_desc else ''}"
            )
        
        # Verificar campos obrigatórios
        required_fields = ['authors', 'status', 'tvTypes', 'language']
        for field in required_fields:
            has_field = f'{field}' in gradle_content or f'{field} =' in gradle_content
            self.add_result(
                f"Gradle: Campo {field}",
                Status.PASS if has_field else Status.FAIL,
                f"Campo {field} {'encontrado' if has_field else 'NÃO encontrado'}"
            )
    
    # =========================================================================
    # TESTE 5: Verificações Adicionais de Qualidade
    # =========================================================================
    def test_quality_checks(self):
        """Testes adicionais de qualidade de código"""
        print("\n" + "="*70)
        print("TESTE 5: VERIFICAÇÕES ADICIONAIS DE QUALIDADE")
        print("="*70 + "\n")
        
        # Verificar documentação/comentários no V5
        v5_content = self.read_file(self.v5_extractor)
        if v5_content:
            has_kdoc = "/**" in v5_content
            has_version_doc = "v5.0" in v5_content or "v5" in v5_content.lower()
            
            self.add_result(
                "Qualidade: Documentação V5",
                Status.PASS if has_kdoc else Status.WARN,
                f"Documentação KDoc {'encontrada' if has_kdoc else 'mínima - considere adicionar'}"
            )
            
            self.add_result(
                "Qualidade: Versão Documentada",
                Status.PASS if has_version_doc else Status.WARN,
                f"Versão V5 {'documentada no código' if has_version_doc else 'não claramente documentada'}"
            )
        
        # Verificar tratamento de erros
        if v5_content:
            has_try_catch = 'try {' in v5_content and 'catch (' in v5_content
            has_null_safety = '?:' in v5_content or '?.' in v5_content
            
            self.add_result(
                "Qualidade: Tratamento de Erros",
                Status.PASS if has_try_catch else Status.WARN,
                f"Blocos try-catch {'encontrados' if has_try_catch else 'não encontrados - verificar'}"
            )
            
            self.add_result(
                "Qualidade: Null Safety",
                Status.PASS if has_null_safety else Status.WARN,
                f"Operadores de null safety {'encontrados' if has_null_safety else 'não encontrados - verificar'}"
            )
        
        # Verificar WebView
        webview_content = self.read_file(self.v5_webview)
        if webview_content:
            has_ssl_security = "onReceivedSslError" in webview_content
            has_cancel = "handler?.cancel()" in webview_content or "handler.cancel()" in webview_content
            
            if has_ssl_security:
                self.add_result(
                    "Segurança: SSL Error Handler",
                    Status.PASS if has_cancel else Status.FAIL,
                    f"SSL Error handler {'configurado corretamente (cancela)' if has_cancel else 'INSEGURO (não cancela)'}"
                )
    
    # =========================================================================
    # GERAÇÃO DO RELATÓRIO FINAL
    # =========================================================================
    def generate_report(self, format_type: str = "text"):
        """Gera relatório final"""
        print("\n" + "="*70)
        print("RELATÓRIO FINAL DE INTEGRAÇÃO")
        print("="*70 + "\n")
        
        self.report.results = self.results
        
        # Calcular estatísticas
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == Status.PASS)
        failed = sum(1 for r in self.results if r.status == Status.FAIL)
        warnings = sum(1 for r in self.results if r.status == Status.WARN)
        
        self.report.summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
        }
        
        if format_type.lower() == "json":
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Gera relatório em formato texto"""
        lines = []
        lines.append("="*70)
        lines.append("RELATÓRIO DE INTEGRAÇÃO - PlayerEmbedAPI v5.0")
        lines.append("="*70)
        lines.append(f"Timestamp: {self.report.timestamp}")
        lines.append(f"Projeto: {self.report.project_path}")
        lines.append("")
        lines.append("-"*70)
        lines.append("RESUMO")
        lines.append("-"*70)
        lines.append(f"Total de Testes: {self.report.summary['total_tests']}")
        lines.append(f"✅ Aprovados: {self.report.summary['passed']}")
        lines.append(f"❌ Falhas: {self.report.summary['failed']}")
        lines.append(f"⚠️ Avisos: {self.report.summary['warnings']}")
        lines.append(f"Taxa de Sucesso: {self.report.summary['success_rate']}")
        lines.append("")
        
        # Listar falhas
        failures = [r for r in self.results if r.status == Status.FAIL]
        if failures:
            lines.append("-"*70)
            lines.append("FALHAS DETECTADAS")
            lines.append("-"*70)
            for f in failures:
                lines.append(f"\n[FALHA] {f.name}")
                lines.append(f"   {f.message}")
                if f.details:
                    for d in f.details:
                        lines.append(f"   -> {d}")
        
        # Listar avisos
        warns = [r for r in self.results if r.status == Status.WARN]
        if warns:
            lines.append("\n" + "-"*70)
            lines.append("AVISOS")
            lines.append("-"*70)
            for w in warns[:10]:  # Limitar a 10
                lines.append(f"\n[AVISO] {w.name}")
                lines.append(f"   {w.message}")
        
        lines.append("\n" + "="*70)
        lines.append("FIM DO RELATÓRIO")
        lines.append("="*70)
        
        report_text = "\n".join(lines)
        
        # Salvar em arquivo
        report_path = self.project_path / "integration_test_report.txt"
        try:
            report_path.write_text(report_text, encoding='utf-8')
            print(f"\nRelatório salvo em: {report_path}")
        except Exception as e:
            print(f"\nErro ao salvar relatório: {e}")
        
        return report_text
    
    def _generate_json_report(self) -> str:
        """Gera relatório em formato JSON"""
        report_dict = {
            "timestamp": self.report.timestamp,
            "project_path": self.report.project_path,
            "summary": self.report.summary,
            "results": [
                {
                    "name": r.name,
                    "status": r.status.name,
                    "message": r.message,
                    "details": r.details,
                    "line_number": r.line_number,
                    "file_path": r.file_path
                }
                for r in self.results
            ]
        }
        
        report_json = json.dumps(report_dict, indent=2, ensure_ascii=False)
        
        # Salvar em arquivo
        report_path = self.project_path / "integration_test_report.json"
        try:
            report_path.write_text(report_json, encoding='utf-8')
            print(f"\nRelatório JSON salvo em: {report_path}")
        except Exception as e:
            print(f"\nErro ao salvar relatório JSON: {e}")
        
        return report_json
    
    # =========================================================================
    # EXECUÇÃO COMPLETA
    # =========================================================================
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*70)
        print("INICIANDO TESTES DE INTEGRAÇÃO - PlayerEmbedAPI v5.0")
        print("="*70)
        
        # Verificar existência dos arquivos principais
        print("\n[VERIFICAÇÃO INICIAL]")
        print(f"Project path: {self.project_path}")
        print(f"V5 Extractor: {'[OK]' if self.v5_extractor.exists() else '[FALHA]'} {self.v5_extractor}")
        print(f"V5 WebView: {'[OK]' if self.v5_webview.exists() else '[FALHA]'} {self.v5_webview}")
        print(f"Provider: {'[OK]' if self.provider.exists() else '[FALHA]'} {self.provider}")
        print(f"Build Gradle: {'[OK]' if self.build_gradle.exists() else '[FALHA]'} {self.build_gradle}")
        
        # Executar testes
        self.test_kotlin_syntax()
        self.test_v5_dependencies()
        self.test_provider_integration()
        self.test_build_gradle()
        self.test_quality_checks()
        
        return self.report


def main():
    parser = argparse.ArgumentParser(
        description="Teste de Integração - PlayerEmbedAPI v5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    python test_integration_v5.py
    python test_integration_v5.py --verbose
    python test_integration_v5.py --report-format json
    python test_integration_v5.py --path /caminho/do/projeto
        """
    )
    parser.add_argument(
        '--path',
        default=r'C:\Users\KYTHOURS\Desktop\brcloudstream',
        help='Caminho do projeto brcloudstream'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose com mais detalhes'
    )
    parser.add_argument(
        '--report-format',
        choices=['text', 'json'],
        default='text',
        help='Formato do relatório (padrão: text)'
    )
    
    args = parser.parse_args()
    
    # Verificar se o caminho existe
    if not os.path.exists(args.path):
        print(f"[ERRO] Caminho nao encontrado: {args.path}")
        sys.exit(1)
    
    # Executar testes
    tester = PlayerEmbedAPIV5IntegrationTester(args.path, verbose=args.verbose)
    report = tester.run_all_tests()
    
    # Gerar relatório
    output = tester.generate_report(format_type=args.report_format)
    
    if args.report_format == 'json':
        print(output)
    
    # Retornar código de saída apropriado
    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
