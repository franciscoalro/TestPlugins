# 📜 Scripts de Análise

Documentação detalhada de cada script incluído no projeto.

## 📁 Estrutura

```
scripts/
├── extract_strings.sh          # Extração de strings
├── find_crypto_patterns.sh     # Busca de padrões crypto
├── analyze_importkey.sh        # Análise de importKey
├── deobfuscate.js             # Deobfuscação JavaScript
├── find_key_formula.py        # Identificação de fórmula
├── advanced_analysis.py       # Análise avançada
├── burp_intercept.sh          # Guia Burp Suite
├── mitmproxy_capture.py       # Captura mitmproxy
├── wireshark_filter.sh        # Guia Wireshark
└── frida_hook.js              # Hook Frida
```

---

## 🔍 Scripts de Análise Estática

### extract_strings.sh

**Descrição:** Extrai strings relevantes do bundle JavaScript.

**Uso:**
```bash
bash scripts/extract_strings.sh output/lite.bundle.js > output/strings.txt
```

**O que faz:**
- Extrai strings relacionadas a crypto (AES, importKey, decrypt)
- Extrai parâmetros (user_id, slug, md5_id)
- Extrai funções de hash (MD5, SHA)
- Extrai strings hexadecimais (possíveis chaves)
- Extrai URLs e endpoints

**Saída:**
```
=== STRINGS RELACIONADAS A CRYPTO ===
crypto.subtle.importKey
AES-CBC
decrypt
...

=== STRINGS RELACIONADAS A PARÂMETROS ===
user_id
slug
md5_id
...
```

---

### find_crypto_patterns.sh

**Descrição:** Procura padrões específicos de criptografia no código.

**Uso:**
```bash
bash scripts/find_crypto_patterns.sh output/lite.bundle.js > output/crypto_patterns.txt
```

**O que faz:**
- Procura por `crypto.subtle.importKey` com contexto
- Procura por algoritmos AES (AES-CBC, AES-GCM)
- Procura por derivação de chave (deriveKey, pbkdf2)
- Procura por concatenação de strings
- Procura por funções MD5/SHA
- Procura por TextEncoder
- Procura por ArrayBuffer/Uint8Array

**Padrões procurados:**
1. `crypto.subtle.importKey` (±20 linhas de contexto)
2. `AES-` (±10 linhas)
3. Derivação de chave (±15 linhas)
4. Concatenação com parâmetros (50 matches)
5. Funções MD5/SHA (±10 linhas, 100 matches)
6. TextEncoder (±5 linhas)
7. ArrayBuffer/Uint8Array (30 matches)

---

### analyze_importkey.sh

**Descrição:** Análise focada em `crypto.subtle.importKey`.

**Uso:**
```bash
bash scripts/analyze_importkey.sh output/lite.bundle.js > output/importkey_analysis.txt
```

**O que faz:**
- Encontra todas as ocorrências de `importKey`
- Mostra 30 linhas antes e 50 linhas depois
- Procura variáveis usadas em `importKey`
- Procura funções chamadas antes de `importKey`

**Contexto fornecido:**
- 30 linhas antes (para ver preparação da chave)
- 50 linhas depois (para ver uso da chave)
- Variáveis declaradas antes
- Funções chamadas antes

---

### deobfuscate.js

**Descrição:** Deobfuscador JavaScript simples.

**Uso:**
```bash
node scripts/deobfuscate.js output/lite.bundle.js output/lite_deobf.js
```

**O que faz:**
1. Adiciona quebras de linha após `;` e `{}`
2. Expande strings hexadecimais (`\x41` → `A`)
3. Expande unicode (`\u0041` → `A`)
4. Remove espaços múltiplos
5. Adiciona indentação básica
6. Adiciona comentários em seções importantes

**Transformações:**
```javascript
// Antes
function a(b){return c(b);}

// Depois
function a(b) {
  return c(b);
}
```

**Comentários adicionados:**
- `// ⚠️ CRYPTO IMPORT KEY` antes de `crypto.subtle.importKey`
- `// ⚠️ CRYPTO DECRYPT` antes de `crypto.subtle.decrypt`
- `// 🔑 PARÂMETRO: user_id` antes de parâmetros

---

### find_key_formula.py

**Descrição:** Procura a fórmula de derivação da chave AES.

**Uso:**
```bash
python3 scripts/find_key_formula.py output/lite_deobf.js > output/key_formula.txt
```

**O que faz:**
1. Procura contextos de `importKey`
2. Procura concatenações de parâmetros
3. Procura funções de hash
4. Procura usos de TextEncoder
5. Procura variáveis com 'key' no nome
6. Identifica possíveis fórmulas completas

**Padrões procurados:**
- `user_id + slug + md5_id`
- `concat(...)`
- Template strings: `` `${user_id}...` ``
- `MD5(...)`, `md5(...)`, `hash(...)`
- `TextEncoder().encode(...)`
- `var/let/const ...Key = ...`

---

### advanced_analysis.py

**Descrição:** Análise avançada de padrões com geração de testes.

**Uso:**
```bash
python3 scripts/advanced_analysis.py output/lite_deobf.js > output/advanced_analysis.txt
```

**O que faz:**
1. Análise de contextos de `importKey`
2. Identificação de concatenações
3. Identificação de funções de hash
4. Análise de TextEncoder
5. Identificação de variáveis de chave
6. Identificação de fórmulas completas
7. **Geração automática de testes**

**Testes gerados:**
```python
# Valores de teste
user_id = "482120"
slug = "kBJLtxCD3"
md5_id = "28930647"

# Combinações testadas
MD5(user_id + slug + md5_id)
MD5(user_id + md5_id + slug)
MD5(slug + user_id + md5_id)
...
```

**Saída:**
- Contextos encontrados
- Concatenações identificadas
- Funções de hash
- Variáveis de chave
- **Possíveis fórmulas**
- **Testes com hashes calculados**

---

## 🌐 Scripts de Análise Dinâmica

### burp_intercept.sh

**Descrição:** Guia de configuração do Burp Suite.

**Uso:**
```bash
bash scripts/burp_intercept.sh
```

**O que mostra:**
1. Como iniciar Burp Suite
2. Como configurar proxy
3. Como configurar navegador
4. Como instalar certificado CA
5. Como interceptar PlayerEmbedAPI
6. O que procurar nas requisições

**Informações fornecidas:**
- Passos de configuração
- Filtros úteis
- O que procurar (headers, JSON, cookies)
- Dicas de uso

---

### mitmproxy_capture.py

**Descrição:** Script de captura para mitmproxy.

**Uso:**
```bash
mitmproxy -p 8080 -s scripts/mitmproxy_capture.py
```

**O que faz:**
- Intercepta respostas HTTP
- Salva arquivos JavaScript automaticamente
- Detecta conteúdo com crypto
- Salva respostas interessantes
- Extrai padrões específicos

**Detecção automática:**
- Arquivos `.js`
- Conteúdo com palavras-chave: crypto, AES, importKey, user_id, slug, md5_id
- Chaves hexadecimais
- JSON com campos 'key', 'secret', 'token'

**Saída:**
- `output/js_*.js` - Arquivos JavaScript capturados
- `output/mitmproxy_crypto.txt` - Respostas com crypto

---

### wireshark_filter.sh

**Descrição:** Guia de filtros Wireshark.

**Uso:**
```bash
bash scripts/wireshark_filter.sh
```

**O que mostra:**
1. Como iniciar Wireshark
2. Filtros úteis para PlayerEmbedAPI
3. Como exportar objetos HTTP
4. Como analisar pacotes

**Filtros fornecidos:**
```
# Filtrar por domínio
http.host contains "playerembedapi.link"

# Filtrar JavaScript
http.request.uri contains ".js"

# Filtrar respostas com 'key'
http.response contains "key"

# Combinação completa
(http.host contains "playerembedapi" or http.host contains "iamcdn") and ...
```

---

### frida_hook.js

**Descrição:** Script de hook para Frida.

**Uso:**
```bash
frida -U Chrome -l scripts/frida_hook.js
```

**O que faz:**
1. Hook em `crypto.subtle.importKey`
2. Hook em `crypto.subtle.decrypt`
3. Hook em `TextEncoder.encode`
4. Procura e hook em funções MD5

**Informações capturadas:**

#### crypto.subtle.importKey
- `format` (raw, jwk, etc.)
- `keyData` (hex e text)
- `algorithm` (AES-CBC, etc.)
- `extractable`
- `keyUsages`
- Stack trace

#### crypto.subtle.decrypt
- `algorithm`
- `key`
- `data` (primeiros 100 bytes)

#### TextEncoder.encode
- `text` (se contém user_id, slug, md5_id)
- Stack trace

#### Funções MD5
- Argumentos
- Resultado

**Saída:**
```
[+] ═══════════════════════════════════════
[+] crypto.subtle.importKey() chamado!
[+] ═══════════════════════════════════════
[+] Argumentos:
    format: raw
    keyData (hex): 6b424a4c...
    keyData (text): kBJLtxCD3...
    algorithm: {"name":"AES-CBC","length":256}
    ...
```

---

## 📊 Comparação de Scripts

| Script | Tipo | Tempo | Complexidade | Efetividade |
|--------|------|-------|--------------|-------------|
| extract_strings.sh | Estático | 1s | Baixa | Média |
| find_crypto_patterns.sh | Estático | 2s | Baixa | Alta |
| analyze_importkey.sh | Estático | 2s | Baixa | Alta |
| deobfuscate.js | Estático | 5s | Média | Alta |
| find_key_formula.py | Estático | 3s | Média | Alta |
| advanced_analysis.py | Estático | 5s | Alta | Muito Alta |
| mitmproxy_capture.py | Dinâmico | Variável | Média | Alta |
| frida_hook.js | Dinâmico | Variável | Alta | Muito Alta |

---

## 🎯 Ordem Recomendada de Uso

### Análise Básica
1. `extract_strings.sh` - Ver strings relevantes
2. `find_crypto_patterns.sh` - Ver padrões
3. `deobfuscate.js` - Deobfuscar código

### Análise Intermediária
4. `analyze_importkey.sh` - Focar em importKey
5. `find_key_formula.py` - Identificar fórmula

### Análise Avançada
6. `advanced_analysis.py` - Análise completa + testes

### Análise Dinâmica (se necessário)
7. `mitmproxy_capture.py` - Capturar tráfego
8. `frida_hook.js` - Hook em runtime

---

## 💡 Dicas de Uso

### 1. Usar em sequência
```bash
# Executar todos de uma vez
bash run_analysis.sh
```

### 2. Focar nos mais importantes
```bash
# Análise rápida
bash scripts/find_crypto_patterns.sh output/lite.bundle.js | less
python3 scripts/advanced_analysis.py output/lite_deobf.js | less
```

### 3. Combinar resultados
```bash
# Procurar padrão específico em todos os resultados
grep -i "MD5" output/*.txt
```

### 4. Usar ferramentas dinâmicas quando estático falhar
```bash
# Se análise estática não funcionar
mitmproxy -s scripts/mitmproxy_capture.py
# ou
frida -U Chrome -l scripts/frida_hook.js
```

---

## 🔧 Customização

### Adicionar novos padrões

**extract_strings.sh:**
```bash
# Adicionar nova busca
echo "=== MINHA BUSCA ==="
grep -oE "meu_padrao[a-zA-Z0-9_]*" "$FILE" | sort -u
```

**find_crypto_patterns.sh:**
```bash
# Adicionar novo padrão
echo "=== MEU PADRÃO ==="
grep -n -A 10 -B 5 "meu_padrao" "$FILE"
```

**advanced_analysis.py:**
```python
# Adicionar nova análise
def my_analysis(content):
    pattern = r'my_pattern'
    matches = re.finditer(pattern, content)
    return list(matches)
```

---

## 📚 Recursos Adicionais

### Regex
- https://regex101.com/ - Testar expressões regulares

### JavaScript
- https://astexplorer.net/ - Explorar AST JavaScript

### Python
- https://docs.python.org/3/library/re.html - Módulo re

### Frida
- https://frida.re/docs/javascript-api/ - API JavaScript

---

## 🚨 Troubleshooting

### Script não executa
```bash
chmod +x scripts/*.sh
```

### Python script falha
```bash
python3 --version  # Verificar versão
pip3 install --upgrade pip
```

### Node.js script falha
```bash
node --version  # Verificar versão
npm install -g npm
```

### Frida não conecta
```bash
frida-ps -U  # Listar processos
frida --version  # Verificar versão
```

---

## 📞 Suporte

Para problemas com scripts específicos, consulte:
- Documentação principal: `../USAGE.md`
- Exemplos: `../EXAMPLES.md`
- Checklist: `../CHECKLIST.md`
