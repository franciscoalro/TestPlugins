# MegaEmbed - Próximos Passos

## 📊 O Que Descobrimos

### ✅ Confirmado
1. **Fluxo da API**: Mapeamos todas as chamadas (info → video → player)
2. **Token Format**: Token hex de ~512 caracteres
3. **Criptografia**: AES-CBC confirmado no código JavaScript
4. **Resposta**: Hex string de 2500 bytes criptografado
5. **Entropia**: 7.92 bits/byte (alta = criptografado)

### ❌ Ainda Desconhecido
1. **Chave AES**: Não encontramos a chave hardcoded
2. **IV (Initialization Vector)**: Desconhecido
3. **Algoritmo do Token**: Como o token longo é gerado

## 🎯 3 Opções para Resolver

### Opção 1: Capturar Chave no Browser (MAIS RÁPIDO) ⭐

**Tempo estimado**: 5 minutos

**Passos**:
1. Abra https://megaembed.link/#3wnuij no Chrome
2. Abra DevTools (F12) → Console
3. Cole o conteúdo de `capture-megaembed-key-devtools.js`
4. Pressione Enter
5. Recarregue a página (F5)
6. Aguarde o vídeo carregar
7. A chave e IV aparecerão no console

**Resultado esperado**:
```
🔑 crypto.subtle.importKey() CHAMADO:
   📦 Key Data (hex): a1b2c3d4e5f6...
   📦 Key Length: 16 bytes

🔓 crypto.subtle.decrypt() CHAMADO:
   🔢 IV (hex): 0123456789abcdef...
   🔢 IV Length: 16 bytes
   
🎯 JSON completo: {"url": "https://srcf.marvellaholdings.sbs/..."}
```

**Depois**:
```python
# Use a chave capturada em decrypt-megaembed-response.py
key_hex = "a1b2c3d4e5f6..."  # Do console
iv_hex = "0123456789abcdef..."  # Do console

key = binascii.unhexlify(key_hex)
iv = binascii.unhexlify(iv_hex)

cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)
print(decrypted.decode('utf-8'))
```

---

### Opção 2: Usar WebView no CloudStream (MAIS FÁCIL) ⭐⭐

**Tempo estimado**: 30 minutos

**Vantagens**:
- Não precisa reverse engineering
- Funciona mesmo se mudarem a chave
- Código simples

**Desvantagens**:
- WebView é pesado (~50MB RAM)
- Mais lento que HTTP direto
- Pode ter problemas de compatibilidade

**Implementação**:
```kotlin
// MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/MegaEmbedExtractor.kt

class MegaEmbedExtractor : ExtractorApi() {
    override val name = "MegaEmbed"
    override val mainUrl = "https://megaembed.link"
    override val requiresReferer = true

    override suspend fun getUrl(
        url: String,
        referer: String?,
        subtitleCallback: (SubtitleFile) -> Unit,
        callback: (ExtractorLink) -> Unit
    ) {
        // Usar WebView para deixar o JavaScript descriptografar
        val webView = WebView(context)
        webView.settings.javaScriptEnabled = true
        
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? {
                val requestUrl = request.url.toString()
                
                // Interceptar URL do m3u8 (arquivo .txt)
                if (requestUrl.contains("cf-master") || 
                    requestUrl.endsWith(".txt")) {
                    
                    callback(
                        ExtractorLink(
                            name,
                            name,
                            requestUrl,
                            mainUrl,
                            Qualities.Unknown.value,
                            INFER_TYPE
                        )
                    )
                    
                    // Parar WebView
                    view.stopLoading()
                }
                
                return super.shouldInterceptRequest(view, request)
            }
        }
        
        webView.loadUrl(url)
    }
}
```

---

### Opção 3: Reverse Engineering Completo (MAIS DIFÍCIL) ⭐⭐⭐

**Tempo estimado**: 4-8 horas

**Passos**:
1. Beautify o JavaScript minificado
2. Encontrar a função de geração do token
3. Encontrar a chave hardcoded
4. Replicar o algoritmo em Kotlin
5. Testar e validar

**Ferramentas**:
```bash
# Beautify
npx js-beautify megaembed_index.js > megaembed_readable.js

# Procurar funções relevantes
grep -A 100 "location.hash" megaembed_readable.js
grep -A 100 "player.*token" megaembed_readable.js
grep -A 100 "crypto.subtle" megaembed_readable.js
```

**Não recomendado porque**:
- Muito trabalho
- Pode quebrar quando atualizarem o site
- Outros 9 players já funcionam

---

## 💡 Recomendação Final

### Para Teste Rápido (5 min)
Use **Opção 1** (DevTools) para capturar a chave e confirmar que conseguimos descriptografar.

### Para Produção
**NÃO IMPLEMENTE** MegaEmbed porque:

1. ✅ **9 outros players funcionam** perfeitamente
2. ✅ **MegaEmbed já é prioridade 10** (última opção)
3. ⚠️ **WebView é pesado** e lento
4. ⚠️ **Manutenção constante** se fizer reverse engineering
5. ⚠️ **Pode quebrar** a qualquer momento

**Mantenha como está**: MegaEmbed como fallback, outros players como prioridade.

---

## 📝 Checklist

### Se quiser testar (Opção 1)
- [ ] Abrir https://megaembed.link/#3wnuij
- [ ] Abrir DevTools (F12)
- [ ] Colar `capture-megaembed-key-devtools.js`
- [ ] Recarregar página
- [ ] Copiar chave e IV do console
- [ ] Testar descriptografia em Python
- [ ] Documentar resultado

### Se quiser implementar (Opção 2)
- [ ] Criar `MegaEmbedExtractor.kt`
- [ ] Implementar WebView
- [ ] Interceptar requisições
- [ ] Capturar URL do m3u8
- [ ] Testar no CloudStream
- [ ] Validar com múltiplos vídeos

### Se quiser ignorar (RECOMENDADO)
- [x] Documentar descobertas
- [x] Manter MegaEmbed como prioridade 10
- [x] Focar em melhorar outros extractors
- [x] Monitorar se usuários reclamam

---

## 📚 Arquivos Criados

### Análise
- `MEGAEMBED_BURP_ANALYSIS.md` - Análise completa do Burp Suite
- `MEGAEMBED_SOLUTION.md` - Solução e recomendações
- `MEGAEMBED_PROXIMOS_PASSOS.md` - Este arquivo

### Scripts Python
- `analyze-megaembed-response.py` - Analisa resposta criptografada
- `find-decrypt-key.py` - Procura chave no JS
- `extract-megaembed-key.py` - Extrai chaves hardcoded
- `decrypt-megaembed-response.py` - Tenta descriptografar

### Scripts JavaScript
- `capture-megaembed-key-devtools.js` - Captura chave no browser

### Dados
- `sniffer_results.json` - Captura do Burp Suite
- `megaembed_index.js` - JavaScript completo (880KB)

---

## 🔗 Links Úteis

- **Burp Suite Export**: `logsburpsuit/megaembed_burp_export.xml`
- **Provider Atual**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/MaxSeriesProvider.kt`
- **Extractors**: `MaxSeries/src/main/kotlin/com/franciscoalro/maxseries/extractors/`

---

## ❓ Dúvidas?

Se precisar de ajuda:
1. Leia `MEGAEMBED_BURP_ANALYSIS.md` para entender o fluxo
2. Use `capture-megaembed-key-devtools.js` para capturar a chave
3. Teste descriptografia com `decrypt-megaembed-response.py`
4. Se ainda tiver dúvidas, me avise!
