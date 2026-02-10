#!/bin/bash

# Script de instalação de dependências

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📦 Instalação de Dependências        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Detectar sistema operacional
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
else
    OS=$(uname -s)
fi

echo -e "${YELLOW}Sistema detectado:${NC} $OS"
echo ""

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para instalar pacote
install_package() {
    local package=$1
    local command_name=${2:-$1}
    
    if command_exists "$command_name"; then
        echo -e "${GREEN}✓${NC} $package já instalado"
    else
        echo -e "${YELLOW}→${NC} Instalando $package..."
        if command_exists apt-get; then
            sudo apt-get install -y "$package"
        elif command_exists yum; then
            sudo yum install -y "$package"
        elif command_exists pacman; then
            sudo pacman -S --noconfirm "$package"
        else
            echo -e "${RED}✗${NC} Gerenciador de pacotes não suportado"
            return 1
        fi
        echo -e "${GREEN}✓${NC} $package instalado"
    fi
}

# Atualizar repositórios
echo -e "${BLUE}[1/3] Atualizando repositórios...${NC}"
if command_exists apt-get; then
    sudo apt-get update -qq
elif command_exists yum; then
    sudo yum update -y -q
fi
echo -e "${GREEN}✓${NC} Repositórios atualizados"
echo ""

# Instalar dependências básicas
echo -e "${BLUE}[2/3] Instalando dependências básicas...${NC}"
install_package "curl" "curl"
install_package "jq" "jq"
install_package "python3" "python3"
install_package "nodejs" "node"
install_package "npm" "npm"
install_package "git" "git"
echo -e "${GREEN}✓${NC} Dependências básicas instaladas"
echo ""

# Instalar dependências Python
echo -e "${BLUE}[3/3] Instalando dependências Python...${NC}"

if command_exists pip3; then
    echo -e "${GREEN}✓${NC} pip3 já instalado"
else
    echo -e "${YELLOW}→${NC} Instalando pip3..."
    if command_exists apt-get; then
        sudo apt-get install -y python3-pip
    fi
fi

# Instalar pacotes Python opcionais
echo ""
echo -e "${YELLOW}Deseja instalar ferramentas avançadas? (mitmproxy, frida)${NC}"
echo -e "Estas ferramentas são opcionais mas úteis para análise avançada."
read -p "Instalar? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo -e "${YELLOW}→${NC} Instalando mitmproxy..."
    pip3 install --user mitmproxy
    echo -e "${GREEN}✓${NC} mitmproxy instalado"
    
    echo -e "${YELLOW}→${NC} Instalando frida..."
    pip3 install --user frida frida-tools
    echo -e "${GREEN}✓${NC} frida instalado"
else
    echo -e "${YELLOW}⊘${NC} Ferramentas avançadas não instaladas"
    echo -e "   Você pode instalá-las depois com:"
    echo -e "   ${BLUE}pip3 install mitmproxy frida frida-tools${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Instalação concluída!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# Verificar instalações
echo -e "${YELLOW}Verificando instalações:${NC}"
echo ""

check_command() {
    if command_exists "$1"; then
        local version=$($1 --version 2>&1 | head -n 1)
        echo -e "  ${GREEN}✓${NC} $1: $version"
    else
        echo -e "  ${RED}✗${NC} $1: não instalado"
    fi
}

check_command "curl"
check_command "jq"
check_command "python3"
check_command "node"
check_command "npm"
check_command "git"

echo ""
if command_exists mitmproxy; then
    echo -e "  ${GREEN}✓${NC} mitmproxy: $(mitmproxy --version 2>&1 | head -n 1)"
else
    echo -e "  ${YELLOW}⊘${NC} mitmproxy: não instalado (opcional)"
fi

if command_exists frida; then
    echo -e "  ${GREEN}✓${NC} frida: $(frida --version 2>&1)"
else
    echo -e "  ${YELLOW}⊘${NC} frida: não instalado (opcional)"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}Pronto para usar!${NC}"
echo ""
echo -e "Próximos passos:"
echo -e "  1. ${BLUE}bash quick_test.sh${NC}      - Teste rápido"
echo -e "  2. ${BLUE}bash run_analysis.sh${NC}    - Análise completa"
echo ""
