# ðŸ”¬ Reverse Engineering Tools - MaxSeries

Ferramentas Python para engenharia reversa de sites de streaming.

## ðŸ“¦ InstalaÃ§Ã£o

```bash
# Instalar dependÃªncias
pip install mitmproxy requests beautifulsoup4

# Instalar Node.js tools (para deobfuscation)
npm install -g js-beautify
```

---

## ðŸ› ï¸ Ferramentas DisponÃ­veis

### 0. alidate_cloudstream_repo.py - ValidaÃ§Ã£o de repo.json/plugins.json

**PropÃ³sito**: Valida o formato dos arquivos epo.json e plugins.json contra o schema oficial do Cloudstream.

**Uso**:
`ash
# ValidaÃ§Ã£o bÃ¡sica
python tools/validate_cloudstream_repo.py --repo repo.json --plugins plugins.json

# Modo estrito (falha com chaves desconhecidas)
python tools/validate_cloudstream_repo.py --repo repo.json --plugins plugins.json --strict

# ValidaÃ§Ã£o com checagem local de arquivos builds/
python tools/validate_cloudstream_repo.py --repo repo.json --plugins plugins.json --check-local
`

**O que valida**:
- epo.json com manifestVersion = 1 e pluginLists vÃ¡lido
- plugins.json como **lista (array)** de plugins
- Campos obrigatÃ³rios e piVersion = 1
- URLs vÃ¡lidas e .cs3 apontando para o arquivo correto
### 1. `mitm_capture.py` - Captura de TrÃ¡fego HTTP

**PropÃ³sito**: Intercepta e registra todo trÃ¡fego HTTP relacionado a vÃ­deos.

**Uso**:
```bash
# Terminal 1: Iniciar proxy
mitmproxy -s tools/mitm_capture.py --listen-port 8080

# Terminal 2: Configurar Android para usar proxy
adb shell settings put global http_proxy 192.168.1.100:8080

# Navegar no site e capturar trÃ¡fego
# Resultado: captured_requests.json
```

**Output**:
- `captured_requests.json` - Todas as requisiÃ§Ãµes capturadas
- `api_response_*.json` - Respostas de API com tokens/URLs

---

### 2. `deobfuscate_js.py` - AnÃ¡lise de JavaScript

**PropÃ³sito**: Extrai e analisa JavaScript de sites, identificando funÃ§Ãµes de criptografia.

**Uso**:
```bash
python tools/deobfuscate_js.py https://playerembedapi.link
```

**Output**:
- `extracted_script_*.js` - Scripts com crypto detectado
- Console: Resumo de funÃ§Ãµes encontradas (JWPlayer, CryptoJS, etc.)

**Detecta**:
- Web Crypto API (`crypto.subtle.decrypt`)
- CryptoJS (AES, DES, etc.)
- JWPlayer setup
- Fetch/XHR calls

---

### 3. `playerembedapi_extractor.py` - ProtÃ³tipo de ExtraÃ§Ã£o

**PropÃ³sito**: Testa extraÃ§Ã£o pura HTTP antes de portar para Kotlin.

**Uso**:
```bash
python tools/playerembedapi_extractor.py ABC123
```

**MÃ©todos de ExtraÃ§Ã£o**:
1. **JWPlayer Setup** - Parse de `jwplayer().setup({...})`
2. **Direct Regex** - Busca padrÃµes de URL (.m3u8, cloudatacdn, etc.)
3. **API Discovery** - Descobre e chama endpoints de API

**Output**:
- Console: URL de vÃ­deo extraÃ­da (se sucesso)
- `playerembedapi_debug.html` - HTML salvo para anÃ¡lise manual (se falha)

**Teste da URL**:
```bash
# Se extraiu com sucesso, testar no VLC
vlc "https://cloudatacdn.com/..."
```

---

## ðŸ”„ Workflow de Engenharia Reversa

```
1. Capturar TrÃ¡fego (mitm_capture.py)
   â†“
2. Analisar JavaScript (deobfuscate_js.py)
   â†“
3. Prototipar ExtraÃ§Ã£o (playerembedapi_extractor.py)
   â†“
4. Portar para Kotlin (PlayerEmbedAPIExtractorV8.kt)
   â†“
5. Testar no CloudStream
```

---

## ðŸ“Š Exemplo de AnÃ¡lise Completa

```bash
# 1. Capturar trÃ¡fego de uma sessÃ£o
mitmproxy -s tools/mitm_capture.py --listen-port 8080
# (Navegar no site via proxy)

# 2. Analisar JavaScript do site
python tools/deobfuscate_js.py https://playerembedapi.link

# 3. Testar extraÃ§Ã£o com ID real
python tools/playerembedapi_extractor.py ABC123

# 4. Se funcionou, a lÃ³gica estÃ¡ pronta para Kotlin!
```

---

## ðŸŽ¯ Casos de Uso

### Descobrir Novo CDN

```bash
# Capturar trÃ¡fego
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

### Validar ExtraÃ§Ã£o Antes de Implementar

```bash
# Testar com mÃºltiplos IDs
for id in ABC123 XYZ789 DEF456; do
    echo "Testing $id..."
    python tools/playerembedapi_extractor.py $id
done
```

---

## âš ï¸ Troubleshooting

### mitmproxy nÃ£o captura HTTPS

**Problema**: Certificado SSL nÃ£o confiÃ¡vel no Android.

**SoluÃ§Ã£o**:
```bash
# Instalar certificado do mitmproxy no Android
adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/
# Ir em Settings > Security > Install from storage
```

### JavaScript muito ofuscado

**Problema**: `deobfuscate_js.py` nÃ£o consegue parsear.

**SoluÃ§Ã£o**:
```bash
# Usar CyberChef online
# https://gchq.github.io/CyberChef/
# Recipe: "JavaScript Beautify" + "Extract URLs"
```

### ExtraÃ§Ã£o falha no Python mas funciona no navegador

**Problema**: Site detecta bot via User-Agent ou headers.

**SoluÃ§Ã£o**:
```python
# Editar playerembedapi_extractor.py
self.session.headers.update({
    'User-Agent': 'Mozilla/5.0 ...',  # Copiar do navegador real
    'Cookie': 'cf_clearance=...'      # Copiar cookies de sessÃ£o
})
```

---

## ðŸ“ Contribuindo

Ao adicionar novas ferramentas:

1. Documentar no README
2. Adicionar exemplos de uso
3. Incluir tratamento de erros
4. Salvar outputs para debug

---

**Ãšltima atualizaÃ§Ã£o**: 31/01/2026  
**VersÃ£o**: 1.0
