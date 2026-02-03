# GUIA DAS FERRAMENTAS KALI - PlayerEmbedAPI Analysis

## Instalação

```bash
# Instalar dependencias
pip install requests colorama beautifulsoup4

# Opcional: para browser automation
pip install playwright
playwright install
```

---

## Ferramentas Disponíveis

### 1. kali_master_analyzer.py (RECOMENDADO)
**Descrição:** Suite completa de análise automatizada

**Uso:**
```bash
python kali_master_analyzer.py --url "https://playerembedapi.link/?v=xxx"
```

**Output:**
- `kali_analysis_XXX/response.html` - HTML da página
- `kali_analysis_XXX/core_bundle.js` - JavaScript analisado
- `kali_analysis_XXX/full_report.json` - Relatório completo

**Funcionalidades:**
- Download do HTML
- Extração de dados (slug, md5_id, user_id)
- Download e análise do core.bundle.js
- Construção de URLs CDN
- Análise de headers de segurança

---

### 2. kali_js_deobfuscator.py
**Descrição:** Deobfuscador e analisador de JavaScript

**Uso:**
```bash
python kali_js_deobfuscator.py --file core.bundle.js --output js_analysis.json
```

**Output:**
- Tipo de ofuscação detectada
- Strings extraídas
- Funções encontradas
- Chamadas de criptografia
- Endpoints descobertos

**Exemplo de resultado:**
```json
{
  "obfuscation_type": ["Javascript Obfuscator", "Obfuscator.io"],
  "strings_count": 1877,
  "has_sotrym": true,
  "crypto_calls": ["AES-CTR", "btoa"]
}
```

---

### 3. kali_request_manipulator.py
**Descrição:** Manipulador de requisições HTTP

**Modo interativo:**
```bash
python kali_request_manipulator.py --url "https://playerembedapi.link/?v=xxx" --interactive
```

**Comandos disponíveis:**
- `get` - GET básico
- `headers` - Testar bypass headers
- `uas` - Testar User-Agents
- `methods` - Testar métodos HTTP
- `extract` - Extrair URLs de vídeo
- `custom` - Requisição customizada

**Testes automáticos:**
```bash
# Testar bypass de headers
python kali_request_manipulator.py --url "URL" --test-bypass

# Extrair URLs de vídeo
python kali_request_manipulator.py --url "URL" --extract
```

---

### 4. kali_param_fuzzer.py
**Descrição:** Fuzzing de parâmetros (tipo wfuzz/ffuf)

**Uso:**
```bash
# Fuzzing de IDs de vídeo
python kali_param_fuzzer.py --url "https://playerembedapi.link/?v=FUZZ" --mode video

# Descoberta de endpoints
python kali_param_fuzzer.py --url "https://playerembedapi.link/FUZZ" --mode endpoint

# Com wordlist customizada
python kali_param_fuzzer.py --url "URL/FUZZ" --wordlist wordlist.txt --threads 20
```

**Payloads incluídos:**
- IDs numéricos: `1`, `100`, `999999`
- IDs alfanuméricos: `abc123`, `test123`
- Bypass: `../`, `%2e%2e%2f`, `null`, `undefined`

---

### 5. kali_session_extractor.py
**Descrição:** Extrator de sessões e cookies

**Uso:**
```bash
# Analisar sessão
python kali_session_extractor.py --url "URL" --save session.json

# Testar session fixation
python kali_session_extractor.py --url "URL" --test-fixation

# Extrair com browser (requer Playwright)
python kali_session_extractor.py --url "URL" --browser
```

**Funcionalidades:**
- Extração de cookies
- Decodificação de JWT tokens
- Análise de flags de segurança
- Teste de session fixation
- Replay de sessões

---

### 6. kali_mitm_proxy.py
**Descrição:** Proxy MITM para interceptação (tipo Burp Suite)

**Uso:**
```bash
# Iniciar proxy
python kali_mitm_proxy.py --port 8080 --target playerembedapi.link

# Com modificação de headers
python kali_mitm_proxy.py --port 8080 --modify-header "X-Forwarded-For:127.0.0.1"
```

**Configuração do navegador:**
- Proxy HTTP: `127.0.0.1:8080`
- Ignorar erros SSL

**Funcionalidades:**
- Interceptar requests/responses
- Modificar headers em tempo real
- Extrair URLs de vídeo automaticamente
- Salvar sessão em JSON

---

## Fluxo de Análise Recomendado

### Fluxo Básico (5 minutos)
```bash
# 1. Análise completa automatizada
python kali_master_analyzer.py --url "https://playerembedapi.link/?v=xxx"

# 2. Analisar JS baixado
python kali_js_deobfuscator.py --file kali_analysis_xxx/core_bundle.js

# 3. Verificar relatório
ls kali_analysis_xxx/
```

### Fluxo Avançado (30 minutos)
```bash
# 1. Análise master
python kali_master_analyzer.py --url "URL"

# 2. Extrair e analisar sessão
python kali_session_extractor.py --url "URL" --test-fixation

# 3. Fuzzing de parâmetros
python kali_param_fuzzer.py --url "URL/?v=FUZZ" --mode video

# 4. Testar manipulação de requests
python kali_request_manipulator.py --url "URL" --interactive

# 5. Iniciar proxy para interceptação
python kali_mitm_proxy.py --port 8080 --target playerembedapi.link
```

---

## Casos de Uso

### Caso 1: Extração Rápida de Dados
```bash
python kali_master_analyzer.py --url "https://playerembedapi.link/?v=kBJLtxCD3"
# Resultado: slug, md5_id, URLs CDN construídas
```

### Caso 2: Análise de Criptografia
```bash
# Baixar e analisar JS
python kali_master_analyzer.py --url "URL"
python kali_js_deobfuscator.py --file kali_analysis_xxx/core_bundle.js --beautify

# Procurar por "AES", "decrypt", "crypto"
grep -i "aes\|decrypt\|crypto" js_analysis.json
```

### Caso 3: Descoberta de Endpoints
```bash
# Fuzzing de endpoints
python kali_param_fuzzer.py --url "https://playerembedapi.link/FUZZ" --mode endpoint

# Ou usar request manipulator
python kali_request_manipulator.py --url "https://playerembedapi.link/api/v1/" --interactive
```

### Caso 4: Interceptação de Vídeo
```bash
# Terminal 1: Iniciar proxy
python kali_mitm_proxy.py --port 8080

# Terminal 2: Acessar URL via proxy
curl -x http://127.0.0.1:8080 "https://playerembedapi.link/?v=xxx"

# Ver URLs interceptadas
# Salvas em: mitm_session_xxx.json
```

---

## Interpretação de Resultados

### Dados Extraídos
```json
{
  "slug": "kBJLtxCD3",
  "md5_id": 28930647,
  "user_id": 482120
}
```

**Significado:**
- `slug`: Identificador único do vídeo
- `md5_id`: ID numérico usado no CDN
- `user_id`: ID do usuário (possível watermark)

### URLs CDN Construídas
```
https://{slug}.sssrr.org/sora/{md5_id}/
https://cdn.sssrr.org/sora/{md5_id}/
```

**Como usar:**
```bash
curl -H "Referer: https://playerembedapi.link/" \
     "https://kBJLtxCD3.sssrr.org/sora/28930647/"
```

### Headers de Segurança
```
X-Frame-Options: N/A          <- Vulnerável a clickjacking
X-XSS-Protection: N/A         <- Sem proteção XSS
Content-Security-Policy: N/A  <- Sem CSP
```

---

## Solução de Problemas

### Erro de SSL
```bash
# Desabilitar verificação SSL (já configurado nas ferramentas)
# Ou instalar certificados
pip install certifi
```

### Timeout
```bash
# Aumentar timeout
python kali_master_analyzer.py --url "URL"
# Default: 30s (configurável no código)
```

### Playwright não encontrado
```bash
pip install playwright
playwright install chromium
```

---

## Integração com MaxSeries Provider

### Exemplo de implementação
```kotlin
class PlayerEmbedAPIExtractor {
    
    suspend fun extract(url: String, callback: (ExtractorLink) -> Unit): Boolean {
        // 1. HTTP direto
        val response = app.get(url, timeout = 30)
        
        // 2. Extrair dados
        val datas = extractDatas(response.text)
        
        // 3. Construir URL CDN
        val cdnUrl = "https://${datas.slug}.sssrr.org/sora/${datas.md5Id}/"
        
        // 4. WebView para obter URL final
        val resolver = WebViewResolver(
            interceptUrl = Regex("""(?i)(sssrr\.org|\.m3u8)"""),
            timeout = 35_000L
        )
        
        val finalResponse = app.get(cdnUrl, interceptor = resolver)
        
        // 5. Retornar link
        callback(newExtractorLink("PlayerEmbedAPI", "HD", finalResponse.url))
        return true
    }
}
```

---

## Recursos Adicionais

### Arquivos de Referência
- `HACKER_REPORT_PLAYEREMBEDAPI.md` - Relatório técnico completo
- `KALI_TOOLS_REPORT.md` - Resultados das ferramentas
- `PlayerEmbedAPIExtractor.kt` - Implementação Kotlin

### Wordlists
Criar arquivo `wordlist.txt` para fuzzing:
```
api
sora
future
video
player
stream
v1
v2
test
dev
```

---

## Contato

Para mais informações ou problemas:
- Verificar logs em `kali_analysis_xxx/`
- Executar com `python -v` para debug
- Usar modo interativo para testes manuais

---

*Ferramentas criadas para pesquisa de segurança legítima*
*White Hat Security Research*
