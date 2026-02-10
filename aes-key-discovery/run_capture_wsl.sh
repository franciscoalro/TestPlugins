#!/bin/bash

# Script para executar captura automatizada no WSL
# Instala dependências e executa a captura

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🐧 CAPTURA AUTOMATIZADA - WSL Linux                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Diretório: $SCRIPT_DIR"
echo ""

# Verificar se Node.js está instalado
echo "🔍 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado!"
    echo ""
    echo "📦 Instalando Node.js..."
    
    # Instalar Node.js via nvm (recomendado)
    if ! command -v nvm &> /dev/null; then
        echo "📥 Instalando NVM..."
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi
    
    echo "📥 Instalando Node.js LTS..."
    nvm install --lts
    nvm use --lts
else
    NODE_VERSION=$(node --version)
    echo "✅ Node.js encontrado: $NODE_VERSION"
fi

echo ""

# Verificar se npm está instalado
echo "🔍 Verificando npm..."
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado!"
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo "✅ npm encontrado: $NPM_VERSION"
fi

echo ""

# Verificar se Playwright está instalado
echo "🔍 Verificando Playwright..."
if [ ! -d "node_modules/playwright" ]; then
    echo "📦 Playwright não encontrado. Instalando..."
    echo ""
    
    # Criar package.json se não existir
    if [ ! -f "package.json" ]; then
        echo "📝 Criando package.json..."
        cat > package.json << 'EOF'
{
  "name": "aes-key-discovery",
  "version": "1.0.0",
  "description": "AES Key Discovery - PlayerEmbedAPI",
  "main": "capture_algorithm_headless.js",
  "scripts": {
    "capture": "node capture_algorithm_headless.js"
  },
  "dependencies": {
    "playwright": "^1.40.0"
  }
}
EOF
    fi
    
    echo "📥 Instalando Playwright..."
    npm install
    
    echo ""
    echo "📥 Instalando navegadores do Playwright..."
    npx playwright install chromium
    
    echo ""
    echo "📥 Instalando dependências do sistema..."
    npx playwright install-deps chromium
else
    echo "✅ Playwright já instalado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Executar captura
echo "🚀 Executando captura automatizada..."
echo ""

node capture_algorithm_headless.js

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ CAPTURA CONCLUÍDA COM SUCESSO!                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📄 Resultados salvos em:"
    echo "  output/algorithm_captured.json"
    echo ""
    echo "🔍 Para ver os resultados:"
    echo "  cat output/algorithm_captured.json | jq ."
    echo ""
    echo "📚 Próximos passos:"
    echo "  1. Revisar: output/algorithm_captured.json"
    echo "  2. Implementar: IMPLEMENTACAO_PLUGIN.md"
    echo "  3. Testar com múltiplos vídeos"
else
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  CAPTURA FALHOU                                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "💡 Possíveis soluções:"
    echo "  1. Executar novamente: bash run_capture_wsl.sh"
    echo "  2. Verificar logs acima para erros"
    echo "  3. Usar método manual: SOLUCAO_FINAL.md"
    echo ""
    echo "🔧 Debug:"
    echo "  • Verificar conexão com internet"
    echo "  • Verificar se o vídeo ainda existe"
    echo "  • Tentar com outro slug de vídeo"
fi

echo ""

exit $EXIT_CODE
