# 📚 Exemplos Práticos

## 🎯 Cenário 1: Análise Rápida (5 minutos)

```bash
# No Windows, abrir PowerShell e executar:
wsl

# Navegar até o diretório
cd /mnt/c/caminho/para/aes-key-discovery

# Executar teste rápido
bash quick_test.sh

# Ver resultados
cat output/quick_importkey.txt
cat output/quick_params.txt
```

**Resultado esperado:**
- Arquivo `lite.bundle.js` baixado
- Ocorrências de `importKey` encontradas
- Parâmetros `user_id`, `slug`, `md5_id` identificados

---

## 🎯 Cenário 2: Análise Completa (15-30 minutos)

```bash
# Executar análise completa
bash run_analysis.sh

# Ver fórmula identificada
cat output/key_formula.txt | less

# Ver análise avançada
cat output/advanced_analysis.txt | less

# Procurar por fórmulas específicas
grep -i "possível fórmula" output/advanced_analysis.txt
grep -i "MD5" output/advanced_analysis.txt
```

**Resultado esperado:**
- Código JavaScript deobfuscado
- Padrões de concatenação identificados
- Possíveis fórmulas listadas
- Testes sugeridos com valores conhecidos

---

## 🎯 Cenário 3: Interceptação com Burp Suite (30-60 minutos)

### Passo 1: Configurar Burp Suite

```bash
# Iniciar Burp Suite
burpsuite &
```

### Passo 2: Configurar Firefox

1. Abrir Firefox
2. Preferences → Network Settings
3. Manual proxy configuration:
   - HTTP Proxy: `127.0.0.1`
   - Port: `8080`
   - Use for all protocols: ✓

### Passo 3: Instalar certificado CA

1. Abrir: `http://burp`
2. Download CA Certificate
3. Firefox → Preferences → Certificates → Import
4. Trust for websites: ✓

### Passo 4: Interceptar tráfego

1. Burp Suite → Proxy → Intercept is on
2. Firefox → Abrir: `https://playerembedapi.link/?v=kBJLtxCD3`
3. Burp Suite → HTTP history

### Passo 5: Analisar requisições

Procurar por:

```
# Requisições interessantes
GET /player-v2/lite.bundle.js
GET /api/key
GET /api/decrypt
POST /api/video

# Headers interessantes
X-Key: ...
X-Token: ...
Authorization: ...

# Respostas JSON
{
  "key": "...",
  "secret": "...",
  "token": "..."
}
```

### Passo 6: Salvar resultados

1. Right-click na requisição → Save item
2. Salvar em: `output/burp_request.txt`

**Resultado esperado:**
- Requisições HTTP capturadas
- Headers customizados identificados
- Possível chave ou token encontrado

---

## 🎯 Cenário 4: Captura com mitmproxy (20-40 minutos)

### Passo 1: Instalar mitmproxy

```bash
pip3 install mitmproxy
```

### Passo 2: Executar com script

```bash
# Iniciar mitmproxy com script de captura
mitmproxy -p 8080 -s scripts/mitmproxy_capture.py
```

### Passo 3: Configurar navegador

Firefox → Proxy: `127.0.0.1:8080`

### Passo 4: Abrir PlayerEmbedAPI

```
https://playerembedapi.link/?v=kBJLtxCD3
```

### Passo 5: Ver capturas

```bash
# Ver arquivo de saída
cat output/mitmproxy_crypto.txt | less

# Procurar por padrões
grep -i "key" output/mitmproxy_crypto.txt
grep -i "crypto" output/mitmproxy_crypto.txt
```

**Resultado esperado:**
- Arquivos JavaScript salvos em `output/js_*.js`
- Respostas com crypto capturadas
- Padrões extraídos automaticamente

---

## 🎯 Cenário 5: Hook Dinâmico com Frida (Avançado)

### Passo 1: Instalar Frida

```bash
pip3 install frida frida-tools
```

### Passo 2: Iniciar Chrome

```bash
# Iniciar Chrome (ou usar Chrome já aberto)
google-chrome &
```

### Passo 3: Executar hook

```bash
# Hook no Chrome
frida -U Chrome -l scripts/frida_hook.js
```

### Passo 4: Abrir PlayerEmbedAPI no Chrome

```
https://playerembedapi.link/?v=kBJLtxCD3
```

### Passo 5: Ver logs

O terminal do Frida mostrará:

```
[+] ═══════════════════════════════════════
[+] crypto.subtle.importKey() chamado!
[+] ═══════════════════════════════════════
[+] Argumentos:
    format: raw
    keyData (hex): 6b424a4c7478434433343832313230323839333036343
    keyData (text): kBJLtxCD3482120289306...
    algorithm: {"name":"AES-CBC","length":256}
    extractable: false
    keyUsages: ["decrypt"]

[+] Stack trace:
    at importKey (...)
    at decrypt (...)
    ...
```

**Resultado esperado:**
- Chamadas para `crypto.subtle.importKey` capturadas
- Chave AES em hexadecimal e texto
- Stack trace mostrando onde a chave é gerada

---

## 🎯 Cenário 6: Análise Manual do Código (60+ minutos)

### Passo 1: Deobfuscar código

```bash
# Executar análise completa primeiro
bash run_analysis.sh
```

### Passo 2: Abrir código deobfuscado

```bash
# Usar editor de texto
nano output/lite_deobf.js
# ou
code output/lite_deobf.js
```

### Passo 3: Procurar por importKey

```bash
# Procurar e ver contexto
grep -n -A 50 -B 20 "importKey" output/lite_deobf.js | less
```

### Passo 4: Identificar variável da chave

Procurar por algo como:

```javascript
// Exemplo 1
var key = user_id + slug + md5_id;
crypto.subtle.importKey("raw", encoder.encode(key), ...);

// Exemplo 2
var keyString = MD5(user_id + slug + md5_id);
var keyData = hexToBytes(keyString);
crypto.subtle.importKey("raw", keyData, ...);

// Exemplo 3
var combined = `${slug}${user_id}${md5_id}`;
var hashed = await crypto.subtle.digest("SHA-256", encoder.encode(combined));
crypto.subtle.importKey("raw", hashed, ...);
```

### Passo 5: Testar fórmula

```bash
# Criar script de teste
cat > test.sh << 'EOF'
#!/bin/bash

USER_ID="482120"
SLUG="kBJLtxCD3"
MD5_ID="28930647"

# Testar fórmula identificada
echo -n "${SLUG}${USER_ID}${MD5_ID}" | md5sum
EOF

chmod +x test.sh
bash test.sh
```

**Resultado esperado:**
- Fórmula exata identificada
- Ordem dos parâmetros descoberta
- Hash (se aplicável) identificado

---

## 🎯 Cenário 7: Validação da Fórmula

### Passo 1: Implementar função de geração de chave

```javascript
// test_key.js
const crypto = require('crypto');

function generateKey(user_id, slug, md5_id) {
    // Testar diferentes combinações
    const combinations = [
        user_id + slug + md5_id,
        user_id + md5_id + slug,
        slug + user_id + md5_id,
        slug + md5_id + user_id,
        md5_id + user_id + slug,
        md5_id + slug + user_id
    ];
    
    console.log("Testando combinações:");
    combinations.forEach((combo, i) => {
        const md5 = crypto.createHash('md5').update(combo).digest('hex');
        console.log(`${i + 1}. ${combo}`);
        console.log(`   MD5: ${md5}\n`);
    });
}

// Valores de teste
generateKey("482120", "kBJLtxCD3", "28930647");
```

### Passo 2: Executar teste

```bash
node test_key.js
```

### Passo 3: Comparar com chave capturada

Comparar os hashes gerados com a chave capturada pelo Frida ou Burp Suite.

**Resultado esperado:**
- Uma das combinações gera a chave correta
- Fórmula validada

---

## 🎯 Cenário 8: Decriptação Completa

### Passo 1: Implementar decriptação

```javascript
// decrypt.js
const crypto = require('crypto');

async function decryptMedia(encryptedData, user_id, slug, md5_id) {
    // Gerar chave (usar fórmula descoberta)
    const keyString = slug + user_id + md5_id; // Exemplo
    const keyHash = crypto.createHash('md5').update(keyString).digest('hex');
    
    // Converter para bytes
    const keyBytes = Buffer.from(keyHash, 'hex');
    
    // Importar chave
    const key = await crypto.subtle.importKey(
        'raw',
        keyBytes,
        { name: 'AES-CBC', length: 256 },
        false,
        ['decrypt']
    );
    
    // Decriptar
    const decrypted = await crypto.subtle.decrypt(
        { name: 'AES-CBC', iv: /* IV aqui */ },
        key,
        encryptedData
    );
    
    return decrypted;
}
```

### Passo 2: Testar com dados reais

```bash
node decrypt.js
```

**Resultado esperado:**
- Dados decriptados com sucesso
- URL do vídeo obtida

---

## 💡 Dicas Gerais

### 1. Começar pelo mais simples

```bash
quick_test.sh → run_analysis.sh → Burp Suite → Frida
```

### 2. Documentar tudo

```bash
# Criar arquivo de notas
cat > notes.txt << EOF
Data: $(date)
Vídeo testado: kBJLtxCD3
user_id: 482120
slug: kBJLtxCD3
md5_id: 28930647

Descobertas:
- ...
EOF
```

### 3. Testar com múltiplos vídeos

```bash
# Testar com diferentes vídeos
for video in kBJLtxCD3 anotherID yetAnother; do
    echo "Testando: $video"
    # ... análise ...
done
```

### 4. Comparar resultados

```bash
# Comparar padrões entre diferentes vídeos
diff output/video1_analysis.txt output/video2_analysis.txt
```

---

## 🚨 Troubleshooting

### Problema: "Permission denied"

```bash
chmod +x *.sh
chmod +x scripts/*.sh
```

### Problema: "Command not found"

```bash
# Instalar dependências
sudo apt-get update
sudo apt-get install -y curl jq python3 nodejs npm
```

### Problema: Burp Suite não intercepta HTTPS

```bash
# Reinstalar certificado CA
# Firefox → Preferences → Certificates → View Certificates
# Authorities → Delete "PortSwigger CA"
# Reimportar de http://burp
```

### Problema: mitmproxy não captura nada

```bash
# Verificar proxy no navegador
# Verificar se mitmproxy está rodando na porta correta
netstat -tulpn | grep 8080
```

---

## 📞 Próximos Passos

Após descobrir a fórmula:

1. ✅ Documentar a fórmula exata
2. ✅ Criar função de geração de chave
3. ✅ Testar com múltiplos vídeos
4. ✅ Implementar decriptação completa
5. ✅ Validar com dados reais
