#!/bin/bash

# Script para análise manual do código deobfuscado

OUTPUT_DIR="output"
DEOBF_FILE="$OUTPUT_DIR/lite_deobf.js"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔍 Análise Manual do Código Deobfuscado                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

if [ ! -f "$DEOBF_FILE" ]; then
    echo "❌ Arquivo não encontrado: $DEOBF_FILE"
    echo "   Execute primeiro: bash run_analysis.sh"
    exit 1
fi

echo "📄 Analisando: $DEOBF_FILE"
echo ""

# 1. Procurar por importKey com contexto amplo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 1. Procurando crypto.subtle.importKey"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "importKey" "$DEOBF_FILE" | head -10
echo ""

# 2. Procurar por decrypt
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔓 2. Procurando crypto.subtle.decrypt"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "decrypt" "$DEOBF_FILE" | head -10
echo ""

# 3. Procurar por user_id, slug, md5_id juntos
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 3. Procurando uso de user_id, slug, md5_id"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "user_id.*slug.*md5_id\|slug.*user_id.*md5_id\|md5_id.*user_id.*slug" "$DEOBF_FILE" | head -5
echo ""

# 4. Procurar por concatenação com +
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 4. Procurando concatenações"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "user_id.*+.*slug\|slug.*+.*user_id\|md5_id.*+.*slug" "$DEOBF_FILE" | head -10
echo ""

# 5. Procurar por TextEncoder
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 5. Procurando TextEncoder"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "TextEncoder" "$DEOBF_FILE" | head -5
echo ""

# 6. Procurar por funções que podem gerar a chave
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 6. Procurando funções de geração de chave"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n "function.*key\|const.*key.*=\|let.*key.*=" "$DEOBF_FILE" | head -10
echo ""

# 7. Procurar por MD5 ou hash
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "#️⃣  7. Procurando funções de hash"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -n -i "md5\|hash\|digest" "$DEOBF_FILE" | head -10
echo ""

# 8. Extrair linha específica com importKey
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 8. Contexto detalhado de importKey"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Encontrar linha com importKey
LINE_NUM=$(grep -n "importKey" "$DEOBF_FILE" | head -1 | cut -d: -f1)

if [ -n "$LINE_NUM" ]; then
    echo "Linha $LINE_NUM (±50 linhas):"
    START=$((LINE_NUM - 50))
    END=$((LINE_NUM + 50))
    
    if [ $START -lt 1 ]; then
        START=1
    fi
    
    sed -n "${START},${END}p" "$DEOBF_FILE" | cat -n
else
    echo "⚠️  importKey não encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 DICAS PARA ANÁLISE MANUAL:"
echo "  1. Procurar a linha onde importKey é chamado"
echo "  2. Rastrear de onde vem o primeiro argumento (keyData)"
echo "  3. Verificar se há concatenação de user_id, slug, md5_id"
echo "  4. Verificar se há função MD5 ou hash aplicada"
echo "  5. Abrir o arquivo em um editor para análise detalhada:"
echo "     code $DEOBF_FILE"
echo ""
echo "📁 Arquivo completo: $DEOBF_FILE"
echo ""
