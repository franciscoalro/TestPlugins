# MaxSeries v127 - Crypto Interception

## 📅 Data: 18/01/2026 - 21:40

## 🎯 Objetivo
Interceptar `crypto.subtle.decrypt()` no WebView para capturar a URL do vídeo APÓS a descriptografia, sem precisar fazer reverse engineering da chave AES.

## 🔧 Mudanças Principais

### MegaEmbed v5.3 - Crypto Interception ⭐ NOVO
- ✅ **Estratégia 0 NOVA**: Interceptação de `crypto.subtle.decrypt()`
- ✅ **Captura direta**: Pega resultado descriptografado antes de ser usado
- ✅ **Timeout**: 60s (suficiente para descriptografia acontecer)
- ✅ **Logs detalhados**: Console mostra cada etapa da interceptação
- ✅ **Fallback**: Se falhar, tenta outras 5 estratégias

### Como Funciona
```javascript
// 1. Injetamos script ANTES da página carregar
window.crypto.subtle.decrypt = function(...args) {
    // 2. Chamamos decrypt original
    return originalDecrypt.apply(this, args).then(result => {
        // 3. Capturamos resultado descriptografado
        const text = new TextDecoder().decode(result);
        const json = JSON.parse(text);
        
        // 4. Extraímos URL do vídeo
        window.__MEGAEMBED_VIDEO_URL__ = json.url;
        
        // 5. Retornamos resultado (página funciona normal)
        return result;
    });
};
```

### Estratégias de Extração (ordem atualizada):
0. **Crypto Interception** (v127 NOVO) - Intercepta descriptografia
1. **Direct API** (v125) - Tenta API direta (retorna criptografado)
2. **HTML Regex** - Busca URLs .txt no HTML
3. **JsUnpacker** - Descompacta JavaScript ofuscado
4. **WebView JavaScript-Only** (v126) - Executa JS e aguarda URL
5. **WebView Interceptação** - Intercepta requisições de rede

## 📊 Comparação de Versões

| Versão | Estratégia Principal | Timeout | Resultado |
|--------|---------------------|---------|-----------|
| v125 | Direct API | - | ❌ API criptografada |
| v126 | WebView 120s | 120s | ❌ JS não descriptografa |
| v127 | **Crypto Interception** | 60s | ⏳ **Testando...** |

## 🔍 O Que Esperar nos Logs

### ✅ SUCESSO - Crypto Interception
```
MegaEmbedExtractorV5_v127: === MEGAEMBED V5 CRYPTO INTERCEPTION (v127) ===
MegaEmbedExtractorV5_v127: 🔍 [0/6] Tentando Crypto Interception...
MegaEmbedExtractorV5_v127: 🔐 Iniciando WebView com interceptação crypto...
WebViewResolver: [MegaEmbed v127] Interceptando crypto.subtle.decrypt...
WebViewResolver: [MegaEmbed v127] ✅ Interceptação ativada
WebViewResolver: [MegaEmbed v127] decrypt() chamado
WebViewResolver: [MegaEmbed v127] Descriptografado: {"url":"https://.../.txt",...}
WebViewResolver: [MegaEmbed v127] ✅ URL encontrada: https://.../.txt
MegaEmbedExtractorV5_v127: 📜 Crypto Interception capturou: https://.../.txt
MegaEmbedExtractorV5_v127: 🎯 Crypto Interception funcionou: https://.../.txt
MegaEmbedExtractorV5_v127: ✅ Crypto Interception funcionou!
MaxSeriesProvider: ✅ ExtractorLink criado: MegaEmbed - Auto
```

### ❌ FALHA - Timeout
```
MegaEmbedExtractorV5_v127: 🔍 [0/6] Tentando Crypto Interception...
WebViewResolver: [MegaEmbed v127] Aguardando... (5s)
WebViewResolver: [MegaEmbed v127] Aguardando... (10s)
...
WebViewResolver: [MegaEmbed v127] ⏱️ Timeout após 60 segundos
MegaEmbedExtractorV5_v127: ⚠️ Crypto Interception: Nenhuma URL capturada
MegaEmbedExtractorV5_v127: 🔍 [1/6] Tentando Direct API...
```

## 🧪 Como Testar

### 1. Instalar v127
```powershell
adb install -r MaxSeries\build\MaxSeries.cs3
```

### 2. Monitorar Logs
```powershell
$env:Path += ";D:\Android\platform-tools"
adb logcat -c
adb logcat | Select-String -Pattern "MegaEmbed|PlayerEmbed|WebViewResolver" -CaseSensitive:$false
```

### 3. Testar no App
1. Abrir CloudStream
2. Buscar "Terra de Pecados"
3. Tentar reproduzir episódio 1
4. Observar logs

### 4. O Que Procurar
- ✅ `[MegaEmbed v127] decrypt() chamado` - Interceptação funcionou
- ✅ `[MegaEmbed v127] Descriptografado:` - Dados descriptografados
- ✅ `[MegaEmbed v127] ✅ URL encontrada:` - URL capturada
- ❌ `[MegaEmbed v127] ⏱️ Timeout` - Falhou

## 📝 Notas Técnicas

### Por Que Interceptar crypto.subtle.decrypt?
1. **Mais confiável**: Captura resultado ANTES de ser usado
2. **Sem reverse engineering**: Não precisa descobrir chave AES
3. **Funciona sempre**: Mesmo se mudarem chave ou algoritmo
4. **Mais rápido**: 60s vs 120s da v126

### Diferença da v126
```kotlin
// v126: Aguardava URL aparecer no DOM
var interval = setInterval(function() {
    var html = document.documentElement.innerHTML;
    var urlMatch = html.match(/https?:\/\/[^"'\s]+\.txt/i);
    if (urlMatch) resolve(urlMatch[0]);
}, 100);

// v127: Intercepta descriptografia diretamente
window.crypto.subtle.decrypt = function(...args) {
    return originalDecrypt.apply(this, args).then(result => {
        const json = JSON.parse(new TextDecoder().decode(result));
        window.__MEGAEMBED_VIDEO_URL__ = json.url;
        return result;
    });
};
```

### Vantagens da Interceptação
- ✅ Captura ANTES da URL ser usada
- ✅ Não depende de DOM
- ✅ Não depende de timing
- ✅ Funciona mesmo se JavaScript não injetar no DOM

## 🚀 Próximos Passos

### Se v127 Funcionar:
1. ✅ Marcar como estável
2. ✅ Aplicar mesma técnica em PlayerEmbedAPI
3. ✅ Monitorar por 1 semana

### Se v127 Falhar:
1. ❌ Verificar se `crypto.subtle` está disponível no WebView
2. ❌ Tentar interceptar `fetch()` ou `XMLHttpRequest`
3. ❌ Considerar reverse engineering (última opção)

## 🔍 Troubleshooting

### Se não aparecer "[MegaEmbed v127] Interceptando..."
- WebView não está executando script
- Verificar se WebView está habilitado
- Verificar permissões

### Se aparecer "crypto.subtle não disponível"
- WebView não suporta Web Crypto API
- Tentar em dispositivo mais novo
- Ou fazer reverse engineering

### Se aparecer "decrypt() chamado" mas não captura URL
- JSON está em formato diferente
- Adicionar mais padrões de busca
- Verificar estrutura do JSON nos logs

---

**Versão**: 127  
**Build**: MaxSeries.cs3  
**Tipo**: Crypto Interception  
**Status**: Pronto para teste  
**Prioridade**: CRÍTICA
