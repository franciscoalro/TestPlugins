# 🔬 Reverse Engineering Tools - MaxSeries

Ferramentas Python para engenharia reversa de sites de streaming.

## 📦 Instalação

```bash
# Instalar dependências
pip install mitmproxy requests beautifulsoup4

# Instalar Node.js tools (para deobfuscation)
npm install -g js-beautify
```

---

## 🛠️ Ferramentas Disponíveis

### 1. `mitm_capture.py` - Captura de Tráfego HTTP

**Propósito**: Intercepta e registra todo tráfego HTTP relacionado a vídeos.

**Uso**:
```bash
# Terminal 1: Iniciar proxy
mitmproxy -s tools/mitm_capture.py --listen-port 8080

# Terminal 2: Configurar Android para usar proxy
adb shell settings put global http_proxy 192.168.1.100:8080

# Navegar no site e capturar tráfego
# Resultado: captured_requests.json
```

**Output**:
- `captured_requests.json` - Todas as requisições capturadas
- `api_response_*.json` - Respostas de API com tokens/URLs

---

### 2. `deobfuscate_js.py` - Análise de JavaScript

**Propósito**: Extrai e analisa JavaScript de sites, identificando funções de criptografia.

**Uso**:
```bash
python tools/deobfuscate_js.py https://playerembedapi.link
```

**Output**:
- `extracted_script_*.js` - Scripts com crypto detectado
- Console: Resumo de funções encontradas (JWPlayer, CryptoJS, etc.)

**Detecta**:
- Web Crypto API (`crypto.subtle.decrypt`)
- CryptoJS (AES, DES, etc.)
- JWPlayer setup
- Fetch/XHR calls

---

### 3. `playerembedapi_extractor.py` - Protótipo de Extração

**Propósito**: Testa extração pura HTTP antes de portar para Kotlin.

**Uso**:
```bash
python tools/playerembedapi_extractor.py ABC123
```

**Métodos de Extração**:
1. **JWPlayer Setup** - Parse de `jwplayer().setup({...})`
2. **Direct Regex** - Busca padrões de URL (.m3u8, cloudatacdn, etc.)
3. **API Discovery** - Descobre e chama endpoints de API

**Output**:
- Console: URL de vídeo extraída (se sucesso)
- `playerembedapi_debug.html` - HTML salvo para análise manual (se falha)

**Teste da URL**:
```bash
# Se extraiu com sucesso, testar no VLC
vlc "https://cloudatacdn.com/..."
```

---

## 🔄 Workflow de Engenharia Reversa

```
1. Capturar Tráfego (mitm_capture.py)
   ↓
2. Analisar JavaScript (deobfuscate_js.py)
   ↓
3. Prototipar Extração (playerembedapi_extractor.py)
   ↓
4. Portar para Kotlin (PlayerEmbedAPIExtractorV8.kt)
   ↓
5. Testar no CloudStream
```

---

## 📊 Exemplo de Análise Completa

```bash
# 1. Capturar tráfego de uma sessão
mitmproxy -s tools/mitm_capture.py --listen-port 8080
# (Navegar no site via proxy)

# 2. Analisar JavaScript do site
python tools/deobfuscate_js.py https://playerembedapi.link

# 3. Testar extração com ID real
python tools/playerembedapi_extractor.py ABC123

# 4. Se funcionou, a lógica está pronta para Kotlin!
```

---

## 🎯 Casos de Uso

### Descobrir Novo CDN

```bash
# Capturar tráfego
mitmproxy -s tools/mitm_capture.py --listen-port 8080

# Analisar captured_requests.json
cat captured_requests.json | grep -E "(cloudatacdn|googleapis|sssrr)"
```

### Identificar Algoritmo de Criptografia

```bash
# Extrair e analisar JS
python tools/deobfuscate_js.py https://megaembed.link

# Procurar em extracted_script_*.js por:
# - crypto.subtle.decrypt
# - CryptoJS.AES
# - atob/btoa (Base64)
```

### Validar Extração Antes de Implementar

```bash
# Testar com múltiplos IDs
for id in ABC123 XYZ789 DEF456; do
    echo "Testing $id..."
    python tools/playerembedapi_extractor.py $id
done
```

---

## ⚠️ Troubleshooting

### mitmproxy não captura HTTPS

**Problema**: Certificado SSL não confiável no Android.

**Solução**:
```bash
# Instalar certificado do mitmproxy no Android
adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/
# Ir em Settings > Security > Install from storage
```

### JavaScript muito ofuscado

**Problema**: `deobfuscate_js.py` não consegue parsear.

**Solução**:
```bash
# Usar CyberChef online
# https://gchq.github.io/CyberChef/
# Recipe: "JavaScript Beautify" + "Extract URLs"
```

### Extração falha no Python mas funciona no navegador

**Problema**: Site detecta bot via User-Agent ou headers.

**Solução**:
```python
# Editar playerembedapi_extractor.py
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 ...',  # Copiar do navegador real
    'Cookie': 'cf_clearance=...'      # Copiar cookies de sessão
})
```

---

## 📝 Contribuindo

Ao adicionar novas ferramentas:

1. Documentar no README
2. Adicionar exemplos de uso
3. Incluir tratamento de erros
4. Salvar outputs para debug

---

**Última atualização**: 31/01/2026  
**Versão**: 1.0
