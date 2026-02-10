# 🔓 AES Key Discovery - PlayerEmbedAPI

Ferramentas automatizadas para descobrir a chave AES do PlayerEmbedAPI usando WSL/Kali Linux no Windows.

> **👋 Primeira vez aqui?** Leia [START_HERE.txt](START_HERE.txt) para um guia de boas-vindas!

## 🎯 Objetivo

Descobrir a fórmula de derivação da chave AES usada para decriptar o campo `media` do PlayerEmbedAPI.

## ⚡ Início Rápido (Windows)

### Opção 1: Usar o launcher (Mais fácil)

```cmd
# No CMD ou PowerShell do Windows
run_wsl.bat
```

Escolha uma opção do menu:
1. Teste Rápido (5 min)
2. Análise Completa (15-30 min)
3. Burp Suite
4. mitmproxy
5. Wireshark
6. Abrir WSL

### Opção 2: Linha de comando

```powershell
# Abrir WSL
wsl

# Navegar até o diretório
cd /mnt/c/caminho/para/aes-key-discovery

# Dar permissões
chmod +x *.sh scripts/*.sh

# Executar teste rápido
bash quick_test.sh

# OU análise completa
bash run_analysis.sh
```

## 📋 Pré-requisitos

### Windows

- WSL (Windows Subsystem for Linux) instalado
- Distribuição Linux (Ubuntu, Debian, Kali)

```powershell
# Instalar WSL (se necessário)
wsl --install
```

### Linux (WSL)

```bash
# Instalar dependências básicas
sudo apt-get update
sudo apt-get install -y curl jq python3 nodejs npm

# Opcionais (para análise avançada)
pip3 install mitmproxy frida frida-tools
```

## 📁 Estrutura do Projeto

```
aes-key-discovery/
├── run_wsl.bat              # 🪟 Launcher para Windows
├── quick_test.sh            # ⚡ Teste rápido (5 min)
├── run_analysis.sh          # 🔬 Análise completa (15-30 min)
├── scripts/                 # 📜 Scripts de análise
│   ├── extract_strings.sh
│   ├── find_crypto_patterns.sh
│   ├── analyze_importkey.sh
│   ├── deobfuscate.js
│   ├── find_key_formula.py
│   ├── advanced_analysis.py
│   ├── burp_intercept.sh
│   ├── mitmproxy_capture.py
│   ├── wireshark_filter.sh
│   └── frida_hook.js
├── output/                  # 📊 Resultados (gerado automaticamente)
├── README.md               # 📖 Este arquivo
├── USAGE.md                # 📚 Guia detalhado de uso
└── EXAMPLES.md             # 💡 Exemplos práticos

```

## 🔍 Métodos de Análise

### 1. Análise Automatizada (Recomendado para começar)

```bash
bash run_analysis.sh
```

**O que faz:**
- ✅ Baixa `lite.bundle.js`
- ✅ Extrai strings e padrões
- ✅ Deobfusca JavaScript
- ✅ Identifica possíveis fórmulas
- ✅ Gera testes com valores conhecidos

**Tempo:** 15-30 minutos

### 2. Interceptação com Burp Suite

```bash
bash scripts/burp_intercept.sh  # Ver instruções
burpsuite &
```

**O que faz:**
- Intercepta tráfego HTTP/HTTPS
- Captura requisições e respostas
- Identifica headers e tokens

**Tempo:** 30-60 minutos

### 3. Captura com mitmproxy

```bash
mitmproxy -p 8080 -s scripts/mitmproxy_capture.py
```

**O que faz:**
- Proxy interativo
- Captura automática de crypto
- Salva JavaScript e respostas

**Tempo:** 20-40 minutos

### 4. Hook Dinâmico com Frida (Avançado)

```bash
frida -U Chrome -l scripts/frida_hook.js
```

**O que faz:**
- Hook em `crypto.subtle.importKey`
- Captura chave em runtime
- Mostra stack trace

**Tempo:** 30-60 minutos

## 📊 Resultados

Após executar `run_analysis.sh`, os resultados estarão em `output/`:

```
output/
├── lite.bundle.js           # Bundle original
├── lite_deobf.js           # Bundle deobfuscado
├── strings.txt             # Strings extraídas
├── crypto_patterns.txt     # Padrões de crypto
├── importkey_analysis.txt  # Análise de importKey
├── key_formula.txt         # 🔑 Fórmula básica
└── advanced_analysis.txt   # 🔑 Análise avançada (IMPORTANTE)
```

**Arquivos mais importantes:**
- `key_formula.txt` - Primeira análise da fórmula
- `advanced_analysis.txt` - Análise detalhada com testes

## 🎓 Documentação

- **[USAGE.md](USAGE.md)** - Guia completo de uso
- **[EXAMPLES.md](EXAMPLES.md)** - Exemplos práticos passo a passo

## 💡 Fluxo Recomendado

```
1. quick_test.sh          # Teste rápido (5 min)
   ↓
2. run_analysis.sh        # Análise completa (15-30 min)
   ↓
3. Ler output/advanced_analysis.txt
   ↓
4. Se não encontrar: Burp Suite ou Frida
   ↓
5. Validar fórmula descoberta
```

## 🔑 O Que Estamos Procurando

A chave AES é derivada de 3 parâmetros:

```javascript
user_id = "482120"
slug = "kBJLtxCD3"
md5_id = "28930647"
```

Possíveis fórmulas:

```javascript
// Opção 1: Concatenação simples
key = user_id + slug + md5_id

// Opção 2: Com hash MD5
key = MD5(user_id + slug + md5_id)

// Opção 3: Ordem diferente
key = MD5(slug + user_id + md5_id)

// Opção 4: Com separadores
key = MD5(user_id + ":" + slug + ":" + md5_id)
```

## 🚨 Troubleshooting

### WSL não instalado

```powershell
wsl --install
# Reiniciar o computador
```

### Permission denied

```bash
chmod +x *.sh scripts/*.sh
```

### Command not found

```bash
sudo apt-get update
sudo apt-get install -y curl jq python3 nodejs
```

### Caminho não encontrado no WSL

```bash
# Windows: C:\Users\Nome\Desktop\projeto
# WSL: /mnt/c/Users/Nome/Desktop/projeto
cd /mnt/c/Users/Nome/Desktop/aes-key-discovery
```

## 📞 Suporte

- Ver exemplos detalhados: `EXAMPLES.md`
- Ver guia de uso completo: `USAGE.md`
- Problemas com WSL: https://docs.microsoft.com/windows/wsl/

## ⚖️ Aviso Legal

Este projeto é apenas para fins educacionais e de pesquisa. Use de forma responsável e ética.
