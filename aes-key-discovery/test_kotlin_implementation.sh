#!/bin/bash

# Script de teste para validar implementação Kotlin do PlayerEmbedAPI v5.0

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  TESTE: PlayerEmbedAPI v5.0 - Implementação Kotlin            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
PROJECT_DIR="MaxSeries"
EXTRACTOR_FILE="$PROJECT_DIR/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor.kt"
NEW_EXTRACTOR="$PROJECT_DIR/src/main/kotlin/com/franciscoalro/maxseries/extractors/PlayerEmbedAPIExtractor_V5_FINAL.kt"
BACKUP_FILE="${EXTRACTOR_FILE}.backup_$(date +%Y%m%d_%H%M%S)"

# Função de log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Verificar se arquivos existem
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. VERIFICANDO ARQUIVOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$EXTRACTOR_FILE" ]; then
    log_error "Arquivo atual não encontrado: $EXTRACTOR_FILE"
    exit 1
fi
log_info "✅ Arquivo atual encontrado"

if [ ! -f "$NEW_EXTRACTOR" ]; then
    log_error "Nova implementação não encontrada: $NEW_EXTRACTOR"
    exit 1
fi
log_info "✅ Nova implementação encontrada"

# 2. Fazer backup
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. FAZENDO BACKUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cp "$EXTRACTOR_FILE" "$BACKUP_FILE"
if [ $? -eq 0 ]; then
    log_info "✅ Backup criado: $BACKUP_FILE"
else
    log_error "Falha ao criar backup"
    exit 1
fi

# 3. Comparar implementações
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. COMPARANDO IMPLEMENTAÇÕES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar se nova versão tem algoritmo AES-CTR
if grep -q "AES/CTR/NoPadding" "$NEW_EXTRACTOR"; then
    log_info "✅ Algoritmo AES-CTR encontrado"
else
    log_error "Algoritmo AES-CTR não encontrado"
    exit 1
fi

# Verificar se tem fallback
if grep -q "tryIframeFallback" "$NEW_EXTRACTOR"; then
    log_info "✅ Fallback iframe encontrado"
else
    log_warn "⚠️  Fallback iframe não encontrado"
fi

# Verificar se tem suporte a múltiplas qualidades
if grep -q "360p\|720p\|1080p" "$NEW_EXTRACTOR"; then
    log_info "✅ Suporte a múltiplas qualidades"
else
    log_warn "⚠️  Suporte a múltiplas qualidades não encontrado"
fi

# Verificar se tem suporte a legendas
if grep -q "subtitleCallback" "$NEW_EXTRACTOR"; then
    log_info "✅ Suporte a legendas"
else
    log_warn "⚠️  Suporte a legendas não encontrado"
fi

# 4. Análise de código
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. ANÁLISE DE CÓDIGO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Contar linhas
OLD_LINES=$(wc -l < "$EXTRACTOR_FILE")
NEW_LINES=$(wc -l < "$NEW_EXTRACTOR")

log_info "Linhas (antiga): $OLD_LINES"
log_info "Linhas (nova): $NEW_LINES"
log_info "Diferença: $((NEW_LINES - OLD_LINES)) linhas"

# Verificar imports necessários
echo ""
log_info "Verificando imports necessários..."

REQUIRED_IMPORTS=(
    "javax.crypto.Cipher"
    "javax.crypto.spec.SecretKeySpec"
    "javax.crypto.spec.IvParameterSpec"
    "java.security.MessageDigest"
)

for import in "${REQUIRED_IMPORTS[@]}"; do
    if grep -q "$import" "$NEW_EXTRACTOR"; then
        log_info "  ✅ $import"
    else
        log_error "  ❌ $import (FALTANDO)"
    fi
done

# 5. Verificar compatibilidade
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. VERIFICANDO COMPATIBILIDADE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar se mantém mesma interface
if grep -q "override suspend fun getUrl" "$NEW_EXTRACTOR"; then
    log_info "✅ Interface getUrl mantida"
else
    log_error "Interface getUrl alterada"
    exit 1
fi

if grep -q "override var name = \"PlayerEmbedAPI\"" "$NEW_EXTRACTOR"; then
    log_info "✅ Nome do extractor mantido"
else
    log_warn "⚠️  Nome do extractor alterado"
fi

if grep -q "fun canHandle" "$NEW_EXTRACTOR"; then
    log_info "✅ Função canHandle mantida"
else
    log_error "Função canHandle removida"
    exit 1
fi

# 6. Resumo
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. RESUMO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
log_info "✅ Implementação validada com sucesso!"
echo ""
log_info "Próximos passos:"
echo "  1. Substituir arquivo:"
echo "     cp $NEW_EXTRACTOR $EXTRACTOR_FILE"
echo ""
echo "  2. Compilar plugin:"
echo "     cd $PROJECT_DIR && ./gradlew assembleDebug"
echo ""
echo "  3. Testar com vídeo real:"
echo "     URL: https://playerembedapi.link/?v=kBJLtxCD3"
echo ""
echo "  4. Verificar logs:"
echo "     adb logcat | grep PlayerEmbedAPI_V5"
echo ""
echo "  5. Restaurar backup (se necessário):"
echo "     cp $BACKUP_FILE $EXTRACTOR_FILE"
echo ""

# 7. Perguntar se quer substituir
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Deseja substituir o arquivo agora? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    log_info "Substituindo arquivo..."
    cp "$NEW_EXTRACTOR" "$EXTRACTOR_FILE"
    
    if [ $? -eq 0 ]; then
        log_info "✅ Arquivo substituído com sucesso!"
        log_info "Backup disponível em: $BACKUP_FILE"
    else
        log_error "Falha ao substituir arquivo"
        exit 1
    fi
else
    log_info "Substituição cancelada"
    log_info "Backup disponível em: $BACKUP_FILE"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  TESTE CONCLUÍDO                                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
