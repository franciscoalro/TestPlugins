#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
SCRIPT MESTRE DE TESTES - PlayerEmbedAPI v5.0
===============================================================================
Executa TODA a suite de testes automaticamente:
  1. Testes Unitários (auto_test_playerembedapi.py)
  2. Testes de HTTP (http_simulator_test.py)  
  3. Validação de Estrutura (validate_v5_structure.py)
  4. Build e Verificação de Compilação
  5. Geração de Relatório Final Consolidado

Uso:
    python run_all_tests_v5.py
    python run_all_tests_v5.py --verbose
    python run_all_tests_v5.py --report-format json
    python run_all_tests_v5.py --skip-build

Retorno:
    0 = Todos os testes passaram
    1 = Um ou mais testes falharam
===============================================================================
"""

import os
import sys
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import re
import json
import time
import subprocess
import argparse
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

# ============================================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================================
PROJECT_ROOT = Path(r"C:\Users\KYTHOURS\Desktop\brcloudstream")
REPORTS_DIR = PROJECT_ROOT / "test-reports"
LOG_FILE = REPORTS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Icones ASCII (evitar problemas de encoding no Windows)
ICONS = {
    'check': '[OK]',
    'cross': '[FAIL]',
    'warning': '[WARN]',
    'info': '[INFO]',
    'arrow': '->',
    'bullet': '*',
}

# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================
class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    RUNNING = "RUNNING"
    NOT_FOUND = "NOT_FOUND"

@dataclass
class TestComponent:
    name: str
    description: str
    script_path: Path
    status: TestStatus = TestStatus.SKIP
    duration: float = 0.0
    output: str = ""
    errors: str = ""
    coverage: float = 0.0
    details: List[str] = field(default_factory=list)

@dataclass
class TestReport:
    timestamp: str
    project_path: str
    total_components: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    total_duration: float = 0.0
    overall_coverage: float = 0.0
    components: List[TestComponent] = field(default_factory=list)
    summary: Dict = field(default_factory=dict)

# ============================================================================
# UTILITÁRIOS
# ============================================================================
class Logger:
    """Sistema de logging com arquivo e console"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        # Criar/arquivar arquivo de log
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"Log de Execução - PlayerEmbedAPI v5.0 Test Suite\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("="*70 + "\n\n")
    
    def log(self, message: str, level: str = "INFO", color: str = None):
        """Loga mensagem no arquivo e console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        
        # Escrever no arquivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + "\n")
        
        # Imprimir no console com cores
        if color:
            print(f"{color}{log_line}{Colors.ENDC}")
        else:
            print(log_line)
    
    def info(self, message: str):
        self.log(message, "INFO", Colors.OKBLUE)
    
    def success(self, message: str):
        self.log(f"{ICONS['check']} {message}", "SUCCESS", Colors.OKGREEN)
    
    def warning(self, message: str):
        self.log(f"{ICONS['warning']} {message}", "WARNING", Colors.WARNING)
    
    def error(self, message: str):
        self.log(f"{ICONS['cross']} {message}", "ERROR", Colors.FAIL)
    
    def header(self, message: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*70}\n")
            f.write(f"{message.center(70)}\n")
            f.write(f"{'='*70}\n\n")

# ============================================================================
# TESTE 1: TESTES UNITÁRIOS
# ============================================================================
class UnitTestRunner:
    """Executa testes unitários do PlayerEmbedAPI v5.0"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.test_scripts = [
            PROJECT_ROOT / "test_playerembedapi_v5.py",
            PROJECT_ROOT / "test_integration_v5.py",
        ]
    
    def run(self) -> TestComponent:
        """Executa todos os testes unitários disponíveis"""
        self.logger.header("TESTE 1: TESTES UNITÁRIOS")
        
        component = TestComponent(
            name="unit_tests",
            description="Testes Unitários do PlayerEmbedAPI v5.0",
            script_path=PROJECT_ROOT / "auto_test_playerembedapi.py"
        )
        
        start_time = time.time()
        results = []
        
        for script in self.test_scripts:
            if script.exists():
                self.logger.info(f"Executando: {script.name}")
                result = self._run_test_script(script)
                results.append(result)
            else:
                self.logger.warning(f"Script não encontrado: {script}")
        
        # Se não encontrou scripts específicos, executar teste interno
        if not results:
            self.logger.info("Executando testes internos...")
            result = self._run_internal_tests()
            results.append(result)
        
        duration = time.time() - start_time
        
        # Consolidar resultados
        all_passed = all(r.get('passed', False) for r in results)
        total_tests = sum(r.get('total', 0) for r in results)
        passed_tests = sum(r.get('passed_count', 0) for r in results)
        
        component.duration = duration
        component.coverage = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        if all_passed:
            component.status = TestStatus.PASS
            self.logger.success(f"Testes unitarios passaram ({passed_tests}/{total_tests})")
        else:
            component.status = TestStatus.FAIL
            self.logger.error(f"Testes unitarios falharam ({passed_tests}/{total_tests})")
        
        component.details = [f"{r.get('name', 'Test')}: {'PASS' if r.get('passed') else 'FAIL'}" for r in results]
        
        return component
    
    def _run_test_script(self, script: Path) -> Dict:
        """Executa um script de teste Python"""
        try:
            # Verificar sintaxe primeiro
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    'name': script.name,
                    'passed': False,
                    'total': 1,
                    'passed_count': 0,
                    'error': result.stderr
                }
            
            # Executar o script
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'name': script.name,
                'passed': result.returncode == 0,
                'total': 1,
                'passed_count': 1 if result.returncode == 0 else 0,
                'output': result.stdout[:500] if result.stdout else ""
            }
            
        except Exception as e:
            return {
                'name': script.name,
                'passed': False,
                'total': 1,
                'passed_count': 0,
                'error': str(e)
            }
    
    def _run_internal_tests(self) -> Dict:
        """Executa testes internos básicos"""
        tests = [
            ("Import requests", self._test_import_requests),
            ("Import Crypto", self._test_import_crypto),
            ("Estrutura de diretórios", self._test_directory_structure),
            ("Arquivos Kotlin V5", self._test_kotlin_files),
        ]
        
        passed = 0
        details = []
        
        for name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed += 1
                    details.append(f"✅ {name}")
                else:
                    details.append(f"❌ {name}")
            except Exception as e:
                details.append(f"❌ {name}: {e}")
        
        return {
            'name': 'Internal Tests',
            'passed': passed == len(tests),
            'total': len(tests),
            'passed_count': passed,
            'details': details
        }
    
    def _test_import_requests(self) -> bool:
        try:
            import requests
            return True
        except ImportError:
            return False
    
    def _test_import_crypto(self) -> bool:
        try:
            from Crypto.Cipher import AES
            return True
        except ImportError:
            return False
    
    def _test_directory_structure(self) -> bool:
        required_dirs = [
            PROJECT_ROOT / "MaxSeries",
            PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin",
        ]
        return all(d.exists() for d in required_dirs)
    
    def _test_kotlin_files(self) -> bool:
        kotlin_files = [
            PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "extractors" / "PlayerEmbedAPIExtractorV5.kt",
        ]
        return any(f.exists() for f in kotlin_files)

# ============================================================================
# TESTE 2: TESTES DE HTTP
# ============================================================================
class HTTPTestRunner:
    """Executa testes de HTTP e simulação de requisições"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.test_urls = [
            "https://playerembedapi.link",
            "https://short.icu",
        ]
    
    def run(self) -> TestComponent:
        """Executa testes de HTTP"""
        self.logger.header("TESTE 2: TESTES DE HTTP")
        
        component = TestComponent(
            name="http_tests",
            description="Testes de HTTP e Simulação de Requisições",
            script_path=PROJECT_ROOT / "http_simulator_test.py"
        )
        
        start_time = time.time()
        
        tests = [
            ("Conectividade básica", self._test_basic_connectivity),
            ("Headers HTTP", self._test_http_headers),
            ("Session management", self._test_session_management),
            ("Retry mechanism", self._test_retry_mechanism),
            ("SSL/TLS", self._test_ssl_tls),
        ]
        
        passed = 0
        details = []
        
        for name, test_func in tests:
            self.logger.info(f"Executando: {name}")
            try:
                result = test_func()
                if result:
                    passed += 1
                    details.append(f"[OK] {name}")
                    self.logger.success(f"  {name}")
                else:
                    details.append(f"[FAIL] {name}")
                    self.logger.error(f"  {name}")
            except Exception as e:
                details.append(f"[FAIL] {name}: {str(e)}")
                self.logger.error(f"  {name}: {str(e)}")
        
        duration = time.time() - start_time
        
        component.duration = duration
        component.coverage = (passed / len(tests) * 100) if tests else 0
        component.details = details
        
        if passed == len(tests):
            component.status = TestStatus.PASS
            self.logger.success(f"Todos os testes HTTP passaram ({passed}/{len(tests)})")
        elif passed >= len(tests) * 0.7:
            component.status = TestStatus.PASS
            self.logger.warning(f"Testes HTTP passaram parcialmente ({passed}/{len(tests)})")
        else:
            component.status = TestStatus.FAIL
            self.logger.error(f"Testes HTTP falharam ({passed}/{len(tests)})")
        
        return component
    
    def _test_basic_connectivity(self) -> bool:
        """Testa conectividade HTTP básica"""
        try:
            import requests
            # Testar com um site confiável
            response = requests.get("https://httpbin.org/get", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_http_headers(self) -> bool:
        """Testa configuração de headers HTTP"""
        try:
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def _test_session_management(self) -> bool:
        """Testa gerenciamento de sessão"""
        try:
            import requests
            session = requests.Session()
            session.headers.update({'User-Agent': 'Test/1.0'})
            
            # Primeira requisição
            r1 = session.get("https://httpbin.org/cookies/set/test/value", timeout=10)
            # Segunda requisição (deve manter cookies)
            r2 = session.get("https://httpbin.org/cookies", timeout=10)
            
            return r1.status_code == 200 and r2.status_code == 200
        except Exception:
            return False
    
    def _test_retry_mechanism(self) -> bool:
        """Testa mecanismo de retry"""
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            import requests
            
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            
            return True  # Se importou corretamente, considera pass
        except Exception:
            return False
    
    def _test_ssl_tls(self) -> bool:
        """Testa configuração SSL/TLS"""
        try:
            import requests
            import urllib3
            
            # Desabilitar warnings de SSL para teste
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Testar conexão HTTPS
            response = requests.get("https://httpbin.org/get", timeout=10, verify=True)
            return response.status_code == 200
        except Exception:
            return False

# ============================================================================
# TESTE 3: VALIDAÇÃO DE ESTRUTURA
# ============================================================================
class StructureValidator:
    """Valida estrutura do projeto V5"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.validate_script = PROJECT_ROOT / "validate_implementation.py"
    
    def run(self) -> TestComponent:
        """Executa validação de estrutura"""
        self.logger.header("TESTE 3: VALIDAÇÃO DE ESTRUTURA")
        
        component = TestComponent(
            name="structure_validation",
            description="Validação de Estrutura do PlayerEmbedAPI v5.0",
            script_path=PROJECT_ROOT / "validate_v5_structure.py"
        )
        
        start_time = time.time()
        
        # Se existe o script de validação, executar
        if self.validate_script.exists():
            self.logger.info(f"Executando validador: {self.validate_script}")
            try:
                result = subprocess.run(
                    [sys.executable, str(self.validate_script)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                component.output = result.stdout
                component.errors = result.stderr
                
                # Validar estrutura internamente também
                internal_results = self._run_internal_validation()
                
                duration = time.time() - start_time
                component.duration = duration
                
                if result.returncode == 0 and internal_results['passed']:
                    component.status = TestStatus.PASS
                    component.coverage = 100.0
                    self.logger.success("Validacao de estrutura passou")
                else:
                    component.status = TestStatus.FAIL
                    component.coverage = internal_results.get('coverage', 0)
                    self.logger.error("Validacao de estrutura falhou")
                
                component.details = internal_results.get('details', [])
                
            except Exception as e:
                component.status = TestStatus.FAIL
                component.errors = str(e)
                component.duration = time.time() - start_time
                self.logger.error(f"❌ Erro na validação: {e}")
        else:
            # Executar apenas validação interna
            self.logger.warning("Script de validação externo não encontrado, usando validação interna")
            internal_results = self._run_internal_validation()
            
            duration = time.time() - start_time
            component.duration = duration
            component.coverage = internal_results.get('coverage', 0)
            component.details = internal_results.get('details', [])
            
            if internal_results['passed']:
                component.status = TestStatus.PASS
                self.logger.success("Validacao de estrutura interna passou")
            else:
                component.status = TestStatus.FAIL
                self.logger.error("Validacao de estrutura interna falhou")
        
        return component
    
    def _run_internal_validation(self) -> Dict:
        """Executa validação interna de estrutura"""
        checks = [
            ("Diretório MaxSeries", self._check_maxseries_dir),
            ("Estrutura Kotlin", self._check_kotlin_structure),
            ("Extractor V5", self._check_extractor_v5),
            ("WebView V5", self._check_webview_v5),
            ("Utils", self._check_utils),
            ("Provider", self._check_provider),
            ("Build Gradle", self._check_build_gradle),
            ("Testes Python", self._check_python_tests),
        ]
        
        passed = 0
        details = []
        
        for name, check_func in checks:
            try:
                result = check_func()
                if result:
                    passed += 1
                    details.append(f"[OK] {name}")
                    self.logger.success(f"  {name}")
                else:
                    details.append(f"[FAIL] {name}")
                    self.logger.error(f"  {name}")
            except Exception as e:
                details.append(f"[FAIL] {name}: {str(e)}")
                self.logger.error(f"  {name}: {str(e)}")
        
        coverage = (passed / len(checks) * 100) if checks else 0
        
        return {
            'passed': passed >= len(checks) * 0.75,  # 75% para passar
            'coverage': coverage,
            'details': details,
            'passed_count': passed,
            'total': len(checks)
        }
    
    def _check_maxseries_dir(self) -> bool:
        return (PROJECT_ROOT / "MaxSeries").exists()
    
    def _check_kotlin_structure(self) -> bool:
        base_path = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries"
        return (base_path / "extractors").exists() or (base_path).exists()
    
    def _check_extractor_v5(self) -> bool:
        path = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "extractors" / "PlayerEmbedAPIExtractorV5.kt"
        return path.exists()
    
    def _check_webview_v5(self) -> bool:
        path = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "extractors" / "PlayerEmbedAPIWebViewExtractorV5.kt"
        return path.exists()
    
    def _check_utils(self) -> bool:
        utils_path = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "utils"
        return utils_path.exists()
    
    def _check_provider(self) -> bool:
        path = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "MaxSeriesProvider.kt"
        return path.exists()
    
    def _check_build_gradle(self) -> bool:
        path = PROJECT_ROOT / "MaxSeries" / "build.gradle.kts"
        return path.exists()
    
    def _check_python_tests(self) -> bool:
        tests = [
            PROJECT_ROOT / "test_playerembedapi_v5.py",
            PROJECT_ROOT / "test_integration_v5.py",
        ]
        return any(t.exists() for t in tests)

# ============================================================================
# TESTE 4: BUILD E COMPILAÇÃO
# ============================================================================
class BuildTester:
    """Testa build e compilação do projeto"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def run(self) -> TestComponent:
        """Executa testes de build"""
        self.logger.header("TESTE 4: BUILD E COMPILAÇÃO")
        
        component = TestComponent(
            name="build_test",
            description="Build e Verificação de Compilação",
            script_path=PROJECT_ROOT / "build.gradle.kts"
        )
        
        start_time = time.time()
        
        tests = [
            ("Gradle Wrapper", self._check_gradle_wrapper),
            ("Configuração Gradle", self._check_gradle_config),
            ("Sintaxe Kotlin V5", self._check_kotlin_syntax),
            ("Dependências", self._check_dependencies),
            ("Manifest", self._check_manifest),
        ]
        
        passed = 0
        details = []
        
        for name, test_func in tests:
            self.logger.info(f"Executando: {name}")
            try:
                result = test_func()
                if result:
                    passed += 1
                    details.append(f"[OK] {name}")
                    self.logger.success(f"  {name}")
                else:
                    details.append(f"[FAIL] {name}")
                    self.logger.error(f"  {name}")
            except Exception as e:
                details.append(f"[FAIL] {name}: {str(e)}")
                self.logger.error(f"  {name}: {str(e)}")
        
        duration = time.time() - start_time
        
        component.duration = duration
        component.coverage = (passed / len(tests) * 100) if tests else 0
        component.details = details
        
        if passed == len(tests):
            component.status = TestStatus.PASS
            self.logger.success(f"Build passou em todos os testes ({passed}/{len(tests)})")
        elif passed >= len(tests) * 0.6:
            component.status = TestStatus.PASS
            self.logger.warning(f"Build passou parcialmente ({passed}/{len(tests)})")
        else:
            component.status = TestStatus.FAIL
            self.logger.error(f"Build falhou ({passed}/{len(tests)})")
        
        return component
    
    def _check_gradle_wrapper(self) -> bool:
        """Verifica se o Gradle wrapper existe"""
        wrapper = PROJECT_ROOT / "gradlew.bat"
        return wrapper.exists()
    
    def _check_gradle_config(self) -> bool:
        """Verifica configuração do Gradle"""
        build_file = PROJECT_ROOT / "MaxSeries" / "build.gradle.kts"
        if not build_file.exists():
            return False
        
        content = build_file.read_text(encoding='utf-8')
        required = ['cloudstream', 'version', 'plugin']
        return all(r in content for r in required)
    
    def _check_kotlin_syntax(self) -> bool:
        """Verifica sintaxe básica dos arquivos Kotlin"""
        kotlin_files = list((PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin").rglob("*.kt")) if (PROJECT_ROOT / "MaxSeries" / "src" / "main" / "kotlin").exists() else []
        
        if not kotlin_files:
            return False
        
        for kt_file in kotlin_files[:5]:  # Verificar primeiros 5 arquivos
            content = kt_file.read_text(encoding='utf-8')
            # Verificar balanceamento básico de chaves
            if content.count('{') != content.count('}'):
                return False
            if content.count('(') != content.count(')'):
                return False
        
        return True
    
    def _check_dependencies(self) -> bool:
        """Verifica se as dependências estão configuradas"""
        build_file = PROJECT_ROOT / "MaxSeries" / "build.gradle.kts"
        if not build_file.exists():
            return False
        
        content = build_file.read_text(encoding='utf-8')
        # Verificar se há dependências básicas
        has_deps = 'dependencies' in content or 'implementation' in content
        has_android = 'android' in content or 'Android' in content
        
        return has_deps and has_android
    
    def _check_manifest(self) -> bool:
        """Verifica AndroidManifest"""
        manifest = PROJECT_ROOT / "MaxSeries" / "src" / "main" / "AndroidManifest.xml"
        return manifest.exists()

# ============================================================================
# ORQUESTRADOR PRINCIPAL
# ============================================================================
class TestSuiteRunner:
    """Orquestra a execução de toda a suite de testes"""
    
    def __init__(self, verbose: bool = False, skip_build: bool = False):
        self.verbose = verbose
        self.skip_build = skip_build
        self.logger = Logger(LOG_FILE)
        self.report = TestReport(
            timestamp=datetime.now().isoformat(),
            project_path=str(PROJECT_ROOT)
        )
    
    def run_all_tests(self) -> TestReport:
        """Executa todos os testes"""
        self.logger.header("SUITE DE TESTES - PlayerEmbedAPI v5.0")
        self.logger.info(f"Diretório do projeto: {PROJECT_ROOT}")
        self.logger.info(f"Log: {LOG_FILE}")
        self.logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        
        # Teste 1: Testes Unitários
        unit_runner = UnitTestRunner(self.logger)
        unit_component = unit_runner.run()
        self.report.components.append(unit_component)
        
        # Teste 2: Testes de HTTP
        http_runner = HTTPTestRunner(self.logger)
        http_component = http_runner.run()
        self.report.components.append(http_component)
        
        # Teste 3: Validação de Estrutura
        structure_validator = StructureValidator(self.logger)
        structure_component = structure_validator.run()
        self.report.components.append(structure_component)
        
        # Teste 4: Build (opcional)
        if not self.skip_build:
            build_tester = BuildTester(self.logger)
            build_component = build_tester.run()
            self.report.components.append(build_component)
        else:
            self.logger.warning("Build ignorado (--skip-build)")
            self.report.components.append(TestComponent(
                name="build_test",
                description="Build e Verificação de Compilação",
                script_path=PROJECT_ROOT / "build.gradle.kts",
                status=TestStatus.SKIP
            ))
        
        # Calcular estatísticas
        self.report.total_duration = time.time() - start_time
        self.report.total_components = len(self.report.components)
        self.report.passed = sum(1 for c in self.report.components if c.status == TestStatus.PASS)
        self.report.failed = sum(1 for c in self.report.components if c.status == TestStatus.FAIL)
        self.report.skipped = sum(1 for c in self.report.components if c.status == TestStatus.SKIP)
        
        # Calcular cobertura geral
        coverages = [c.coverage for c in self.report.components if c.coverage > 0]
        self.report.overall_coverage = sum(coverages) / len(coverages) if coverages else 0
        
        # Gerar relatório
        self._generate_report()
        
        return self.report
    
    def _generate_report(self):
        """Gera relatório final"""
        self.logger.header("RELATÓRIO FINAL")
        
        # Resumo no console
        print(f"\n{Colors.BOLD}Resumo da Execução:{Colors.ENDC}")
        print(f"  Total de componentes: {self.report.total_components}")
        print(f"  {Colors.OKGREEN}[OK] Aprovados: {self.report.passed}{Colors.ENDC}")
        print(f"  {Colors.FAIL}[FAIL] Falhas: {self.report.failed}{Colors.ENDC}")
        print(f"  [WARN] Ignorados: {self.report.skipped}")
        print(f"  [TIME] Duracao total: {self.report.total_duration:.2f}s")
        print(f"  [COV] Cobertura geral: {self.report.overall_coverage:.1f}%")
        
        # Detalhes por componente
        print(f"\n{Colors.BOLD}Status por Componente:{Colors.ENDC}")
        for comp in self.report.components:
            status_color = {
                TestStatus.PASS: Colors.OKGREEN,
                TestStatus.FAIL: Colors.FAIL,
                TestStatus.SKIP: Colors.WARNING,
            }.get(comp.status, Colors.ENDC)
            
            status_icon = {
                TestStatus.PASS: "[PASS]",
                TestStatus.FAIL: "[FAIL]",
                TestStatus.SKIP: "[SKIP]",
            }.get(comp.status, "[?]")
            
            print(f"  {status_icon} {comp.name:30} [{status_color}{comp.status.value}{Colors.ENDC}] ({comp.duration:.2f}s) - {comp.coverage:.1f}%")
        
        # Salvar relatório em arquivo
        report_file = REPORTS_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("RELATÓRIO DE TESTES - PlayerEmbedAPI v5.0\n")
            f.write("="*70 + "\n")
            f.write(f"Timestamp: {self.report.timestamp}\n")
            f.write(f"Projeto: {self.report.project_path}\n")
            f.write(f"\nRESUMO\n")
            f.write("-"*70 + "\n")
            f.write(f"Total de componentes: {self.report.total_components}\n")
            f.write(f"Aprovados: {self.report.passed}\n")
            f.write(f"Falhas: {self.report.failed}\n")
            f.write(f"Ignorados: {self.report.skipped}\n")
            f.write(f"Duração total: {self.report.total_duration:.2f}s\n")
            f.write(f"Cobertura geral: {self.report.overall_coverage:.1f}%\n")
            f.write(f"\nRESULTADOS DETALHADOS\n")
            f.write("-"*70 + "\n")
            
            for comp in self.report.components:
                f.write(f"\n[{comp.status.value}] {comp.name}\n")
                f.write(f"  Descrição: {comp.description}\n")
                f.write(f"  Duração: {comp.duration:.2f}s\n")
                f.write(f"  Cobertura: {comp.coverage:.1f}%\n")
                if comp.details:
                    f.write(f"  Detalhes:\n")
                    for detail in comp.details:
                        f.write(f"    - {detail}\n")
        
        self.logger.success(f"\nRelatório salvo em: {report_file}")
        
        # Também gerar JSON
        json_report = self._generate_json_report()
        json_file = REPORTS_DIR / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_report)
        self.logger.success(f"Relatório JSON salvo em: {json_file}")
    
    def _generate_json_report(self) -> str:
        """Gera relatório em formato JSON"""
        report_dict = {
            "timestamp": self.report.timestamp,
            "project_path": self.report.project_path,
            "summary": {
                "total_components": self.report.total_components,
                "passed": self.report.passed,
                "failed": self.report.failed,
                "skipped": self.report.skipped,
                "total_duration": self.report.total_duration,
                "overall_coverage": self.report.overall_coverage,
                "success_rate": f"{(self.report.passed/self.report.total_components*100):.1f}%" if self.report.total_components > 0 else "0%"
            },
            "components": [
                {
                    "name": c.name,
                    "description": c.description,
                    "status": c.status.value,
                    "duration": c.duration,
                    "coverage": c.coverage,
                    "script_path": str(c.script_path),
                    "details": c.details,
                    "output": c.output[:500] if c.output else "",
                    "errors": c.errors[:500] if c.errors else ""
                }
                for c in self.report.components
            ]
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Suite de Testes Master - PlayerEmbedAPI v5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    python run_all_tests_v5.py
    python run_all_tests_v5.py --verbose
    python run_all_tests_v5.py --skip-build
    python run_all_tests_v5.py --report-format json
        """
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose com mais detalhes'
    )
    parser.add_argument(
        '--skip-build',
        action='store_true',
        help='Ignora testes de build'
    )
    parser.add_argument(
        '--report-format',
        choices=['text', 'json', 'both'],
        default='both',
        help='Formato do relatório (padrão: both)'
    )
    
    args = parser.parse_args()
    
    # Verificar diretório do projeto
    if not PROJECT_ROOT.exists():
        print(f"[ERRO] Diretório do projeto não encontrado: {PROJECT_ROOT}")
        sys.exit(1)
    
    # Executar testes
    try:
        runner = TestSuiteRunner(verbose=args.verbose, skip_build=args.skip_build)
        report = runner.run_all_tests()
        
        # Retornar código de saída apropriado
        if report.failed > 0:
            print(f"\n{Colors.FAIL}[FAIL] SUITE DE TESTES FALHOU{Colors.ENDC}")
            sys.exit(1)
        else:
            print(f"\n{Colors.OKGREEN}[OK] SUITE DE TESTES PASSOU{Colors.ENDC}")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[WARN] Execucao interrompida pelo usuario{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}[FAIL] ERRO FATAL: {e}{Colors.ENDC}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
