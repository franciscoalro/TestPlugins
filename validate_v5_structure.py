#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação - PlayerEmbedAPI v5.0
Valida se a implementação do PlayerEmbedAPI v5.0 está correta

Autor: Assistente IA
Data: 31/01/2026
Versão: 1.0.0
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class ValidationStatus(Enum):
    PASS = " PASS"
    FAIL = " FAIL"
    WARN = "️ WARN"
    SKIP = "⏭️ SKIP"
    INFO = "ℹ️ INFO"


@dataclass
class ValidationResult:
    name: str
    status: ValidationStatus
    message: str
    details: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        result = f"{self.status.value} | {self.name}"
        if self.message:
            result += f"\n   └─ {self.message}"
        for detail in self.details:
            result += f"\n      • {detail}"
        return result


class PlayerEmbedAPIV5Validator:
    """Validador completo da implementação PlayerEmbedAPI v5.0"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: List[ValidationResult] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Caminhos importantes
        self.maxseries_path = self.project_path / "MaxSeries"
        self.extractors_path = self.maxseries_path / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "extractors"
        self.utils_path = self.maxseries_path / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "utils"
        self.test_path = self.maxseries_path / "src" / "test" / "kotlin" / "com" / "franciscoalro" / "maxseries"
        
        # Arquivos V5 esperados
        self.v5_files = {
            "extractor": self.extractors_path / "PlayerEmbedAPIExtractorV5.kt",
            "webview": self.extractors_path / "PlayerEmbedAPIWebViewExtractorV5.kt",
            "test": self.test_path / "PlayerEmbedAPIV5Test.kt",
        }
        
        # Arquivos utilitários necessários
        self.utils_files = {
            "link_decryptor": self.utils_path / "LinkDecryptor.kt",
            "quality_detector": self.utils_path / "QualityDetector.kt",
            "regex_patterns": self.utils_path / "RegexPatterns.kt",
            "video_cache": self.utils_path / "VideoUrlCache.kt",
        }
        
        # Arquivos de configuração
        self.config_files = {
            "root_build": self.project_path / "build.gradle.kts",
            "module_build": self.maxseries_path / "build.gradle.kts",
            "provider": self.maxseries_path / "src" / "main" / "kotlin" / "com" / "franciscoalro" / "maxseries" / "MaxSeriesProvider.kt",
        }
    
    def validate_all(self) -> Tuple[int, int, int]:
        """Executa todas as validações e retorna (pass, fail, warn)"""
        print("=" * 80)
        print(" VALIDAÇÃO DO PLAYEREMBEDAPI v5.0")
        print("=" * 80)
        print(f" Projeto: {self.project_path}")
        print(f" Data: 31/01/2026")
        print("-" * 80)
        
        # 1. Validar estrutura de arquivos
        self._validate_file_structure()
        
        # 2. Validar funções principais
        self._validate_main_functions()
        
        # 3. Validar constantes e regex
        self._validate_constants_and_regex()
        
        # 4. Verificar ausência de código v4.x
        self._validate_no_v4_references()
        
        # 5. Validar dependências
        self._validate_dependencies()
        
        # 6. Validar build.gradle.kts
        self._validate_build_gradle()
        
        # 7. Validar testes
        self._validate_tests()
        
        # 8. Validar segurança
        self._validate_security()
        
        # 9. Validar performance
        self._validate_performance()
        
        # 10. Validar provider
        self._validate_provider_integration()
        
        # Exibir relatório
        self._print_report()
        
        return self._count_results()
    
    def _add_result(self, name: str, status: ValidationStatus, message: str = "", details: List[str] = None):
        """Adiciona resultado de validação"""
        result = ValidationResult(
            name=name,
            status=status,
            message=message,
            details=details or []
        )
        self.results.append(result)
        print(result)
        print()
    
    def _read_file(self, path: Path) -> Optional[str]:
        """Lê conteúdo de arquivo com tratamento de erro"""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            return None
    
    def _file_exists(self, path: Path) -> bool:
        """Verifica se arquivo existe"""
        return path.exists() and path.is_file()
    
    def _validate_file_structure(self):
        """Valida se todos os arquivos V5 existem"""
        print("\n" + "─" * 80)
        print(" 1. VALIDAÇÃO DA ESTRUTURA DE ARQUIVOS")
        print("─" * 80)
        
        all_files_exist = True
        missing_files = []
        found_files = []
        
        # Verificar arquivos V5
        for name, path in self.v5_files.items():
            if self._file_exists(path):
                found_files.append(f"{name}: {path.name}")
            else:
                missing_files.append(f"{name}: {path}")
                all_files_exist = False
        
        # Verificar arquivos utilitários
        for name, path in self.utils_files.items():
            if self._file_exists(path):
                found_files.append(f"{name}: {path.name}")
            else:
                missing_files.append(f"{name}: {path}")
                all_files_exist = False
        
        if all_files_exist:
            self._add_result(
                "Estrutura de Arquivos V5",
                ValidationStatus.PASS,
                "Todos os arquivos necessários existem",
                found_files
            )
        else:
            self._add_result(
                "Estrutura de Arquivos V5",
                ValidationStatus.FAIL,
                f"Faltando {len(missing_files)} arquivo(s)",
                missing_files
            )
    
    def _validate_main_functions(self):
        """Valida se as funções principais estão implementadas"""
        print("\n" + "─" * 80)
        print(" 2. VALIDAÇÃO DAS FUNÇÕES PRINCIPAIS")
        print("─" * 80)
        
        extractor_content = self._read_file(self.v5_files["extractor"])
        if not extractor_content:
            self._add_result(
                "Funções Principais",
                ValidationStatus.FAIL,
                "Não foi possível ler PlayerEmbedAPIExtractorV5.kt"
            )
            return
        
        required_functions = {
            "getUrl": "Função principal de extração",
            "extractViaApi": "Estratégia 1: API (base64 + AES-CTR)",
            "extractViaShortIcu": "Estratégia 2: ShortIcu",
            "extractViaRegexFallback": "Estratégia 3: Regex Fallback",
            "extractViaWebView": "Estratégia 4: WebView",
            "processBase64Data": "Processamento de base64",
            "extractUrlsFromDecrypted": "Extração de URLs decriptadas",
            "findBase64Datas": "Busca de base64 no HTML",
            "extractShortIcuUrl": "Extração de URL short.icu",
            "extractVideoUrlFromHtml": "Extração de URL de vídeo do HTML",
            "isValidVideoUrl": "Validação de URL de vídeo",
            "processJsonStringToBytes": "Processamento de JSON escapado",
        }
        
        found_functions = []
        missing_functions = []
        
        for func_name, description in required_functions.items():
            # Buscar por declaração de função
            pattern = rf"(suspend\s+)?fun\s+{re.escape(func_name)}\s*\("
            if re.search(pattern, extractor_content):
                found_functions.append(f" {func_name}: {description}")
            else:
                missing_functions.append(f" {func_name}: {description}")
        
        if not missing_functions:
            self._add_result(
                "Funções Principais",
                ValidationStatus.PASS,
                f"Todas as {len(found_functions)} funções encontradas",
                found_functions
            )
        else:
            self._add_result(
                "Funções Principais",
                ValidationStatus.FAIL,
                f"{len(missing_functions)} função(ões) não encontrada(s)",
                missing_functions + found_functions
            )
    
    def _validate_constants_and_regex(self):
        """Valida se as constantes e regex estão definidos"""
        print("\n" + "─" * 80)
        print(" 3. VALIDAÇÃO DE CONSTANTES E REGEX")
        print("─" * 80)
        
        extractor_content = self._read_file(self.v5_files["extractor"])
        if not extractor_content:
            self._add_result(
                "Constantes e Regex",
                ValidationStatus.FAIL,
                "Não foi possível ler o extractor V5"
            )
            return
        
        required_constants = {
            "TAG": "Tag de logging",
            "USER_AGENT": "User-Agent para requisições",
            "EXTRACTION_TIMEOUT_MS": "Timeout de extração",
            "DATA_SOURCE_PATTERN": "Pattern data-source",
            "DATA_SRC_PATTERN": "Pattern data-src",
            "IFRAME_SRC_PATTERN": "Pattern iframe src",
            "BASE64_PATTERNS": "Lista de patterns base64",
            "VIDEO_URL_PATTERNS": "Lista de patterns de URL de vídeo",
            "RES_ID_QUALITY": "Mapeamento de res_id para qualidade",
            "ALLOWED_VIDEO_DOMAINS": "Domínios permitidos",
        }
        
        found_constants = []
        missing_constants = []
        
        for const_name, description in required_constants.items():
            if const_name in extractor_content:
                found_constants.append(f" {const_name}: {description}")
            else:
                missing_constants.append(f" {const_name}: {description}")
        
        # Verificar companion object
        has_companion = "companion object" in extractor_content
        
        if not missing_constants and has_companion:
            self._add_result(
                "Constantes e Regex",
                ValidationStatus.PASS,
                f"Todas as {len(found_constants)} constantes encontradas no companion object",
                found_constants
            )
        else:
            details = missing_constants + found_constants
            if not has_companion:
                details.insert(0, " companion object não encontrado")
            self._add_result(
                "Constantes e Regex",
                ValidationStatus.FAIL,
                f"{len(missing_constants)} constante(s) não encontrada(s)",
                details
            )
    
    def _validate_no_v4_references(self):
        """Verifica se não há referências ao código antigo v4.x"""
        print("\n" + "─" * 80)
        print(" 4. VALIDAÇÃO DE AUSÊNCIA DE CÓDIGO v4.x")
        print("─" * 80)
        
        provider_content = self._read_file(self.config_files["provider"])
        if not provider_content:
            self._add_result(
                "Ausência de Código v4.x",
                ValidationStatus.FAIL,
                "Não foi possível ler MaxSeriesProvider.kt"
            )
            return
        
        # Padrões que NÃO devem existir (código antigo)
        forbidden_patterns = {
            r"PlayerEmbedAPIExtractor\s*\(": "Chamada direta ao extractor v4 antigo",
            r"handler\?\.proceed\(\)": "Ignora erros SSL (inseguro)",
            r"GlobalScope\.launch": "Uso de GlobalScope (memory leak)",
            r"Log\.d\s*\(\s*\"[^\"]*\",\s*\"[^\"]*preKey": "Logging de chave sensível",
            r"Log\.d\s*\(\s*\"[^\"]*\",\s*\"[^\"]*md5Hash": "Logging de hash sensível",
        }
        
        found_issues = []
        
        for pattern, description in forbidden_patterns.items():
            if re.search(pattern, provider_content, re.IGNORECASE):
                found_issues.append(f" {description}")
        
        # Verificar se importa o V5
        imports_v5 = "PlayerEmbedAPIExtractorV5" in provider_content
        
        if not found_issues and imports_v5:
            self._add_result(
                "Ausência de Código v4.x",
                ValidationStatus.PASS,
                "Nenhuma referência a código antigo encontrada; PlayerEmbedAPIExtractorV5 importado",
                [" Usando PlayerEmbedAPIExtractorV5"]
            )
        elif found_issues:
            self._add_result(
                "Ausência de Código v4.x",
                ValidationStatus.FAIL,
                f"{len(found_issues)} referência(s) a código antigo encontrada(s)",
                found_issues
            )
        else:
            self._add_result(
                "Ausência de Código v4.x",
                ValidationStatus.WARN,
                "PlayerEmbedAPIExtractorV5 não encontrado nos imports",
                [" Verifique se o provider está atualizado para v5.0"]
            )
    
    def _validate_dependencies(self):
        """Valida se as dependências estão corretas"""
        print("\n" + "─" * 80)
        print(" 5. VALIDAÇÃO DE DEPENDÊNCIAS")
        print("─" * 80)
        
        root_build_content = self._read_file(self.config_files["root_build"])
        if not root_build_content:
            self._add_result(
                "Dependências",
                ValidationStatus.FAIL,
                "Não foi possível ler build.gradle.kts raiz"
            )
            return
        
        required_deps = {
            "kotlin-stdlib": "Biblioteca Kotlin",
            "jackson-module-kotlin": "Serialização JSON",
            "jackson-databind": "Processamento JSON",
            "okhttp": "Cliente HTTP",
            "jsoup": "Parsing HTML",
            "webkit": "WebView",
            "kotlinx-coroutines-android": "Coroutines",
        }
        
        found_deps = []
        missing_deps = []
        
        for dep_name, description in required_deps.items():
            if dep_name in root_build_content:
                found_deps.append(f" {dep_name}: {description}")
            else:
                missing_deps.append(f" {dep_name}: {description}")
        
        # Verificar versões mínimas
        version_checks = [
            (r"kotlin-gradle-plugin:(\d+\.\d+)", "2.3", "Kotlin Gradle Plugin"),
            (r"okhttp:(\d+\.\d+)", "4.12", "OkHttp"),
            (r"jsoup:(\d+\.\d+)", "1.19", "JSoup"),
        ]
        
        version_issues = []
        for pattern, min_version, name in version_checks:
            match = re.search(pattern, root_build_content)
            if match:
                current_version = match.group(1)
                if current_version < min_version:
                    version_issues.append(f" {name}: {current_version} (recomendado >= {min_version})")
        
        if not missing_deps:
            details = found_deps
            if version_issues:
                details.extend(version_issues)
                status = ValidationStatus.WARN
                message = "Dependências OK, mas há avisos de versão"
            else:
                status = ValidationStatus.PASS
                message = f"Todas as {len(found_deps)} dependências encontradas"
            
            self._add_result(
                "Dependências",
                status,
                message,
                details
            )
        else:
            self._add_result(
                "Dependências",
                ValidationStatus.FAIL,
                f"{len(missing_deps)} dependência(s) não encontrada(s)",
                missing_deps + found_deps
            )
    
    def _validate_build_gradle(self):
        """Valida se o build.gradle.kts está atualizado"""
        print("\n" + "─" * 80)
        print(" 6. VALIDAÇÃO DO BUILD.GRADLE.KTS")
        print("─" * 80)
        
        module_build_content = self._read_file(self.config_files["module_build"])
        if not module_build_content:
            self._add_result(
                "Build Gradle",
                ValidationStatus.FAIL,
                "Não foi possível ler build.gradle.kts do módulo"
            )
            return
        
        checks = []
        
        # Verificar versão
        version_match = re.search(r"version\s*=\s*(\d+)", module_build_content)
        if version_match:
            version = int(version_match.group(1))
            if version >= 253:
                checks.append(f" Versão: {version} (>= 253 requerido para v5.0)")
            else:
                checks.append(f" Versão: {version} (deve ser >= 253)")
        else:
            checks.append(" Versão não encontrada")
        
        # Verificar descrição
        if "v5.0" in module_build_content or "V5.0" in module_build_content:
            checks.append(" Descrição menciona v5.0")
        else:
            checks.append(" Descrição não menciona v5.0 explicitamente")
        
        # Verificar status
        if "status = 1" in module_build_content:
            checks.append(" Status = 1 (ativo)")
        else:
            checks.append(" Status não está ativo")
        
        # Verificar configurações
        if "cloudstream {" in module_build_content:
            checks.append(" Bloco cloudstream configurado")
        else:
            checks.append(" Bloco cloudstream não encontrado")
        
        self._add_result(
            "Build Gradle",
            ValidationStatus.PASS if not any("" in c for c in checks) else ValidationStatus.WARN,
            "Configuração do módulo verificada",
            checks
        )
    
    def _validate_tests(self):
        """Valida se os testes unitários estão implementados"""
        print("\n" + "─" * 80)
        print(" 7. VALIDAÇÃO DOS TESTES")
        print("─" * 80)
        
        test_content = self._read_file(self.v5_files["test"])
        if not test_content:
            self._add_result(
                "Testes Unitários",
                ValidationStatus.FAIL,
                "Arquivo de teste PlayerEmbedAPIV5Test.kt não encontrado"
            )
            return
        
        # Contar testes
        test_methods = re.findall(r"@Test\s+fun", test_content)
        num_tests = len(test_methods)
        
        # Verificar tipos de testes
        test_types = []
        if "isValidVideoUrl" in test_content:
            test_types.append(" Validação de URLs")
        if "detectQualityFromUrl" in test_content or "detectQuality" in test_content:
            test_types.append(" Detecção de qualidade")
        if "findBase64Datas" in test_content:
            test_types.append(" Extração de base64")
        if "extractShortIcuUrl" in test_content:
            test_types.append(" Extração ShortIcu")
        if "extractVideoUrlFromHtml" in test_content:
            test_types.append(" Extração de URL de vídeo")
        if "processJsonStringToBytes" in test_content:
            test_types.append(" Processamento JSON")
        if "canHandle" in test_content:
            test_types.append(" CanHandle")
        
        if num_tests >= 10:
            self._add_result(
                "Testes Unitários",
                ValidationStatus.PASS,
                f"{num_tests} testes implementados",
                test_types
            )
        else:
            self._add_result(
                "Testes Unitários",
                ValidationStatus.WARN,
                f"Apenas {num_tests} testes (recomendado >= 10)",
                test_types
            )
    
    def _validate_security(self):
        """Valida aspectos de segurança"""
        print("\n" + "─" * 80)
        print(" 8. VALIDAÇÃO DE SEGURANÇA")
        print("─" * 80)
        
        webview_content = self._read_file(self.v5_files["webview"])
        extractor_content = self._read_file(self.v5_files["extractor"])
        
        security_checks = []
        
        # Verificar SSL seguro no WebView
        if webview_content:
            # Verificar se há chamada real (não em comentário)
            lines = webview_content.split('\n')
            has_proceed_call = False
            for line in lines:
                stripped = line.strip()
                # Ignorar comentários
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if stripped.startswith('/*') or stripped.startswith('*/'):
                    continue
                if 'handler?.proceed()' in line and not stripped.startswith('//'):
                    has_proceed_call = True
                    break
            
            if has_proceed_call:
                security_checks.append(" WebView chama handler?.proceed() (INSEGURO)")
            else:
                security_checks.append(" WebView NÃO ignora erros SSL")
            
            if "handler?.cancel()" in webview_content:
                security_checks.append(" WebView cancela requisições inseguras")
        
        # Verificar ausência de logging sensível
        if extractor_content:
            sensitive_patterns = ["preKey", "md5Hash", "secret", "password", "api_key"]
            has_sensitive_logging = False
            for pattern in sensitive_patterns:
                if f'Log.d(' in extractor_content and pattern in extractor_content:
                    # Verificar se está em contexto de log
                    if re.search(rf'Log\.[dwv]\s*\([^)]*{pattern}', extractor_content, re.IGNORECASE):
                        has_sensitive_logging = True
                        security_checks.append(f" Possível logging de '{pattern}'")
            
            if not has_sensitive_logging:
                security_checks.append(" Nenhum logging sensível detectado")
        
        # Verificar ALLOWED_DOMAINS
        if webview_content and "ALLOWED_DOMAINS" in webview_content:
            security_checks.append(" Domínios permitidos configurados")
        
        # Verificar validação de URLs
        if extractor_content and "isValidVideoUrl" in extractor_content:
            security_checks.append(" Validação de URLs implementada")
        
        if all("" in c for c in security_checks):
            self._add_result(
                "Segurança",
                ValidationStatus.PASS,
                "Todas as verificações de segurança passaram",
                security_checks
            )
        else:
            self._add_result(
                "Segurança",
                ValidationStatus.WARN if not any("" in c for c in security_checks) else ValidationStatus.FAIL,
                "Verificações de segurança concluídas com avisos",
                security_checks
            )
    
    def _validate_performance(self):
        """Valida aspectos de performance"""
        print("\n" + "─" * 80)
        print(" 9. VALIDAÇÃO DE PERFORMANCE")
        print("─" * 80)
        
        extractor_content = self._read_file(self.v5_files["extractor"])
        webview_content = self._read_file(self.v5_files["webview"])
        
        perf_checks = []
        
        # Verificar regex compilados em companion object
        if extractor_content:
            if "companion object" in extractor_content and "private val" in extractor_content:
                perf_checks.append(" Regex compilados em companion object")
            else:
                perf_checks.append(" Regex podem não estar otimizados")
            
            # Verificar VideoUrlCache
            if "VideoUrlCache" in extractor_content:
                perf_checks.append(" Sistema de cache implementado")
            else:
                perf_checks.append(" Cache não encontrado")
        
        # Verificar uso de CoroutineScope em vez de GlobalScope
        if webview_content:
            # Verificar se há uso real (não em comentários)
            lines = webview_content.split('\n')
            has_global_scope = False
            for line in lines:
                stripped = line.strip()
                # Ignorar comentários
                if stripped.startswith('//') or stripped.startswith('*'):
                    continue
                if 'GlobalScope' in line and not stripped.startswith('//'):
                    has_global_scope = True
                    break
            
            if has_global_scope:
                perf_checks.append(" Uso de GlobalScope detectado (memory leak)")
            else:
                perf_checks.append(" Não usa GlobalScope")
            
            if "CoroutineScope" in webview_content:
                perf_checks.append(" Usa CoroutineScope controlado")
        
        # Verificar timeout
        if extractor_content and "EXTRACTION_TIMEOUT_MS" in extractor_content:
            perf_checks.append(" Timeout configurado")
        
        self._add_result(
            "Performance",
            ValidationStatus.PASS if not any("" in c for c in perf_checks) else ValidationStatus.WARN,
            "Verificações de performance concluídas",
            perf_checks
        )
    
    def _validate_provider_integration(self):
        """Valida integração com o provider"""
        print("\n" + "─" * 80)
        print(" 10. VALIDAÇÃO DA INTEGRAÇÃO COM PROVIDER")
        print("─" * 80)
        
        provider_content = self._read_file(self.config_files["provider"])
        if not provider_content:
            self._add_result(
                "Integração com Provider",
                ValidationStatus.FAIL,
                "Não foi possível ler MaxSeriesProvider.kt"
            )
            return
        
        integration_checks = []
        
        # Verificar import do V5
        if "PlayerEmbedAPIExtractorV5" in provider_content:
            integration_checks.append(" PlayerEmbedAPIExtractorV5 importado")
        else:
            integration_checks.append(" PlayerEmbedAPIExtractorV5 NÃO importado")
        
        # Verificar versão do provider
        version_match = re.search(r'override\s+var\s+name\s*=\s*"MaxSeries\s+v(\d+)"', provider_content)
        if version_match:
            version = version_match.group(1)
            integration_checks.append(f" Versão do provider: v{version}")
        else:
            # Tentar outro padrão
            version_match2 = re.search(r'name\s*=\s*"MaxSeries[^"]*(\d{3})', provider_content)
            if version_match2:
                integration_checks.append(f" Versão do provider detectada")
        
        # Verificar menção ao v5.0 nos comentários
        if "v5.0" in provider_content or "V5.0" in provider_content or "v253" in provider_content:
            integration_checks.append(" Provider menciona v5.0 nos comentários")
        
        # Verificar extractors mencionados
        extractors = ["MegaEmbed", "PlayerThree", "PlayerEmbedAPI", "MyVidPlay", "DoodStream"]
        for ext in extractors:
            if ext in provider_content:
                integration_checks.append(f" {ext} mencionado")
        
        self._add_result(
            "Integração com Provider",
            ValidationStatus.PASS if not any("" in c for c in integration_checks) else ValidationStatus.WARN,
            "Integração verificada",
            integration_checks
        )
    
    def _print_report(self):
        """Imprime relatório final"""
        print("\n" + "=" * 80)
        print(" RELATÓRIO DE CONFORMIDADE - PLAYEREMBEDAPI v5.0")
        print("=" * 80)
        
        pass_count = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        fail_count = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warn_count = sum(1 for r in self.results if r.status == ValidationStatus.WARN)
        
        print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│                         RESUMO DAS VALIDAÇÕES                       │
├─────────────────────────────────────────────────────────────────────┤
│   PASS:  {pass_count:2d}                                                      │
│   FAIL:  {fail_count:2d}                                                      │
│  ️ WARN:  {warn_count:2d}                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  TOTAL:   {len(self.results):2d}                                                      │
└─────────────────────────────────────────────────────────────────────┘
""")
        
        # Lista de validações
        print("\n LISTA DE VALIDAÇÕES REALIZADAS:")
        print("-" * 80)
        
        validations = [
            ("1", "Estrutura de Arquivos V5", "Verifica se todos os arquivos V5 existem"),
            ("2", "Funções Principais", "Verifica se as funções principais estão implementadas"),
            ("3", "Constantes e Regex", "Verifica se constantes e regex estão definidos"),
            ("4", "Ausência de Código v4.x", "Verifica se não há referências ao código antigo"),
            ("5", "Dependências", "Verifica se as dependências estão corretas"),
            ("6", "Build Gradle", "Verifica se o build.gradle.kts está atualizado"),
            ("7", "Testes Unitários", "Verifica se os testes estão implementados"),
            ("8", "Segurança", "Verifica aspectos de segurança"),
            ("9", "Performance", "Verifica aspectos de performance"),
            ("10", "Integração com Provider", "Verifica integração com MaxSeriesProvider"),
        ]
        
        for num, name, desc in validations:
            # Encontrar resultado correspondente
            result = next((r for r in self.results if name in r.name), None)
            status = result.status.value if result else "⏭️ SKIP"
            print(f"  {num}. {status:12} │ {name:30} │ {desc}")
        
        print("\n" + "=" * 80)
        
        # Status final
        if fail_count == 0:
            if warn_count == 0:
                print(" STATUS: TODAS AS VALIDAÇÕES PASSARAM!")
                print(" A implementação do PlayerEmbedAPI v5.0 está correta e pronta para uso.")
            else:
                print(" STATUS: VALIDAÇÕES PASSARAM COM AVISOS")
                print("️ A implementação está funcional, mas há itens que merecem atenção.")
        else:
            print(" STATUS: VALIDAÇÕES FALHARAM")
            print(f" {fail_count} validação(ões) falharam. Corrija os problemas antes de prosseguir.")
        
        print("=" * 80)
    
    def _count_results(self) -> Tuple[int, int, int]:
        """Conta resultados por status"""
        pass_count = sum(1 for r in self.results if r.status == ValidationStatus.PASS)
        fail_count = sum(1 for r in self.results if r.status == ValidationStatus.FAIL)
        warn_count = sum(1 for r in self.results if r.status == ValidationStatus.WARN)
        return pass_count, fail_count, warn_count


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validador da implementação PlayerEmbedAPI v5.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python validate_v5_structure.py
  python validate_v5_structure.py --save-report
  python validate_v5_structure.py --project /caminho/do/projeto --output relatorio.txt
        """
    )
    parser.add_argument(
        "--project", "-p",
        default=r"C:\Users\KYTHOURS\Desktop\brcloudstream",
        help="Caminho do projeto (padrao: Desktop/brcloudstream)"
    )
    parser.add_argument(
        "--output", "-o",
        default="validation_report_v5.txt",
        help="Arquivo de saída para o relatório (padrão: validation_report_v5.txt)"
    )
    parser.add_argument(
        "--save-report", "-s",
        action="store_true",
        help="Salva o relatório em arquivo"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Exporta resultados em formato JSON"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.project):
        print(f" ERRO: Diretório do projeto não encontrado: {args.project}")
        sys.exit(1)
    
    # Redirecionar saída se necessário
    if args.save_report:
        import io
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
    
    # Criar validador e executar
    validator = PlayerEmbedAPIV5Validator(args.project)
    pass_count, fail_count, warn_count = validator.validate_all()
    
    # Salvar relatório
    if args.save_report:
        sys.stdout = old_stdout
        report_content = buffer.getvalue()
        output_path = os.path.join(args.project, args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f" Relatório salvo em: {output_path}")
        print(report_content)
    
    # Exportar JSON se necessário
    if args.json:
        import json
        json_data = {
            "timestamp": "2026-01-31T12:39:20",
            "project_path": args.project,
            "summary": {
                "pass": pass_count,
                "fail": fail_count,
                "warn": warn_count,
                "total": pass_count + fail_count + warn_count
            },
            "validations": [
                {
                    "name": r.name,
                    "status": r.status.name,
                    "message": r.message,
                    "details": r.details
                }
                for r in validator.results
            ]
        }
        json_path = os.path.join(args.project, "validation_report_v5.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f" Relatório JSON salvo em: {json_path}")
    
    # Retornar código de saída apropriado
    if fail_count > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
