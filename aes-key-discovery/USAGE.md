# 📖 Guia de Uso - AES Key Discovery

## 🎯 Objetivo

Descobrir a chave AES usada pelo PlayerEmbedAPI para decriptar o campo `media`.

---

## 🚀 Início Rápido (Windows + WSL)

### 1. Abrir WSL

```powershell
# No PowerShell/CMD do Windows
wsl
```

### 2. Navegar até o diretório

```bash
cd /mnt/c/caminho/para/aes-key-discovery
```

### 3. Dar permissão de execução

```bash
chmod +x *.sh
chmod +x scripts/*.sh
```

### 4. Executar teste rápido

```bash
bash quick_test.sh
```

### 5. Executar análise completa

```bash
bash run_analysis.sh
```

---

## 📊 Métodos de Análise

### Método 1: Análise Automatizada (Recomendado)

```bash
# Análise completa com todos os scripts
bash run_analysis.sh

# Ver resultados
cat output/key_formula.txt
```

**O que faz:**
- ✅ Baixa lite.bundle.js
- ✅ Extrai strings relevantes
- ✅ Procura padrões de crypto
- ✅ Analisa importKey
- ✅ Deobfusca JavaScript
- ✅ Identifica fórmula da chave

---

### Método 2: Interceptação com Burp Suite

```bash
# Ver instruções
bash scripts/burp_intercept.sh

# Iniciar Burp Suite
burpsuite &

# Configurar proxy no navegador
# Abrir: https://playerembedapi.link/?v=kBJLtxCD3
# Analisar HTTP History
```

**O que procurar:**
- Headers customizados (X-Key, X-Token)
- Respostas JSON com campo "key"
- Requisições para /api/key ou similar

---

### Método 3: Captura com mitmproxy

```bash
# Instalar mitmproxy
pip3 install mitmproxy

# Executar com script de captura
mitmproxy -p 8080 -s scripts/mitmproxy_capture.py

# Configurar navegador para usar proxy 127.0.0.1:8080
# Abrir PlayerEmbedAPI
# Ver resultados em: output/mitmproxy_crypto.txt
```

---

### Método 4: Análise de Rede com Wireshark

```bash
# Ver instruções
bash scripts/wireshark_filter.sh

# Iniciar Wireshark
sudo wireshark &

# Usar filtro:
# (http.host contains "playerembedapi" or http.host contains "iamcdn")

# Exportar objetos HTTP (.js files)
```

---

### Método 5: Hook Dinâmico com Frida

```bash
# Instalar Frida
pip3 install frida frida-tools

# Executar hook no Chrome
frida -U Chrome -l scripts/frida_hook.js

# Abrir PlayerEmbedAPI no Chrome
# Ver logs no terminal
```

**O que captura:**
- Chamadas para crypto.subtle.importKey
- Chamadas para crypto.subtle.decrypt
- Conversões com TextEncoder
- Funções MD5

---

## 📁 Estrutura de Saída

```
output/
├── lite.bundle.js          # Bundle original
├── lite_deobf.js          # Bundle deobfuscado
├── strings.txt            # Strings extraídas
├── crypto_patterns.txt    # Padrões de crypto
├── importkey_analysis.txt # Análise de importKey
├── key_formula.txt        # 🔑 FÓRMULA DA CHAVE (IMPORTANTE)
├── burp_*.txt            # Capturas do Burp Suite
└── mitmproxy_crypto.txt  # Capturas do mitmproxy
```

---

## 🔍 Análise Manual

### 1. Ler o arquivo deobfuscado

```bash
# Procurar por importKey
grep -n -A 50 "importKey" output/lite_deobf.js | less

# Procurar por user_id, slug, md5_id
grep -n -E "(user_id|slug|md5_id)" output/lite_deobf.js | less

# Procurar por MD5
grep -n "MD5" output/lite_deobf.js | less
```

### 2. Identificar a fórmula

Procurar por padrões como:

```javascript
// Exemplo 1: Concatenação simples
key = user_id + slug + md5_id

// Exemplo 2: Com hash
key = MD5(user_id + slug + md5_id)

// Exemplo 3: Com ordem diferente
key = MD5(md5_id + user_id + slug)

// Exemplo 4: Com separadores
key = MD5(user_id + ":" + slug + ":" + md5_id)
```

### 3. Testar a fórmula

```bash
# Criar script de teste
cat > test_formula.sh << 'EOF'
#!/bin/bash

USER_ID="482120"
SLUG="kBJLtxCD3"
MD5_ID="28930647"

# Testar diferentes combinações
echo "Teste 1: user_id + slug + md5_id"
echo -n "${USER_ID}${SLUG}${MD5_ID}" | md5sum

echo "Teste 2: md5_id + user_id + slug"
echo -n "${MD5_ID}${USER_ID}${SLUG}" | md5sum

echo "Teste 3: slug + user_id + md5_id"
echo -n "${SLUG}${USER_ID}${MD5_ID}" | md5sum
EOF

chmod +x test_formula.sh
bash test_formula.sh
```

---

## 🛠️ Ferramentas Necessárias

### Básicas (para análise automatizada)

```bash
sudo apt-get update
sudo apt-get install -y curl jq python3 nodejs npm
```

### Avançadas (opcionais)

```bash
# Burp Suite (já vem no Kali)
burpsuite

# mitmproxy
pip3 install mitmproxy

# Wireshark
sudo apt-get install wireshark

# Frida
pip3 install frida frida-tools
```

---

## 💡 Dicas

### 1. Começar pelo mais simples

```bash
# Teste rápido primeiro
bash quick_test.sh

# Se não encontrar, análise completa
bash run_analysis.sh
```

### 2. Focar em key_formula.txt

```bash
# Este arquivo tem as informações mais importantes
cat output/key_formula.txt | less
```

### 3. Procurar por padrões conhecidos

- `user_id + slug + md5_id`
- `MD5(user_id + slug + md5_id)`
- `SHA256(...)`
- `btoa(...)` (Base64)

### 4. Usar múltiplos métodos

Se um método não funcionar, tentar outro:
1. Análise automatizada
2. Burp Suite (interceptação)
3. mitmproxy (captura)
4. Frida (hook dinâmico)

---

## 🎯 Checklist

- [ ] Executar `quick_test.sh`
- [ ] Executar `run_analysis.sh`
- [ ] Ler `output/key_formula.txt`
- [ ] Procurar por `importKey` no código deobfuscado
- [ ] Identificar concatenação de `user_id`, `slug`, `md5_id`
- [ ] Verificar se há `MD5()` ou `SHA()` aplicado
- [ ] Testar fórmula com valores conhecidos
- [ ] Se necessário, usar Burp Suite para interceptação
- [ ] Se necessário, usar Frida para hook dinâmico

---

## 📞 Próximos Passos

Após descobrir a fórmula:

1. Documentar a fórmula encontrada
2. Criar função para gerar a chave
3. Testar decriptação com a chave gerada
4. Validar com múltiplos vídeos

---

## ⚠️ Troubleshooting

### Erro: "bash: command not found"

```bash
# Instalar bash (se necessário)
sudo apt-get install bash
```

### Erro: "Permission denied"

```bash
# Dar permissão de execução
chmod +x *.sh
chmod +x scripts/*.sh
```

### Erro: "curl: command not found"

```bash
# Instalar curl
sudo apt-get install curl
```

### WSL não encontra o diretório

```bash
# Navegar pelo Windows
cd /mnt/c/Users/SeuUsuario/Desktop/aes-key-discovery

# Ou copiar para home do WSL
cp -r /mnt/c/caminho/para/aes-key-discovery ~/
cd ~/aes-key-discovery
```

---

## 🎓 Recursos Adicionais

- [Burp Suite Documentation](https://portswigger.net/burp/documentation)
- [mitmproxy Documentation](https://docs.mitmproxy.org/)
- [Frida Documentation](https://frida.re/docs/)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
