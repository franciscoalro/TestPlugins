#!/bin/bash

# Teste rápido - Análise básica sem ferramentas pesadas

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output"

mkdir -p "$OUTPUT_DIR"

echo "🚀 Teste Rápido - AES Key Discovery"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Download do bundle
echo "[1/4] Baixando lite.bundle.js..."
curl -s "https://iamcdn.net/player-v2/lite.bundle.js" -o "$OUTPUT_DIR/lite.bundle.js"
SIZE=$(wc -c < "$OUTPUT_DIR/lite.bundle.js")
echo "✓ Bundle baixado: $SIZE bytes"
echo ""

# 2. Procurar por importKey
echo "[2/4] Procurando por importKey..."
grep -o ".{0,200}importKey.{0,200}" "$OUTPUT_DIR/lite.bundle.js" | head -5 > "$OUTPUT_DIR/quick_importkey.txt"
echo "✓ Encontradas $(wc -l < "$OUTPUT_DIR/quick_importkey.txt") ocorrências"
cat "$OUTPUT_DIR/quick_importkey.txt"
echo ""

# 3. Procurar por user_id, slug, md5_id
echo "[3/4] Procurando parâmetros..."
grep -oE "(user_id|slug|md5_id)[^,;]{0,100}" "$OUTPUT_DIR/lite.bundle.js" | head -10 > "$OUTPUT_DIR/quick_params.txt"
echo "✓ Parâmetros encontrados:"
cat "$OUTPUT_DIR/quick_params.txt"
echo ""

# 4. Procurar por MD5
echo "[4/4] Procurando funções MD5..."
grep -oE "MD5\([^)]+\)" "$OUTPUT_DIR/lite.bundle.js" | head -5 > "$OUTPUT_DIR/quick_md5.txt"
if [ -s "$OUTPUT_DIR/quick_md5.txt" ]; then
    echo "✓ Funções MD5 encontradas:"
    cat "$OUTPUT_DIR/quick_md5.txt"
else
    echo "⚠ Nenhuma função MD5 explícita encontrada"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ Teste rápido concluído!"
echo ""
echo "📁 Resultados em: $OUTPUT_DIR"
echo ""
echo "💡 Próximo passo:"
echo "   bash run_analysis.sh  # Análise completa"
echo ""
