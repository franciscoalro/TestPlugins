# Análise Logs ADB - v149 Problema CRÍTICO

## ❌ PROBLEMA IDENTIFICADO

### App Ainda Está na v148!
```
D MegaEmbedV7: === MEGAEMBED V7 v148 FIX WEBVIEW ===
```

**O app NÃO atualizou para v149!**

### WebView Retorna URL Original
```
D MegaEmbedV7: 📄 WebView interceptou: https://megaembed.link/#q5kra9
E MegaEmbedV7: ❌ URL capturada não é válida: https://megaembed.link/#q5kra9
```

```
D MegaEmbedV7: 📄 WebView interceptou: https://megaembed.link/#caojzl
E MegaEmbedV7: ❌ URL capturada não é válida: https://megaembed.link/#caojzl
```

### WebView ESTÁ Carregando Recursos
O WebView está funcionando e carregando:
```
I WebViewResolver: Loading WebView URL: https://megaembed.link/api/v1/info?id=q5kra9
I WebViewResolver: Loading WebView URL: https://megaembed.link/assets/index-CZ_ja_1t.js
I WebViewResolver: Loading WebView URL: https://megaembed.link/assets/prod-cvEtvBo1.js
I WebViewResolver: Loading WebView URL: https://megaembed.link/assets/vidstack-hls-BcPzC22e.js
```

**MAS** o interceptor NÃO está capturando essas URLs!

## 🔍 Causa Raiz

1. **App não atualizou**: Ainda está em v148
2. **Interceptação falha**: Regex não captura `/api/v1/info` ou assets
3. **Timeout**: WebView espera 15s e retorna URL original

## ✅ Solução

### 1. Atualizar App para v149

**Opção A: Via Cloudstream**
```
Settings → Extensions → MaxSeries → Update
```

**Opção B: Manual (RECOMENDADO)**
```bash
cd C:\Users\KYTHOURS\Desktop\brcloudstream
adb install -r MaxSeries\build\MaxSeries.cs3
```

### 2. Verificar Versão Instalada
```bash
adb logcat -c
adb logcat | findstr "MEGAEMBED V7"
```

**Deve mostrar:**
```
D MegaEmbedV7: === MEGAEMBED V7 v149 HÍBRIDO ===
```

**NÃO deve mostrar:**
```
D MegaEmbedV7: === MEGAEMBED V7 v148 FIX WEBVIEW ===
```

### 3. Testar Novamente

Após atualizar para v149:
1. Abrir Cloudstream
2. Selecionar episódio
3. Verificar logs

**Logs esperados v149:**
```
D MegaEmbedV7: === MEGAEMBED V7 v149 HÍBRIDO ===
D MegaEmbedV7: 🔍 Iniciando WebView HÍBRIDO (Script + additionalUrls + Interceptação)...
D MegaEmbedV7: 📱 Script capturou: https://...
D MegaEmbedV7: ✅ Usando URL do script (prioridade)
```

## 📊 Comparação

| Aspecto | v148 (ATUAL) | v149 (ESPERADO) |
|---------|--------------|-----------------|
| Versão no log | v148 FIX WEBVIEW | v149 HÍBRIDO |
| Script JavaScript | ❌ Nenhum | ✅ Completo |
| additionalUrls | ❌ Nenhum | ✅ 6 padrões |
| Interceptação | Apenas /v4/ | /v4/ + /api/v1/ |
| Resultado | URL original | URL de vídeo |

## 🎯 Próximos Passos

1. **URGENTE**: Instalar v149 manualmente
   ```bash
   adb install -r MaxSeries\build\MaxSeries.cs3
   ```

2. Verificar versão nos logs
   ```bash
   adb logcat | findstr "v149 HÍBRIDO"
   ```

3. Testar vídeos:
   - q5kra9 (testado e falhou em v148)
   - caojzl (testado e falhou em v148)

4. Capturar novos logs com v149

## 📝 Observações

### URLs que DEVERIAM ser Capturadas
```
https://megaembed.link/api/v1/info?id=q5kra9
https://megaembed.link/api/v1/info?id=caojzl
```

Essas URLs contêm as informações do vídeo, mas v148 não as intercepta porque:
- Regex v148: `https?://[^/]+/v4/[^"'\s]+` (apenas /v4/)
- Regex v149: Inclui `/api/v1/info` e `/api/v1/video` em additionalUrls

### Por Que v148 Falha
1. Regex muito específico (apenas /v4/)
2. Sem JavaScript para buscar no HTML
3. Sem additionalUrls para APIs
4. Timeout 15s → retorna URL original

### Por Que v149 Deve Funcionar
1. Script JavaScript busca variáveis globais
2. additionalUrls captura `/api/v1/info`
3. Interceptação de /v4/ como fallback
4. Timeout 20s (mais tempo)
5. Validação flexível (aceita index, cf-master, .txt)

---

**Data**: 2026-01-20 22:11  
**Problema**: App não atualizou para v149 (ainda em v148)  
**Solução**: Instalar v149 manualmente via ADB  
**Status**: ⏳ AGUARDANDO ATUALIZAÇÃO
