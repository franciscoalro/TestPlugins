#!/usr/bin/env powershell
<#
.SYNOPSIS
    Script para preparar arquivos de teste do CloudStream
.DESCRIPTION
    Este script prepara todos os arquivos necessários para testar
    a implementação PlayerEmbedAPI no CloudStream
#>

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PREPARAR TESTE - CLOUDSTREAM" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Criar diretório de teste
$testDir = "teste_cloudstream_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null

Write-Host "[+] Diretório criado: $testDir" -ForegroundColor Green

# Copiar arquivos principais
$arquivos = @(
    "MaxSeriesProvider_Final.kt",
    "PlayerEmbedAPIExtractor_Final.kt",
    "PlayerEmbedAPIExtractor.kt",
    "INTEGRACAO_MAXSERIES.md",
    "TESTE_CLOUDSTREAM.md"
)

foreach ($arquivo in $arquivos) {
    if (Test-Path $arquivo) {
        Copy-Item $arquivo -Destination $testDir
        Write-Host "  ✓ Copiado: $arquivo" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ Não encontrado: $arquivo" -ForegroundColor Red
    }
}

# Criar instruções rápidas
$instrucoes = @"
============================================
INSTRUÇÕES RÁPIDAS - TESTE CLOUDSTREAM
============================================

1. ESTRUTURA DE ARQUIVOS
------------------------
Copiar para seu projeto CloudStream:

cloudstream-extensions/
└── MaxSeries/
    └── src/
        └── main/
            └── kotlin/
                └── com/
                    └── franciscoalro/
                        └── maxseries/
                            ├── MaxSeriesProvider.kt
                            └── extractors/
                                └── PlayerEmbedAPIExtractor.kt  <- NOVO

2. COMANDOS DE BUILD
--------------------
./gradlew :MaxSeries:clean
./gradlew :MaxSeries:build
./gradlew :MaxSeries:generateCS3

3. INSTALAÇÃO
-------------
- Transferir MaxSeries/build/MaxSeries.cs3 para celular
- Abrir CloudStream → Configurações → Extensões
- Instalar de arquivo .cs3

4. VERIFICAÇÃO
--------------
adb logcat -s MaxSeries:D PlayerEmbedAPI:D

Logs esperados:
D/PlayerEmbedAPI: ✅ Extração rápida em XXXms

============================================
LINKS ÚTEIS
============================================

Release GitHub:
https://github.com/franciscoalro/TestPlugins/releases/tag/v2.1.0

Documentação completa:
- INTEGRACAO_MAXSERIES.md
- TESTE_CLOUDSTREAM.md

============================================
"@

$instrucoes | Out-File -FilePath "$testDir\INSTRUCOES.txt" -Encoding UTF8

# Listar conteúdo
Write-Host ""
Write-Host "[+] Conteúdo do diretório $testDir:" -ForegroundColor Green
Get-ChildItem $testDir | ForEach-Object {
    $tamanho = if ($_.Length -gt 1KB) { "{0:N1} KB" -f ($_.Length/1KB) } else { "$($_.Length) bytes" }
    Write-Host "  📄 $($_.Name) ($tamanho)" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  PREPARAÇÃO CONCLUÍDA!" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Acesse a pasta: $testDir" -ForegroundColor White
Write-Host "  2. Leia INSTRUCOES.txt" -ForegroundColor White
Write-Host "  3. Siga o guia INTEGRACAO_MAXSERIES.md" -ForegroundColor White
Write-Host ""
