#!/bin/bash

# Script para executar captura com Selenium no WSL

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🐧 CAPTURA AUTOMATIZADA - Selenium + Chrome Headless     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Diretório: $SCRIPT_DIR"
echo ""

# Verificar se Python3 está instalado
echo "🔍 Verificando Python3..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    echo "📦 Instalando Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
else
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python3 encontrado: $PYTHON_VERSION"
fi

echo ""

# Verificar se pip está instalado
echo "🔍 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    echo "📦 Instalando pip3..."
    sudo apt-get install -y python3-pip
else
    PIP_VERSION=$(pip3 --version)
    echo "✅ pip3 encontrado: $PIP_VERSION"
fi

echo ""

# Instalar Selenium
echo "🔍 Verificando Selenium..."
if ! python3 -c "import selenium" 2>/dev/null; then
    echo "📦 Instalando Selenium..."
    pip3 install selenium
else
    echo "✅ Selenium já instalado"
fi

echo ""

# Instalar Chrome e ChromeDriver
echo "🔍 Verificando Chrome..."
if ! command -v chromium-browser &> /dev/null && ! command -v google-chrome &> /dev/null; then
    echo "📦 Instalando Chromium..."
    sudo apt-get update
    sudo apt-get install -y chromium-browser chromium-chromedriver
else
    echo "✅ Chrome encontrado"
fi

echo ""

# Verificar ChromeDriver
echo "🔍 Verificando ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "📦 Instalando ChromeDriver..."
    sudo apt-get install -y chromium-chromedriver
else
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>/dev/null || echo "unknown")
    echo "✅ ChromeDriver encontrado: $CHROMEDRIVER_VERSION"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Executar captura
echo "🚀 Executando captura automatizada..."
echo ""

python3 capture_algorithm_selenium.py

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
    echo "  cat output/algorithm_captured.json | python3 -m json.tool"
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
    echo "  1. Executar novamente: bash run_capture_selenium.sh"
    echo "  2. Verificar logs acima para erros"
    echo "  3. Usar método manual: SOLUCAO_FINAL.md"
fi

echo ""

exit $EXIT_CODE
