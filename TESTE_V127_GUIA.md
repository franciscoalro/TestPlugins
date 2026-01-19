# Guia de Teste - MaxSeries v127

## 📅 Data: 18/01/2026 - 21:45

## 🎯 O Que Mudou

### v127: Crypto Interception ⭐
- **Intercepta `crypto.subtle.decrypt()`** no WebView
- Captura URL do vídeo APÓS descriptografia
- Não precisa aguardar URL aparecer no DOM
- Mais confiável que v126

## 📋 Passo a Passo

### 1. Instalar v127
```powershell
cd C:\Users\KYTHOURS\Desktop\brcloudstream
adb install -r MaxSeries\build\MaxSeries.cs3
```

**Resultado esperado**:
```
Success
```

### 2. Iniciar Monitoramento
```powershell
$env:Path += ";D:\Android\platform-tools"
adb logcat -c
adb logcat | Select-String -Pattern "MegaEmbed|PlayerEmbed|WebViewResolver" -CaseSensitive:$false
```

### 3. Testar no App
1. Abrir **CloudStream**
2. Ir em **Configurações** → **Extensões**
3. Verificar: **MaxSeries v127** instalado
4. Voltar para tela inicial
5. Buscar: **"Terra de Pecados"**
6. Selecionar série
7. Clicar em **Episódio 1**
8. Tentar reproduzir

### 4. Analisar Logs

#### ✅ SUCESSO - Crypto Interception
```
MegaEmbedExtractorV5_v127: === MEGAEMBED V5 CRYPTO INTERCEPTION (v127) ===
MegaEmbedExtractorV5_v127: 🔍 [0/6] Tentando Crypto Interception...
MegaEmbedExtractorV5_v127: 🔐 Iniciando WebView com interceptação crypto...

WebViewResolver: [MegaEmbed v127] Interceptando crypto.subtle.decrypt...
WebViewResolver: [MegaEmbed v127] ✅ Interceptação ativada
WebViewResolver: [MegaEmbed v127] decrypt() chamado
WebViewResolver: [MegaEmbed v127] Algorithm: {name: "AES-CBC", ...}
WebViewResolver: [MegaEmbed v127] Descriptografado: {"url":"https://.../.txt",...}
WebViewResolver: [MegaEmbed v127] JSON keys: ["url", "title", "duration"]
WebViewResolver: [MegaEmbed v127] ✅ URL encontrada: https://.../.txt

MegaEmbedExtractorV5_v127: 📜 Crypto Interception capturou: https://.../.txt
MegaEmbedExtractorV5_v127: 🎯 Crypto Interception funcionou: https://.../.txt
MegaEmbedExtractorV5_v127: ✅ Crypto Interception funcionou!

MaxSeriesProvider: ✅ ExtractorLink criado: MegaEmbed - Auto
```

#### ❌ FALHA - Timeout
```
MegaEmbedExtractorV5_v127: 🔍 [0/6] Tentando Crypto Interception...
WebViewResolver: [MegaEmbed v127] Aguardando... (5s)
WebViewResolver: [MegaEmbed v127] Aguardando... (10s)
WebViewResolver: [MegaEmbed v127] Aguardando... (15s)
...
WebViewResolver: [MegaEmbed v127] ⏱️ Timeout após 60 segundos
MegaEmbedExtractorV5_v127: ⚠️ Crypto Interception: Nenhuma URL capturada
MegaEmbedExtractorV5_v127: 🔍 [1/6] Tentando Direct API...
```

#### ⚠️ PROBLEMA - crypto.subtle não disponível
```
WebViewResolver: [MegaEmbed v127] crypto.subtle não disponível
MegaEmbedExtractorV5_v127: ⚠️ Crypto Interception: Nenhuma URL capturada
```

## 🔍 Diagnóstico

### Cenário 1: Crypto Interception Funciona ✅
**Logs mostram**:
- `[MegaEmbed v127] decrypt() chamado`
- `[MegaEmbed v127] ✅ URL encontrada`
- `ExtractorLink criado`

**Resultado**: ✅ v127 resolveu o problema!  
**Ação**: Marcar como estável, monitorar por 1 semana

---

### Cenário 2: Timeout (60s) ❌
**Logs mostram**:
- `[MegaEmbed v127] Aguardando...`
- `[MegaEmbed v127] ⏱️ Timeout`
- Nenhum `decrypt() chamado`

**Problema**: JavaScript não está chamando `crypto.subtle.decrypt()`  
**Possíveis causas**:
1. Site mudou método de descriptografia
2. WebView não está executando JavaScript
3. Página não carregou completamente

**Ação**: Verificar se PlayerEmbedAPI funciona (fallback)

---

### Cenário 3: crypto.subtle não disponível ❌
**Logs mostram**:
- `[MegaEmbed v127] crypto.subtle não disponível`

**Problema**: WebView não suporta Web Crypto API  
**Possíveis causas**:
1. Dispositivo muito antigo (Android < 6.0)
2. WebView desatualizado
3. Permissões faltando

**Ação**: 
1. Atualizar WebView do dispositivo
2. Ou testar em dispositivo mais novo
3. Ou fazer reverse engineering (última opção)

---

### Cenário 4: decrypt() chamado mas não captura URL ❌
**Logs mostram**:
- `[MegaEmbed v127] decrypt() chamado`
- `[MegaEmbed v127] Descriptografado: ...`
- `[MegaEmbed v127] Não é JSON` ou `JSON keys: ...`
- Mas não mostra `✅ URL encontrada`

**Problema**: JSON está em formato diferente  
**Ação**: Copiar JSON dos logs e analisar estrutura

---

## 📊 Comparação de Versões

| Versão | Estratégia | Timeout | Resultado Esperado |
|--------|-----------|---------|-------------------|
| v124 | Regex sssrr.org | 30s | ❌ WebView não faz requests |
| v125 | Direct API | - | ❌ API criptografada |
| v126 | WebView 120s | 120s | ❌ JS não descriptografa |
| v127 | **Crypto Interception** | 60s | ⏳ **Testando agora** |

## 🚀 Próximos Passos

### Se v127 Funcionar:
1. ✅ Aplicar mesma técnica em PlayerEmbedAPI
2. ✅ Criar v128 com ambos melhorados
3. ✅ Monitorar estabilidade

### Se v127 Falhar:
1. ❌ Analisar logs para entender por quê
2. ❌ Tentar interceptar `fetch()` ou `XMLHttpRequest`
3. ❌ Considerar reverse engineering da chave AES

## 📝 Comandos Úteis

### Instalar
```powershell
adb install -r MaxSeries\build\MaxSeries.cs3
```

### Monitorar (Simples)
```powershell
$env:Path += ";D:\Android\platform-tools"
adb logcat | Select-String "MegaEmbed"
```

### Monitorar (Completo)
```powershell
$env:Path += ";D:\Android\platform-tools"
adb logcat | Select-String -Pattern "MegaEmbed|PlayerEmbed|WebViewResolver|ExtractorLink" -CaseSensitive:$false
```

### Limpar Logs
```powershell
adb logcat -c
```

### Verificar Dispositivo
```powershell
adb devices
```

---

**Versão**: 127  
**Status**: Aguardando teste  
**Prioridade**: CRÍTICA  
**Tempo estimado de teste**: 5-10 minutos
