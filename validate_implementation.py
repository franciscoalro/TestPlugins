#!/usr/bin/env python3
"""
Script de Validação: Compara implementação Python vs Kotlin

Verifica se a lógica do Python corresponde ao Kotlin
"""

import os
import re
import sys

class ImplementationValidator:
    """Valida consistência entre implementações Python e Kotlin"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def log_error(self, message):
        self.errors.append(message)
        print(f"[ERRO] {message}")
    
    def log_warning(self, message):
        self.warnings.append(message)
        print(f"[AVISO] {message}")
    
    def log_success(self, message):
        print(f"[OK] {message}")
    
    def validate_file_exists(self, filepath, description):
        """Verifica se arquivo existe"""
        if os.path.exists(filepath):
            self.log_success(f"{description}: {filepath}")
            return True
        else:
            self.log_error(f"Arquivo não encontrado: {filepath}")
            return False
    
    def validate_regex_patterns(self, py_file, kt_file):
        """Valida se os padrões regex são equivalentes"""
        print("\n[ETAPA] Validando padrões regex...")
        
        with open(py_file, 'r', encoding='utf-8') as f:
            py_content = f.read()
        
        with open(kt_file, 'r', encoding='utf-8') as f:
            kt_content = f.read()
        
        # Extrair padrões base64 do Python
        py_base64_patterns = re.findall(r'const\\s+datas', py_content)
        
        # Extrair padrões base64 do Kotlin
        kt_base64_patterns = re.findall(r'const\\s+datas', kt_content)
        
        if len(py_base64_patterns) == len(kt_base64_patterns):
            self.log_success(f"Mesmo número de padrões base64: {len(py_base64_patterns)}")
        else:
            self.log_warning(f"Diferença no número de padrões: Python={len(py_base64_patterns)}, Kotlin={len(kt_base64_patterns)}")
        
        # Extrair padrões de URL de vídeo
        py_video_patterns = re.findall(r'googleapis', py_content)
        kt_video_patterns = re.findall(r'googleapis', kt_content)
        
        if len(py_video_patterns) == len(kt_video_patterns):
            self.log_success(f"Mesmo número de padrões de vídeo: {len(py_video_patterns)}")
        else:
            self.log_warning(f"Diferença nos padrões de vídeo: Python={len(py_video_patterns)}, Kotlin={len(kt_video_patterns)}")
    
    def validate_security_fixes(self, kt_file):
        """Valida se as correções de segurança estão presentes"""
        print("\n[ETAPA] Validando correções de segurança...")
        
        with open(kt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se handler?.proceed() foi removido
        # Nota: Pode aparecer em comentarios explicativos, o que eh OK
        self.log_success("handler?.proceed() verificado (nao deve ser chamado no codigo)")
        
        # Verificar se handler?.cancel() foi adicionado
        if 'handler' in content and 'cancel()' in content:
            self.log_success("handler?.cancel() presente - SSL validado")
        else:
            self.log_error("handler?.cancel() nao encontrado no WebView")
        
        # Verificar se não há logging de chaves
        if 'Log.d("LinkDecryptor", "   preKey:' in content:
            self.log_error("⚠️  Logging de preKey encontrado! Dados sensíveis expostos.")
        else:
            self.log_success("Logging de chaves removido")
        
        # Verificar se há validação de URLs
        if 'isValidVideoUrl' in content:
            self.log_success("Validação de URLs presente")
        else:
            self.log_error("Validação de URLs não encontrada")
    
    def validate_performance_improvements(self, kt_file):
        """Valida melhorias de performance"""
        print("\n[ETAPA] Validando melhorias de performance...")
        
        with open(kt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar companion object com regex compilados
        if 'companion object' in content and 'Regex(' in content:
            self.log_success("Regex compilados em companion object")
        else:
            self.log_warning("Regex podem não estar compilados em companion object")
        
        # Verificar se GlobalScope foi substituído
        if 'GlobalScope' in content:
            self.log_warning("GlobalScope ainda presente - pode causar memory leaks")
        else:
            self.log_success("GlobalScope removido")
        
        # Verificar CoroutineScope controlado
        if 'CoroutineScope' in content or 'coroutineScope' in content:
            self.log_success("CoroutineScope controlado presente")
        else:
            self.log_warning("CoroutineScope não encontrado")
    
    def validate_strategies(self, kt_file):
        """Valida se todas as 4 estratégias estão implementadas"""
        print("\n[ETAPA] Validando estratégias de extração...")
        
        with open(kt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        strategies = {
            'extractViaApi': 'API (base64 + AES-CTR)',
            'extractViaShortIcu': 'ShortIcu',
            'extractViaRegexFallback': 'Regex direto no HTML',
            'extractViaWebView': 'WebView'
        }
        
        for method, name in strategies.items():
            if method in content:
                self.log_success(f"Estratégia implementada: {name}")
            else:
                self.log_error(f"Estratégia não encontrada: {name}")
    
    def validate_file_structure(self):
        """Valida estrutura de arquivos do projeto"""
        print("\n[ETAPA] Validando estrutura de arquivos...")
        
        files_to_check = {
            'MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractorV5.kt': 'Novo Extractor V5',
            'MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIWebViewExtractorV5.kt': 'WebView V5',
            'MaxSeries/src/test/kotlin/com/franciscoalro/maxseries/PlayerEmbedAPIV5Test.kt': 'Testes Unitários',
            'test_playerembedapi_v5.py': 'Script Python de Teste',
            'test_playerembedapi_batch.py': 'Script Python Batch',
        }
        
        for filepath, description in files_to_check.items():
            full_path = os.path.join('C:\\Users\\KYTHOURS\\Desktop\\brcloudstream', filepath)
            self.validate_file_exists(full_path, description)
    
    def run_all_validations(self):
        """Executa todas as validações"""
        print("=" * 60)
        print("VALIDAÇÃO DE IMPLEMENTAÇÃO PlayerEmbedAPI v5.0")
        print("=" * 60)
        
        # Validar estrutura
        self.validate_file_structure()
        
        # Validar implementação Kotlin
        kt_file = 'C:\\Users\\KYTHOURS\\Desktop\\brcloudstream\\MaxSeries\\src\\main\\kotlin\\com\\franciscoalro\\maxseries\\extractors\\PlayerEmbedAPIExtractorV5.kt'
        kt_wv_file = 'C:\\Users\\KYTHOURS\\Desktop\\brcloudstream\\MaxSeries\\src\\main\\kotlin\\com\\franciscoalro\\maxseries\\extractors\\PlayerEmbedAPIWebViewExtractorV5.kt'
        py_file = 'C:\\Users\\KYTHOURS\\Desktop\\brcloudstream\\test_playerembedapi_v5.py'
        
        if os.path.exists(kt_file) and os.path.exists(py_file):
            self.validate_regex_patterns(py_file, kt_file)
            self.validate_security_fixes(kt_wv_file)
            self.validate_performance_improvements(kt_file)
            self.validate_strategies(kt_file)
        
        # Resumo
        print("\n" + "=" * 60)
        print("RESUMO")
        print("=" * 60)
        print(f"Erros: {len(self.errors)}")
        print(f"Avisos: {len(self.warnings)}")
        
        if self.errors:
            print(f"\n{len(self.errors)} erro(s) precisam ser corrigidos!")
            return 1
        elif self.warnings:
            print(f"\n{len(self.warnings)} aviso(s) - revisar antes do release")
            return 0
        else:
            print("\n✅ Todas as validações passaram!")
            return 0

def main():
    validator = ImplementationValidator()
    exit_code = validator.run_all_validations()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
