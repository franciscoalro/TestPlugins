#!/bin/bash

# 🔓 AES Key Discovery - Script Principal
# Executa análise completa do PlayerEmbedAPI

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# Criar diretórios
mkdir -p "$OUTPUT_DIR"
mkdir -p "$SCRIPTS_DIR"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔓 AES Key Discovery Tool            ║${NC}"
echo -e "${BLUE}║  PlayerEmbedAPI Analysis               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# URL de teste
TEST_URL="https://playerembedapi.link/?v=kBJLtxCD3"
BUNDLE_URL="https://iamcdn.net/player-v2/lite.bundle.js"

echo -e "${YELLOW}[1/6]${NC} Baixando lite.bundle.js..."
curl -s "$BUNDLE_URL" -o "$OUTPUT_DIR/lite.bundle.js"
echo -e "${GREEN}✓${NC} Bundle baixado ($(wc -c < "$OUTPUT_DIR/lite.bundle.js") bytes)"

echo -e "${YELLOW}[2/6]${NC} Extraindo strings relevantes..."
bash "$SCRIPTS_DIR/extract_strings.sh" "$OUTPUT_DIR/lite.bundle.js" > "$OUTPUT_DIR/strings.txt"
echo -e "${GREEN}✓${NC} Strings extraídas ($(wc -l < "$OUTPUT_DIR/strings.txt") linhas)"

echo -e "${YELLOW}[3/6]${NC} Procurando padrões de crypto..."
bash "$SCRIPTS_DIR/find_crypto_patterns.sh" "$OUTPUT_DIR/lite.bundle.js" > "$OUTPUT_DIR/crypto_patterns.txt"
echo -e "${GREEN}✓${NC} Padrões encontrados"

echo -e "${YELLOW}[4/6]${NC} Analisando importKey..."
bash "$SCRIPTS_DIR/analyze_importkey.sh" "$OUTPUT_DIR/lite.bundle.js" > "$OUTPUT_DIR/importkey_analysis.txt"
echo -e "${GREEN}✓${NC} Análise de importKey completa"

echo -e "${YELLOW}[5/6]${NC} Deobfuscando JavaScript..."
node "$SCRIPTS_DIR/deobfuscate.js" "$OUTPUT_DIR/lite.bundle.js" "$OUTPUT_DIR/lite_deobf.js"
echo -e "${GREEN}✓${NC} JavaScript deobfuscado"

echo -e "${YELLOW}[6/7]${NC} Procurando fórmula da chave..."
python3 "$SCRIPTS_DIR/find_key_formula.py" "$OUTPUT_DIR/lite_deobf.js" > "$OUTPUT_DIR/key_formula.txt"
echo -e "${GREEN}✓${NC} Fórmula básica identificada"

echo -e "${YELLOW}[7/7]${NC} Análise avançada de padrões..."
python3 "$SCRIPTS_DIR/advanced_analysis.py" "$OUTPUT_DIR/lite_deobf.js" > "$OUTPUT_DIR/advanced_analysis.txt"
echo -e "${GREEN}✓${NC} Análise avançada completa"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Análise concluída!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""
echo -e "📁 Resultados em: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""
echo -e "📄 Arquivos gerados:"
echo -e "  • strings.txt            - Strings extraídas"
echo -e "  • crypto_patterns.txt    - Padrões de crypto"
echo -e "  • importkey_analysis.txt - Análise de importKey"
echo -e "  • lite_deobf.js          - JavaScript deobfuscado"
echo -e "  • key_formula.txt        - Fórmula da chave (IMPORTANTE)"
echo -e "  • advanced_analysis.txt  - Análise avançada (IMPORTANTE)"
echo ""
echo -e "${YELLOW}🔍 Próximos passos:${NC}"
echo -e "1. cat $OUTPUT_DIR/key_formula.txt"
echo -e "2. cat $OUTPUT_DIR/advanced_analysis.txt"
echo -e "3. grep -i 'possível fórmula' $OUTPUT_DIR/advanced_analysis.txt"
